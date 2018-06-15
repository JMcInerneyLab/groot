from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush, QColor, QPen, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView

from groot import ESiteType

from mhelper import array_helper
from mhelper_qt import Colours, Pens, qt_colour_helper


_DARK_TEXT = QPen( QColor( 0, 0, 0 ) )
_LIGHT_TEXT = QPen( QColor( 255, 255, 255 ) )


class InteractiveGraphicsView( QGraphicsView ):
    """
    Subclasses QGraphicsView to provide mouse zooming. 
    """
    
    
    def wheelEvent( self, event: QWheelEvent ):
        """
        Zoom in or out of the view.
        """
        if event.modifiers() & Qt.ControlModifier or event.modifiers() & Qt.MetaModifier:
            zoomInFactor = 1.25
            zoomOutFactor = 1 / zoomInFactor
            
            # Save the scene pos
            oldPos = self.mapToScene( event.pos() )
            
            # Zoom
            if event.angleDelta().y() > 0:
                zoomFactor = zoomInFactor
            else:
                zoomFactor = zoomOutFactor
            self.scale( zoomFactor, zoomFactor )
            
            # Get the new position
            newPos = self.mapToScene( event.pos() )
            
            # Move scene to old position
            delta = newPos - oldPos
            self.translate( delta.x(), delta.y() )


class ColourBlock:
    """
    Represents a colour on a domain.
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
    SIZE_MULTIPLIER = 1
    PROTEIN_SIZE = SIZE_MULTIPLIER * 1
    NUCLEOTIDE_SIZE = SIZE_MULTIPLIER * 1
    TEXT_MARGIN = SIZE_MULTIPLIER * 4
    
    # Pens and brushes
    PIANO_ROLL_SELECTED_BACKGROUND = QBrush( QColor( 0, 0, 0 ) )
    PIANO_ROLL_UNSELECTED_BACKGROUND = QBrush( QColor( 0, 0, 0, alpha = 128 ) )
    GENE_DEFAULT_FG = QPen( QColor( 255, 255, 0 ) )
    SELECTION_EDGE_LINE = QPen( QColor( 0, 0, 255 ) )
    SELECTION_EDGE_LINE.setWidth( 2 )
    EDGE_LINE = QPen( QColor( 128, 128, 128 ) )
    FOCUS_LINE = QPen( QColor( 255, 255, 255 ) )
    FOCUS_LINE.setStyle( Qt.DashLine )
    SELECTION_LINE = QPen( QColor( 0, 0, 255 ) )
    SELECTION_LINE.setWidth( 3 )
    PARTIAL_SELECTION_LINE = QPen( QColor( 128, 128, 255 ) )
    PARTIAL_SELECTION_LINE.setWidth( 2 )
    MOVE_LINE = QPen( QColor( 255, 0, 0 ) )
    MOVE_LINE.setWidth( 3 )
    MOVE_LINE_SEL = QPen( QColor( 0, 255, 255 ) )
    MOVE_LINE_SEL.setWidth( 3 )
    MOVE_LINE_SEL.setStyle( Qt.DotLine )
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
    Z_GENE = 1
    Z_EDGES = 2
    Z_FOCUS = 3


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
        self.gene_height = max( self.letter_size * (self.count + 2), 16 )
        self.gene_ysep = self.gene_height
