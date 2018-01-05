from typing import List, Tuple
from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPen
from PyQt5.QtWidgets import QDialog, QSizePolicy, QWidget, QMessageBox
from mhelper import bio_helper
from mhelper_qt import exqtSlot, qt_colour_helper
from groot.frontends.gui.forms.designer.frm_alignment_designer import Ui_Dialog
from groot.frontends.gui.gui_view import LookupTable


XSTEP = 16
RESCOL = 6
DEFAULT_PEN = QPen( QColor( 255, 0, 0 ) )


class AlignmentViewWidget( QWidget ):
    def __init__( self, parent, table: LookupTable, sequences: List[Tuple[str, str]], owner ):
        QWidget.__init__( self, parent )
        self.max_len: int = max( len( x[1] ) for x in sequences )
        self.sequences = []
        
        for i in range( len( sequences ) ):
            self.sequences.append( (sequences[i][0], sequences[i][1].ljust( self.max_len )) )
        self.table: LookupTable = table
        self.owner: FrmAlignment = owner
        self.hrow = None
        self.hcol = None
    
    
    def paintEvent( self, ev ):
        p = QPainter( self )
        y = 0
        x = 0
        table = self.table
        
        for row, (name, sequence) in enumerate( self.sequences ):
            # Name background
            color = QColor( 0, 0, 255 )
            brush = QBrush( color )
            r = QRect( 0, y, XSTEP * RESCOL, XSTEP )
            p.fillRect( r, brush )
            
            # Name text
            text_pen = QPen( QColor( 255, 255, 255 ) )
            p.setPen( text_pen )
            p.drawText( r, Qt.AlignRight | Qt.AlignVCenter, name )
            
            x = XSTEP * RESCOL
            
            for col in range( self.owner.ui.SCR_MAIN.value(), len( sequence ) ):
                char = sequence[col]
                pen: QPen = table.letter_colour_table.get( char, DEFAULT_PEN )
                color = pen.color()
                color = qt_colour_helper.interpolate_colours( color, QColor( 255, 255, 255 ), 0.5 )
                brush = QBrush( color )
                
                # Site background
                r = QRect( x, y, XSTEP, XSTEP )
                p.fillRect( r, brush )
                
                # Site text
                if row == self.hrow and col == self.hcol:
                    text_pen = QPen( QColor( 0, 0, 255 ) )
                elif row == self.hrow or col == self.hcol:
                    text_pen = QPen( QColor( 0, 0, 0 ) )
                else:
                    text_pen = QPen( QColor( 128, 128, 128 ) )
                
                p.setPen( text_pen )
                p.drawText( r, Qt.AlignHCenter | Qt.AlignVCenter, char )
                
                # Site changed indicator
                if row != 0 and char != self.sequences[row - 1][1][col]:
                    p.setPen( QPen( QColor( 0, 0, 0 ) ) )
                    p.drawLine( QPoint( x + 4, y ), QPoint( x + XSTEP - 4, y ), )
                
                x += XSTEP
            
            y += XSTEP
    
    
    def get_pos( self, e: QMouseEvent ):
        col = e.x() // XSTEP
        row = e.y() // XSTEP
        
        if row < 0 or row >= len( self.sequences ):
            return None, None
        
        if col >= RESCOL:
            col = col + self.owner.ui.SCR_MAIN.value() - RESCOL
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
        self.hcol = col
        self.hrow = row
        
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


class FrmAlignment( QDialog ):
    def __init__( self, parent, title:str,table: LookupTable, fasta: str ):
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        self.setWindowTitle(title)
        
        fastas: List[Tuple[str, str]] = list( bio_helper.parse_fasta( text = fasta ) )
        
        
        self.seq_view = AlignmentViewWidget( None, table, fastas, self )
        self.seq_view.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        self.ui.GRID_MAIN.addWidget( self.seq_view, 0, 0 )
        
        win_width = self.seq_view.rect().width() // XSTEP
        self.ui.SCR_MAIN.setPageStep( win_width )
        self.ui.SCR_MAIN.setMaximum( self.seq_view.max_len - win_width )
        self.ui.SCR_MAIN.setValue( 0 )
        self.ui.SCR_MAIN.valueChanged[int].connect( self.on_scroll_value_changed )
    
    
    def on_scroll_value_changed( self, _: int ):
        self.seq_view.update()
    
    
    @staticmethod
    def request( parent, title, table: LookupTable, fasta: str ):
        if not fasta:
            QMessageBox.warning(parent, "FASTA", "There is no FASTA data for this item.")
            return
        
        frm = FrmAlignment( parent, title, table, fasta )
        
        frm.exec_()
    
    
    @exqtSlot()
    def on_BTN_START_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.ui.SCR_MAIN.setValue(0)
    
    
    @exqtSlot()
    def on_BTN_END_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.ui.SCR_MAIN.setValue(self.ui.SCR_MAIN.maximum())
    
    
    @exqtSlot()
    def on_BTNBOX_MAIN_accepted( self ) -> None:
        """
        Signal handler:
        """
        self.accept()
    
    
    @exqtSlot()
    def on_BTNBOX_MAIN_rejected( self ) -> None:
        """
        Signal handler:
        """
        self.reject()
