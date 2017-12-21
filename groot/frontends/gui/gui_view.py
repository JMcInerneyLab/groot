"""
MVC architecture.

Classes that manage the view of the model.
"""
from typing import Dict, Iterable, List, Optional, Set, Tuple

from PyQt5.QtCore import QPointF, QRect, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFontMetrics, QKeyEvent, QLinearGradient, QPainter, QPolygonF
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QStyleOptionGraphicsItem, QWidget

from groot.algorithms import userdomains
from groot.data.lego_model import ESiteType, ILegoVisualisable, LegoComponent, LegoEdge, LegoModel, LegoSequence, LegoSubsequence, LegoUserDomain, LegoViewOptions
from groot.frontends.gui.gui_view_support import ColourBlock, DRAWING, EDomainFunction, EMode, ESelect
from mhelper import SwitchError, array_helper, override, misc_helper
from mhelper_qt import Pens, qt_colour_helper


_LegoViewInfo_Edge_ = "LegoViewInfo_Edge"
_LegoView_AllEdges_ = "LegoView_AllEdges"
_LegoViewInfo_Side_ = "LegoViewInfo_Side"
_LegoViewSequence_ = "LegoView_Sequence"
_LegoView_Subsequence_ = "LegoView_UserDomain"
_LegoViewModel_ = "LegoViewModel"


class LegoViewInfo_Side:
    def __init__( self, edge: _LegoViewInfo_Edge_, subsequence: LegoSubsequence ) -> None:
        self.edge = edge
        self.subsequence = subsequence
        self.userdomain_views: List[LegoView_UserDomain] = []
        
        self.userdomain_views.extend( edge.owner_view.view_model.find_userdomain_views_for_subsequence( subsequence ) )
    
    
    def __bool__( self ):
        return bool( self.userdomain_views )
    
    
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


class LegoViewInfo_Edge:
    """
    Represents a view of a single edge.
    
    Mostly just a utility class, drawing is done elsewhere.
    """
    
    
    def __init__( self, owner: _LegoView_AllEdges_, edge: LegoEdge ) -> None:
        self.owner_view: LegoView_AllEdges = owner
        self.edge: LegoEdge = edge
        self.left = LegoViewInfo_Side( self, edge.left )
        self.right = LegoViewInfo_Side( self, edge.right )
    
    
    def paint_edge( self, painter: QPainter ) -> None:
        if not self.is_selected:
            return
        
        self.paint_to( painter, self.left, self.right, False )
    
    
    @staticmethod
    def paint_to( painter: QPainter,
                  upper: _LegoViewInfo_Side_,
                  lower: _LegoViewInfo_Side_,
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
        
        brush = QBrush( gradient )
        
        if is_highlighted:
            painter.setPen( DRAWING.SELECTION_EDGE_LINE )
        else:
            painter.setPen( Qt.NoPen )
        
        painter.setBrush( brush )
        painter.drawPolygon( QPolygonF( upper_points + lower_points + [upper_points[0]] ) )
    
    
    @property
    def is_selected( self ) -> bool:
        return any( x.isSelected() for x in self.left.userdomain_views ) and any( x.isSelected() for x in self.right.userdomain_views )
    
    
    def get_upper_and_lower( self ) -> Tuple[_LegoViewInfo_Side_, _LegoViewInfo_Side_]:
        """
        
        :return: lower, upper 
        """
        if self.left.top() < self.right.top():
            return self.right, self.left
        else:
            return self.left, self.right
    
    
    @staticmethod
    def __extract_rect( the_list ) -> QRectF:
        result = the_list[0].window_rect()
        
        for x in the_list[1:]:
            r = x.window_rect()
            
            if r.top() < result.top():
                result.setTop( r.top() )
            
            if r.bottom() > result.bottom():
                result.setBottom( r.bottom() )
            
            if r.right() > result.right():
                result.setRight( r.right() )
            
            if r.left() < result.left():
                result.setLeft( r.left() )
        
        return result


class LegoView_Component:
    """
    View of a component
    """
    
    
    def __init__( self, owner: _LegoView_AllEdges_, component: LegoComponent ) -> None:
        domain_views: List[LegoView_UserDomain] = []
        
        for domain_view in owner.view_model.userdomain_views.values():
            for subsequence in component.minor_subsequences:
                if domain_view.domain.has_overlap( subsequence ):
                    domain_views.append( domain_view )
                    break
        
        self.owner = owner
        self.component = component
        self.subsequence_views: Dict[LegoUserDomain, LegoView_UserDomain] = dict( (x.domain, x) for x in domain_views )
        self.colour = ColourBlock( owner.next_colour() )
    
    
    def paint_component( self, painter: QPainter ) -> None:
        """
        Paint edge group
        """
        pass


class LegoView_UserDomain( QGraphicsItem ):
    def __init__( self, userdomain: LegoUserDomain, owner_view: _LegoViewSequence_, positional_index: int, precursor: Optional[_LegoView_Subsequence_] ) -> None:
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
        self.setFlag( QGraphicsItem.ItemSendsGeometryChanges, True )
        self.setFlag( QGraphicsItem.ItemIsFocusable, True )
        self.setFlag( QGraphicsItem.ItemIsSelectable, True )
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
    def owner_model_view( self ) -> "LegoViewModel":
        return self.owner_sequence_view.owner_model_view
    
    
    @property
    def options( self ):
        return self.owner_model_view.options
    
    
    def load_state( self ):
        """
        Loads the state (position) of this domain view from the options.
        If there is no saved state, the default is applied.
        """
        position = self.options.domain_positions.get( (self.domain.sequence.id, self.domain.start) )
        
        if position is None:
            self.reset_state()
        else:
            self.setPos( position[0], position[1] )
    
    
    def save_state( self ):
        """
        Saves the state (position) of this domain view to the options.
        """
        self.options.domain_positions[(self.domain.sequence.id, self.domain.start)] = self.pos().x(), self.pos().y()
    
    
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
        
        is_selected = self.isSelected()
        
        if is_selected:
            MARGIN = 4
            painter.setBrush( 0 )
            painter.setPen( DRAWING.SELECTION_LINE if is_selected else DRAWING.PARTIAL_SELECTION_LINE )
            painter.drawLine( r.left(), r.top() - MARGIN, r.right(), r.top() - MARGIN )
            painter.drawLine( r.left(), r.bottom() + MARGIN, r.right(), r.bottom() + MARGIN )
        
        if misc_helper.coalesce( self.options.move_enabled, self.owner_sequence_view.owner_model_view.user_move_enabled ):
            MARGIN = 16
            painter.setBrush( 0 )
            painter.setPen( DRAWING.MOVE_LINE_SEL if is_selected else DRAWING.MOVE_LINE )
            painter.drawLine( r.left() - MARGIN, r.top(), r.right() + MARGIN, r.top() )
            painter.drawLine( r.left() - MARGIN, r.bottom(), r.right() + MARGIN, r.bottom() )
            painter.drawLine( r.left(), r.top() - MARGIN, r.left(), r.bottom() + MARGIN )
            painter.drawLine( r.right(), r.top() - MARGIN, r.right(), r.bottom() + MARGIN )
            
            if self.sibling_next and self.sibling_next.window_rect().left() != self.window_rect().right():
                MARGIN = 8
                painter.setPen( DRAWING.DISJOINT_LINE )
                painter.drawLine( r.right(), r.top() - MARGIN, r.right(), r.bottom() + MARGIN )
            
            if self.sibling_previous and self.sibling_previous.window_rect().right() != self.window_rect().left():
                MARGIN = 8
                painter.setPen( DRAWING.DISJOINT_LINE )
                painter.drawLine( r.left(), r.top() - MARGIN, r.left(), r.bottom() + MARGIN )
        
        draw_piano_roll = misc_helper.coalesce( self.options.view_piano_roll, is_selected )
        
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
        else:
            if self.__draw_position( is_selected ):
                # Draw position
                if self.sibling_previous is None or self.sibling_next is None or self.sibling_previous.rect.width() > 32:
                    painter.setPen( DRAWING.POSITION_TEXT )
                    
                    text = str( self.domain.start )
                    lx = self.rect.left() - QFontMetrics( painter.font() ).width( text ) / 2
                    painter.setPen( DRAWING.TEXT_LINE )
                    painter.drawText( QPointF( lx, self.rect.top() - DRAWING.TEXT_MARGIN ), text )
            else:
                # Draw component name
                painter.setPen( DRAWING.COMPONENT_PEN )
                painter.setBrush( 0 )
                text = "".join( str( x ) for x in self.components )
                x = (self.rect.left() + self.rect.right()) / 2 - QFontMetrics( painter.font() ).width( text ) / 2
                y = self.rect.top() - DRAWING.TEXT_MARGIN
                painter.drawText( QPointF( x, y ), text )
    
    
    def __draw_position( self, is_selected ):
        return misc_helper.coalesce( self.options.view_positions, is_selected )
    
    
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
    
    
    def keyPressEvent( self, e: QKeyEvent ):
        # TODO: Reimplement
        # if e.key() == Qt.Key_Left:
        #     my_index = self.owner_sequence_view.subsequence_views.index( self )
        #     my_index -= 1
        #     if my_index >= 0:
        #         self.owner_sequence_view.subsequence_views[ my_index ].setFocus()
        # elif e.key() == Qt.Key_Right:
        #     my_index = self.owner_sequence_view.subsequence_views.index( self )
        #     my_index += 1
        #     if my_index < len( self.owner_sequence_view.subsequence_views ):
        #         self.owner_sequence_view.subsequence_views[ my_index ].setFocus()
        # 
        # self.__apply_colour( e )
        pass
    
    
    def mousePressEvent( self, m: QGraphicsSceneMouseEvent ):
        """
        OVERRIDE
        Mouse press on subsequence view
        i.e. Use clicks a subsequence
        """
        if m.buttons() & Qt.LeftButton:
            # Remember the initial position items in case we drag stuff
            # - do this for all items because it's still possible for the selection to change post-mouse-down
            for item in self.owner_sequence_view.owner_model_view.scene.items():
                item.mousedown_original_pos = item.pos()
            
            # If ctrl or meta is down, add to the selection 
            if (m.modifiers() & Qt.ControlModifier) or (m.modifiers() & Qt.MetaModifier):
                select = ESelect.TOGGLE
            else:
                select = ESelect.ONLY
                
                if self.isSelected():
                    # If we are selected stop, this confuses with dragging from a design perspective
                    return
            
            self.owner_model_view.select_userdomain_view( self, select )
    
    
    def mouseDoubleClickEvent( self, m: QGraphicsSceneMouseEvent ):
        """
        OVERRIDE
        Double click
        Just toggles "move enabled" 
        """
        self.owner_model_view.user_move_enabled = not self.owner_model_view.user_move_enabled
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
            if not misc_helper.coalesce( self.options.move_enabled, self.owner_model_view.user_move_enabled ) or self.mousedown_original_pos is None:
                return
            
            new_pos: QPointF = self.mousedown_original_pos + (m.scenePos() - m.buttonDownScenePos( Qt.LeftButton ))
            new_x = new_pos.x()
            new_y = new_pos.y()
            new_x2 = new_x + self.boundingRect().width()
            
            self.mousemove_label = "({0} {1})".format( new_pos.x(), new_pos.y() )
            self.mousemove_snapline = None
            
            x_snap_enabled = misc_helper.coalesce( self.options.x_snap, not bool( m.modifiers() & Qt.ControlModifier ) )
            y_snap_enabled = misc_helper.coalesce( self.options.y_snap, not bool( m.modifiers() & Qt.AltModifier ) )
            
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
            
            for selected_item in self.owner_sequence_view.owner_model_view.scene.selectedItems():
                if selected_item is not self and selected_item.mousedown_original_pos is not None:
                    selected_item.setPos( selected_item.mousedown_original_pos.x() + delta_x, selected_item.mousedown_original_pos.y() + delta_y )
                    selected_item.save_state()
    
    
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
        
        switch = self.owner_model_view.options.domain_function
        param = self.owner_model_view.options.domain_function_parameter
        
        if switch == EDomainFunction.COMPONENT:
            userdomains_ = userdomains.by_component( self.sequence )
        elif switch == EDomainFunction.FIXED_COUNT:
            userdomains_ = userdomains.fixed_count( self.sequence, param )
        elif switch == EDomainFunction.FIXED_WIDTH:
            userdomains_ = userdomains.fixed_width( self.sequence, param )
        else:
            raise SwitchError( "self.owner_model_view.options.domain_function", switch )
        
        for userdomain in userdomains_:
            subsequence_view = LegoView_UserDomain( userdomain, self, len( self.userdomain_views ), previous_subsequence )
            self.userdomain_views[userdomain] = subsequence_view
            self.owner_model_view.scene.addItem( subsequence_view )
            previous_subsequence = subsequence_view
    
    
    def paint_name( self, painter: QPainter ):
        if not misc_helper.coalesce( self.owner_model_view.options.view_names, any( x.isSelected() for x in self.userdomain_views.values() ) ):
            return
        
        leftmost_subsequence = sorted( self.userdomain_views.values(), key = lambda xx: xx.pos().x() )[0]
        text = self.sequence.accession
        
        if self.sequence.is_root:
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
    Manages all of the line things:
        * edge views.
        * empty legos (subsequence-subsequence)
        * components
    
    This is actually a single graphics item drawn over the top of everything else.
    It is passive and doesn't react with the user in any way.
    """
    
    
    def __init__( self, view_model: "LegoViewModel" ):
        super().__init__()
        self.setZValue( DRAWING.Z_EDGES )
        self.__next_colour = -1
        self.view_model = view_model
        self.edge_views: Dict[LegoEdge, LegoViewInfo_Edge] = { }
        self.component_views: Dict[LegoComponent, LegoView_Component] = { }
        self.interlink_views: Dict[LegoSubsequence, LegoViewInfo_Interlink] = { }
        
        # Create the edge views
        for edge in view_model.model.edges:
            self.edge_views[edge] = LegoViewInfo_Edge( self, edge )
        
        # Create the component views
        for component in view_model.model.components:
            self.component_views[component] = LegoView_Component( self, component )
        
        # Create our interlink views
        for sequence_view in view_model.sequence_views.values():
            for left, right in array_helper.lagged_iterate( sequence_view.userdomain_views.values() ):
                self.interlink_views[left] = LegoViewInfo_Interlink( self, left, right )
        
        # Our bounds has_encompass the totality of the model
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
        # Draw all the edges
        if self.view_model.options.mode == EMode.EDGE:
            for edge in self.edge_views.values():
                edge.paint_edge( painter )
        
        # Draw all the components
        for component in self.component_views.values():
            component.paint_component( painter )
        
        # Draw all the interlinks
        for interlink in self.interlink_views.values():
            interlink.paint_interlink( painter )
        
        # Draw all the names
        for sequence in self.view_model.sequence_views.values():
            sequence.paint_name( painter )


class ILegoViewModelObserver:
    def ILegoViewModelObserver_selection_changed( self ):
        pass
    
    
    def ILegoViewModelObserver_options_changed( self ):
        pass


class LookupTable:
    def __init__( self, type_: ESiteType ):
        self.type = type_
        
        if type_ == ESiteType.PROTEIN:
            self.letter_size = DRAWING.PROTEIN_SIZE
            self.letter_order_table = DRAWING.PROTEIN_ORDER_TABLE
            self.letter_colour_table = DRAWING.PROTEIN_COLOUR_TABLE
        elif type_ == ESiteType.DNA:
            self.letter_size = DRAWING.NUCLEOTIDE_SIZE
            self.letter_order_table = DRAWING.DNA_ORDER_TABLE
            self.letter_colour_table = DRAWING.DNA_COLOUR_TABLE
        elif type_ == ESiteType.RNA:
            self.letter_size = DRAWING.NUCLEOTIDE_SIZE
            self.letter_order_table = DRAWING.RNA_ORDER_TABLE
            self.letter_colour_table = DRAWING.RNA_COLOUR_TABLE
        else:
            self.letter_size = DRAWING.PROTEIN_SIZE
            self.letter_order_table = DRAWING.PROTEIN_ORDER_TABLE
            self.letter_colour_table = DRAWING.PROTEIN_COLOUR_TABLE
            print( "Warning: Cannot create the lookup table because I don't know the letter type. Defaulting to `protein`." )
        
        self.count = len( self.letter_order_table )
        self.sequence_height = self.letter_size * (self.count + 2)
        self.sequence_ysep = self.sequence_height


class LegoViewModel:
    """
    The view of the model.
    Holds all of the other views.
    """
    
    
    def __init__( self, observer: ILegoViewModelObserver, view: QGraphicsView, model: LegoModel ) -> None:
        """
        CONSTRUCTOR
        :param observer:                To who we report changes 
        :param view:                    To where we draw the view
        :param model:                   The model we represent
        """
        self.lookup_table = LookupTable( model.site_type )
        self.observer: ILegoViewModelObserver = observer
        self.view: QGraphicsView = view
        self.model: LegoModel = model
        self.scene = QGraphicsScene()
        self.sequence_views: Dict[LegoSequence, LegoView_Sequence] = { }
        self.userdomain_views: Dict[LegoUserDomain, LegoView_UserDomain] = { }
        self.edges_view: LegoView_AllEdges = None
        self.user_move_enabled = False
        
        for sequence in self.model.sequences:
            item = LegoView_Sequence( self, sequence )
            self.sequence_views[sequence] = item
            self.userdomain_views.update( item.userdomain_views )
        
        self.edges_view = self.update_edges()
        self.scene.addItem( self.edges_view )
        
        self._selections = 0
    
    
    @property
    def options( self ) -> LegoViewOptions:
        if not hasattr( self.model, "ui_options" ):
            self.model.ui_options = LegoViewOptions()
        
        return self.model.ui_options
    
    
    def _call_selection_changed( self ):
        """
        Calls the selection changed handler
        We do this manually because the native Qt signal handler is raised for every slight change, and slows things down.
        """
        self.observer.ILegoViewModelObserver_selection_changed()
    
    
    def _call_options_changed( self ):
        """
        Calls the options-changed handler
        """
        self.observer.ILegoViewModelObserver_options_changed()
    
    
    def update_edges( self ) -> LegoView_AllEdges:
        if self.edges_view:
            self.scene.removeItem( self.edges_view )
        
        self.edges_view = LegoView_AllEdges( self )
        self.scene.addItem( self.edges_view )
        return self.edges_view
    
    
    def selected_userdomain_views( self ) -> Set[LegoView_UserDomain]:
        result = set()
        
        for sequence_view in self.sequence_views.values():
            for subsequence_view in sequence_view.userdomain_views.values():
                if subsequence_view.isSelected():
                    result.add( subsequence_view )
        
        return result
    
    
    def selected_subsequence_expansions( self ) -> List[LegoSubsequence]:
        """
        This gets the list of selected subsequences, but joins together those which are adjacent.
        :return: 
        """
        return LegoSubsequence.merge_list( list( self.selected_userdomains() ) )
    
    
    def selected_userdomains( self ) -> Set[LegoUserDomain]:
        """
        Subsequences selected by the user
        """
        result = set( x.domain for x in self.selected_userdomain_views() )
        
        return result
    
    
    def selected_domain( self ) -> Optional[LegoUserDomain]:
        return array_helper.extract_single_item( self.selected_userdomains() )
    
    
    def selected_sequences( self ) -> Set[LegoSequence]:
        """
        Sequences selected by the user (complete or partial)
        """
        result = set( x.sequence for x in self.selected_userdomains() )
        
        return result
    
    
    def selected_complete_sequences( self ) -> Set[LegoSequence]:
        sel = self.selected_userdomains()
        seqs = set( x.sequence for x in sel )
        results = set()
        
        for seq in seqs:
            if len( seq.subsequences ) == sum( x.sequence == seq for x in sel ):
                results.add( seq )
        
        return results
    
    
    def selected_complete_sequence( self ) -> Optional[LegoSequence]:
        return array_helper.extract_single_item( self.selected_complete_sequences() )
    
    
    def selected_sequence( self ) -> Optional[LegoSequence]:
        return array_helper.extract_single_item( self.selected_sequences() )
    
    
    def selected_edges( self, ) -> Set[LegoEdge]:
        """
        Edges selected by the user (complete or partial)
        """
        selected_subsequences = self.selected_userdomains()
        
        if len( selected_subsequences ) == 0:
            return set()
        
        result = None  # type: Set[LegoEdge]
        
        for subsequence in selected_subsequences:
            if result is None:
                result = set( subsequence.edges )
            else:
                assert isinstance( result, set )
                result = result.intersection( set( subsequence.edges ) )
        
        return result
    
    
    def selected_edge( self ) -> Optional[LegoEdge]:
        return array_helper.extract_single_item( self.selected_edges() )
    
    
    def selected_entities( self ) -> Set[ILegoVisualisable]:
        mode = self.options.mode
        
        if mode == EMode.COMPONENT:
            return self.selected_components()
        elif mode == EMode.SUBSEQUENCE:
            return self.selected_userdomains()
        elif mode == EMode.SEQUENCE:
            return self.selected_sequences()
        elif mode == EMode.EDGE:
            return self.selected_edges()
        else:
            raise SwitchError( "self.options.mode", mode )
    
    
    def selected_components( self ) -> Set[LegoComponent]:
        """
        Components selected by the user (complete)
        """
        
        r = set()
        selected_userdomains = self.selected_subsequence_expansions()
        
        for component in self.model.components:
            if all( any( λuserdomain.has_encompass( λsubsequence ) for λuserdomain in selected_userdomains ) for λsubsequence in component.minor_subsequences ):
                r.add( component )
        
        return r
    
    
    def add_new_sequence( self, sequence: LegoSequence ):
        view = LegoView_Sequence( self, sequence )
        self.sequence_views[sequence] = view
        self.recreate_edges()
    
    
    def recreate_sequences( self, sequences: Iterable[LegoSequence] ):
        to_do = set( sequences )
        
        for sequence in self.sequence_views.values():
            if sequence.sequence in to_do:
                sequence._recreate()
                to_do.remove( sequence.sequence )
        
        for sequence in to_do:
            self.add_new_sequence( sequence )
        
        self.recreate_edges()
        self._call_selection_changed()
    
    
    def find_userdomain_views_for_subsequence( self, target: LegoSubsequence ):
        for sequence_view in self.sequence_views.values():  # todo: this is terribly inefficient
            if sequence_view.sequence is not target.sequence:
                continue
            
            for domain_view in sequence_view.userdomain_views.values():
                if domain_view.domain.has_overlap( target ):
                    yield domain_view
    
    
    def find_domain_view( self, target: LegoUserDomain ) -> LegoView_UserDomain:
        assert isinstance( target, LegoUserDomain )
        
        result = self.userdomain_views.get( target )
        
        if result is None:
            raise KeyError( "Cannot find the UI element for the domain '{0}'.".format( target ) )
        
        return result
    
    
    def recreate_edges( self ):
        self.scene.removeItem( self.edges_view )
        self.edges_view = LegoView_AllEdges( self )
        self.scene.addItem( self.edges_view )
    
    
    def remove_sequences( self, sequences: Iterable[LegoSequence] ):
        for sequence in sequences:
            sequence_view = self.find_sequence_view( sequence )
            
            for domain_view in sequence_view.userdomain_views:
                self.scene.removeItem( domain_view )
            
            del self.sequence_views[sequence]
        
        self.update_edges()
        self._call_selection_changed()
    
    
    def _clear_selection( self ):
        """
        Internal function (externally just use `select_all(ESelect.REMOVE)`, which calls the handler)
        """
        for x in self.userdomain_views.values():
            x.setSelected( False )
    
    
    def select_left( self, select: ESelect = ESelect.APPEND ):
        the_list = list( self.selected_userdomain_views() )
        
        with self.on_selecting( select ):
            for subsequence_view in the_list:
                x = subsequence_view.sibling_previous
                
                while x is not None:
                    select.set( x )
                    x = x.sibling_previous
    
    
    def select_right( self, select: ESelect = ESelect.APPEND ):
        the_list = list( self.selected_userdomain_views() )
        
        with self.on_selecting( select ):
            for subsequence_view in the_list:
                x = subsequence_view.sibling_next
                
                while x is not None:
                    select.set( x )
                    x = x.sibling_next
    
    
    def select_direct_connections( self, select: ESelect = ESelect.APPEND ):
        the_set = set( self.selected_userdomain_views() )
        to_select = []
        
        for userdomain_view in the_set:
            for edge in self.model.edges:
                if edge.left.has_overlap( userdomain_view.domain ):
                    to_select.append( edge.right )
                elif edge.right.has_overlap( userdomain_view.domain ):
                    to_select.append( edge.left )
        
        with self.on_selecting( select ) as select:
            for subsequence in to_select:
                self.select_overlapping_domains( subsequence, select )
    
    
    def select_all( self, select: ESelect = ESelect.ONLY ) -> None:
        """
        Selects everything.
        """
        with self.on_selecting( select ) as select:
            for subsequence_view in self.userdomain_views.values():
                self.select_userdomain_view( subsequence_view, select )
    
    
    def select_entity( self, entity: ILegoVisualisable, select: ESelect = ESelect.ONLY ):
        if isinstance( entity, LegoSequence ):
            self.select_sequence( entity, select )
        elif isinstance( entity, LegoUserDomain ):
            self.select_userdomain( entity, select )
        elif isinstance( entity, LegoSubsequence ):
            self.select_overlapping_domains( entity, select )
        elif isinstance( entity, LegoEdge ):
            self.select_edge( entity, select )
        elif isinstance( entity, LegoComponent ):
            self.select_component( entity, select )
        else:
            raise SwitchError( "entity", entity, instance = True )
    
    
    def select_empty( self, select: ESelect = ESelect.ONLY ) -> None:
        """
        Selects subsequences with no `array` data.
        """
        self.select_all()
        
        for x in self.sequence_views.values():
            if x.sequence.site_array is None:
                for y in x.userdomain_views.values():
                    select.set( y )
        
        self._call_selection_changed()
    
    
    def find_component_view( self, component: LegoComponent ) -> LegoView_Component:
        return self.edges_view.component_views[component]
    
    
    def find_sequence_view( self, sequence: LegoSequence ) -> LegoView_Sequence:
        """
        Finds the view of the specified `sequence`.
        :exception KeyError:
        """
        return self.sequence_views[sequence]
    
    
    class __on_selecting:
        def __init__( self, owner: "LegoViewModel", select: ESelect ):
            assert isinstance( select, ESelect )
            
            self.owner = owner
            self.select = select
            self.original_updates = None
            self.original_signals = None
        
        
        def __enter__( self ):
            if self.owner._selections == 0:
                self.original_updates = self.owner.view.updatesEnabled()
                self.original_signals = self.owner.view.signalsBlocked()
                self.owner.view.setUpdatesEnabled( False )
                self.owner.view.blockSignals( True )
            
            self.owner._selections += 1
            
            if self.select == ESelect.ONLY:
                self.owner._clear_selection()
                return ESelect.APPEND
            
            return self.select
        
        
        def __exit__( self, exc_type, exc_val, exc_tb ):
            self.owner._selections -= 1
            assert self.owner._selections >= 0
            
            if self.owner._selections == 0:
                self.owner.view.setUpdatesEnabled( self.original_updates )
                self.owner.view.blockSignals( self.original_signals )
                self.owner._call_selection_changed()
    
    
    def on_selecting( self, select ):
        return self.__on_selecting( self, select )
    
    
    def select_edge( self, edge: LegoEdge, select: ESelect = ESelect.ONLY ):
        """
        Selects the specified `LegoEdge`.
        If the selection mode is SEQUENCE or COMPONENT, the selection will be expanded accordingly.
        """
        with self.on_selecting( select ) as select:
            if self.options.mode == EMode.SEQUENCE:
                self.select_sequence( edge.left.sequence, select )
                self.select_sequence( edge.right.sequence, select )
            else:
                for side in (edge.left, edge.right):
                    for subsequence in side:
                        self.select_userdomain( subsequence, select )  # nb. this expands for mode == COMPONENT for us
    
    
    def select_component( self, component: LegoComponent, select: ESelect = ESelect.ONLY ):
        """
        Selects the specified `LegoComponent`.
        If the selection mode is SEQUENCE, the selection will be expanded accordingly.
        """
        with self.on_selecting( select ) as select:
            if self.options.mode == EMode.SEQUENCE:
                for sequence in component.minor_sequences:
                    self.select_sequence( sequence, select )
            else:
                for subsequence in component.minor_subsequences:
                    for userdomain in self.find_userdomain_views_for_subsequence( subsequence ):
                        self.select_userdomain_view( userdomain, select, True )
    
    
    def select_sequence( self, sequence: LegoSequence, select: ESelect = ESelect.ONLY ):
        """
        Selects the specified `LegoSequence`.
        If the selection mode is COMPONENT, the selection will be expanded accordingly.
        """
        with self.on_selecting( select ) as select:
            if self.options.mode == EMode.SEQUENCE:
                sequence_view = self.find_sequence_view( sequence )
                
                for subsequence_view in sequence_view.userdomain_views.values():
                    self.select_userdomain_view( subsequence_view, select )
            elif self.options.mode == EMode.COMPONENT:
                component = self.model.components.find_component_for_major_sequence( sequence )
                self.select_component( component, select )
            else:
                for domain_view in self.userdomain_views.values():
                    if domain_view.domain.sequence is sequence:
                        self.select_userdomain_view( domain_view, select )
    
    
    def select_overlapping_domains( self, subsequence: LegoSubsequence, select: ESelect = ESelect.ONLY ):
        """
        Selects domain views that overlap the specified subsequence.
        """
        with self.on_selecting( select ) as select:
            for domain_view in self.userdomain_views.values():
                if domain_view.domain.has_overlap( subsequence ):
                    self.select_userdomain_view( domain_view, select )
    
    
    def select_userdomain_view( self, userdomain_view: LegoView_UserDomain, select: ESelect = ESelect.ONLY, absolute: bool = False ):
        """
        Selects the specified `LegoSubsequence`.
        Unlike `select_userdomain` this does not account for the current selection mode and hence is a private function.
        """
        with self.on_selecting( select ) as select:
            if self.options.mode == EMode.SUBSEQUENCE or self.options.mode == EMode.EDGE or absolute:
                self.__select_subsequence_view( select, userdomain_view )
            elif self.options.mode == EMode.SEQUENCE:
                for sibling_view in userdomain_view.owner_sequence_view.userdomain_views.values():
                    self.__select_subsequence_view( select, sibling_view )
            elif self.options.mode == EMode.COMPONENT:
                for component in self.model.components.find_components_for_minor_subsequence( userdomain_view.domain ):
                    self.select_component( component, select )
            else:
                raise SwitchError( "self.options.mode", self.options.mode )
    
    
    def __select_subsequence_view( self, select, subsequence_view ):
        if select == ESelect.APPEND:
            subsequence_view.setSelected( True )
        elif select == ESelect.REMOVE:
            subsequence_view.setSelected( False )
        elif select == ESelect.TOGGLE:
            subsequence_view.setSelected( not subsequence_view.isSelected() )
        else:
            raise SwitchError( "ESelect.set(item)", select )
    
    
    def select_userdomain( self, userdomain: LegoUserDomain, select: ESelect = ESelect.ONLY, absolute: bool = False ):
        """
        Selects the specified `LegoSubsequence`.
        If the selection mode is SEQUENCE or COMPONENT, the selection will be expanded accordingly.
        """
        with self.on_selecting( select ) as select:
            if absolute or self.options.mode == EMode.EDGE or self.options.mode == EMode.SUBSEQUENCE:
                view = self.find_domain_view( userdomain )
                self.select_userdomain_view( view, select, absolute )
            elif self.options.mode == EMode.SEQUENCE:
                self.select_sequence( userdomain.sequence, select )
            elif self.options.mode == EMode.COMPONENT:
                for component in self.model.components.find_components_for_minor_subsequence( userdomain ):
                    self.select_component( component, select )
            else:
                raise SwitchError( "self.options.mode", self.options.mode )
    
    
    def align_about_domain( self, target_userdomain_view: LegoView_UserDomain ) -> None:
        """
        Repositions all domains in the same component to be in line with the specified domain.
        """
        target_components = set( target_userdomain_view.components )
        
        for sequence_view in self.sequence_views.values():
            l = sequence_view.get_sorted_userdomain_views()
            for userdomain_view in l:
                s = set( userdomain_view.components )
                if all( x in s for x in target_components ):
                    userdomain_view.setX( target_userdomain_view.x() )
                    userdomain_view.save_state()
                    self.align_about( userdomain_view, relaxed = True )
                    break
    
    
    def align_about( self, userdomain_view: LegoView_UserDomain, left = True, right = True, relaxed = False ):
        """
        Aligns the elements of a sequence, fixing the position of the specified domain.
        
        :param userdomain_view:     Fixed domain
        :param left:                Align predecessors 
        :param right:               Align successors 
        :param relaxed:             Only align if not aligning would make the sequences out of order
        """
        if left:
            op = userdomain_view.sibling_previous
            
            while op:
                m = op.sibling_next.x() - op.rect.width()
                
                if not relaxed or op.x() > m:
                    op.setX( m )
                    op.save_state()
                
                op = op.sibling_previous
        
        if right:
            op = userdomain_view.sibling_next
            
            while op:
                m = op.sibling_previous.x() + op.sibling_previous.rect.width()
                
                if not relaxed or op.x() < m:
                    op.setX( m )
                    op.save_state()
                
                op = op.sibling_next
