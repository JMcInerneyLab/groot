"""
MVC architecture.

Classes that manage the view of the model.
"""
from typing import Dict, FrozenSet, Iterator, List, Optional, Tuple, Set

from PyQt5.QtCore import QPointF, QRect, QRectF, Qt, QPoint
from PyQt5.QtGui import QBrush, QColor, QFontMetrics, QLinearGradient, QPainter, QPolygonF
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QStyleOptionGraphicsItem, QWidget

import groot as gr
from groot_gui.lego.support import ColourBlock, DRAWING, LookupTable
from mhelper import MEnum, array_helper, misc_helper, override, Event
from mhelper_qt import Pens, qt_colour_helper


class ESMode( MEnum ):
    COMPONENT = 1
    GENE = 2
    DOMAIN = 3


class SideView:
    def __init__( self, model_view: "ModelView", domain: gr.Domain ) -> None:
        self.model_view = model_view
        self.domain = domain
        self.domain_views: List[DomainView] = []
        
        for domain_, domain_view in model_view.domain_views.items():
            if domain_.has_overlap( domain ):
                self.domain_views.append( domain_view )
        
        self.domain_views.sort( key = lambda domain_view: domain_view.domain.start )
        self.first_domain_view = self.domain_views[0]
        self.last_domain_view = self.domain_views[-1]
    
    
    def get_y( self ):
        return self.domain_views[0].window_rect().top()
    
    
    def average_colour( self ):
        return qt_colour_helper.average_colour( list( x.colour.colour for x in self.domain_views ) )
    
    
    def extract_points( self, backwards ):
        results = []
        
        if not backwards:
            for x in sorted( self.domain_views, key = lambda z: z.window_rect().left() ):
                r: QRect = x.window_rect()
                
                if x is self.first_domain_view:
                    results.append( QPoint( x.get_x_for_site( self.domain.start ), r.bottom() ) )
                else:
                    results.append( r.bottomLeft() )
                
                if x is self.last_domain_view:
                    results.append( QPoint( x.get_x_for_site( self.domain.end ), r.bottom() ) )
                else:
                    results.append( r.bottomRight() )
        else:
            for x in sorted( self.domain_views, key = lambda z: -z.window_rect().left() ):
                r: QRect = x.window_rect()
                
                if x is self.last_domain_view:
                    results.append( QPoint( x.get_x_for_site( self.domain.end ), r.top() ) )
                else:
                    results.append( r.topRight() )
                
                if x is self.first_domain_view:
                    results.append( QPoint( x.get_x_for_site( self.domain.start ), r.top() ) )
                else:
                    results.append( r.topLeft() )
        
        return results
    
    
    def top( self ):
        return self.domain_views[0].window_rect().top()
    
    
    def paint_to( self,
                  painter: QPainter,
                  lower: "SideView",
                  is_component_style: bool ) -> None:
        upper: SideView = self
        
        if not upper or not lower:
            return
        
        alpha = 64
        
        upper_points = upper.extract_points( False )
        lower_points = lower.extract_points( True )
        
        upper_colour = upper.average_colour()
        upper_colour = QColor( upper_colour )
        upper_colour.setAlpha( alpha )
        
        lower_colour = lower.average_colour()
        lower_colour = QColor( lower_colour )
        lower_colour.setAlpha( alpha )
        
        left = min( upper_points[0].x(), lower_points[-1].x() )
        # right = max( upper_points[ -1 ].x(), lower_points[ 0 ].x() )
        top = min( x.y() for x in upper_points )
        bottom = max( x.x() for x in lower_points )
        
        gradient = QLinearGradient( left, top, left, bottom )
        gradient.setColorAt( 0, upper_colour )
        gradient.setColorAt( 1, lower_colour )
        
        if is_component_style:
            painter.setBrush( QBrush( gradient ) )
            painter.setPen( Qt.NoPen )
        else:
            painter.setBrush( QBrush( gradient ) )
            painter.setPen( DRAWING.EDGE_LINE )
        
        painter.drawPolygon( QPolygonF( upper_points + lower_points + [upper_points[0]] ) )


class ComponentView:
    """
    View of a component.
    
    This paints a simplified view of the edges between its domains.
    """
    
    
    def __init__( self, owner: "OverlayView", component: gr.Component ) -> None:
        self.owner: OverlayView = owner
        self.model_view: ModelView = self.owner.view_model
        self.component = component
        self.sides: List[SideView] = []
        
        if component.minor_domains:
            for domain in component.minor_domains:
                self.sides.append( SideView( self.model_view, domain ) )
    
    
    def iter_domain_views( self ):
        for x in self.sides:
            yield from x.domain_views
    
    
    def paint_component( self, painter: QPainter ) -> None:
        """
        Paint component edges
        """
        if len( self.model_view.selection ) != 1:
            return
        
        if not any( x.is_selected for x in self.iter_domain_views() ):
            return
        
        sides = sorted( self.sides, key = lambda x: x.get_y() )
        
        for a, b in array_helper.lagged_iterate( sides ):
            a.paint_to( painter, b, True )


class DomainView( QGraphicsItem ):
    """
    The basic and only interactive unit of the view.
    Paints a domain.
    
    We have an `is_selected` variable.
    This is independent and used in lieu of either Qt's selection or the selection on the groot form.   
    """
    
    
    def __init__( self,
                  domain: gr.UserDomain,
                  gene_view: "GeneView",
                  positional_index: int,
                  precursor: Optional["DomainView"] ) -> None:
        """
        CONSTRUCTOR
        
        :param domain:             Domain to view 
        :param gene_view:              Owning view 
        :param positional_index:        Index of domain within gene 
        :param precursor:               Previous domain, or None 
        """
        assert isinstance( domain, gr.UserDomain )
        
        #
        # SUPER
        #
        super().__init__()
        self.setZValue( DRAWING.Z_GENE )
        
        #
        # FIELDS
        #
        self.gene_view = gene_view
        self.model_view = gene_view.model_view
        self.sibling_next: DomainView = None
        self.sibling_previous: DomainView = precursor
        self.domain: gr.UserDomain = domain
        self.mousedown_original_pos: QPointF = None
        self.mousemove_label: str = None
        self.mousemove_snapline: Tuple[int, int] = None
        self.mousedown_move_all = False
        self.index = positional_index
        self.is_selected = False
        self.colour = DRAWING.DEFAULT_COLOUR
        
        #
        # POSITION
        #
        table = gene_view.model_view.lookup_table
        self.rect = QRectF( 0, 0, domain.length * table.letter_size, table.gene_height )
        
        self.load_state()
        
        #
        # PRECURSOR
        #
        if precursor:
            precursor.sibling_next = self
        
        #
        # COMPONENTS
        #
        self.components: List[gr.Component] = self.model_view.model.components.find_components_for_minor_domain( self.domain )
    
    
    def get_x_for_site( self, site ):
        offset = site - self.domain.start
        offset *= self.model_view.lookup_table.letter_size
        return self.x() + offset
    
    
    @property
    def options( self ) -> gr.GlobalOptions:
        return gr.global_view.options()
    
    
    @property
    def model( self ) -> gr.Model:
        return self.model_view.model
    
    
    def load_state( self ):
        """
        Loads the state (position and colour) of this domain view from the options.
        If there is no saved state, the default is applied.
        """
        ac = (self.domain.gene.index, self.domain.start)
        position = self.model.lego_domain_positions.get( ac )
        
        if not isinstance( position, dict ):
            self.reset_state()
            return
        
        x = position.get( "x", 0 )
        y = position.get( "y", 0 )
        c = position.get( "c", DRAWING.DEFAULT_COLOUR.colour.name() )
        
        self.setPos( x, y )
        self.colour = ColourBlock( QColor( c ) )
    
    
    def save_state( self ):
        """
        Saves the state (position) of this domain view to the options.
        """
        ac = (self.domain.gene.index, self.domain.start)
        self.model.lego_domain_positions[ac] = { "x": self.pos().x(),
                                                 "y": self.pos().y(),
                                                 "c": self.colour.colour.name() }
    
    
    def reset_state( self ):
        """
        Resets the state (position and colour) of this domain view to the default.
        The reset state is automatically saved to the options.
        """
        table = self.gene_view.model_view.lookup_table
        precursor = self.sibling_previous
        domain = self.domain
        
        if precursor:
            x = precursor.window_rect().right()
            y = precursor.window_rect().top()
        else:
            x = domain.start * table.letter_size
            y = domain.gene.index * (table.gene_ysep + table.gene_height)
        
        self.setPos( x, y )
        self.colour = DRAWING.DEFAULT_COLOUR
        self.save_state()
    
    
    @override
    def boundingRect( self ) -> QRectF:
        return self.rect
    
    
    @override
    def paint( self, painter: QPainter, *args, **kwargs ):
        """
        Paint the domains
        """
        r = self.rect
        painter.setBrush( self.colour.brush )
        painter.setPen( self.colour.pen )
        painter.drawRect( r )
        
        is_selected = self.is_selected
        
        # Movement is allowed if we have enabled it
        move_enabled = misc_helper.coalesce( self.options.lego_move_enabled, self.gene_view.model_view.user_move_enabled )
        
        # Draw the piano roll unless we're moving
        if self.options.lego_view_piano_roll is False or move_enabled:
            draw_piano_roll = False
        elif self.options.lego_view_piano_roll is None:
            draw_piano_roll = is_selected
        else:
            draw_piano_roll = not is_selected
        
        # Draw the selection bars, unless the piano roll is indicative of this already
        draw_sel_bars = is_selected and not draw_piano_roll
        
        # Selection bars
        # (A blue box inside the gene box)
        if draw_sel_bars:
            self.__paint_selection_rect( painter )
        
        # Movement bars
        # (The same as the selection bars but dotted in red and cyan)
        if move_enabled and is_selected:
            self.__paint_movement_rect( painter )
        
        # Piano roll
        # (A piano roll for genes)
        if draw_piano_roll:
            lookup_table = self.model_view.lookup_table
            letter_size = lookup_table.letter_size
            painter.setPen( Qt.NoPen )
            painter.setBrush( DRAWING.PIANO_ROLL_SELECTED_BACKGROUND if is_selected else DRAWING.PIANO_ROLL_UNSELECTED_BACKGROUND )
            OFFSET_X = letter_size
            rect_width = self.rect.width()
            rect_height = lookup_table.count * letter_size
            painter.drawRect( 0, OFFSET_X, rect_width, rect_height )
            
            array = self.domain.site_array
            
            if not array:
                painter.setPen( Pens.RED )
                painter.drawLine( 0, 0, rect_width, rect_height )
                painter.drawLine( 0, rect_height, rect_width, 0 )
            else:
                for i, c in enumerate( array ):
                    pos = lookup_table.letter_order_table.get( c )
                    
                    if pos is not None:
                        painter.setPen( lookup_table.letter_colour_table.get( c, DRAWING.GENE_DEFAULT_FG ) )
                        painter.drawEllipse( i * letter_size, pos * letter_size + OFFSET_X, letter_size, letter_size )
        
        # Snap-lines, when moving
        if self.mousemove_snapline:
            x = self.mousemove_snapline[0] - self.pos().x()
            y = self.mousemove_snapline[1] - self.pos().y()
            painter.setPen( DRAWING.SNAP_LINE_2 )
            painter.drawLine( x, self.boundingRect().height() / 2, x, y )
            painter.setPen( DRAWING.SNAP_LINE )
            painter.drawLine( x, self.boundingRect().height() / 2, x, y )
            if not self.mousemove_label.startswith( "<" ):
                x -= QFontMetrics( painter.font() ).width( self.mousemove_label )
            
            if y < 0:
                y = self.rect.top() - DRAWING.TEXT_MARGIN
            else:
                y = self.rect.bottom() + DRAWING.TEXT_MARGIN + QFontMetrics( painter.font() ).xHeight()
            painter.setPen( DRAWING.TEXT_LINE )
            painter.drawText( QPointF( x, y ), self.mousemove_label )  # Mouse snapline position
        elif self.mousemove_label:
            painter.setPen( DRAWING.TEXT_LINE )
            painter.drawText( QPointF( self.rect.left() + DRAWING.TEXT_MARGIN, self.rect.top() - DRAWING.TEXT_MARGIN ), self.mousemove_label )  # Mouse position
        
        if not move_enabled:
            # Positions (when not in move mode)
            if misc_helper.coalesce( self.options.lego_view_positions, is_selected ):
                # Draw position
                if self.sibling_previous is None or self.sibling_next is None or self.sibling_previous.rect.width() > 32:
                    self.__draw_position( painter )
            
            # Domains (when not in move mode)
            if misc_helper.coalesce( self.options.lego_view_components, is_selected ):
                self.__draw_component_name( painter )
    
    
    def __draw_component_name( self, painter: QPainter ):
        text = ", ".join( str( x ) for x in self.components )
        x = (self.rect.left() + self.rect.right()) / 2 - QFontMetrics( painter.font() ).width( text ) / 2
        y = self.rect.top() - DRAWING.TEXT_MARGIN
        
        painter.setPen( DRAWING.COMPONENT_PEN )
        painter.setBrush( 0 )
        painter.drawText( QPointF( x, y ), text )
    
    
    def __draw_position( self, painter: QPainter ):
        text = str( self.domain.start )
        lx = self.rect.left() - QFontMetrics( painter.font() ).width( text ) / 2
        
        painter.setPen( DRAWING.POSITION_TEXT )
        painter.drawText( QPointF( lx, self.rect.top() - DRAWING.TEXT_MARGIN ), text )
    
    
    def __paint_movement_rect( self, painter: QPainter ):
        r = self.rect
        MARGIN = 4
        painter.setBrush( 0 )
        painter.setPen( DRAWING.MOVE_LINE )
        painter.drawRect( r.left() + MARGIN, r.top() + MARGIN, r.width() - MARGIN * 2, r.height() - MARGIN * 2 )
        painter.setPen( DRAWING.MOVE_LINE_SEL )
        painter.drawRect( r.left() + MARGIN, r.top() + MARGIN, r.width() - MARGIN * 2, r.height() - MARGIN * 2 )
        # Black start/end when in movement mode if domain isn't adjacent to its siblings
        if self.sibling_next and self.sibling_next.window_rect().left() != self.window_rect().right():
            MARGIN = 8
            painter.setPen( DRAWING.DISJOINT_LINE )
            painter.drawLine( r.right(), r.top() - MARGIN, r.right(), r.bottom() + MARGIN )
        if self.sibling_previous and self.sibling_previous.window_rect().right() != self.window_rect().left():
            MARGIN = 8
            painter.setPen( DRAWING.DISJOINT_LINE )
            painter.drawLine( r.left(), r.top() - MARGIN, r.left(), r.bottom() + MARGIN )
    
    
    def __paint_selection_rect( self, painter: QPainter ):
        r = self.rect
        MARGIN = 4
        painter.setBrush( 0 )
        painter.setPen( DRAWING.SELECTION_LINE )
        painter.drawRect( r.left() + MARGIN, r.top() + MARGIN, r.width() - MARGIN * 2, r.height() - MARGIN * 2 )
    
    
    def __is_draw_position( self, is_selected ):
        return misc_helper.coalesce( self.options.lego_view_positions, is_selected )
    
    
    def __draw_next_sibling_position( self, is_selected ):
        ns = self.sibling_next
        
        if ns is None:
            return False
        
        if not ns.__is_draw_position( is_selected ):
            return False
        
        return ns.pos().x() == self.window_rect().right()
    
    
    def window_rect( self ) -> QRectF:
        result = self.boundingRect().translated( self.scenePos() )
        assert result.left() == self.pos().x(), "{} {}".format( self.window_rect().left(), self.pos().x() )  # todo: remove
        assert result.top() == self.pos().y()
        return result
    
    
    def mousePressEvent( self, m: QGraphicsSceneMouseEvent ):
        """
        OVERRIDE
        Mouse press on domain view
        i.e. Use clicks a domain
        """
        if m.buttons() & Qt.LeftButton:
            # Remember the initial position items in case we drag stuff
            # - do this for all items because it's still possible for the selection to change post-mouse-down
            for item in self.gene_view.domain_views.values():
                item.mousedown_original_pos = item.pos()
            
            # If ctrl or meta is down, add to the selection 
            if (m.modifiers() & Qt.ControlModifier) or (m.modifiers() & Qt.MetaModifier):
                toggle = True
            else:
                toggle = False
            
            if self.is_selected:
                # If we are selected stop, this confuses with dragging from a design perspective
                return
            
            self.model_view.handle_domain_clicked( self.domain, toggle )
    
    
    def mouseDoubleClickEvent( self, m: QGraphicsSceneMouseEvent ):
        """
        OVERRIDE
        Double click
        Just toggles "move enabled" 
        """
        self.model_view.user_move_enabled = not self.model_view.user_move_enabled
        self.model_view.scene.setBackgroundBrush( QBrush( QColor( 255, 255, 0 ) ) )
        self.model_view.scene.update()
    
    
    def focusInEvent( self, QFocusEvent ):
        self.setZValue( DRAWING.Z_FOCUS )
    
    
    def focusOutEvent( self, QFocusEvent ):
        self.setZValue( DRAWING.Z_GENE )
    
    
    def snaps( self ):
        for gene_view in self.gene_view.model_view.gene_views.values():
            for domain_view in gene_view.domain_views.values():
                if domain_view is not self:
                    left_snap = domain_view.scenePos().x()
                    right_snap = domain_view.scenePos().x() + domain_view.boundingRect().width()
                    yield left_snap, "Start of {}[{}]".format( domain_view.domain.gene, domain_view.domain.start ), domain_view.scenePos().y()
                    yield right_snap, "End of {}[{}]".format( domain_view.domain.gene, domain_view.domain.end ), domain_view.scenePos().y()
    
    
    def mouseMoveEvent( self, m: QGraphicsSceneMouseEvent ) -> None:
        if m.buttons() & Qt.LeftButton:
            if not misc_helper.coalesce( self.options.lego_move_enabled, self.model_view.user_move_enabled ) or self.mousedown_original_pos is None:
                return
            
            new_pos: QPointF = self.mousedown_original_pos + (m.scenePos() - m.buttonDownScenePos( Qt.LeftButton ))
            new_x = new_pos.x()
            new_y = new_pos.y()
            new_x2 = new_x + self.boundingRect().width()
            
            self.mousemove_label = "({0} {1})".format( new_pos.x(), new_pos.y() )
            self.mousemove_snapline = None
            
            x_snap_enabled = misc_helper.coalesce( self.options.lego_x_snap, not bool( m.modifiers() & Qt.ControlModifier ) )
            y_snap_enabled = misc_helper.coalesce( self.options.lego_y_snap, not bool( m.modifiers() & Qt.AltModifier ) )
            
            if x_snap_enabled:
                for snap_x, snap_label, snap_y in self.snaps():
                    if (snap_x - 8) <= new_x <= (snap_x + 8):
                        new_x = snap_x
                        self.mousemove_label = "<-- " + snap_label
                        self.mousemove_snapline = snap_x, snap_y
                        break
                    elif (snap_x - 8) <= new_x2 <= (snap_x + 8):
                        new_x = snap_x - self.boundingRect().width()
                        self.mousemove_label = snap_label + " -->"
                        self.mousemove_snapline = snap_x, snap_y
                        break
            
            if y_snap_enabled:
                ysep = self.rect.height()
                yy = (self.rect.height() + ysep)
                new_y += yy / 2
                new_y = new_y - new_y % yy
            
            new_pos.setX( new_x )
            new_pos.setY( new_y )
            
            self.setPos( new_pos )
            self.save_state()
            
            delta_x = new_x - self.mousedown_original_pos.x()
            delta_y = new_y - self.mousedown_original_pos.y()
            
            selected_items = self.model_view.get_selected_userdomain_views()
            
            for selected_item in selected_items:
                if selected_item is not self and selected_item.mousedown_original_pos is not None:
                    selected_item.setPos( selected_item.mousedown_original_pos.x() + delta_x, selected_item.mousedown_original_pos.y() + delta_y )
                    selected_item.save_state()
            
            self.model_view.overlay_view.update()
    
    
    def mouseReleaseEvent( self, m: QGraphicsSceneMouseEvent ):
        self.mousemove_label = None
        self.mousemove_snapline = None
        self.update()
        pass  # suppress default mouse handling implementation
    
    
    def __repr__( self ):
        return "<<View of '{}' at ({},{})>>".format( self.domain, self.window_rect().left(), self.window_rect().top() )


class GeneView:
    """
    Views a gene
    """
    
    
    def __init__( self, owner_model_view: "ModelView", gene: gr.Gene ) -> None:
        """
        :param owner_model_view: Owning view
        :param gene: The gene we are viewing
        """
        
        self.model_view = owner_model_view
        self.gene = gene
        self.domain_views: Dict[gr.UserDomain, DomainView] = { }
        self._recreate()
    
    
    def get_sorted_userdomain_views( self ):
        return sorted( self.domain_views.values(), key = lambda y: y.domain.start )
    
    
    def _recreate( self ):
        # Remove existing items
        for x in self.domain_views:
            self.model_view.scene.removeItem( x )
        
        self.domain_views.clear()
        
        # Add new items
        previous_domain = None
        
        userdomains_ = self.model_view.model.user_domains.by_gene( self.gene )
        
        for userdomain in userdomains_:
            domain_view = DomainView( userdomain, self, len( self.domain_views ), previous_domain )
            self.domain_views[userdomain] = domain_view
            self.model_view.scene.addItem( domain_view )
            previous_domain = domain_view
    
    
    def paint_name( self, painter: QPainter ):
        """
        Paints the name of this gene.
        """
        if not misc_helper.coalesce( gr.global_view.options().lego_view_names, any( x.is_selected for x in self.domain_views.values() ) ):
            return
        
        leftmost_domain = sorted( self.domain_views.values(), key = lambda xx: xx.pos().x() )[0]
        text = str( self.gene )
        
        # Add a sigil for outgroups
        if self.gene.position == gr.EPosition.OUTGROUP:
            text = "←" + text
        
        r = leftmost_domain.window_rect()
        x = r.left() - DRAWING.TEXT_MARGIN - QFontMetrics( painter.font() ).width( text )
        y = r.top() + r.height() / 2
        painter.setPen( DRAWING.DARK_TEXT )
        painter.drawText( QPointF( x, y ), text )


class EdgeView:
    def __init__( self, owner_view: "OverlayView", edge: gr.Edge ):
        self.owner_view = owner_view
        self.model_view = owner_view.view_model
        self.edge = edge
        
        self.left_view = SideView( self.model_view, edge.left )
        self.right_view = SideView( self.model_view, edge.right )
    
    
    def iter_domain_views( self ):
        yield from self.left_view.domain_views
        yield from self.right_view.domain_views
    
    
    def paint_edge( self, painter: QPainter ):
        if self.edge not in self.model_view.selected_edges:
            return
        
        if self.left_view.get_y() < self.right_view.get_y():
            self.left_view.paint_to( painter, self.right_view, False )
        else:
            self.right_view.paint_to( painter, self.left_view, False )


class InterlinkView:
    """
                     ⤹ This bit!
    ┌──────────┬┄┄┄┬──────────┐
    │          │     │          │
    └──────────┴┄┄┄┴──────────┘
    """
    
    
    def __init__( self, owner_view: "OverlayView", left: DomainView, right: DomainView ) -> None:
        self.owner_view = owner_view
        self.left = left
        self.right = right
    
    
    def paint_interlink( self, painter: QPainter ):
        painter.setPen( DRAWING.NO_SEQUENCE_LINE )
        painter.setBrush( DRAWING.NO_SEQUENCE_FILL )
        
        # Draw my connection (left-right)
        precursor_rect = self.left.window_rect()
        my_rect = self.right.window_rect()
        
        if precursor_rect.right() == my_rect.left():
            return
        
        if my_rect.left() < precursor_rect.right():
            painter.drawLine( my_rect.left(), (my_rect.top() - 8), precursor_rect.right(), (precursor_rect.top() - 8) )
            painter.drawLine( my_rect.left(), (my_rect.bottom() + 8), precursor_rect.right(), (precursor_rect.bottom() + 8) )
            painter.drawLine( my_rect.left(), (my_rect.top() - 8), my_rect.left(), (my_rect.bottom() + 8) )
            painter.drawLine( precursor_rect.right(), (precursor_rect.top() - 8), precursor_rect.right(), (precursor_rect.bottom() + 8) )
        else:
            points = [QPointF( my_rect.left(), my_rect.top() + 8 ),  # a |x...|
                      QPointF( my_rect.left(), my_rect.bottom() - 8 ),  # b |x...|
                      QPointF( precursor_rect.right(), precursor_rect.bottom() - 8 ),  # b |...x|
                      QPointF( precursor_rect.right(), precursor_rect.top() + 8 )]  # a |...x|
            
            points.append( points[0] )
            
            painter.drawPolygon( QPolygonF( points ) )


class OverlayView( QGraphicsItem ):
    """
    This is a "global" view which manages all of the line things:
        * edge views.
        * interlinks (domain-domain)
        * components
    
    It is actually a single graphics item drawn over the top of everything else.
    Therefore, it is passive and doesn't react with the user in any way.
    """
    
    
    def __init__( self, view_model: "ModelView" ) -> None:
        super().__init__()
        self.setZValue( DRAWING.Z_EDGES )
        self.view_model = view_model
        self.component_views: Dict[gr.Component, ComponentView] = { }
        self.interlink_views: Dict[gr.Domain, InterlinkView] = { }
        self.edge_views: Dict[gr.Edge, EdgeView] = { }
        
        # Create the edge views
        for edge in view_model.model.edges:
            self.edge_views[edge] = EdgeView( self, edge )
        
        # Create the component views
        for component in view_model.model.components:
            self.component_views[component] = ComponentView( self, component )
        
        # Create our interlink views
        for gene_view in view_model.gene_views.values():
            for left, right in array_helper.lagged_iterate( gene_view.domain_views.values() ):
                self.interlink_views[left] = InterlinkView( self, left, right )
        
        # Our bounds encompass the totality of the model
        # - find this!
        self.rect = QRectF( 0, 0, 0, 0 )
        
        for gene_view in view_model.gene_views.values():
            for domain_view in gene_view.domain_views.values():
                r = domain_view.window_rect()
                
                if r.left() < self.rect.left():
                    self.rect.setLeft( r.left() )
                
                if r.right() > self.rect.right():
                    self.rect.setRight( r.right() )
                
                if r.top() < self.rect.top():
                    self.rect.setTop( r.top() )
                
                if r.bottom() > self.rect.bottom():
                    self.rect.setBottom( r.bottom() )
        
        MARGIN = 256
        self.rect.setTop( self.rect.top() - MARGIN * 2 )
        self.rect.setLeft( self.rect.left() - MARGIN * 2 )
        self.rect.setBottom( self.rect.bottom() + MARGIN )
        self.rect.setRight( self.rect.right() + MARGIN )
    
    
    def boundingRect( self ):
        return self.rect
    
    
    def paint( self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None ) -> None:
        """
        Paint all edges
        """
        # Draw all the edges
        for edge_view in self.edge_views.values():
            edge_view.paint_edge( painter )
        
        # Draw all the components
        for component in self.component_views.values():
            component.paint_component( painter )
        
        # Draw all the interlinks
        for interlink in self.interlink_views.values():
            interlink.paint_interlink( painter )
        
        # Draw all the names
        for gene_view in self.view_model.gene_views.values():
            gene_view.paint_name( painter )


class ModelView:
    """
    Manages the view of the model.
    
    Holds all of the other views and creates the :ivar:`scene` (:class:`QGraphicsScene`).
    """
    
    
    class CustomGraphicsScene( QGraphicsScene ):
        def __init__( self, parent ):
            super().__init__()
            self.parent: ModelView = parent
        
        
        def mousePressEvent( self, e: QGraphicsSceneMouseEvent ) -> None:
            super().mousePressEvent( e )
            p: QPointF = e.pos()
            
            for domain_view in self.parent.domain_views.values():
                r = domain_view.rect
                if r.left() <= p.x() <= r.right() and r.top() <= p.y() <= r.bottom():
                    return
            
            self.parent.handle_domain_clicked( None, False )
    
    
    def handle_domain_clicked( self, domain: Optional[gr.UserDomain], toggle ):
        if domain is None:
            select = frozenset()
        elif toggle:
            if domain in self.selection:
                # Deactivate
                select = self.selection - { domain }
            else:
                # Activate
                select = self.selection.union( { domain } )
        else:
            select = frozenset( { domain } )
        
        # Whenever we change the selection disable movement
        self.user_move_enabled = False
        self.selection = select
        self.scene.update()
    
    
    @property
    def selection( self ) -> FrozenSet[gr.UserDomain]:
        return self.__selection
    
    
    @property
    def all( self ) -> FrozenSet[gr.UserDomain]:
        return frozenset( self.domain_views.keys() )
    
    
    @selection.setter
    def selection( self, value: FrozenSet[gr.UserDomain] ):
        assert isinstance( value, frozenset ), value
        
        for domain in self.__selection:
            self.domain_views[domain].is_selected = False
        
        self.__selection = value
        
        for domain in self.__selection:
            self.domain_views[domain].is_selected = True
        
        self.selected_edges = set( self.model.edges.iter_touching( self.__selection ) )
        
        self.on_selection_changed( value )
    
    
    def __init__( self, form, view: QGraphicsView, model: gr.Model ) -> None:
        """
        CONSTRUCTOR 
        :param view:                    To where we draw the view
        :param model:                   The model we represent
        """
        from groot_gui.forms.frm_lego import FrmLego
        
        self.form: FrmLego = form
        self.lookup_table = LookupTable( model.site_type )
        self.view: QGraphicsView = view
        self.model: gr.Model = model
        self.scene = self.CustomGraphicsScene( self )
        self.gene_views: Dict[gr.Gene, GeneView] = { }
        self.domain_views: Dict[gr.UserDomain, DomainView] = { }
        self.selected_edges: Set[gr.Edge] = set()
        self.overlay_view: OverlayView = None
        self.user_move_enabled = False
        self.__selection: FrozenSet[gr.UserDomain] = frozenset()
        self.legend: Dict[frozenset, ColourBlock] = { }
        self.on_selection_changed = Event()
        
        # Create the gene and domain views
        for gene in self.model.genes:
            item = GeneView( self, gene )
            self.gene_views[gene] = item
            self.domain_views.update( item.domain_views )
        
        # Create the edges view
        self.overlay_view = OverlayView( self )
        self.overlay_view.setZValue( -1 )
        self.scene.addItem( self.overlay_view )
    
    
    def find_userdomain_views_for_domain( self, domain: gr.Domain ) -> Iterator[DomainView]:
        for gene_view in self.gene_views.values():  # todo: this is terribly inefficient
            if gene_view.gene is not domain.gene:
                continue
            
            for domain_view in gene_view.domain_views.values():
                if domain_view.domain.has_overlap( domain ):
                    yield domain_view
    
    
    def find_component_view( self, component: gr.Component ) -> ComponentView:
        return self.overlay_view.component_views[component]
    
    
    def get_selected_userdomain_views( self ):
        return (x for x in self.domain_views.values() if x.is_selected)
    
    
    def save_all_states( self ):
        for domain_view in self.domain_views.values():
            domain_view.save_state()
