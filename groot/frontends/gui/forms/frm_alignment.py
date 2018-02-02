from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPen
from PyQt5.QtWidgets import QSizePolicy, QWidget
from groot.frontends.gui.forms.designer import frm_alignment_designer

from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view import LookupTable
from mhelper import array_helper, bio_helper
from mhelper_qt import exqtSlot, qt_colour_helper


COL_WIDTH = 16
NUM_RESERVED_COLS = 6
DEFAULT_PEN = QPen( QColor( 255, 0, 0 ) )


class AlignmentViewWidget( QWidget ):
    def __init__( self, parent, owner ):
        super().__init__( parent )
        self.owner: FrmAlignment = owner
        self.highlight_row = None
        self.highlight_col = None
        self.max_len: int = 0
        self.sequences = []
        self.table: LookupTable = None
    
    
    def clear( self ):
        self.max_len = 0
        self.sequences = []
        self.table = None
        self.highlight_row = None
        self.highlight_col = None
    
    
    def load( self, table: LookupTable, fasta: str ):
        sequences = list( bio_helper.parse_fasta( text = fasta ) )
        self.max_len = max( len( x[1] ) for x in sequences )
        self.sequences = []
        
        for i in range( len( sequences ) ):
            self.sequences.append( (sequences[i][0], sequences[i][1].ljust( self.max_len )) )
        
        self.table = table
        self.highlight_row = None
        self.highlight_col = None
    
    
    def paintEvent( self, ev ):
        p = QPainter( self )
        y = 0
        table = self.table
        
        for row, (name, sequence) in enumerate( self.sequences ):
            # Name background
            color = QColor( 0, 0, 255 )
            brush = QBrush( color )
            r = QRect( 0, y, COL_WIDTH * NUM_RESERVED_COLS, COL_WIDTH )
            p.fillRect( r, brush )
            
            # Name text
            text_pen = QPen( QColor( 255, 255, 255 ) )
            p.setPen( text_pen )
            p.drawText( r, Qt.AlignRight | Qt.AlignVCenter, name )
            
            x = COL_WIDTH * NUM_RESERVED_COLS
            
            start = max( 0, self.owner.ui.SCR_MAIN.value() )
            
            for col in range( start, len( sequence ) ):
                char = sequence[col]
                pen: QPen = table.letter_colour_table.get( char, DEFAULT_PEN )
                color = pen.color()
                color = qt_colour_helper.interpolate_colours( color, QColor( 255, 255, 255 ), 0.5 )
                brush = QBrush( color )
                
                # Site background
                r = QRect( x, y, COL_WIDTH, COL_WIDTH )
                p.fillRect( r, brush )
                
                # Site text
                if row == self.highlight_row and col == self.highlight_col:
                    text_pen = QPen( QColor( 0, 0, 255 ) )
                elif row == self.highlight_row or col == self.highlight_col:
                    text_pen = QPen( QColor( 0, 0, 0 ) )
                else:
                    text_pen = QPen( QColor( 128, 128, 128 ) )
                
                p.setPen( text_pen )
                p.drawText( r, Qt.AlignHCenter | Qt.AlignVCenter, char )
                
                # Site changed indicator
                if row != 0 and char != self.sequences[row - 1][1][col]:
                    p.setPen( QPen( QColor( 0, 0, 0 ) ) )
                    p.drawLine( QPoint( x + 4, y ), QPoint( x + COL_WIDTH - 4, y ), )
                
                x += COL_WIDTH
            
            y += COL_WIDTH
    
    
    def get_pos( self, e: QMouseEvent ):
        col = e.x() // COL_WIDTH
        row = e.y() // COL_WIDTH
        
        if row < 0 or row >= len( self.sequences ):
            return None, None
        
        if col >= NUM_RESERVED_COLS:
            col = col + self.owner.ui.SCR_MAIN.value() - NUM_RESERVED_COLS
            if 0 <= col < self.max_len:
                return row, col
            else:
                return None, None
        elif col >= 0:
            return row, None
        else:
            return None, None
    
    
    def mousePressEvent( self, e: QMouseEvent ):
        row, col = self.get_pos( e )
        self.highlight_col = col
        self.highlight_row = row
        
        if row is None:
            self.owner.ui.LBL_INFO.setText( "Not a valid selection." )
        elif col is None:
            self.owner.ui.LBL_INFO.setText( "Sequence {}: {}".format( row, self.sequences[row][0] ) )
        else:
            self.owner.ui.LBL_INFO.setText( "Sequence: {} {}, Site {}: {}".format( row, self.sequences[row][0], col, self.sequences[row][1][col] ) )
        
        self.update()
    
    
    def mouseDoubleClickEvent( self, e: QMouseEvent ):
        row, col = self.get_pos( e )
        
        if row is None:
            return
        
        if col is not None:
            x = self.sequences[row][1][col]
            
            
            def ___dist( sequence ):
                return 0 if sequence[col] == x else 1
            
            
            self.sort_sequences( ___dist )
            self.owner.ui.LBL_INFO.setText( "Sorted by presence of {} at site {}.".format( x, col ) )
        
        else:
            def ___dist( sequence ):
                sequence_b = self.sequences[row][1]
                
                return sum( sequence[i] != sequence_b[i] for i in range( len( sequence_b ) ) )
            
            
            self.sort_sequences( ___dist )
            self.owner.ui.LBL_INFO.setText( "Sorted by hamming distance to {}.".format( self.sequences[row][0] ) )
    
    
    def sort_sequences( self, distance_function ):
        with_dist = [(name, sequence, distance_function( sequence )) for (name, sequence) in self.sequences]
        with_dist = sorted( with_dist, key = lambda x: x[2] )
        self.sequences = [(btn, view) for (btn, view, _) in with_dist]
        self.update()


class FrmAlignment( FrmBase ):
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_alignment_designer.Ui_Dialog( self )
        self.setWindowTitle( "Alignments" )
        
        self.seq_view = AlignmentViewWidget( None, self )
        self.seq_view.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        self.ui.GRID_MAIN.addWidget( self.seq_view, 0, 0 )
        self.actions.bind_to_label(self.ui.LBL_SELECTION_WARNING)
        self.actions.bind_to_select(self.ui.BTN_SELECTION)
    
    
    def update_view( self ):
        model = self.get_model()
        selection = self.get_selection()
        
        win_width = (self.seq_view.rect().width() // COL_WIDTH) - NUM_RESERVED_COLS
        self.ui.SCR_MAIN.setPageStep( win_width )
        self.ui.SCR_MAIN.setMinimum( 0 )
        self.ui.SCR_MAIN.setMaximum( max( 0, self.seq_view.max_len - win_width ) )
        self.ui.SCR_MAIN.setValue( 0 )
        self.ui.SCR_MAIN.valueChanged[int].connect( self.on_scroll_value_changed )
        self.ui.BTN_SELECTION.setText( str( selection ) )
        
        component = array_helper.first_or_none( selection.components )
        
        if component:
            self.ui.LBL_SELECTION_WARNING.setVisible( False )
            self.seq_view.load( LookupTable( model.site_type ), component.get_alignment_by_accession() )
        else:
            self.ui.LBL_SELECTION_WARNING.setVisible( True )
            self.seq_view.clear()
        
        self.repaint_view()
    
    
    def on_selection_changed( self ):
        self.update_view()
    
    
    def on_scroll_value_changed( self, _: int ):
        self.repaint_view()
    
    
    def repaint_view( self ):
        self.seq_view.update()
        self.ui.LBL_POSITION_START.setText( str( self.ui.SCR_MAIN.value() ) )
        self.ui.LBL_POSITION_END.setText( str( self.ui.SCR_MAIN.value() + self.ui.SCR_MAIN.pageStep() ) )
    
    
    @exqtSlot()
    def on_BTN_START_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.ui.SCR_MAIN.setValue( 0 )
    
    
    @exqtSlot()
    def on_BTN_END_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.ui.SCR_MAIN.setValue( self.ui.SCR_MAIN.maximum() )
    
    
    @exqtSlot()
    def on_BTN_SELECTION_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
