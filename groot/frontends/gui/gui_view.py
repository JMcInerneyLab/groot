"""
MVC architecture.

Classes that manage the view of the model.
"""
from random import randint
from typing import Dict, Iterable, List, Optional, Set, Tuple, Union
from mhelper import SwitchError, array_helper, override
from mhelper_qt import qt_colour_helper, Pens

from PyQt5.QtCore import QPointF, QRect, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor, QFontMetrics, QKeyEvent, QLinearGradient, QPainter, QPolygonF
from PyQt5.QtWidgets import QGraphicsItem, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QStyleOptionGraphicsItem, QWidget

from groot.data.lego_model import ESiteType, LegoComponent, LegoEdge, LegoModel, LegoSequence, LegoSide, LegoSubsequence, ILegoVisualisable
from groot.frontends.gui.gui_view_support import ColourBlock, DRAWING, ESelect, LegoViewOptions, EMode, ESequenceColour


_LegoViewInfo_Edge_ = "LegoViewInfo_Edge"
_LegoView_AllEdges_ = "LegoView_AllEdges"
_LegoViewInfo_Side_ = "LegoViewInfo_Side"
_LegoViewSequence_ = "LegoViewSequence"
_LegoView_Subsequence_ = "LegoView_Subsequence"
_LegoViewModel_ = "LegoViewModel"


class LegoViewInfo_Side:
    def __init__( self, edge: _LegoViewInfo_Edge_, side: LegoSide ) -> None:
        self.edge = edge
        self.list: List[LegoView_Subsequence] = []
        
        for subsequence in side:
            self.list.append( edge.owner_view.view_model.find_subsequence_view( subsequence ) )
    
    
    def __bool__( self ):
        return bool( self.list )
    
    
    def average_colour( self ):
        return qt_colour_helper.average_colour( list( x.colour.colour for x in self.list ) )
    
    
    def extract_points( self, backwards ):
        results = []
        
        if not backwards:
            for x in sorted( self.list, key = lambda z: z.window_rect().left() ):
                r: QRect = x.window_rect()
                results.append( r.bottomLeft() )
                results.append( r.bottomRight() )
        else:
            for x in sorted( self.list, key = lambda z: -z.window_rect().left() ):
                r: QRect = x.window_rect()
                results.append( r.topRight() )
                results.append( r.topLeft() )
        
        return results
    
    
    def top( self ):
        return self.list[0].window_rect().top()


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
        return any( x.isSelected() for x in self.left.list ) and any( x.isSelected() for x in self.right.list )
    
    
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


class LegoViewInfo_Component:
    """
    View of a component
    """
    
    
    def __init__( self, owner: _LegoView_AllEdges_, component: LegoComponent ) -> None:
        subsequence_views: List[LegoView_Subsequence] = [x for x in owner.view_model.subsequence_views.values() if component in x.subsequence.components]
        
        self.owner = owner
        self.component = component
        self.subsequence_views: Dict[LegoSubsequence, LegoView_Subsequence] = dict( (x.subsequence, x) for x in subsequence_views )
        self.colour = ColourBlock( owner.next_colour() )
    
    
    def paint_component( self, painter: QPainter ) -> None:
        """
        Paint edge group
        """
        pass




class LegoView_Subsequence( QGraphicsItem ):
    def __init__( self, subsequences: LegoSubsequence, owner_view: _LegoViewSequence_, positional_index: int, precursor: Optional[_LegoView_Subsequence_] ) -> None:
        """
        CONSTRUCTOR
        
        :param subsequences:             Subsequences to view 
        :param owner_view:              Owning view 
        :param positional_index:        Index of subsequence within sequence 
        :param precursor:               Previous subsequence, or None 
        """
        assert isinstance(subsequences, LegoSubsequence)
        
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
        self.sibling_next: LegoView_Subsequence = None
        self.sibling_previous: LegoView_Subsequence = precursor
        self.subsequence: LegoSubsequence = subsequences
        self.mousedown_original_pos: QPointF = None
        self.mousemove_label: str = None
        self.mousemove_snapline: Tuple[int, int] = None
        self.mousedown_move_all = False
        self.index = positional_index
        self.edge_subsequence_views: List[LegoView_Subsequence] = []
        
        #
        # POSITION
        #
        table = owner_view.owner_model_view.lookup_table
        self.rect = QRectF( 0, 0, subsequences.length * table.letter_size, table.sequence_height )
        
        if not subsequences.ui_position:
            self.restore_default_position()
        else:
            self.setPos( subsequences.ui_position[0], subsequences.ui_position[1] )
        
        #
        # PRECURSOR
        #
        if precursor:
            precursor.sibling_next = self
    
    
    @property
    def colour( self ) -> ColourBlock:
        """
        Subsequence colour.
        """
        if self.subsequence.components:
            colour = None
            
            for component in self.subsequence.components:
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
            
            return colour
        else:
            return DRAWING.DEFAULT_COLOUR
    
    
    def restore_default_position( self ):
        """
        Restores the default position of this view.
        """
        table = self.owner_sequence_view.owner_model_view.lookup_table
        precursor = self.sibling_previous
        subsequence = self.subsequence
        
        if precursor:
            x = precursor.window_rect().right()
            y = precursor.window_rect().top()
        else:
            x = subsequence.start * table.letter_size
            y = subsequence.sequence.index * (table.sequence_ysep + table.sequence_height)
        
        self.setPos( x, y )
        self.update_model()
    
    
    @property
    def owner_model_view( self ) -> "LegoViewModel":
        return self.owner_sequence_view.owner_model_view
    
    
    @property
    def options( self ):
        return self.owner_model_view.options
    
    
    def update_model( self ):
        self.subsequence.ui_position = self.pos().x(), self.pos().y()
        self.subsequence.ui_colour = self.user_colour.colour.rgba() if self.user_colour is not None else None
    
    
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
        
        is_selected = self.is_selected_with_mask()
        is_partially_selected = not is_selected and self.isSelected()
        
        if is_selected or is_partially_selected:
            MARGIN = 4
            painter.setBrush( 0 )
            painter.setPen( DRAWING.SELECTION_LINE if is_selected else DRAWING.PARTIAL_SELECTION_LINE )
            painter.drawLine( r.left(), r.top() - MARGIN, r.right(), r.top() - MARGIN )
            painter.drawLine( r.left(), r.bottom() + MARGIN, r.right(), r.bottom() + MARGIN )
        
        if self.options.move_enabled:
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
        
        draw_piano_roll = self.options.view_piano_roll
        
        if draw_piano_roll is None:
            draw_piano_roll = is_selected or is_partially_selected
        
        if draw_piano_roll:
            lookup_table = self.owner_model_view.lookup_table
            letter_size = lookup_table.letter_size
            painter.setPen( Qt.NoPen )
            painter.setBrush( DRAWING.PIANO_ROLL_SELECTED_BACKGROUND if is_selected else DRAWING.PIANO_ROLL_UNSELECTED_BACKGROUND )
            OFFSET_X = letter_size
            rect_width = self.rect.width()
            rect_height = lookup_table.count * letter_size
            painter.drawRect( 0, OFFSET_X, rect_width, rect_height )
            
            array = self.subsequence.site_array
            
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
                    
                    text = str( self.subsequence.start )
                    lx = self.rect.left() - QFontMetrics( painter.font() ).width( text ) / 2
                    painter.setPen( DRAWING.TEXT_LINE )
                    painter.drawText( QPointF( lx, self.rect.top() - DRAWING.TEXT_MARGIN ), text )
            else:
                # Draw component name
                painter.setPen( DRAWING.COMPONENT_PEN )
                painter.setBrush( 0 )
                text = "".join( str( x ) for x in self.subsequence.components )
                x = (self.rect.left() + self.rect.right()) / 2 - QFontMetrics( painter.font() ).width( text ) / 2
                y = self.rect.top() - DRAWING.TEXT_MARGIN
                painter.drawText( QPointF( x, y ), text )
    
    
    def __draw_position( self, is_selected ):
        result = self.options.view_positions
        
        if result is None:
            result = is_selected
        
        return result
    
    
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
            
            self.owner_model_view.select_subsequence_view( self, select )
    
    
    def mouseDoubleClickEvent( self, m: QGraphicsSceneMouseEvent ):
        """
        OVERRIDE
        Double click
        Just toggles "move enabled" 
        """
        self.options.move_enabled = not self.options.move_enabled
        
        self.owner_model_view._call_options_changed()
        self.owner_model_view.scene.update()
    
    
    def focusInEvent( self, QFocusEvent ):
        self.setZValue( DRAWING.Z_FOCUS )
    
    
    def focusOutEvent( self, QFocusEvent ):
        self.setZValue( DRAWING.Z_SEQUENCE )
    
    
    def snaps( self ):
        for sequence_view in self.owner_sequence_view.owner_model_view.sequence_views.values():
            for subsequence_view in sequence_view.subsequence_views.values():
                if subsequence_view is not self:
                    left_snap = subsequence_view.scenePos().x()
                    right_snap = subsequence_view.scenePos().x() + subsequence_view.boundingRect().width()
                    yield left_snap, "Start of {}[{}]".format( subsequence_view.subsequence.sequence.accession, subsequence_view.subsequence.start ), subsequence_view.scenePos().y()
                    yield right_snap, "End of {}[{}]".format( subsequence_view.subsequence.sequence.accession, subsequence_view.subsequence.end ), subsequence_view.scenePos().y()
    
    
    def mouseMoveEvent( self, m: QGraphicsSceneMouseEvent ) -> None:
        if m.buttons() & Qt.LeftButton:
            if not self.options.move_enabled or self.mousedown_original_pos is None:
                return
            
            new_pos: QPointF = self.mousedown_original_pos + (m.scenePos() - m.buttonDownScenePos( Qt.LeftButton ))
            new_x = new_pos.x()
            new_y = new_pos.y()
            new_x2 = new_x + self.boundingRect().width()
            
            self.mousemove_label = "({0} {1})".format( new_pos.x(), new_pos.y() )
            self.mousemove_snapline = None
            
            x_snap_enabled = self.options.x_snap == (not bool( m.modifiers() & Qt.ControlModifier ))
            y_snap_enabled = self.options.y_snap == (not bool( m.modifiers() & Qt.AltModifier ))
            
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
            self.update_model()
            
            delta_x = new_x - self.mousedown_original_pos.x()
            delta_y = new_y - self.mousedown_original_pos.y()
            
            for selected_item in self.owner_sequence_view.owner_model_view.scene.selectedItems():
                if selected_item is not self and selected_item.mousedown_original_pos is not None:
                    selected_item.setPos( selected_item.mousedown_original_pos.x() + delta_x, selected_item.mousedown_original_pos.y() + delta_y )
                    selected_item.update_model()
    
    
    def mouseReleaseEvent( self, m: QGraphicsSceneMouseEvent ):
        self.mousemove_label = None
        self.mousemove_snapline = None
        self.update()
        pass  # suppress default mouse handling implementation
    
    
    def __repr__( self ):
        return "<<View of '{}' at ({},{})>>".format( self.subsequence, self.window_rect().left(), self.window_rect().top() )
    
    
    def is_selected_with_mask( self, mask: bool = True ):
        if not self.isSelected():
            return False
        
        if mask:
            for to_remove in list( self.owner_model_view.selection_mask ):
                if to_remove == self.subsequence:
                    return False
                elif to_remove == self.subsequence.sequence:
                    return False
        
        return True


class LegoViewSequence:
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
        self.subsequence_views: Dict[LegoSubsequence, LegoView_Subsequence] = { }
        self._recreate()
    
    
    def _recreate( self ):
        # Remove existing items
        for x in self.subsequence_views:
            self.owner_model_view.scene.removeItem( x )
        
        self.subsequence_views.clear()
        
        # Add new items
        previous_subsequence = None
        
        
        for subsequence in self.sequence.subsequences:
            subsequence_view = LegoView_Subsequence( subsequence, self, len( self.subsequence_views ), previous_subsequence )
            self.subsequence_views[subsequence] = subsequence_view
            self.owner_model_view.scene.addItem( subsequence_view )
            previous_subsequence = subsequence_view
    
    
    def paint_name( self, painter: QPainter ):
        if not self.owner_model_view.options.view_names:
            return
        
        leftmost_subsequence = sorted( self.subsequence_views.values(), key = lambda xx: xx.pos().x() )[0]
        text = self.sequence.accession
        
        if self.sequence.is_root:
            text = "↑" + text
        
        r = leftmost_subsequence.window_rect()
        x = r.left() - DRAWING.TEXT_MARGIN - QFontMetrics( painter.font() ).width( text )
        y = r.top() + r.height() / 2
        painter.drawText( QPointF( x, y ), text )


class LegoViewInfo_Interlink:
    def __init__( self, owner_view: "LegoView_AllEdges", left: LegoSubsequence, right: LegoSubsequence ) -> None:
        self.owner_view = owner_view
        self.left = owner_view.view_model.find_subsequence_view( left )
        self.right = owner_view.view_model.find_subsequence_view( right )
    
    
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
        self.component_views: Dict[LegoComponent, LegoViewInfo_Component] = { }
        self.interlink_views: Dict[LegoSubsequence, LegoViewInfo_Interlink] = { }
        
        # Create the edge views
        for edge in view_model.model.all_edges:
            self.edge_views[edge] = LegoViewInfo_Edge( self, edge )
        
        # Create the component views
        for component in view_model.model.components:
            self.component_views[component] = LegoViewInfo_Component( self, component )
        
        # Create our interlink views
        for sequence in view_model.model.sequences:
            for left, right in array_helper.lagged_iterate( sequence.subsequences ):
                self.interlink_views[left] = LegoViewInfo_Interlink( self, left, right )
        
        # Our bounds encompasses the totality of the model
        # - find this!
        self.rect = QRectF( 0, 0, 0, 0 )
        
        for sequence_view in view_model.sequence_views.values():
            for subsequence_view in sequence_view.subsequence_views.values():
                r = subsequence_view.window_rect()
                
                if r.left() < self.rect.left():
                    self.rect.setLeft( r.left() )
                
                if r.right() > self.rect.right():
                    self.rect.setRight( r.right() )
                
                if r.top() < self.rect.top():
                    self.rect.setTop( r.top() )
                
                if r.bottom() > self.rect.bottom():
                    self.rect.setBottom( r.bottom() )
                
                subsequence_view.edge_subsequence_views.clear()
                
                for edge in subsequence_view.subsequence.edges:
                    for subsequence in edge.opposite( subsequence_view.subsequence ):
                        subsequence_view.edge_subsequence_views.append( self.view_model.find_subsequence_view( subsequence ) )
        
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
        self.selection_mask = set()
        self.scene = QGraphicsScene()
        self.sequence_views: Dict[LegoSequence, LegoViewSequence] = { }
        self.subsequence_views: Dict[LegoSubsequence, LegoView_Subsequence] = { }
        self.edges_view: LegoView_AllEdges = None
        
        for sequence in self.model.sequences:
            item = LegoViewSequence( self, sequence )
            self.sequence_views[sequence] = item
            self.subsequence_views.update( item.subsequence_views )
        
        self.edges_view = self.update_edges()
        self.scene.addItem( self.edges_view )
        
        self.options = LegoViewOptions()
        self._selections = 0
    
    
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
    
    
    def selected_subsequence_views( self, mask = True ) -> Set[LegoView_Subsequence]:
        result = set()
        
        for sequence_view in self.sequence_views.values():
            for subsequence_view in sequence_view.subsequence_views.values():
                if subsequence_view.is_selected_with_mask( mask = mask ):
                    result.add( subsequence_view )
        
        return result
    
    
    def selected_subsequence_view( self ) -> Optional[LegoView_Subsequence]:
        return array_helper.extract_single_item( self.selected_subsequence_views() )
    
    
    def selected_subsequences( self, mask = True ) -> Set[LegoSubsequence]:
        """
        Subsequences selected by the user
        """
        result = set( x.subsequence for x in self.selected_subsequence_views( mask = mask ) )
        
        return result
    
    
    def selected_subsequence( self, mask = True ) -> Optional[LegoSubsequence]:
        return array_helper.extract_single_item( self.selected_subsequences( mask = mask ) )
    
    
    def selected_sequences( self, mask = True ) -> Set[LegoSequence]:
        """
        Sequences selected by the user (complete or partial)
        """
        result = set( x.sequence for x in self.selected_subsequences( mask = False ) )
        
        if mask:
            result -= self.selection_mask
        
        return result
    
    
    def selected_complete_sequences( self, mask = True ) -> Set[LegoSequence]:
        sel = self.selected_subsequences( mask = False )
        seqs = set( x.sequence for x in sel )
        results = set()
        
        for seq in seqs:
            if len( seq.subsequences ) == sum( x.sequence == seq for x in sel ):
                results.add( seq )
        
        if mask:
            results -= self.selection_mask
        
        return results
    
    
    def selected_complete_sequence( self ) -> Optional[LegoSequence]:
        return array_helper.extract_single_item( self.selected_complete_sequences() )
    
    
    def selected_sequence( self ) -> Optional[LegoSequence]:
        return array_helper.extract_single_item( self.selected_sequences() )
    
    
    def selected_edges( self, mask = True ) -> Set[LegoEdge]:
        """
        Edges selected by the user (complete or partial)
        """
        selected_subsequences = self.selected_subsequences( mask = False )
        
        if len( selected_subsequences ) == 0:
            return set()
        
        result = None  # type: Set[LegoEdge]
        
        for subsequence in selected_subsequences:
            if result is None:
                result = set( subsequence.edges )
            else:
                assert isinstance( result, set )
                result = result.intersection( set( subsequence.edges ) )
        
        if mask:
            result -= self.selection_mask
        
        return result
    
    
    def selected_edge( self ) -> Optional[LegoEdge]:
        return array_helper.extract_single_item( self.selected_edges() )
    
    
    def selected_entities( self, mask = True ) -> Set[ILegoVisualisable]:
        mode = self.options.mode
        
        if mode == EMode.COMPONENT:
            return self.selected_components( mask = mask )
        elif mode == EMode.SUBSEQUENCE:
            return self.selected_subsequences( mask = mask )
        elif mode == EMode.SEQUENCE:
            return self.selected_sequences( mask = mask )
        elif mode == EMode.EDGE:
            return self.selected_edges( mask = mask )
        else:
            raise SwitchError( "self.options.mode", mode )
    
    
    def selected_components( self, mask = True ) -> Set[LegoComponent]:
        """
        Components selected by the user (complete)
        """
        
        r = set()
        selected_subsequences = self.selected_subsequences( mask = False )
        for component in self.model.components:
            if all( subsequence in selected_subsequences for subsequence in component.minor_subsequences() ):
                r.add( component )
        
        if mask:
            r -= self.selection_mask
        
        return r
    
    
    def clear_selection_mask( self ):
        self.selection_mask.clear()
    
    
    def set_selection_mask( self, item: object, state: bool ):
        assert item is not None
        
        if state:
            if item in self.selection_mask:
                self.selection_mask.remove( item )
        else:
            self.selection_mask.add( item )
    
    
    def change_colours( self, new_colour: Union[QColor, ESequenceColour] ):
        the_list = self.selected_subsequence_views() or self.subsequence_views
        
        if isinstance( new_colour, QColor ):
            the_colour = ColourBlock( new_colour )
        else:
            the_colour = None
        
        for subsequence_view in the_list:
            if new_colour == ESequenceColour.RESET:
                the_colour = None
            elif new_colour == ESequenceColour.RANDOM:
                the_colour = ColourBlock( QColor( randint( 0, 255 ), randint( 0, 255 ), randint( 0, 255 ) ) )
            
            if the_colour is None:
                subsequence_view.colour = None
            if self.options.colour_blend != 1:
                subsequence_view.colour = subsequence_view.colour.blend( the_colour.colour, self.options.colour_blend )
            else:
                subsequence_view.colour = the_colour
            
            subsequence_view.update_model()
            subsequence_view.update()
    
    
    def add_new_sequence( self, sequence: LegoSequence ):
        view = LegoViewSequence( self, sequence )
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
    
    
    def find_subsequence_view( self, target: LegoSubsequence ) -> LegoView_Subsequence:
        result = self.subsequence_views.get( target )
        
        if result is None:
            raise KeyError( "Cannot find the UI element for the subsequence '{0}'.".format( target ) )
        
        return result
    
    
    def recreate_edges( self ):
        self.scene.removeItem( self.edges_view )
        self.edges_view = LegoView_AllEdges( self )
        self.scene.addItem( self.edges_view )
    
    
    def remove_sequences( self, sequences: Iterable[LegoSequence] ):
        for sequence in sequences:
            sequence_view = self.find_sequence_view( sequence )
            
            for subsequence_view in sequence_view.subsequence_views:
                self.scene.removeItem( subsequence_view )
            
            del self.sequence_views[sequence]
        
        self.update_edges()
        self._call_selection_changed()
    
    
    def select( self, subsequences: List[LegoSubsequence] ):
        """
        API
        Replace the current selection
        :param subsequences: 
        """
        
        for x in self.selected_subsequence_views():
            x.setSelected( False )
        
        for x in subsequences:
            self.find_subsequence_view( x ).setSelected( True )
        
        self._call_selection_changed()
    
    
    def _clear_selection( self ):
        """
        Internal function (externally just use `select_all(ESelect.REMOVE)`, which calls the handler)
        """
        for x in self.subsequence_views.values():
            x.setSelected( False )
    
    
    def select_left( self, select: ESelect = ESelect.APPEND ):
        the_list = list( self.selected_subsequence_views() )
        
        with self.on_selecting( select ):
            for subsequence_view in the_list:
                x = subsequence_view.sibling_previous
                
                while x is not None:
                    select.set( x )
                    x = x.sibling_previous
    
    
    def select_right( self, select: ESelect = ESelect.APPEND ):
        the_list = list( self.selected_subsequence_views() )
        
        with self.on_selecting( select ):
            for subsequence_view in the_list:
                x = subsequence_view.sibling_next
                
                while x is not None:
                    select.set( x )
                    x = x.sibling_next
    
    
    def select_direct_connections( self, select: ESelect = ESelect.APPEND ):
        the_list = list( self.selected_subsequence_views() )
        
        with self.on_selecting( select ):
            for subsequence_view in the_list:
                for x in subsequence_view.edge_subsequence_views:
                    select.set( x )
    
    
    def select_all( self, select: ESelect = ESelect.ONLY ) -> None:
        """
        Selects everything.
        """
        with self.on_selecting( select ) as select:
            for subsequence_view in self.subsequence_views.values():
                self.select_subsequence_view( subsequence_view, select )
    
    
    def select_entity( self, entity: ILegoVisualisable, select: ESelect = ESelect.ONLY ):
        if isinstance( entity, LegoSequence ):
            self.select_sequence( entity, select )
        elif isinstance( entity, LegoSubsequence ):
            self.select_subsequence( entity, select )
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
                for y in x.subsequence_views.values():
                    select.set( y )
        
        self._call_selection_changed()
    
    
    def find_component_view( self, component: LegoComponent ) -> LegoViewInfo_Component:
        return self.edges_view.component_views[component]
    
    
    def find_sequence_view( self, sequence: LegoSequence ) -> LegoViewSequence:
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
                        self.select_subsequence( subsequence, select )  # nb. this expands for mode == COMPONENT for us
    
    
    def select_component( self, component: LegoComponent, select: ESelect = ESelect.ONLY ):
        """
        Selects the specified `LegoComponent`.
        If the selection mode is SEQUENCE, the selection will be expanded accordingly.
        """
        with self.on_selecting( select ) as select:
            if self.options.mode == EMode.SEQUENCE:
                for sequence in component.minor_sequences():
                    self.select_sequence( sequence, select )
            else:
                for subsequence in component.minor_subsequences():
                    self.select_subsequence( subsequence, select, True )
    
    
    def select_sequence( self, sequence: LegoSequence, select: ESelect = ESelect.ONLY ):
        """
        Selects the specified `LegoSequence`.
        If the selection mode is COMPONENT, the selection will be expanded accordingly.
        """
        with self.on_selecting( select ) as select:
            if self.options.mode == EMode.SEQUENCE:
                sequence_view = self.find_sequence_view( sequence )
                
                for subsequence_view in sequence_view.subsequence_views.values():
                    self.select_subsequence_view( subsequence_view, select )
            elif self.options.mode == EMode.COMPONENT:
                for component in sequence.minor_components():
                    self.select_component( component, select )
            else:
                for subsequence in sequence.subsequences:
                    self.select_subsequence( subsequence, select )
    
    
    def select_subsequence_view( self, subsequence_view: LegoView_Subsequence, select: ESelect = ESelect.ONLY, absolute: bool = False ):
        """
        Selects the specified `LegoSubsequence`.
        Unlike `select_subsequence` this does not account for the current selection mode and hence is a private function.
        """
        with self.on_selecting( select ) as select:
            if self.options.mode == EMode.SUBSEQUENCE or self.options.mode == EMode.EDGE or absolute:
                self.__select_subsequence_view( select, subsequence_view )
            elif self.options.mode == EMode.SEQUENCE:
                for sibling_view in subsequence_view.owner_sequence_view.subsequence_views.values():
                    self.__select_subsequence_view( select, sibling_view )
            elif self.options.mode == EMode.COMPONENT:
                for component in subsequence_view.subsequence.components:
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
    
    
    def select_subsequence( self, subsequence: LegoSubsequence, select: ESelect = ESelect.ONLY, absolute: bool = False ):
        """
        Selects the specified `LegoSubsequence`.
        If the selection mode is SEQUENCE or COMPONENT, the selection will be expanded accordingly.
        """
        with self.on_selecting( select ) as select:
            if absolute or self.options.mode == EMode.EDGE or self.options.mode == EMode.SUBSEQUENCE:
                view = self.find_subsequence_view( subsequence )
                print( "SELECTING {}.".format( view ) )
                self.select_subsequence_view( view, select, absolute )
            elif self.options.mode == EMode.SEQUENCE:
                self.select_sequence( subsequence.sequence, select )
            elif self.options.mode == EMode.COMPONENT:
                for component in subsequence.components:
                    self.select_component( component, select )
            else:
                raise SwitchError( "self.options.mode", self.options.mode )
    
    
    def align_to_sequence( self, sel_sequence: LegoSequence ) -> None:
        """
        Positions sequence views sharing components with `sel_sequence` so that their components align with those in `sel_sequence`.
        """
        components = [x for x in self.model.components if sel_sequence in x.major_sequences()]
        starts = { }
        
        for component in components:
            for line in component.minor_subsequences():
                if line.sequence is sel_sequence:
                    starts[component] = self.find_subsequence_view( line ).window_rect().left()
        
        touched = set()
        
        for component in components:
            start = starts[component]
            
            for line in component.minor_subsequences():
                sequence = line.sequence
                
                if sequence is sel_sequence:
                    continue
                
                self.align_sequence( line, start, touched )
    
    
    def align_sequence( self, specified_subsequence: LegoSubsequence, target_x: int, touched: Set[LegoView_Subsequence] ):
        """
        Aligns the elements of a sequence, given that the `specified_subsequence` is placed at `target_x`.
        All subsequence views repositioned are added to the `touched` set, and any views already in the `touched` set are not modified.
        """
        what_view = self.find_subsequence_view( specified_subsequence )
        
        print( "ALIGN {} TO {}".format( what_view, target_x ) )
        what_view.setPos( QPointF( target_x, what_view.window_rect().top() ) )
        touched.add( what_view )
        
        prev = what_view
        next = what_view.sibling_next
        
        while next:
            if next not in touched:
                x = prev.window_rect().right()
                if next.window_rect().left() != x:
                    next.setPos( QPointF( x, next.window_rect().top() ) )
                
                touched.add( next )
            
            prev = next
            next = next.sibling_next
        
        prev = what_view
        next = what_view.sibling_previous
        
        while next:
            if next not in touched:
                x = prev.window_rect().left() - next.window_rect().width()
                
                if next.window_rect().left() != x:
                    next.setPos( QPointF( x, next.window_rect().top() ) )
                
                touched.add( next )
            
            prev = next
            next = next.sibling_previous
