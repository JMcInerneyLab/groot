from groot.frontends.gui.forms.designer import frm_big_text_designer

from groot.algorithms import fastaiser
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.forms.frm_base import FrmBase
from mhelper import file_helper
from mhelper_qt import exceptToGui, exqtSlot, qt_gui_helper


class FrmBigText( FrmBase ):
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_big_text_designer.Ui_Dialog( self )
        self.setWindowTitle( "Data" )
        
        self.ANSI_SCHEME = qt_gui_helper.ansi_scheme_dark( family = 'Consolas,"Courier New",monospace' )
        self.on_refresh_data()
    
    
    def on_refresh_data( self ):
        selection = self.get_selection()
        model = self.get_model()
        
        self.ui.BTN_SELECTION.setText( str( self.get_selection() ) )
        
        text = []
        
        if self.ui.RAD_FASTA.isChecked():
            for item in selection:
                fasta = fastaiser.to_fasta( item )
                text.append( qt_gui_helper.ansi_to_html( cli_view_utils.colour_fasta_ansi( fasta, model.site_type ), self.ANSI_SCHEME ) )
        elif self.ui.RAD_BLAST.isChecked():
            for item in selection:
                if hasattr( item, "comments" ):
                    text.append( "\n".join( item.comments ) )
                else:
                    text.append( "; NOT AVAILABLE - BLAST is not available for {}".format( type( item ).__name__ ) )
        
        self.ui.TXT_MAIN.setHtml( "<br/>\n".join( text ) )
    
    
    @exqtSlot()
    def on_BTN_SELECTION_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_selection_menu()
    
    
    @exqtSlot()
    def on_BTN_SAVE_clicked( self ) -> None:
        """
        Signal handler:
        """
        file_name = qt_gui_helper.browse_save( self, "All files (*.*)" )

        if file_name:
            file_helper.write_all_text( file_name, self.ui.TXT_MAIN.toPlainText() )
