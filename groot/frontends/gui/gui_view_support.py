from enum import Enum

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPen

from mhelper import array_helper, MEnum
from mhelper_qt import Colours, Pens, qt_colour_helper


_DARK_TEXT = QPen( QColor( 0, 0, 0 ) )
_LIGHT_TEXT = QPen( QColor( 255, 255, 255 ) )


class ColourBlock:
    """
    Represents a colour on a subsequence.
    """
    
    
    def __init__( self, colour: QColor ) -> None:
        self.colour = colour
        self.brush = QBrush( colour )
        
        dark_colour = QColor( colour.red() // 2, colour.green() // 2, colour.blue() // 2 )
        self.pen = QPen( dark_colour )
        
        if colour.lightness() > 128:
            self.text = _DARK_TEXT
        else:
            self.text = _LIGHT_TEXT
    
    
    def blend( self, colour: QColor, amount: float ) -> "ColourBlock":
        new_colour = qt_colour_helper.interpolate_colours( self.colour, colour, amount )
        
        return ColourBlock( new_colour )


class EMode( Enum ):
    SEQUENCE = 0
    SUBSEQUENCE = 1
    EDGE = 2
    COMPONENT = 3


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


class DRAWING:
    # Order of sites in piano roll
    PROTEIN_ORDER_TABLE = array_helper.create_index_lookup( "IVLFCMAGTSWYPHEQDNKR" )
    DNA_ORDER_TABLE = array_helper.create_index_lookup( "ATCG" )
    RNA_ORDER_TABLE = array_helper.create_index_lookup( "AUCG" )
    
    # Colour of sites in piano roll
    PROTEIN_COLOUR_TABLE = { "G": Pens.WHITE, "A": Pens.WHITE, "V": Pens.WHITE, "L": Pens.WHITE, "I": Pens.WHITE,
                             "F": Pens.ORANGE, "Y": Pens.ORANGE, "W": Pens.ORANGE,
                             "C": Pens.YELLOW, "M": Pens.YELLOW,
                             "S": Pens.GREEN, "T": Pens.GREEN,
                             "K": Pens.RED, "R": Pens.RED, "H": Pens.RED,
                             "D": Pens.CYAN, "E": Pens.CYAN,
                             "N": Pens.DARK_ORANGE, "Q": Pens.DARK_ORANGE,
                             "P": Pens.LIGHT_RED,
                             "-": Pens.GRAY }
    DNA_COLOUR_TABLE = { "A": Pens.YELLOW, "T": Pens.RED, "C": Pens.GREEN, "G": Pens.LIGHT_BLUE, "-": Pens.GRAY }
    RNA_COLOUR_TABLE = { "A": Pens.YELLOW, "U": Pens.RED, "C": Pens.GREEN, "G": Pens.LIGHT_BLUE, "-": Pens.GRAY }
    
    # Colour of components
    COMPONENT_COLOURS = [QColor( 255, 0, 0 ),  # R
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
                         QColor( 128, 0, 255 )]  # Mb
    
    # Sizes
    SIZE_MULTIPLIER = 2
    PROTEIN_SIZE = SIZE_MULTIPLIER * 1
    NUCLEOTIDE_SIZE = SIZE_MULTIPLIER * 1
    TEXT_MARGIN = SIZE_MULTIPLIER * 4
    
    # Pens and brushes
    PIANO_ROLL_SELECTED_BACKGROUND = QBrush( QColor( 0, 0, 0 ) )
    PIANO_ROLL_UNSELECTED_BACKGROUND = QBrush( QColor( 0, 0, 0, alpha = 128 ) )
    SEQUENCE_DEFAULT_FG = QPen( QColor( 255, 255, 0 ) )
    SELECTION_EDGE_LINE = QPen( QColor( 0, 0, 255 ) )
    SELECTION_EDGE_LINE.setWidth( 2 )
    EDGE_LINE = QPen( QColor( 128, 128, 128 ) )
    EDGE_LINE.setStyle( Qt.DotLine )
    FOCUS_LINE = QPen( QColor( 255, 255, 255 ) )
    FOCUS_LINE.setStyle( Qt.DashLine )
    SELECTION_LINE = QPen( QColor( 0, 0, 255 ) )
    SELECTION_LINE.setWidth( 2 )
    PARTIAL_SELECTION_LINE = QPen( QColor( 128, 128, 255 ) )
    PARTIAL_SELECTION_LINE.setWidth( 2 )
    MOVE_LINE = QPen( QColor( 255, 128, 0 ) )
    MOVE_LINE_SEL = QPen( QColor( 0, 128, 255 ) )
    DISJOINT_LINE = QPen( QColor( 0, 0, 0 ) )
    DISJOINT_LINE.setWidth( 3 )
    SELECTION_FILL = Qt.NoBrush
    COMPONENT_PEN = QPen( QColor( 0, 0, 0, alpha = 64 ) )
    SNAP_LINE = QPen( QColor( 0, 255, 255 ) )
    SNAP_LINE.setWidth( 3 )
    SNAP_LINE.setStyle( Qt.DotLine )
    SNAP_LINE_2 = QPen( QColor( 0, 0, 128 ) )
    SNAP_LINE_2.setWidth( 3 )
    NO_SEQUENCE_LINE = QPen( QColor( 0, 0, 0 ) )
    NO_SEQUENCE_LINE.setStyle( Qt.DashLine )
    NO_SEQUENCE_BACKWARDS_LINE = QPen( QColor( 255, 0, 0 ) )
    NO_SEQUENCE_BACKWARDS_LINE.setStyle( Qt.DashLine )
    NO_SEQUENCE_FILL = QBrush( QColor( 0, 0, 0, alpha = 32 ) )
    TEXT_LINE = QPen( QColor( 128, 128, 128 ) )
    POSITION_TEXT = QPen( QColor( 64, 64, 64 ) )
    DARK_TEXT = _DARK_TEXT
    LIGHT_TEXT = _LIGHT_TEXT
    SINGLE_COMPONENT_COLOUR = QColor( 64, 64, 64 )
    DEFAULT_COLOUR = ColourBlock( Colours.GRAY )
    ERROR_COLOUR = ColourBlock( Colours.RED )
    
    # Z-values
    Z_SEQUENCE = 1
    Z_EDGES = 2
    Z_FOCUS = 3


class EDomainFunction( MEnum ):
    """
    Domain generator function.
    
    :data COMPONENT: Components (parameter is unused)
    :data FIXED_WIDTH: Fixed-width (parameter defines width)
    :data FIXED_COUNT: Fixed-count (parameter defines width)
    """
    NONE = 0
    COMPONENT = 1
    FIXED_WIDTH = 2
    FIXED_COUNT = 3
