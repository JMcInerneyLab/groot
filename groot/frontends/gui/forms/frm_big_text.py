from groot.data import global_view
from groot.frontends.gui.forms.designer import frm_big_text_designer
from groot.frontends.gui.forms.frm_base import FrmSelectingToolbar
from groot.frontends.gui.gui_view_utils import ESelect
from groot.utilities import entity_to_html
from mhelper import file_helper
from mhelper_qt import exceptToGui, exqtSlot, qt_gui_helper


class FrmBigText( FrmSelectingToolbar ):
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_big_text_designer.Ui_Dialog( self )
        self.setWindowTitle( "Report generator" )
        
        self.html: str = ""
        
        self.ui.CHK_DATA.setChecked( True )
        self.ui.CHK_COLOURS.setChecked( True )
        
        self.bind_to_workflow_box( self.ui.FRA_TOOLBAR, ESelect.ALL )
        
        self.on_refresh_data()
    
    
    def on_refresh_data( self ):
        selection = self.get_selection()
        
        html = []
        
        for item in selection:
            html.append( entity_to_html.render( item, global_view.current_model() ) )
        
        self.html = "\n".join( html )
        self.ui.TXT_MAIN.setHtml( self.html )
    
    
    @exqtSlot()
    def on_BTN_SAVE_clicked( self ) -> None:
        """
        Signal handler:
        """
        file_name: str = qt_gui_helper.browse_save( self, "HTML (*.html);;Plain text (*.txt)" )
        
        if file_name:
            if file_name.endswith( ".txt" ):
                file_helper.write_all_text( file_name, self.ui.TXT_MAIN.toPlainText() )
            else:
                file_helper.write_all_text( file_name, self.html )
    
    
    def on_BTN_REFRESH_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.on_refresh_data()
