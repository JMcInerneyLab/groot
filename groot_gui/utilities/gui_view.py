"""
MVC architecture.

Classes that manage the view of the model.
"""
from typing import Dict, List, Optional, Tuple

from PyQt5.QtCore import QPointF, QRect, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFontMetrics, QLinearGradient, QPainter, QPolygonF
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QStyleOptionGraphicsItem, QWidget
from groot.data import global_view
from groot.data.global_view import GlobalOptions

from groot.data.model_interfaces import EPosition
from groot.data.model_core import LegoSubsequence
from groot import LegoModel, LegoUserDomain, LegoSequence, LegoComponent
from groot_gui.utilities.gui_view_support import ColourBlock, DRAWING, LookupTable
from mhelper import array_helper, misc_helper, override, MEnum
from mhelper_qt import Pens, qt_colour_helper


_LegoViewInfo_Edge_ = "LegoViewInfo_Edge"
_LegoView_AllEdges_ = "LegoView_AllEdges"
_LegoViewSequence_ = "LegoView_Sequence"
_LegoView_Subsequence_ = "LegoView_UserDomain"
_LegoViewModel_ = "LegoView_Model"


class ESMode( MEnum ):
    COMPONENT = 1
    GENE = 2
    DOMAIN = 3


class LegoViewInfo_Side:
    def __init__( self, userdomain_views: List["LegoView_UserDomain"] ) -> None:
        self.userdomain_views: List[LegoView_UserDomain] = userdomain_views
    
    
    def get_y( self ):
        return self.userdomain_views[0].window_rect().top()
    
    
    def average_colour( self ):
        return qt_colour_helper.average_colour( list( x.colour.colour for x in self.userdomain_views ) )
    
    
    def extract_points( self, backwards ):
        results = []
        
        if not backwards:
            for x in sorted( self.userdomain_views, key = lambda z: z.window_rect().left() ):
                r: QRect = x.window_rect()
                results.append( r.bottomLeft() )
                results.append( r.bottomRight() )
        else:
            for x in sorted( self.userdomain_views, key = lambda z: -z.window_rect().left() ):
                r: QRect = x.window_rect()
                results.append( r.topRight() )
                results.append( r.topLeft() )
        
        return results
    
    
    def top( self ):
        return self.userdomain_views[0].window_rect().top()
    
    
    @staticmethod
    def paint_to( painter: QPainter,
                  upper: "LegoViewInfo_Side",
                  lower: "LegoViewInfo_Side",
                  is_highlighted: bool ) -> None:
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
        
        if is_highlighted:
            painter.setBrush( QBrush( gradient ) )
            painter.setPen( Qt.NoPen )
        else:
            painter.setBrush( Qt.NoBrush )
            painter.setPen( DRAWING.EDGE_LINE )
        
        painter.drawPolygon( QPolygonF( upper_points + lower_points + [upper_points[0]] ) )


class LegoView_Component:
    """
    View of a component
    """
    
    
    def __init__( self, owner: _LegoView_AllEdges_, component: LegoComponent ) -> None:
        # Collect the pertinent domain views
        domain_views: List[LegoView_UserDomain] = []
        
        for domain_view in owner.view_model.userdomain_views.values():
            for subsequence in component.minor_subsequences:
                if domain_view.domain.has_overlap( subsequence ):
                    domain_views.append( domain_view )
                    break
        
        self.owner: LegoView_AllEdges = owner
        self.component = component
        self.colour = ColourBlock( owner.next_colour() )
        
        # We have our "subsequence views", convert these to sides (1 side per gene)
        model = self.owner.view_model.model
        self.sides = []
        
        for sequence in model.sequences:
            p = []
            
            for domain_view in domain_views:
                if domain_view.domain.sequence is sequence:
                    p.append( domain_view )
            
            if p:
                self.sides.append( LegoViewInfo_Side( sorted( p, key = lambda x: x.domain.start ) ) )
    
    
    def paint_component( self, painter: QPainter ) -> None:
        """
        Paint edge group
        """
        sides = sorted( self.sides, key = lambda x: x.get_y() )
        
        for a, b in array_helper.lagged_iterate( sides ):
            LegoViewInfo_Side.paint_to( painter, a, b, True )


class LegoView_UserDomain( QGraphicsItem ):
    def __init__( self,
                  userdomain: LegoUserDomain,
                  owner_view: _LegoViewSequence_,
                  positional_index: int,
                  precursor: Optional[_LegoView_Subsequence_] ) -> None:
        """
        CONSTRUCTOR
        
        :param userdomain:             Subsequences to view 
        :param owner_view:              Owning view 
        :param positional_index:        Index of subsequence within sequence 
        :param precursor:               Previous subsequence, or None 
        """
        assert isinstance( userdomain, LegoUserDomain )
        
        #
        # SUPER
        #
        super().__init__()
        self.setZValue( DRAWING.Z_SEQUENCE )
        
        #
        # FIELDS
        #
        self.owner_sequence_view = owner_view
        self.sibling_next: LegoView_UserDomain = None
        self.sibling_previous: LegoView_UserDomain = precursor
        self.domain: LegoUserDomain = userdomain
        self.mousedown_original_pos: QPointF = None
        self.mousemove_label: str = None
        self.mousemove_snapline: Tuple[int, int] = None
        self.mousedown_move_all = False
        self.index = positional_index
        
        #
        # POSITION
        #
        table = owner_view.owner_model_view.lookup_table
        self.rect = QRectF( 0, 0, userdomain.length * table.letter_size, table.sequence_height )
        
        self.load_state()
        
        #
        # PRECURSOR
        #
        if precursor:
            precursor.sibling_next = self
        
        #
        # COMPONENTS
        #
        self.components: List[LegoComponent] = self.owner_model_view.model.components.find_components_for_minor_subsequence( self.domain )
    
    
    def is_in_global_selection( self ):
        selection = self.owner_model_view.form.actions.get_selection()
        return self.domain in selection
    
    
    @property
    def colour( self ) -> ColourBlock:
        """
        Subsequence colour.
        """
        
        if self.components:
            colour = None
            
            for component in self.components:
                try:
                    view = self.owner_model_view.find_component_view( component )
                except KeyError:
                    return DRAWING.ERROR_COLOUR
                except AttributeError:
                    return DRAWING.ERROR_COLOUR
                
                if colour is None:
                    colour = ColourBlock( view.colour.colour )
                else:
                    assert isinstance( colour, ColourBlock )
                    colour = colour.blend( view.colour.colour, 0.5 )
            
            assert colour is not None
            return colour
        else:
            return DRAWING.DEFAULT_COLOUR
    
    
    @property
    def owner_model_view( self ) -> "LegoView_Model":
        return self.owner_sequence_view.owner_model_view
    
    
    @property
    def options( self ) -> GlobalOptions:
        return global_view.options()
    
    
    @property
    def model( self ) -> LegoModel:
        return self.owner_model_view.model
    
    
    def load_state( self ):
        """
        Loads the state (position) of this domain view from the options.
        If there is no saved state, the default is applied.
        """
        position = self.model.lego_domain_positions.get( (self.domain.sequence.index, self.domain.start) )
        
        if position is None:
            self.reset_state()
        else:
            self.setPos( position[0], position[1] )
    
    
    def save_state( self ):
        """
        Saves the state (position) of this domain view to the options.
        """
        self.model.lego_domain_positions[(self.domain.sequence.index, self.domain.start)] = self.pos().x(), self.pos().y()
    
    
    def reset_state( self ):
        """
        Resets the state (position) of this domain view to the default.
        The reset state is automatically saved to the options.
        """
        table = self.owner_sequence_view.owner_model_view.lookup_table
        precursor = self.sibling_previous
        subsequence = self.domain
        
        if precursor:
            x = precursor.window_rect().right()
            y = precursor.window_rect().top()
        else:
            x = subsequence.start * table.letter_size
            y = subsequence.sequence.index * (table.sequence_ysep + table.sequence_height)
        
        self.setPos( x, y )
        self.save_state()
    
    
    @override
    def boundingRect( self ) -> QRectF:
        return self.rect
    
    
    @override
    def paint( self, painter: QPainter, *args, **kwargs ):
        """
        Paint the subsequence
        """
        r = self.rect
        painter.setBrush( self.colour.brush )
        painter.setPen( self.colour.pen )
        painter.drawRect( r )
        
        is_selected = self.is_in_global_selection()
        
        # Movement is allowed if we have enabled it
        move_enabled = misc_helper.coalesce( self.options.lego_move_enabled, self.owner_sequence_view.owner_model_view.user_move_enabled )
        
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
        # (A blue box inside the sequence box)
        if draw_sel_bars:
            MARGIN = 4
            painter.setBrush( 0 )
            painter.setPen( DRAWING.SELECTION_LINE )
            painter.drawRect( r.left() + MARGIN, r.top() + MARGIN, r.width() - MARGIN * 2, r.height() - MARGIN * 2 )
        
        # Movement bars
        # (The same as the selection bars but dotted in red and cyan)
        if move_enabled and is_selected:
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
        
        # Piano roll
        # (A piano roll for genes)
        if draw_piano_roll:
            lookup_table = self.owner_model_view.lookup_table
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
                        painter.setPen( lookup_table.letter_colour_table.get( c, DRAWING.SEQUENCE_DEFAULT_FG ) )
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
                    painter.setPen( DRAWING.POSITION_TEXT )
                    
                    text = str( self.domain.start )
                    lx = self.rect.left() - QFontMetrics( painter.font() ).width( text ) / 2
                    painter.setPen( DRAWING.TEXT_LINE )
                    painter.drawText( QPointF( lx, self.rect.top() - DRAWING.TEXT_MARGIN ), text )
            
            # Domains (when not in move mode)
            if misc_helper.coalesce( self.options.lego_view_components, is_selected ):
                    # Draw component name
                    painter.setPen( DRAWING.COMPONENT_PEN )
                    painter.setBrush( 0 )
                    text = "".join( str( x ) for x in self.components )
                    x = (self.rect.left() + self.rect.right()) / 2 - QFontMetrics( painter.font() ).width( text ) / 2
                    y = self.rect.top() - DRAWING.TEXT_MARGIN
                    painter.drawText( QPointF( x, y ), text )
    
    
    def __draw_position( self, is_selected ):
        return misc_helper.coalesce( self.options.lego_view_positions, is_selected )
    
    
    def __draw_next_sibling_position( self, is_selected ):
        ns = self.sibling_next
        
        if ns is None:
            return False
        
        if not ns.__draw_position( is_selected ):
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
        Mouse press on subsequence view
        i.e. Use clicks a subsequence
        """
        if m.buttons() & Qt.LeftButton:
            # Remember the initial position items in case we drag stuff
            # - do this for all items because it's still possible for the selection to change post-mouse-down
            for item in self.owner_sequence_view.userdomain_views.values():
                item.mousedown_original_pos = item.pos()
            
            # If ctrl or meta is down, add to the selection 
            if (m.modifiers() & Qt.ControlModifier) or (m.modifiers() & Qt.MetaModifier):
                toggle = True
            else:
                toggle = False
            
            if self.is_in_global_selection():
                # If we are selected stop, this confuses with dragging from a design perspective
                return
            
            self.owner_model_view.form.handle_domain_clicked( self.domain, toggle )
    
    
    def mouseDoubleClickEvent( self, m: QGraphicsSceneMouseEvent ):
        """
        OVERRIDE
        Double click
        Just toggles "move enabled" 
        """
        self.owner_model_view.user_move_enabled = not self.owner_model_view.user_move_enabled
        self.owner_model_view.form.ui.BTN_MOVE.setChecked( self.owner_model_view.user_move_enabled )
        self.owner_model_view.scene.setBackgroundBrush( QBrush( QColor( 255, 255, 0 ) ) )
        self.owner_model_view.scene.update()
    
    
    def focusInEvent( self, QFocusEvent ):
        self.setZValue( DRAWING.Z_FOCUS )
    
    
    def focusOutEvent( self, QFocusEvent ):
        self.setZValue( DRAWING.Z_SEQUENCE )
    
    
    def snaps( self ):
        for sequence_view in self.owner_sequence_view.owner_model_view.sequence_views.values():
            for subsequence_view in sequence_view.userdomain_views.values():
                if subsequence_view is not self:
                    left_snap = subsequence_view.scenePos().x()
                    right_snap = subsequence_view.scenePos().x() + subsequence_view.boundingRect().width()
                    yield left_snap, "Start of {}[{}]".format( subsequence_view.domain.sequence.accession, subsequence_view.domain.start ), subsequence_view.scenePos().y()
                    yield right_snap, "End of {}[{}]".format( subsequence_view.domain.sequence.accession, subsequence_view.domain.end ), subsequence_view.scenePos().y()
    
    
    def mouseMoveEvent( self, m: QGraphicsSceneMouseEvent ) -> None:
        if m.buttons() & Qt.LeftButton:
            if not misc_helper.coalesce( self.options.lego_move_enabled, self.owner_model_view.user_move_enabled ) or self.mousedown_original_pos is None:
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
            
            selected_items = self.owner_model_view.get_selected_userdomain_views()
            
            for selected_item in selected_items:
                if selected_item is not self and selected_item.mousedown_original_pos is not None:
                    selected_item.setPos( selected_item.mousedown_original_pos.x() + delta_x, selected_item.mousedown_original_pos.y() + delta_y )
                    selected_item.save_state()
            
            self.owner_model_view.edges_view.update()
    
    
    def mouseReleaseEvent( self, m: QGraphicsSceneMouseEvent ):
        self.mousemove_label = None
        self.mousemove_snapline = None
        self.update()
        pass  # suppress default mouse handling implementation
    
    
    def __repr__( self ):
        return "<<View of '{}' at ({},{})>>".format( self.domain, self.window_rect().left(), self.window_rect().top() )


class LegoView_Sequence:
    """
    Views a sequence
    """
    
    
    def __init__( self, owner_model_view: _LegoViewModel_, sequence: LegoSequence ) -> None:
        """
        :param owner_model_view: Owning view
        :param sequence: The sequence we are viewing
        """
        
        self.owner_model_view = owner_model_view
        self.sequence = sequence
        self.userdomain_views: Dict[LegoUserDomain, LegoView_UserDomain] = { }
        self._recreate()
    
    
    def get_sorted_userdomain_views( self ):
        return sorted( self.userdomain_views.values(), key = lambda y: y.domain.start )
    
    
    def _recreate( self ):
        # Remove existing items
        for x in self.userdomain_views:
            self.owner_model_view.scene.removeItem( x )
        
        self.userdomain_views.clear()
        
        # Add new items
        previous_subsequence = None
        
        userdomains_ = self.owner_model_view.model.user_domains.by_sequence( self.sequence )
        
        for userdomain in userdomains_:
            subsequence_view = LegoView_UserDomain( userdomain, self, len( self.userdomain_views ), previous_subsequence )
            self.userdomain_views[userdomain] = subsequence_view
            self.owner_model_view.scene.addItem( subsequence_view )
            previous_subsequence = subsequence_view
    
    
    def paint_name( self, painter: QPainter ):
        if not misc_helper.coalesce( global_view.options().lego_view_names, any( x.is_in_global_selection() for x in self.userdomain_views.values() ) ):
            return
        
        leftmost_subsequence = sorted( self.userdomain_views.values(), key = lambda xx: xx.pos().x() )[0]
        text = self.sequence.accession
        
        if self.sequence.position == EPosition.OUTGROUP:
            text = "←" + text
        if self.sequence.position == EPosition.ROOT:
            text = "↑" + text
        
        r = leftmost_subsequence.window_rect()
        x = r.left() - DRAWING.TEXT_MARGIN - QFontMetrics( painter.font() ).width( text )
        y = r.top() + r.height() / 2
        painter.drawText( QPointF( x, y ), text )


class LegoViewInfo_Interlink:
    """
                     ⤹ This bit!
    ┌──────────┬┄┄┄┬──────────┐
    │          │     │          │
    └──────────┴┄┄┄┴──────────┘
    """
    
    
    def __init__( self, owner_view: "LegoView_AllEdges", left: LegoView_UserDomain, right: LegoView_UserDomain ) -> None:
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


class LegoView_AllEdges( QGraphicsItem ):
    """
    This is a "global" view which manages all of the line things:
        * edge views.
        * empty legos (subsequence-subsequence)
        * components
    
    It is actually a single graphics item drawn over the top of everything else.
    Therefore, it is passive and doesn't react with the user in any way.
    """
    
    
    def __init__( self, view_model: "LegoView_Model" ) -> None:
        super().__init__()
        self.setZValue( DRAWING.Z_EDGES )
        self.__next_colour = -1
        self.view_model = view_model
        self.component_views: Dict[LegoComponent, LegoView_Component] = { }
        self.interlink_views: Dict[LegoSubsequence, LegoViewInfo_Interlink] = { }
        
        # Create the component views
        for component in view_model.model.components:
            self.component_views[component] = LegoView_Component( self, component )
        
        # Create our interlink views
        for sequence_view in view_model.sequence_views.values():
            for left, right in array_helper.lagged_iterate( sequence_view.userdomain_views.values() ):
                self.interlink_views[left] = LegoViewInfo_Interlink( self, left, right )
        
        # Our bounds encompass the totality of the model
        # - find this!
        self.rect = QRectF( 0, 0, 0, 0 )
        
        for sequence_view in view_model.sequence_views.values():
            for subsequence_view in sequence_view.userdomain_views.values():
                r = subsequence_view.window_rect()
                
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
    
    
    def next_colour( self ) -> QColor:
        self.__next_colour += 1
        
        if self.__next_colour >= len( DRAWING.COMPONENT_COLOURS ):
            self.__next_colour = 0
        
        return DRAWING.COMPONENT_COLOURS[self.__next_colour]
    
    
    def boundingRect( self ):
        return self.rect
    
    
    def paint( self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[QWidget] = None ) -> None:
        """
        Paint all edges
        """
        # Draw all the components
        for component in self.component_views.values():
            component.paint_component( painter )
        
        # Draw all the interlinks
        for interlink in self.interlink_views.values():
            interlink.paint_interlink( painter )
        
        # Draw all the names
        for sequence in self.view_model.sequence_views.values():
            sequence.paint_name( painter )


class LegoView_Model:
    """
    Manages the view of the model.
    
    Holds all of the other views and creates the :ivar:`scene` (:class:`QGraphicsScene`).
    """
    
    
    class CustomGraphicsScene( QGraphicsScene ):
        def __init__( self, parent ):
            super().__init__()
            self.parent: LegoView_Model = parent
        
        
        def mousePressEvent( self, e: QGraphicsSceneMouseEvent ) -> None:
            super().mousePressEvent( e )
            p: QPointF = e.pos()
            
            for dv in self.parent.userdomain_views.values():
                r = dv.window_rect()
                if r.left() <= p.x() <= r.right() and r.top() <= p.y() <= r.bottom():
                    return
            
            self.parent.form.handle_domain_clicked( None, False )
    
    
    def __init__( self, form, view: QGraphicsView, model: LegoModel ) -> None:
        """
        CONSTRUCTOR 
        :param view:                    To where we draw the view
        :param model:                   The model we represent
        """
        from groot_gui.forms.frm_lego import FrmLego
        
        self.form: FrmLego = form
        self.lookup_table = LookupTable( model.site_type )
        self.view: QGraphicsView = view
        self.model: LegoModel = model
        self.scene = self.CustomGraphicsScene( self )
        self.sequence_views: Dict[LegoSequence, LegoView_Sequence] = { }
        self.userdomain_views: Dict[LegoUserDomain, LegoView_UserDomain] = { }
        self.edges_view: LegoView_AllEdges = None
        self.user_move_enabled = False
        self._selections = 0
        
        # Create the sequence and domain views
        for sequence in self.model.sequences:
            item = LegoView_Sequence( self, sequence )
            self.sequence_views[sequence] = item
            self.userdomain_views.update( item.userdomain_views )
        
        # Create the edges view
        self.edges_view = LegoView_AllEdges( self )
        self.scene.addItem( self.edges_view )
    
    
    def find_userdomain_views_for_subsequence( self, target: LegoSubsequence ):
        for sequence_view in self.sequence_views.values():  # todo: this is terribly inefficient
            if sequence_view.sequence is not target.sequence:
                continue
            
            for domain_view in sequence_view.userdomain_views.values():
                if domain_view.domain.has_overlap( target ):
                    yield domain_view
    
    
    def find_component_view( self, component: LegoComponent ) -> LegoView_Component:
        return self.edges_view.component_views[component]


    def get_selected_userdomain_views( self ):
        return (x for x in self.userdomain_views.values() if x.is_in_global_selection())
