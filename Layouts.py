from typing import Optional, List, Any

from PyQt5.QtCore import QLineF
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QPolygon
from PyQt5.QtGui import QPolygonF
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QStyleOptionGraphicsItem
from PyQt5.QtWidgets import QWidget

import Monkey
from BlastResult import SequenceMananager, Sequence, Target


MULT = 2
MIN_SEQUENCE_HEIGHT = MULT * 16
SEQUENCE_MARGIN = MULT * 8
TARGET_HEIGHT = MULT * 2
TARGET_MARGIN = MULT * 2
TEXT_MARGIN = MULT * 8

SEQ_OL = QPen( QColor( 0, 0, 0 ) )
SEQ_BG = QBrush( QColor( 64, 64, 64 ) )
CUT_OL = QPen( QColor( 0, 0, 0 ) )
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


class GroupSubLayout:
    def __init__( self, owner: "EdgeLayout", targets: "List[TargetSubLayout]" ):
        self.owner = owner
        self.targets = targets
        self.colour = next_colour( )

        print( "GROUP BEGINS" )
        for target in targets:
            target.colour = self.colour
            print( "    + " + str( target.target ) )


    def paint( self, painter: QPainter ):

        previous = None

        for target_ui in sorted( self.targets, key = lambda x: x.window_rect( ).top( ) ):

            if previous:
                self.draw_connection( previous, target_ui, painter )

            previous = target_ui


    def draw_connection( self, a: "TargetSubLayout", b: "TargetSubLayout", painter: QPainter ):
        ar = a.window_rect( )
        br = b.window_rect( )

        ca = (ar.top( ) + ar.bottom( )) / 2
        cb = (br.top( ) + br.bottom( )) / 2

        points = [ QPointF( ar.left( ), ca ),  # a |x...|
                   QPointF( br.left( ), cb ),  # b |x...|
                   QPointF( br.right( ), cb ),  # b |...x|
                   QPointF( ar.right( ), ca ) ]  # a |...x|

        colour = QColor( a.colour )
        colour.setAlpha( 64 )

        painter.setPen( QPen( a.colour ) )
        painter.setBrush( QBrush( colour ) )
        painter.drawPolygon( QPolygonF( points ) )


class TargetSubLayout:
    def __init__( self, target: Target, owner: "SeqLayout", index: int ):
        self.target = target
        self.owner = owner
        self.index = index
        self.edges = [ ]  # type:List[TargetSubLayout]
        self.colour = None


    def boundingRect( self ) -> QRectF:
        owner = self.owner
        return QRectF( owner.rect.x( ) + self.target.start * MULT,
                       owner.rect.top( ) + TARGET_MARGIN + (TARGET_MARGIN + TARGET_HEIGHT) * self.index,
                       owner.rect.x( ) + self.target.length * MULT,
                       TARGET_HEIGHT )


    def paint( self, painter: QPainter ):
        painter.setBrush( QBrush( self.colour ) )
        painter.setPen( QPen( self.colour ) )
        painter.drawRect( self.boundingRect( ) )


    def window_rect( self ) -> QRectF:
        return self.boundingRect( ).translated( self.owner.scenePos( ) )


class SeqLayout( QGraphicsItem ):
    def itemChange( self, change: int, value: Any ):  # change is QGraphicsItem.GraphicsItemChange
        result = super( ).itemChange( change, value )

        if change == QGraphicsItem.ItemPositionChange:
            self.owner.update_edges( )

        return result


    def __init__( self, owner: "SeqLayoutManager", sequence: Sequence, pos: QPointF ):
        super( ).__init__( )
        self.owner = owner
        self.sequence = sequence

        height = max( MIN_SEQUENCE_HEIGHT, (len( sequence.targets ) + 1) * (TARGET_HEIGHT + TARGET_MARGIN) )

        self.rect = QRectF( pos.x( ), pos.y( ), self.sequence.length * MULT, height )

        self.setFlag( QGraphicsItem.ItemIsMovable, True )
        self.setFlag( QGraphicsItem.ItemSendsGeometryChanges, True )

        self.targets = [ ]  # type:List[TargetSubLayout]

        for target in self.sequence.targets:
            self.targets.append( TargetSubLayout( target, self, len( self.targets ) ) )


    def boundingRect( self ) -> QRectF:
        return self.rect


    def paint( self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[ QWidget ] = None ) -> None:
        painter.setBrush( SEQ_BG )
        painter.setPen( SEQ_OL )
        painter.drawRect( self.rect )
        painter.drawText( QPointF( self.rect.right( ) + TEXT_MARGIN, self.rect.top( ) ), self.sequence.name )

        for cut in self.sequence.cuts:
            painter.setPen( CUT_OL )
            painter.drawLine( QLineF( MULT * cut.position, self.rect.top( ), MULT * cut.position, self.rect.bottom( ) ) )

        y = self.rect.top( ) + TARGET_MARGIN

        for target in self.targets:
            target.paint( painter )


class EdgeLayout( QGraphicsItem ):
    def __init__( self, owner: "SeqLayoutManager", manager: SequenceMananager ):
        super( ).__init__( )
        self.manager = manager
        self.group_uis = [ ]

        for group in manager.groups:
            group_ui = list( [ owner.find_ui_element( x ) for x in group ] )
            self.group_uis.append( GroupSubLayout( self, group_ui ) )


    def paint( self, painter: QPainter, option: QStyleOptionGraphicsItem, widget: Optional[ QWidget ] = None ) -> None:
        for group in self.group_uis:
            group.paint( painter )


class SeqLayoutManager:
    def __init__( self, manager: SequenceMananager, scene: QGraphicsScene ):

        y = 0

        self.sequences = [ ]

        for sequence in manager.sequences:
            item = SeqLayout( self, sequence, QPointF( 0, y ) )
            self.sequences.append( item )
            scene.addItem( item )
            y = item.boundingRect( ).bottom( ) + SEQUENCE_MARGIN

        self.edges = EdgeLayout( self, manager )
        scene.addItem( self.edges )


    def update_edges( self ):
        if self.edges:
            self.edges.update( )


    def find_ui_element( self, target: Target ):
        for sequence_ui in self.sequences:
            for target_ui in sequence_ui.targets:
                if target_ui.target == target:
                    return target_ui

        raise KeyError( "Missing target UI element." )
