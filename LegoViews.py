"""
MVC architecture.

Classes that manage the view of the model.
"""
from MHelper.CommentHelper import override
from typing import Optional, List, Any, Set
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QPolygonF
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QStyleOptionGraphicsItem
from PyQt5.QtWidgets import QWidget

from LegoModels import LegoSequence, LegoSubsequence, LegoModel

MULT = 2
ESIZE = 2
MIN_SEQUENCE_HEIGHT = MULT * 16
SEQUENCE_MARGIN = MULT * 8
SEQUENCE_HEIGHT = 32
TARGET_MARGIN = MULT * 2
TEXT_MARGIN = MULT * 8

SEQ_OL = QPen( QColor( 0, 0, 0 ) )
SEQ_BG = QBrush( QColor( 64, 64, 64 ) )
CUTS_OL = QPen( QColor( 255, 255, 255 ) )
CUTE_OL = QPen( QColor( 0, 0, 0 ) )
TARGET_OL = QPen( QColor( 255, 0, 0 ) )
TARGET_BG = QBrush( QColor( 255, 0, 0 ) )
CON_OL = QPen( QColor( 0, 255, 0 ) )

COLOURS = [ QColor( 255, 0, 0 ),  # R
            QColor( 0, 255, 0 ),  # G
            QColor( 0, 0, 255 ),  # B
            QColor( 0, 255, 255 ),  # C
            QColor( 255, 255, 0 ),  # Y
            QColor( 255, 0, 255 ),  # M
            QColor( 0, 255, 128 ),  # Cg
            QColor( 255, 128, 0 ),  # Yr
            QColor( 255, 0, 128 ),  # Mr
            QColor( 0, 128, 255 ),  # Cb
            QColor( 128, 255, 0 ),  # Yg
            QColor( 128, 0, 255 ) ]  # Mb ]

NEXT_COLOUR = -1


def next_colour( ) -> QColor:
    global NEXT_COLOUR
    NEXT_COLOUR += 1
    if NEXT_COLOUR >= len( COLOURS ):
        NEXT_COLOUR = 0

    return COLOURS[ NEXT_COLOUR ]


class LegoComponentView:
    """
    Connected component view
    """

    def __init__( self, owner: "LegoViewAllEdges", targets: "List[LegoViewSubsequence]" ):
        self.owner = owner
        self.targets = targets

        opaque_colour = next_colour( )

        target_brush = QBrush( )

        for target in targets:
            target.brush = target_brush

        transparent_colour = QColor( opaque_colour )
        transparent_colour.setAlpha( 64 )

        self.pen = QPen( opaque_colour )
        self.brush = QBrush( transparent_colour )

    def paint( self, painter: QPainter ):
        previous = None

        for target_ui in sorted( self.targets, key=lambda x: x.window_rect( ).top( ) ):

            if previous:
                self.draw_connection( previous, target_ui, painter )

            previous = target_ui

    def draw_connection( self, a: "LegoViewSubsequence", b: "LegoViewSubsequence", painter: QPainter ):
        ar = a.window_rect( )
        br = b.window_rect( )

        ca = (ar.top( ) + ar.bottom( )) / 2
        cb = (br.top( ) + br.bottom( )) / 2

        points = [ QPointF( ar.left( ), ca ),  # a |x...|
                   QPointF( br.left( ), cb ),  # b |x...|
                   QPointF( br.right( ), cb ),  # b |...x|
                   QPointF( ar.right( ), ca ) ]  # a |...x|

        painter.setPen( self.pen )
        painter.setBrush( self.brush )
        painter.drawPolygon( QPolygonF( points ) )


class LegoViewSubsequence( QGraphicsItem ):
    def __init__( self, subsequence: LegoSubsequence, owner_view: "LegoViewSequence", positional_index: int,
                  pos: QPointF ):
        super( ).__init__( )

        self.rect = QRectF( pos.x( ) + subsequence.start * ESIZE, pos.y( ), subsequence.length * ESIZE,
                            SEQUENCE_HEIGHT )
        self.setFlag( QGraphicsItem.ItemIsMovable, True )
        self.setFlag( QGraphicsItem.ItemSendsGeometryChanges, True )

        self.subsequence = subsequence
        self.owner_view = owner_view
        self.index = positional_index
        self.edges = [ ]  # type:List[LegoViewSubsequence]
        self.brush = None

    @override
    def boundingRect( self ) -> QRectF:
        return self.rect

    @override
    def paint( self, painter: QPainter, **kwargs ):
        painter.setBrush( SEQ_BG )
        painter.setPen( SEQ_OL )
        painter.drawRect( self.rect )

        if self.index == 0:
            text = self.subsequence.sequence.accession
        else:
            text = str( self.index )

        painter.drawText( QPointF( self.rect.right( ) + TEXT_MARGIN, self.rect.center( ).y( ) ), text )

    def window_rect( self ) -> QRectF:
        return self.boundingRect( ).translated( self.scenePos( ) )

    @override
    def itemChange( self, change: int, value: Any ):  # change is QGraphicsItem.GraphicsItemChange
        result = super( ).itemChange( change, value )

        if change == QGraphicsItem.ItemPositionChange:
            self.owner_view.owner.update_edges( )

        return result


class LegoViewSequence:
    """
    Views a sequence
    """

    def __init__( self, owner_view: "LegoViewModel", sequence: LegoSequence, pos: QPointF ):
        """
        :param owner_view: Owning view
        :param sequence: The sequence we are viewing
        :param pos: Position in the view
        """

        self.owner = owner_view
        self.sequence = sequence
        self.subsequence_views = [ ]  # type:List[LegoViewSubsequence]

        for target in sequence.subsequences:
            self.subsequence_views.append( LegoViewSubsequence( target, self, len( self.subsequence_views ), pos ) )


class LegoViewAllEdges( QGraphicsItem ):
    def __init__( self, view_model: "LegoViewModel" ):
        super( ).__init__( )
        self.view_model = view_model
        self.component_views = [ ]  # type: List[LegoComponentView]

        for connected_component in self.__create_components( ):
            self.component_views.append( LegoComponentView( self, connected_component ) )

    def paint( self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[ QWidget ] = None ) -> None:
        for group in self.component_views:
            group.paint( painter )

    def __create_components( self ):
        the_list = [ ]
        for s in self.view_model.model.sequences.values( ):  # type: LegoSequence
            for ss in s.subsequences:
                self.__connect_components( ss, the_list )

        result = [ ]

        for set_ in the_list:
            set_2 = [ ]
            result.append( set_2 )

            for subsequence in set_:
                set_2.append( self.find_ui_element( subsequence ) )

        return result

    def find_ui_element( self, target: LegoSubsequence ):
        for sequence_view in self.view_model.sequence_views:
            for subsequence_view in sequence_view.subsequence_views:
                if subsequence_view.subsequence == target:
                    return subsequence_view

        raise KeyError( "Missing target UI element." )

    @classmethod
    def __connect_components( cls, subsequence: LegoSubsequence, set_list: List[ Set[ LegoViewSubsequence ] ] ):
        for set_ in set_list:
            if subsequence in set_:
                return

        set_ = set( )
        set_list.append( set_ )
        cls.__connect_to( subsequence, set_ )

    @classmethod
    def __connect_to( cls, subsequence: LegoSubsequence, target: set ):
        if subsequence in target:
            return  # Already visited

        target.add( subsequence )

        for friend in subsequence.edges:
            cls.__connect_to( friend, target )


class LegoViewModel:
    def __init__( self, model: LegoModel ):
        self.model = model
        self.scene = QGraphicsScene( )
        self.sequence_views = [ ]  # type: List[LegoViewSequence]
        self.edges = None #type: Optional[LegoViewAllEdges]

    def update( self ):
        y = 0

        for sequence in self.model.sequences:
            item = LegoViewSequence( self, sequence, QPointF( 0, y ) )
            self.sequence_views.append( item )
            self.scene.addItem( item )
            y = item.subsequence_views[ 0 ].boundingRect( ).bottom( ) + SEQUENCE_MARGIN

        self.edges = LegoViewAllEdges( self )
        self.scene.addItem( self.edges )

    def update_edges( self ):
        if self.edges:
            self.edges.update( )