from PyQt5.QtCore import QPoint, QRect, Qt
from PyQt5.QtGui import QBrush, QColor, QMouseEvent, QPainter, QPen
from PyQt5.QtWidgets import QSizePolicy, QWidget
from groot_gui.forms.designer import frm_alignment_designer
from typing import Optional

import groot
from groot_gui.forms.frm_base import FrmBaseWithSelection
from groot_gui.lego import LookupTable
from mhelper import bio_helper
import mhelper_qt as qt


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
        self.genes = []
        self.table: LookupTable = None
    
    
    def clear( self ):
        self.max_len = 0
        self.genes = []
        self.table = None
        self.highlight_row = None
        self.highlight_col = None
    
    
    def load( self, table: LookupTable, fasta: str ):
        sequences = list( bio_helper.parse_fasta( text = fasta ) )
        self.max_len = max( len( x[1] ) for x in sequences ) if sequences else 0
        self.genes = []
        
        for i in range( len( sequences ) ):
            self.genes.append( (sequences[i][0], sequences[i][1].ljust( self.max_len )) )
        
        self.table = table
        self.highlight_row = None
        self.highlight_col = None
    
    
    def get_gene_name( self, row ) -> Optional[str]:
        if row is None or row < 0 or row >= len( self.genes ):
            return None
        
        return self.genes[row][0]
    
    
    def paintEvent( self, ev ):
        p = QPainter( self )
        y = 0
        table = self.table
        
        for row, (name, sequence) in enumerate( self.genes ):
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
                color = qt.qt_colour_helper.interpolate_colours( color, QColor( 255, 255, 255 ), 0.5 )
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
                if row != 0 and char != self.get_site_text( col, row - 1 ):
                    p.setPen( QPen( QColor( 0, 0, 0 ) ) )
                    p.drawLine( QPoint( x + 4, y ), QPoint( x + COL_WIDTH - 4, y ), )
                
                x += COL_WIDTH
            
            y += COL_WIDTH
    
    
    def get_pos( self, e: QMouseEvent ):
        col = e.x() // COL_WIDTH
        row = e.y() // COL_WIDTH
        
        if row < 0 or row >= len( self.genes ):
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
        """
        Mouse click to display current position.
        """
        row, col = self.get_pos( e )
        self.highlight_col = col
        self.highlight_row = row
        
        if row is None:
            self.owner.ui.BTN_SEQUENCE.setText( "" )
        else:
            self.owner.ui.BTN_SEQUENCE.setText( "{} of {}: {}".format( row + 1, len( self.genes ), self.genes[row][0] ) )
        
        if col is None:
            self.owner.ui.BTN_SITE.setText( "" )
            self.owner.ui.BTN_POSITION.setText( "" )
        else:
            self.owner.ui.BTN_SITE.setText( "{}".format( self.get_site_text( col, row ) ) )
            self.owner.ui.BTN_POSITION.setText( "{} of {}".format( col + 1, len( self.genes[row][1] ) ) )
        
        self.update()
    
    
    def get_site_text( self, col, row ):
        if col < 0 or col >= len( self.genes ):
            return ""
        
        gd = self.genes[row][1]
        
        if row < 0 or row >= len( gd ):
            return ""
        
        return gd[col]
    
    
    def mouseDoubleClickEvent( self, e: QMouseEvent ):
        """
        Double click to allow sorting by column:
            * Presence of X for a site (cell value)
            * Hamming distance for a c (row header)
        """
        row, col = self.get_pos( e )
        
        if row is None:
            return
        
        if col is not None:
            x = self.get_site_text( col, row )
            
            
            def ___dist( sequence ):
                return 0 if sequence[col] == x else 1
            
            
            self.sort_sequences( ___dist )
        
        else:
            def ___dist( sequence ):
                sequence_b = self.genes[row][1]
                
                return sum( sequence[i] != sequence_b[i] for i in range( len( sequence_b ) ) )
            
            
            self.sort_sequences( ___dist )
    
    
    def sort_sequences( self, distance_function ):
        with_dist = [(name, sequence, distance_function( sequence )) for (name, sequence) in self.genes]
        with_dist = sorted( with_dist, key = lambda x: x[2] )
        self.genes = [(btn, view) for (btn, view, _) in with_dist]
        self.update()


class FrmAlignment( FrmBaseWithSelection ):
    """
    The alignment screen allows viewing of alignment data, as well as standard sequence data.
    
    Clicking sites displays more information about that site.
    
    Double clicking sites sorts by closeness to that site, whilst double clicking gene names
    sorts by closeness to that gene.
    """
    
    
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
        self.ui.SCR_MAIN.valueChanged[int].connect( self.on_scroll_value_changed )
        
        self.ui.LBL_ERROR.setVisible( False )
        self.bind_to_label( self.ui.LBL_SELECTION_WARNING )
        self.add_select_button( self.ui.FRA_TOOLBAR )
        self.update_view()
    
    
    def update_view( self ):
        model = self.get_model()
        entity = self.selection
        fasta = []
        
        try:
            fasta.append( ";\n;{}\n".format( str( entity ) ) )
            if isinstance( entity, groot.IHasFasta ):
                fasta.append( entity.to_fasta() )
        except groot.FastaError as ex:
            self.ui.LBL_ERROR.setText( str( ex ) )
            self.ui.LBL_ERROR.setVisible( True )
            self.ui.LBL_SELECTION_WARNING.setVisible( False )
            self.seq_view.clear()
            error = True
        else:
            if fasta:
                self.seq_view.load( LookupTable( model.site_type ), "\n".join( fasta ) )
                self.ui.LBL_ERROR.setVisible( False )
                self.ui.LBL_SELECTION_WARNING.setVisible( False )
                error = False
            else:
                self.ui.LBL_SELECTION_WARNING.setVisible( True )
                self.seq_view.clear()
                error = True
        
        self.ui.SCR_MAIN.setEnabled( not error )
        self.ui.LBL_POSITION_START.setEnabled( not error )
        self.ui.LBL_POSITION_END.setEnabled( not error )
        
        if not error:
            win_width = (self.seq_view.rect().width() // COL_WIDTH) - NUM_RESERVED_COLS
            self.ui.SCR_MAIN.setPageStep( win_width )
            self.ui.SCR_MAIN.setMinimum( 0 )
            self.ui.SCR_MAIN.setMaximum( self.seq_view.max_len - 1 )
            self.ui.SCR_MAIN.setValue( 0 )
            self.ui.LBL_POSITION_START.setText( str( 1 ) )
            self.ui.LBL_POSITION_END.setText( str( self.seq_view.max_len ) )
        
        self.repaint_view()
    
    
    def on_inspect( self, item: object ):
        super().on_inspect( item )
        self.update_view()
    
    
    def on_scroll_value_changed( self, _: int ):
        self.repaint_view()
        self.ui.LBL_SCRPOS.setText( str( self.ui.SCR_MAIN.value() + 1 ) )
    
    
    def repaint_view( self ):
        self.seq_view.update()
    
    
    @qt.exqtSlot()
    def on_BTN_VIEW_ELSEWHERE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.inspect_elsewhere()
    
    
    @qt.exqtSlot()
    def on_BTN_REFRESH_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.update_view()
    
    
    @qt.exqtSlot()
    def on_BTN_SEQUENCE_clicked( self ) -> None:
        """
        Signal handler:
        """
        accession = self.seq_view.get_gene_name( self.seq_view.highlight_row )
        
        if accession:
            gene: groot.Gene = groot.current_model().genes[accession]
            self.inspect_elsewhere( gene )
    
    
    @qt.exqtSlot()
    def on_BTN_POSITION_clicked( self ) -> None:
        """
        Signal handler:
        """
        accession = self.seq_view.get_gene_name( self.seq_view.highlight_row )
        
        if accession:
            gene: groot.Gene = groot.current_model().genes[accession]
            col = self.seq_view.highlight_col
            domains = list( x for x in gene.iter_userdomains() if x.start <= col <= x.end )
            self.inspect_elsewhere( domains )
    
    
    @qt.exqtSlot()
    def on_BTN_SITE_clicked( self ) -> None:
        """
        Signal handler:
        """
        accession = self.seq_view.get_gene_name( self.seq_view.highlight_row )
        
        if accession:
            gene: groot.Gene = groot.current_model().genes[accession]
            col = self.seq_view.highlight_col
            site = self.seq_view.get_site_text( self.seq_view.highlight_row, col )
            domains = list( x for x in gene.iter_userdomains() if x.start <= col <= x.end and x.site_array[col] == site )
            self.inspect_elsewhere( domains )
    
    
    @qt.exqtSlot()
    def on_BTN_HELP_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_my_help()
