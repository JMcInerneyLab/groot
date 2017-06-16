"""
MVC architecture.

Classes that manage the view of the model.
"""
from enum   import Enum
from random import randint
from typing import Iterable, List, Optional, Set, Tuple, Union, Dict

from PyQt5.QtCore       import QPointF, QRect, QRectF, Qt
from PyQt5.QtGui        import QBrush, QColor, QFontMetrics, QKeyEvent, QLinearGradient, QPainter, QPen, QPolygonF
from PyQt5.QtWidgets    import QGraphicsItem, QGraphicsScene, QGraphicsSceneMouseEvent, QGraphicsView, QStyleOptionGraphicsItem, QWidget

from MHelper                    import ArrayHelper, QtColourHelper
from MHelper.CommentHelper      import override
from MHelper.ExceptionHelper    import SwitchError
from MHelper.QtColourHelper     import Colours, Pens

from legoalign.LegoModels       import ELetterType, LegoComponent, LegoEdge, LegoModel, LegoSequence, LegoSubsequence


class ESequenceColour( Enum ):
    RESET  = 1
    RANDOM = 2
    
class EMode(Enum):
    SEQUENCE    = 0
    SUBSEQUENCE = 1
    EDGE        = 2
    COMPONENT   = 3


class ESelect( Enum ):
    """
    Selection mode
    """
    ONLY = 1
    """Only select this item (i.e. clear before select)"""
    
    APPEND = 2
    """Add this item from the current selection"""
    
    REMOVE = 3
    """Remove this item from the current selection"""
    
    TOGGLE = 4
    """Toggle this items selected status"""
    
    
    def set( self, item: QGraphicsItem ):
        if self == ESelect.ONLY or self == ESelect.APPEND:
            item.setSelected( True )
        elif self == ESelect.REMOVE:
            item.setSelected( False )
        elif self == ESelect.TOGGLE:
            item.setSelected( not item.isSelected() )
        else:
            raise SwitchError( "ESelect.set(item)", self )


# Order of proteins in piano roll
# noinspection PyTypeChecker
PROTEIN_ORDER_TABLE = ArrayHelper.create_index_lookup( "IVLFCMAGTSWYPHEQDNKR" )
# noinspection PyTypeChecker
DNA_ORDER_TABLE     = ArrayHelper.create_index_lookup( "ATCG" )
# noinspection PyTypeChecker
RNA_ORDER_TABLE     = ArrayHelper.create_index_lookup( "AUCG" )

# Colour of proteins in piano roll
PROTEIN_COLOUR_TABLE = { "G": Pens.WHITE,  "A": Pens.WHITE,  "V": Pens.WHITE, "L": Pens.WHITE, "I": Pens.WHITE,
                         "F": Pens.ORANGE, "Y": Pens.ORANGE, "W": Pens.ORANGE,
                         "C": Pens.YELLOW, "M": Pens.YELLOW,
                         "S": Pens.GREEN,  "T": Pens.GREEN,
                         "K": Pens.RED,    "R": Pens.RED,    "H": Pens.RED,
                         "D": Pens.CYAN,   "E": Pens.CYAN,
                         "N": Pens.DARK_ORANGE, "Q": Pens.DARK_ORANGE,
                         "P": Pens.LIGHT_RED }

DNA_COLOUR_TABLE                                   = { "A": Pens.YELLOW, "T":Pens.RED, "C":Pens.GREEN, "G":Pens.LIGHT_BLUE }
RNA_COLOUR_TABLE                                   = { "A": Pens.YELLOW, "U":Pens.RED, "C":Pens.GREEN, "G":Pens.LIGHT_BLUE }

SIZE_MULTIPLIER                                    = 2
PROTEIN_SIZE                                       = SIZE_MULTIPLIER * 1
NUCLEOTIDE_SIZE                                    = SIZE_MULTIPLIER * 1
TEXT_MARGIN                                        = SIZE_MULTIPLIER * 4

PIANO_ROLL_SELECTED_BACKGROUND                     = QBrush( QColor( 0, 0, 0 ) )
PIANO_ROLL_UNSELECTED_BACKGROUND                   = QBrush( QColor( 0, 0, 0, alpha = 128 ) )
SEQUENCE_DEFAULT_FG                                = QPen( QColor( 255, 255, 0 ) )

SELECTION_EDGE_LINE                                = QPen( QColor( 0, 0, 255 ) )
SELECTION_EDGE_LINE.setWidth(2)
EDGE_LINE                                          = QPen( QColor( 128, 128, 128 ) )
EDGE_LINE.setStyle(Qt.DotLine)
FOCUS_LINE                                         = QPen( QColor( 255, 255, 255 ) )
FOCUS_LINE.setStyle( Qt.DashLine )
SELECTION_LINE                                     = QPen( QColor( 0, 0, 255 ) )
SELECTION_LINE.setWidth(2)
PARTIAL_SELECTION_LINE                             = QPen( QColor( 128, 128, 255 ) )
PARTIAL_SELECTION_LINE.setWidth(2)
MOVE_LINE                                          = QPen( QColor( 255, 128, 0 ) )
MOVE_LINE_SEL                                      = QPen( QColor( 0, 128, 255 ) )
DISJOINT_LINE                                      = QPen( QColor( 0, 0, 0 ) )
DISJOINT_LINE.setWidth(3)
SELECTION_FILL                                     = Qt.NoBrush
COMPONENT_PEN                                      = QPen(QColor(0,0,0,alpha = 64))
SNAP_LINE                                          = QPen( QColor( 0, 255, 255 ) )
SNAP_LINE.setWidth( 3 )
SNAP_LINE.setStyle( Qt.DotLine )
SNAP_LINE_2                                        = QPen( QColor( 0, 0, 128 ) )
SNAP_LINE_2.setWidth( 3 )
NO_SEQUENCE_LINE                                   = QPen( QColor( 0, 0, 0 ) )
NO_SEQUENCE_LINE.setStyle( Qt.DashLine )
NO_SEQUENCE_BACKWARDS_LINE                         = QPen( QColor( 255, 0, 0 ) )
NO_SEQUENCE_BACKWARDS_LINE.setStyle( Qt.DashLine )
NO_SEQUENCE_FILL                                   = QBrush( QColor( 0, 0, 0, alpha = 32 ) )
TEXT_LINE                                          = QPen( QColor( 128, 128, 128 ) )
POSITION_TEXT                                      = QPen( QColor( 64, 64, 64 ) )
DARK_TEXT                                          = QPen( QColor( 0, 0, 0 ) )
LIGHT_TEXT                                         = QPen( QColor( 255, 255, 255 ) )
SINGLE_COMPONENT_COLOUR                            = QColor( 64, 64, 64 )

# Z-values (draw order)
Z_SEQUENCE = 1
Z_EDGES    = 2
Z_FOCUS    = 3


class LegoViewOptions:
    """
    Options on the lego view
    """
    
    def __init__( self ):
        self.colour_blend     = 1              # type: float
        self.toggle_selection = False          # type: bool
        self.y_snap           = True           # type: bool
        self.x_snap           = True           # type: bool
        self.view_edges       = True           # type: Optional[bool]
        self.view_piano_roll  = None           # type: Optional[bool]
        self.view_names       = True           # type: Optional[bool]
        self.view_positions   = None           # type: Optional[bool]
        self.view_component   = True           # type: bool
        self.mode             = EMode.SEQUENCE
        self.move_enabled     = False


class ColourBlock:
    def __init__( self, colour: QColor ):
        self.colour = colour
        self.brush = QBrush( colour )
        
        dark_colour = QColor( colour.red() // 2, colour.green() // 2, colour.blue() // 2 )
        self.pen = QPen( dark_colour )
        
        if colour.lightness() > 128:
            self.text = DARK_TEXT
        else:
            self.text = LIGHT_TEXT
    
    
    def blend( self, colour: QColor, amount ):
        new_colour = QtColourHelper.interpolate_colours( self.colour, colour, amount )
        
        return ColourBlock( new_colour )


class LegoEdgeViewTarget:
    def __init__( self, the_list : "List[LegoViewSubsequence]" ):
        self.list = the_list #type: List[LegoViewSubsequence]
    
    
    def __bool__( self ):
        return bool( self.list )
    
    
    def __average_colour( self ):
        return QtColourHelper.average_colour( list( x.colour.colour for x in self.list ) )
    
    
    def __extract_points( self, backwards ):
        results = [ ]
        
        if not backwards:
            for x in sorted( self.list, key = lambda z: z.window_rect().left() ):
                r = x.window_rect()  # type:QRect
                results.append( r.bottomLeft() )
                results.append( r.bottomRight() )
        else:
            for x in sorted( self.list, key = lambda z: -z.window_rect().left() ):
                r = x.window_rect()  # type:QRect
                results.append( r.topRight() )
                results.append( r.topLeft() )
        
        return results
    
    
    def top( self ):
        return self.list[ 0 ].window_rect().top()
    
    
    @staticmethod
    def paint_to( painter      : QPainter,
                  view_edges   : Optional[ bool ],
                  upper        : "LegoEdgeViewTarget",
                  lower        : "LegoEdgeViewTarget",
                  reduce_alpha : bool,
                  is_selected  : bool ):
        if not upper or not lower:
            return
        
        if view_edges is None:
            view_edges = is_selected
        
        if not view_edges:
            return
        
        alpha = 64 if not reduce_alpha else 32 if is_selected else 16
        
        upper_points = upper.__extract_points( False )
        lower_points = lower.__extract_points( True )
        
        upper_colour = upper.__average_colour()
        upper_colour = QColor( upper_colour )
        upper_colour.setAlpha( alpha )
        
        lower_colour = lower.__average_colour()
        lower_colour = QColor( lower_colour )
        lower_colour.setAlpha( alpha )
        
        left = min( upper_points[ 0 ].x(), lower_points[ -1 ].x() )
        #right = max( upper_points[ -1 ].x(), lower_points[ 0 ].x() )
        top = min( x.y() for x in upper_points )
        bottom = max( x.x() for x in lower_points )
        
        gradient = QLinearGradient( left, top, left, bottom )
        gradient.setColorAt( 0, upper_colour )
        gradient.setColorAt( 1, lower_colour )
        
        brush = QBrush( gradient )
        
        if is_selected:
            painter.setPen( SELECTION_EDGE_LINE )
        else:
            painter.setPen( Qt.NoPen )
            
        painter.setBrush( brush )
        painter.drawPolygon( QPolygonF( upper_points + lower_points + [ upper_points[ 0 ] ] ) )


class LegoEdgeView:
    def __init__( self, owner: "LegoViewComponent", source: LegoEdgeViewTarget, destination: LegoEdgeViewTarget, edge:LegoEdge ):
        self.owner = owner
        self.source = source
        self.destination = destination
        self.edge = edge
    
    
    @staticmethod
    def from_edge( owner: "LegoViewComponent", edge: LegoEdge ):
        source = [ ]  # type:List[LegoViewSubsequence]
        destination = [ ]  # type:List[LegoViewSubsequence]
        
        for x in edge.source:
            source.append( owner.owner.view_model.find_subsequence_view( x ) )
        
        for x in edge.destination:
            destination.append( owner.owner.view_model.find_subsequence_view( x ) )
        
        return LegoEdgeView( owner, LegoEdgeViewTarget( source ), LegoEdgeViewTarget( destination ), edge )
    
    
    def get_upper_and_lower( self ) -> "Tuple[LegoEdgeViewTarget,LegoEdgeViewTarget]":
        """
        
        :return: lower, upper 
        """
        if self.source.top() < self.destination.top():
            return self.destination, self.source
        else:
            return self.source, self.destination
    
    
    def __extract_rect( self, the_list ):
        result = the_list[ 0 ].window_rect()
        
        for x in the_list[ 1: ]:
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


class LegoViewComponent:
    """
    Connected component view
    """
    
    
    def __init__( self, owner: "LegoViewAllEdges", component: LegoComponent ):
        subsequence_views = [ owner.view_model.find_subsequence_view( x ) for x in component.all_subsequences() ]
        
        self.owner = owner
        self.component = component
        self.subsequence_views = subsequence_views
        
        if len( subsequence_views ) == 1:
            opaque_colour = SINGLE_COMPONENT_COLOUR
        else:
            opaque_colour = owner.next_colour()
        
        self.colour = ColourBlock( opaque_colour )
        
        edges = set()  # type:Set[LegoEdge]
        
        for subsequence_view in subsequence_views:
            subsequence_view.components.append(self)
            
            for edge in subsequence_view.subsequence.edges:
                edges.add( edge )
        
        self.edge_views = [ ]  # type: List[LegoEdgeView]
        self.line_view_targets = [ ]  # type:List[LegoEdgeViewTarget]
        
        for edge in edges:
            edge_view = LegoEdgeView.from_edge( self, edge )
            self.edge_views.append( edge_view )
        
        for line in component.lines:
            self.line_view_targets.append( LegoEdgeViewTarget( [ owner.view_model.find_subsequence_view( x ) for x in line ] ) )
    
    
    def paint( self, painter: QPainter ):
        """
        Paint edge group
        """
        options = self.owner.view_model.options
        
        if not options.view_component or options.mode == EMode.EDGE:
            #
            # ALL EDGES VIEW
            #
            for edge_view in self.edge_views:
                lower, upper = edge_view.get_upper_and_lower()
                is_selected  = edge_view.edge in self.owner.view_model.selected_edges()
                LegoEdgeViewTarget.paint_to( painter, options.view_edges, upper, lower, True, is_selected )
        else:
            #
            # COMPONENT VIEW
            #
            sorted_edge_targets = sorted( self.line_view_targets, key = lambda x: x.top() )
            
            for upper, lower in ArrayHelper.lagged_iterate( sorted_edge_targets ):
                assert isinstance(lower, LegoEdgeViewTarget)
                assert isinstance(upper, LegoEdgeViewTarget)
                LegoEdgeViewTarget.paint_to( painter, options.view_edges, upper, lower, False, False )


class LegoViewSubsequence( QGraphicsItem ):
    def __init__( self, subsequence: LegoSubsequence, owner_view: "LegoViewSequence", positional_index: int, precursor: "LegoViewSubsequence" ):
        #
        # SUPER
        #
        super().__init__()
        self.setFlag( QGraphicsItem.ItemSendsGeometryChanges, True )
        self.setFlag( QGraphicsItem.ItemIsFocusable, True )
        self.setFlag( QGraphicsItem.ItemIsSelectable, True )
        self.setZValue( Z_SEQUENCE )
        
        #
        # FIELDS
        #
        self.owner_sequence_view    = owner_view
        self.sibling_previous       = precursor
        self.sibling_next           = None #type: LegoViewSubsequence
        self.subsequence            = subsequence
        self.components             = [] # type:List[LegoViewComponent]
        self.mousedown_original_pos = None  # type:QPointF
        self.mousemove_label        = None  # type:str
        self.mousemove_snapline     = None  # type:Tuple[int,int]
        self.mousedown_move_all     = False
        self.index                  = positional_index
        self.edge_subsequence_views = [ ]  # type:List[LegoViewSubsequence]
        self.__colour               = ColourBlock( QColor( subsequence.ui_colour ) ) if subsequence.ui_colour else None
        
        #
        # POSITION
        #
        table = owner_view.owner_model_view.lookup_table
        self.rect = QRectF( 0, 0, subsequence.length * table.letter_size, table.sequence_height )
        
        if not subsequence.ui_position:
            self.restore_default_position()
        else:
            self.setPos( subsequence.ui_position[ 0 ], subsequence.ui_position[ 1 ] )
        
        #
        # PRECURSOR
        #
        if precursor:
            precursor.sibling_next = self
            
    @property
    def colour(self) -> ColourBlock:
        if self.__colour is not None:
            return self.__colour
        elif self.components:
            c = None
            
            for x in self.components:
                if c is None:
                    c = ColourBlock(x.colour.colour)
                else:
                    c = c.blend(x.colour.colour, 0.5)
            
            return c
        else:
            return DEFAULT_COLOUR
        
    @colour.setter
    def colour(self, value : Optional[ColourBlock]):
        self.__colour = value

    def restore_default_position( self ):
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
        self.subsequence.ui_colour = self.colour.colour.rgba() if self.colour is not None else None
    
    
    @override
    def boundingRect( self ) -> QRectF:
        return self.rect
    
    
    @override
    def paint( self, painter: QPainter, *args, **kwargs ):
        """
        Paint subsequence
        """
        r = self.rect
        painter.setBrush( self.colour.brush )
        painter.setPen( self.colour.pen )
        painter.drawRect( r )
        
        is_selected = self.is_selected_with_mask()
        is_partially_selected = not is_selected and self.isSelected()
        
        if is_selected or is_partially_selected:
            MARGIN = 4
            painter.setBrush(0)
            painter.setPen(SELECTION_LINE if is_selected else PARTIAL_SELECTION_LINE)
            painter.drawLine( r.left(), r.top() - MARGIN, r.right(), r.top()-MARGIN )
            painter.drawLine( r.left(), r.bottom() + MARGIN, r.right(), r.bottom()+MARGIN )
        
        if self.options.move_enabled:
            MARGIN = 16
            painter.setBrush( 0 )
            painter.setPen( MOVE_LINE_SEL if is_selected else MOVE_LINE )
            painter.drawLine( r.left()-MARGIN, r.top(), r.right()+MARGIN, r.top() )
            painter.drawLine( r.left()-MARGIN, r.bottom(), r.right()+MARGIN, r.bottom() )
            painter.drawLine( r.left(), r.top()-MARGIN, r.left(), r.bottom()+MARGIN )
            painter.drawLine( r.right(), r.top()-MARGIN, r.right(), r.bottom()+MARGIN )
            
            if self.sibling_next and self.sibling_next.window_rect().left() != self.window_rect().right():
                MARGIN = 8
                painter.setPen( DISJOINT_LINE )
                painter.drawLine( r.right(), r.top()-MARGIN, r.right(), r.bottom()+MARGIN )
                
            if self.sibling_previous and self.sibling_previous.window_rect().right() != self.window_rect().left():
                MARGIN = 8
                painter.setPen( DISJOINT_LINE )
                painter.drawLine( r.left(), r.top()-MARGIN, r.left(), r.bottom()+MARGIN )
                
        
        draw_piano_roll = self.options.view_piano_roll
        
        
        
        if draw_piano_roll is None:
            draw_piano_roll = is_selected or is_partially_selected
        
        if draw_piano_roll:
            lookup_table = self.owner_model_view.lookup_table
            letter_size = lookup_table.letter_size
            painter.setPen( Qt.NoPen )
            painter.setBrush( PIANO_ROLL_SELECTED_BACKGROUND if is_selected else PIANO_ROLL_UNSELECTED_BACKGROUND )
            OFFSET_X = letter_size
            rect_width = self.rect.width()
            rect_height = lookup_table.count * letter_size
            painter.drawRect( 0, OFFSET_X, rect_width, rect_height )
            
            array = self.subsequence.array
            
            if not array:
                painter.setPen( Pens.RED )
                painter.drawLine( 0, 0, rect_width, rect_height )
                painter.drawLine( 0, rect_height, rect_width, 0 )
            else:
                for i, c in enumerate( array ):
                    pos = lookup_table.letter_order_table.get( c )
                    
                    if pos is not None:
                        painter.setPen( lookup_table.letter_colour_table.get( c, SEQUENCE_DEFAULT_FG ) )
                        painter.drawEllipse( i * letter_size, pos * letter_size + OFFSET_X, letter_size, letter_size )
        
        if self.mousemove_snapline:
            x = self.mousemove_snapline[ 0 ] - self.pos().x()
            y = self.mousemove_snapline[ 1 ] - self.pos().y()
            painter.setPen( SNAP_LINE_2 )
            painter.drawLine( x, self.boundingRect().height() / 2, x, y )
            painter.setPen( SNAP_LINE )
            painter.drawLine( x, self.boundingRect().height() / 2, x, y )
            if not self.mousemove_label.startswith( "<" ):
                x -= QFontMetrics( painter.font() ).width( self.mousemove_label )
            
            if y < 0:
                y = self.rect.top() - TEXT_MARGIN
            else:
                y = self.rect.bottom() + TEXT_MARGIN + QFontMetrics( painter.font() ).xHeight()
            painter.setPen( TEXT_LINE )
            painter.drawText( QPointF( x, y ), self.mousemove_label ) # Mouse snapline position
        elif self.mousemove_label:
            painter.setPen( TEXT_LINE )
            painter.drawText( QPointF( self.rect.left() + TEXT_MARGIN, self.rect.top() - TEXT_MARGIN ), self.mousemove_label ) # Mouse position
        else:
            if self.__draw_position(is_selected):
                painter.setPen( POSITION_TEXT )
                
                text = str( self.subsequence.start )
                lx = self.rect.left() - QFontMetrics( painter.font() ).width( text ) / 2
                painter.setPen( TEXT_LINE )
                painter.drawText( QPointF( lx, self.rect.top() - TEXT_MARGIN ), text )
                
                if not self.__draw_next_sibling_position(is_selected):
                    text = str( self.subsequence.end )
                    x = self.rect.right() - QFontMetrics( painter.font() ).width( text ) / 2
                    y = self.rect.top() - TEXT_MARGIN if (x - lx) > 32 else self.rect.bottom() + QFontMetrics( painter.font() ).xHeight() + TEXT_MARGIN
                    painter.drawText( QPointF( x, y ), text )
            else:
                painter.setPen( COMPONENT_PEN )
                painter.setBrush( 0 )
                text = "".join(str(x.component) for x in self.components)
                x = (self.rect.left() + self.rect.right())/2 - QFontMetrics( painter.font() ).width( text ) / 2
                y = self.rect.top() - TEXT_MARGIN
                painter.drawText( QPointF( x, y ), text )
        
        # if self.hasFocus():
        #     r = self.rect.adjusted( 1, 1, -1, -1 )
        #     painter.setPen( FOCUS_LINE )
        #     painter.setBrush( 0 )
        #     painter.drawRect( r )
    
    
    def __draw_position( self, is_selected ):
        result = self.options.view_positions
        
        if result is None:
            result = is_selected
        
        return result
    
    
    def __draw_next_sibling_position( self, is_selected ):
        ns = self.sibling_next
        
        if ns is None:
            return False
        
        if not ns.__draw_position(is_selected):
            return False
        
        return ns.pos().x() == self.window_rect().right()
    
    
    def window_rect( self ) -> QRectF:
        result = self.boundingRect().translated( self.scenePos() )
        assert result.left() == self.pos().x(), "{} {}".format(self.window_rect().left(),self.pos().x())  #todo: remove
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
        """
        if m.buttons() & Qt.LeftButton:
            # Remember the initial position of ALL items because it IS possible for the selection to change via double-click events
            for item in self.owner_sequence_view.owner_model_view.scene.items():
                item.mousedown_original_pos = item.pos()
            
            enable_toggle_selection = not self.options.toggle_selection == (bool( (m.modifiers() & Qt.ControlModifier) or (m.modifiers() & Qt.MetaModifier) ))
            
            
            if not enable_toggle_selection:
                if self.isSelected():
                    return
                
                self.owner_sequence_view.owner_model_view.scene.clearSelection()
            
            status = not self.isSelected()
            
            mode = self.options.mode
            
            if mode == EMode.SEQUENCE:
                for x in self.owner_sequence_view.subsequence_views:
                    x.setSelected( status )
            elif mode == EMode.SUBSEQUENCE:
                self.setSelected( status )
            elif mode == EMode.EDGE:
                self.setSelected( status )
            elif mode == EMode.COMPONENT:
                for y in self.components:
                    for x in y.subsequence_views:
                        x.setSelected(status)
                    
            
            m.accept()
            self.owner_model_view._call_selection_changed()
    
    
    def mouseDoubleClickEvent(self, m:QGraphicsSceneMouseEvent):
        self.options.move_enabled = not self.options.move_enabled
        
        self.owner_model_view._call_options_changed()
        self.owner_model_view.scene.update()
    
    def focusInEvent( self, QFocusEvent ):
        self.setZValue( Z_FOCUS )
    
    
    def focusOutEvent( self, QFocusEvent ):
        self.setZValue( Z_SEQUENCE )
    
    
    def snaps( self ):
        for sequence_view in self.owner_sequence_view.owner_model_view.sequence_views:
            for subsequence_view in sequence_view.subsequence_views:
                if subsequence_view is not self:
                    left_snap = subsequence_view.scenePos().x()
                    right_snap = subsequence_view.scenePos().x() + subsequence_view.boundingRect().width()
                    yield left_snap, "Start of {0}".format( subsequence_view.subsequence ), subsequence_view.scenePos().y()
                    yield right_snap, "End of {0}".format( subsequence_view.subsequence ), subsequence_view.scenePos().y()
    
    
    def mouseMoveEvent( self, m: QGraphicsSceneMouseEvent ):
        if m.buttons() & Qt.LeftButton:
            if not self.options.move_enabled or self.mousedown_original_pos is None:
                return
            
            new_pos = self.mousedown_original_pos + (m.scenePos() - m.buttonDownScenePos( Qt.LeftButton ))  # type:QPointF
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
    
    
    def __apply_colour( self, e: QKeyEvent ):
        new_colour = KEY_COLOURS.get( e.key() )
        
        if new_colour is None:
            return
        
        self.owner_model_view.change_colours( new_colour )
        
    def __repr__(self):
        return "<<View of '{}' at ({},{})>>".format(self.subsequence, self.window_rect().left(), self.window_rect().top())


    def is_selected_with_mask( self, mask : bool = True ):
        if not self.isSelected():
            return False
            
        if mask:
            for to_remove in list(self.owner_model_view.selection_mask):
                if to_remove == self.subsequence:
                    return False  
                elif to_remove == self.subsequence.sequence:
                    return False
                    
        return True


class LegoViewSequence:
    """
    Views a sequence
    """
    
    
    def __init__( self, owner_model_view: "LegoViewModel", sequence: LegoSequence ):
        """
        :param owner_model_view: Owning view
        :param sequence: The sequence we are viewing
        """
        
        self.owner_model_view = owner_model_view
        self.sequence = sequence
        self.subsequence_view_lookup = {}  # type:Dict[LegoSubsequence, LegoViewSubsequence]
        self._recreate()
    
    @property
    def subsequence_views(self):
        return self.subsequence_view_lookup.values()
    
    def _recreate( self ):
        # Remove existing items
        for x in self.subsequence_views:
            self.owner_model_view.scene.removeItem( x )
            
        self.subsequence_view_lookup.clear()
        
        # Add new items
        previous_subsequence = None
        
        for subsequence in self.sequence.subsequences:
            subsequence_view                                        = LegoViewSubsequence( subsequence, self, len( self.subsequence_views ), previous_subsequence )
            self.subsequence_view_lookup[subsequence]               = subsequence_view
            self.owner_model_view.scene.addItem( subsequence_view )
            previous_subsequence                                    = subsequence_view


class LegoViewAllEdges( QGraphicsItem ):
    def __init__( self, view_model: "LegoViewModel" ):
        super().__init__()
        self.setZValue( Z_EDGES )
        self.__next_colour = -1
        self.view_model = view_model
        self.component_views = [ ]  # type: List[LegoViewComponent]
        
        for component in view_model.model.components:
            self.component_views.append( LegoViewComponent( self, component ) )
        
        self.rect = QRectF( 0, 0, 0, 0 )
        
        for sequence_view in view_model.sequence_views:
            for subsequence_view in sequence_view.subsequence_views:
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
        
        if self.__next_colour >= len( COMPONENT_COLOURS ):
            self.__next_colour = 0
        
        return COMPONENT_COLOURS[ self.__next_colour ]
    
    
    def boundingRect( self ):
        return self.rect
    
    
    def paint( self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[ QWidget ] = None ) -> None:
        """
        Paint all edges
        """
        for group in self.component_views:
            group.paint( painter )
        
        painter.setPen( NO_SEQUENCE_LINE )
        painter.setBrush( NO_SEQUENCE_FILL )
        
        for sequence_view in self.view_model.sequence_views:
            for subsequence_view in sequence_view.subsequence_views:
                # Draw my connection (left)
                if subsequence_view.sibling_previous is None:
                    continue
                
                precursor_rect = subsequence_view.sibling_previous.window_rect()
                my_rect = subsequence_view.window_rect()
                
                if precursor_rect.right() == my_rect.left():
                    continue
                
                if my_rect.left() < precursor_rect.right():
                    painter.drawLine( my_rect.left(), (my_rect.top() - 8), precursor_rect.right(), (precursor_rect.top() - 8) )
                    painter.drawLine( my_rect.left(), (my_rect.bottom() + 8), precursor_rect.right(), (precursor_rect.bottom() + 8) )
                    painter.drawLine( my_rect.left(), (my_rect.top() - 8), my_rect.left(), (my_rect.bottom() + 8) )
                    painter.drawLine( precursor_rect.right(), (precursor_rect.top() - 8), precursor_rect.right(), (precursor_rect.bottom() + 8) )
                else:
                    points = [ QPointF( my_rect.left(), my_rect.top() + 8 ),  # a |x...|
                               QPointF( my_rect.left(), my_rect.bottom() - 8 ),  # b |x...|
                               QPointF( precursor_rect.right(), precursor_rect.bottom() - 8 ),  # b |...x|
                               QPointF( precursor_rect.right(), precursor_rect.top() + 8 ) ]  # a |...x|
                    
                    points.append( points[ 0 ] )
                    
                    painter.drawPolygon( QPolygonF( points ) )
        
        if self.view_model.options.view_names is not False:
            for sequence_view in self.view_model.sequence_views:
                if self.view_model.options.view_names or any( x.is_selected_with_mask() for x in sequence_view.subsequence_views ):   #todo: reiterrant
                    leftmost_subsequence = sorted( sequence_view.subsequence_views, key = lambda xx: xx.pos().x() )[ 0 ]
                    text = sequence_view.sequence.accession
                    
                    if sequence_view.sequence.is_composite:
                        text = "⇌" + text
                        
                    if not hasattr(sequence_view.sequence, "is_root"):
                        sequence_view.sequence.is_root = False
                        
                    if sequence_view.sequence.is_root:
                        text = "↑" + text
                    
                    r = leftmost_subsequence.window_rect()
                    x = r.left() - TEXT_MARGIN - QFontMetrics( painter.font() ).width( text )
                    y = r.top() + r.height() / 2
                    painter.drawText( QPointF( x, y ), text )

class ILegoViewModelObserver:
    def ILegoViewModelObserver_selection_changed(self):
        pass
    
    def ILegoViewModelObserver_options_changed(self):
        pass
    
class LookupTable:
    def __init__( self, type_: ELetterType ):
        self.type = type_
        
        if type_ == ELetterType.PROTEIN:
            self.letter_size         = PROTEIN_SIZE
            self.letter_order_table  = PROTEIN_ORDER_TABLE
            self.letter_colour_table = PROTEIN_COLOUR_TABLE
        elif type_ == ELetterType.DNA:
            self.letter_size         = NUCLEOTIDE_SIZE
            self.letter_order_table  = DNA_ORDER_TABLE
            self.letter_colour_table = DNA_COLOUR_TABLE
        elif type_ == ELetterType.RNA:
            self.letter_size         = NUCLEOTIDE_SIZE
            self.letter_order_table  = RNA_ORDER_TABLE
            self.letter_colour_table = RNA_COLOUR_TABLE
        else:
            self.letter_size         = PROTEIN_SIZE
            self.letter_order_table  = PROTEIN_ORDER_TABLE
            self.letter_colour_table = PROTEIN_COLOUR_TABLE
            print( "Warning: Cannot create the lookup table because I don't know the letter type. Defaulting to `protein`.")
            
        self.count = len(self.letter_order_table)
        self.sequence_height = self.letter_size * (self.count + 2)
        self.sequence_ysep = self.sequence_height 

class LegoViewModel:
    def __init__( self, observer:ILegoViewModelObserver, view: QGraphicsView, focus_notification, model: LegoModel ):
        self.lookup_table = LookupTable( model.letter_type() )
        self.observer = observer
        self.view = view
        self.model = model
        self.selection_mask = set()
        self.scene = QGraphicsScene()
        self.sequence_views = [ ]  # type: List[LegoViewSequence]
        self.subsequence_views_lookup = {} #type: Dict[LegoSubsequence, LegoViewSubsequence]
        self.edges_view = None  # type: Optional[LegoViewAllEdges]
        self.focus_notification = focus_notification
        
        for sequence in self.model.sequences:
            item = LegoViewSequence( self, sequence )
            self.sequence_views.append( item )
            self.subsequence_views_lookup.update(item.subsequence_view_lookup)
        
        self.edges_view = self.update_edges()
        self.scene.addItem( self.edges_view )
        
        self.options = LegoViewOptions() 
    
    
    def _call_selection_changed( self ):
        """
        Calls the selection changed handler
        We do this manually because the native Qt signal handler is raised for every slight change, and slows things down.
        """
        self.observer.ILegoViewModelObserver_selection_changed()
        
    def _call_options_changed(self):
        """
        Calls the options-changed handler
        """
        self.observer.ILegoViewModelObserver_options_changed()
    
    
    def update_edges( self ) -> LegoViewAllEdges:
        if self.edges_view:
            self.scene.removeItem(self.edges_view)
            
        self.edges_view = LegoViewAllEdges( self )
        self.scene.addItem( self.edges_view )
        return self.edges_view
            
    
    
    def selected_subsequence_views( self, mask = True ) -> Set[ LegoViewSubsequence ]:
        result = set()
        
        for sequence_view in self.sequence_views:
            for subsequence_view in sequence_view.subsequence_views:
                if subsequence_view.is_selected_with_mask(mask = mask):
                    result.add( subsequence_view )
                    
        
        
        return result
    
    
    def selected_subsequence_view( self ) -> Optional[ LegoViewSubsequence ]:
        return ArrayHelper.only_first( self.selected_subsequence_views() )
    
    
    def selected_subsequences( self, mask = True ) -> Set[ LegoSubsequence ]:
        """
        Subsequences selected by the user
        """
        result = set( x.subsequence for x in self.selected_subsequence_views(mask = mask) )
            
        return result
    
    
    def selected_subsequence( self, mask = True ) -> Optional[ LegoSubsequence ]:
        return ArrayHelper.only_first( self.selected_subsequences(mask = mask) )
    
    
    def selected_sequences( self, mask = True ) -> Set[ LegoSequence ]:
        """
        Sequences selected by the user (complete or partial)
        """
        result = set( x.sequence for x in self.selected_subsequences(mask = False) )
        
        if mask:
            result -= self.selection_mask
            
        return result
    
    
    def selected_complete_sequences( self, mask = True ) -> Set[ LegoSequence ]:
        sel = self.selected_subsequences(mask = False)
        seqs = set( x.sequence for x in sel )
        results = set()
        
        for seq in seqs:
            if len( seq.subsequences ) == sum( x.sequence == seq for x in sel ):
                results.add( seq )
                
        if mask:
            results -= self.selection_mask
        
        return results
    
    
    def selected_complete_sequence( self ) -> Optional[ LegoSequence ]:
        return ArrayHelper.only_first( self.selected_complete_sequences() )
    
    
    def selected_sequence( self ) -> Optional[ LegoSequence ]:
        return ArrayHelper.only_first( self.selected_sequences() )
    
    
    def selected_edges( self, mask = True ) -> Set[ LegoEdge ]:
        """
        Edges selected by the user (complete or partial)
        """
        selected_subsequences = self.selected_subsequences(mask = False)
        
        if len( selected_subsequences ) == 0:
            return set()
        
        result = None  #type: Set[LegoEdge]
        
        for subsequence in selected_subsequences:
            if result is None:
                result = set( subsequence.edges )
            else:
                result = result.intersection( set( subsequence.edges ) )
            
        if mask:
            result -= self.selection_mask
        
        return result
    
    
    def selected_edge( self ) -> Optional[ LegoEdge ]:
        return ArrayHelper.only_first( self.selected_edges() )
    
    
    def selected_entities( self, mask = True ) -> Set[object ]:
        mode = self.options.mode
        
        if mode == EMode.COMPONENT:
            return self.selected_components(mask = mask)
        elif mode == EMode.SUBSEQUENCE:
            return self.selected_subsequences(mask = mask)
        elif mode== EMode.SEQUENCE:
            return self.selected_sequences(mask = mask)
        elif mode==EMode.EDGE:
            return self.selected_edges(mask = mask)
        else:
            raise SwitchError("self.options.mode", mode)


    def selected_components( self, mask = True ) -> Set[LegoComponent]:
        """
        Components selected by the user (complete)
        """
        
        r = set()
        selected_subsequences = self.selected_subsequences(mask = False)
        for component in self.model.components:
            if all( subsequence in selected_subsequences for subsequence in component.all_subsequences() ):
                r.add( component )
                
        if mask:
            r -= self.selection_mask
                
        return r
    
    def clear_selection_mask(self):
        self.selection_mask.clear()
    
    def set_selection_mask(self, item : object, state : bool):
        assert item is not None
        
        if state:
            if item in self.selection_mask: 
                self.selection_mask.remove(item)
        else:
            self.selection_mask.add(item)


    def change_colours( self, new_colour: Union[ QColor, ESequenceColour ] ):
        the_list = self.selected_subsequence_views() or self.subsequence_views
        
        if isinstance( new_colour, QColor ):
            the_colour = ColourBlock( new_colour )
        
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
        self.sequence_views.append( view )
        self.recreate_edges()
    
    
    def recreate_sequences( self, sequences: Iterable[LegoSequence] ):
        to_do = set(sequences)
        
        for sequence in self.sequence_views:
            if sequence.sequence in to_do:
                sequence._recreate()
                to_do.remove(sequence.sequence)
                
        for sequence in to_do:
            self.add_new_sequence(sequence)
        
        self.recreate_edges()
        self._call_selection_changed()
    
    
    def find_subsequence_view( self, target: LegoSubsequence ) -> LegoViewSubsequence:
        result = self.subsequence_views_lookup.get(target)
        
        if result is None:
            raise KeyError( "Cannot find the UI element for the subsequence '{0}'.".format( target ) )
        
        return result
    
    
    def recreate_edges( self ):
        self.scene.removeItem( self.edges_view )
        self.edges_view = LegoViewAllEdges( self )
        self.scene.addItem( self.edges_view )
    
    
    def remove_sequences( self, sequences : Iterable[LegoSequence] ):
        for sequence in sequences:
            sequence_view = self.find_sequence_view(sequence)
            
            for subsequence_view in sequence_view.subsequence_views:
                self.scene.removeItem(subsequence_view)
            
            self.sequence_views.remove(sequence_view)
            
        self.update_edges()
        self._call_selection_changed()
    
    
    def select( self, subsequences: List[ LegoSubsequence ] ):
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
    
    
    @property
    def subsequence_views( self ):
        return [ y for x in self.sequence_views for y in x.subsequence_views ]
    
    
    def __clear_selection( self ):
        """
        Internal function (externally just use `select_all(ESelect.REMOVE)`, which calls the handler)
        """
        for x in self.subsequence_views:
            x.setSelected( False )
    
    
    class __selection:
        def __init__( self, owner: "LegoViewModel" ):
            self.view = owner.view
            self.original_updates = None
            self.original_signals = None
        
        
        def __enter__( self ):
            self.original_updates = self.view.updatesEnabled()
            self.original_signals = self.view.signalsBlocked()
            self.view.setUpdatesEnabled( False )
            self.view.blockSignals( True )
        
        
        def __exit__( self, exc_type, exc_val, exc_tb ):
            self.view.setUpdatesEnabled( self.original_updates )
            self.view.blockSignals( self.original_signals )
            
    def select_left( self, select: ESelect = ESelect.APPEND ):
        the_list = list(self.selected_subsequence_views())
        
        with self.__selection( self ):
            for subsequence_view in the_list:
                x = subsequence_view.sibling_previous
                
                while x is not None:
                    select.set(x)
                    x = x.sibling_previous
                    


    def select_right( self, select: ESelect = ESelect.APPEND ):
        the_list = list(self.selected_subsequence_views())
        
        with self.__selection( self ):
            for subsequence_view in the_list:
                x = subsequence_view.sibling_next
                
                while x is not None:
                    select.set(x)
                    x = x.sibling_next


    def select_direct_connections( self, select: ESelect = ESelect.APPEND ):
        the_list = list(self.selected_subsequence_views())
        
        with self.__selection( self ):
            for subsequence_view in the_list:
                for x in subsequence_view.edge_subsequence_views:
                    select.set(x)
    
    
    def select_all( self, select: ESelect = ESelect.ONLY ):
        """
        Selects everything.
        """
        with self.__selection( self ):
            for i, x in enumerate( self.subsequence_views ):
                select.set( x )
    
    
    def select_empty( self, select: ESelect = ESelect.ONLY ):
        """
        Selects subsequences with no `array` data.
        """
        self.__clear_selection()
        
        for x in self.sequence_views:
            if x.sequence.array is None:
                for y in x.subsequence_views:
                    select.set( y )
        
        self._call_selection_changed()
    
    
    def select_component( self, component: LegoComponent, select: ESelect = ESelect.ONLY ):
        """
        Selects the specified `component`.
        """
        ss = component.all_subsequences()
        
        for x in self.subsequence_views:
            if x in ss:
                select.set( x )
        
        self._call_selection_changed()
    
    
    def find_sequence_view( self, sequence: LegoSequence ) -> LegoViewSequence:
        """
        Finds the view of the specified `sequence`.
        :exception KeyError:
        """
        for x in self.sequence_views:
            if x.sequence is sequence:
                return x
        
        raise KeyError( "sequence '{}' has no view.".format( sequence ) )
    
    
    def select_sequence( self, sequence: LegoSequence, select: ESelect = ESelect.ONLY ):
        """
        Selects the specified `sequence`.
        """
        self.__clear_selection()
        
        for x in self.find_sequence_view( sequence ).subsequence_views:
            select.set( x )
        
        self._call_selection_changed()
    
    
    def select_subsequence( self, subsequence: LegoSubsequence, select: ESelect = ESelect.ONLY ):
        """
        Selects the specified `subsequence`.
        """
        if select == ESelect.ONLY:
            self.__clear_selection()
        
        select.set( self.find_subsequence_view( subsequence ) )
        
        self._call_selection_changed()


    def align_to_sequence( self, sel_sequence : LegoSequence ):
        """
        Positions sequence views sharing components with `sel_sequence` so that their components align with those in `sel_sequence`.
        """
        components = [x for x in self.model.components if sel_sequence in x.all_sequences()]
        starts = {}
        
        for component in components:
            for line in component.lines:
                if line[0].sequence is sel_sequence:
                    starts[component] = self.find_subsequence_view(line[0]).window_rect().left()
                    
        touched = set()
                
        for component in components:
            start = starts[component]
            
            for line in component.lines:
                sequence = line[0].sequence
                
                if sequence is sel_sequence:
                    continue
                    
                self.align_sequence(line[0], start, touched)
                
    def align_sequence( self, specified_subsequence:LegoSubsequence, target_x:int, touched:Set[LegoViewSubsequence ] ):
        """
        Aligns the elements of a sequence, given that the `specified_subsequence` is placed at `target_x`.
        All subsequence views repositioned are added to the `touched` set, and any views already in the `touched` set are not modified.
        """
        what_view = self.find_subsequence_view( specified_subsequence )
        
        print("ALIGN {} TO {}".format( what_view, target_x ) )
        what_view.setPos( QPointF( target_x, what_view.window_rect().top() ) ) 
        touched.add(what_view)
        
        prev = what_view
        next = what_view.sibling_next
        
        while next:
            if next not in touched:
                x = prev.window_rect().right()
                if next.window_rect().left() != x:
                    next.setPos(QPointF(x, next.window_rect().top()) )
                    
                touched.add(next)
            
            prev = next
            next = next.sibling_next
            
        prev = what_view
        next = what_view.sibling_previous
        
        while next:
            if next not in touched:
                x = prev.window_rect().left() - next.window_rect().width() 
                
                if next.window_rect().left() != x:
                    next.setPos(QPointF(x, next.window_rect().top()) )
                    
                touched.add(next)
            
            prev = next
            next = next.sibling_previous


    


COMPONENT_COLOURS = [ QColor( 255, 0, 0 ),     # R
                      QColor( 0, 255, 0 ),     # G
                      QColor( 0, 0, 255 ),     # B
                      QColor( 0, 255, 255 ),   # C
                      QColor( 255, 255, 0 ),   # Y
                      QColor( 255, 0, 255 ),   # M
                      QColor( 0, 255, 128 ),   # Cg
                      QColor( 255, 128, 0 ),   # Yr
                      QColor( 255, 0, 128 ),   # Mr
                      QColor( 0, 128, 255 ),   # Cb
                      QColor( 128, 255, 0 ),   # Yg
                      QColor( 128, 0, 255 ) ]  # Mb ]

KEY_COLOURS = { 
                Qt.Key_0: Colours.BLACK,
                Qt.Key_1: Colours.BLUE,
                Qt.Key_2: Colours.GREEN,
                Qt.Key_3: Colours.CYAN,
                Qt.Key_4: Colours.RED,
                Qt.Key_5: Colours.MAGENTA,
                Qt.Key_6: Colours.YELLOW,
                Qt.Key_7: Colours.WHITE,
                Qt.Key_8: Colours.GRAY,
                Qt.Key_9: Colours.DARK_GRAY,
                Qt.Key_K: Colours.BLACK,
                Qt.Key_B: Colours.BLUE,
                Qt.Key_G: Colours.GREEN,
                Qt.Key_C: Colours.CYAN,
                Qt.Key_R: Colours.RED,
                Qt.Key_M: Colours.MAGENTA,
                Qt.Key_Y: Colours.YELLOW,
                Qt.Key_W: Colours.WHITE,
                Qt.Key_L: Colours.GRAY,
                Qt.Key_D: Colours.DARK_GRAY,
                Qt.Key_P: ESequenceColour.RANDOM,
                Qt.Key_O: ESequenceColour.RESET,
              }

DEFAULT_COLOUR = ColourBlock( Colours.GRAY )
