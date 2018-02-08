from groot.frontends.gui.forms.designer import frm_startup_designer
from groot.data import global_view
from groot.frontends.gui.forms.frm_base import FrmBase
from intermake.engine.environment import MENV
from mhelper import file_helper
from mhelper_qt import exceptToGui


class FrmStartup( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_startup_designer.Ui_Dialog( self )
        self.setWindowTitle( "Startup" )
        
        txt = self.ui.LBL_FIRST_MESSAGE.text()
        
        txt = txt.replace( "$(VERSION)", MENV.version )
        r = []
        
        r.append( "<h3>Recent files</h3><ul>" )
        
        for file in reversed( global_view.options().recent_files ):
            r.append( '<li><a href="load_file:{}">{}</a></li>'.format( file, file_helper.get_filename_without_extension( file ) ) )
        
        r.append( '<li><a href="action:{}"><i>browse...</i></a></li>'.format( self.actions.browse_open.__name__ ) )
        r.append( "</ul>" )
        
        r.append( "<h3>Sample data</h3><ul>" )
        
        for file in global_view.get_samples():
            r.append( '<li><a href="load_sample:{}">{}</a><li/>'.format( file, file_helper.get_filename_without_extension( file ) ) )
        
        r.append( '<li><a href="action:{}"><i>browse...</i></a></li>'.format( self.actions.show_load_model.__name__ ) )
        r.append( "</ul>" )
        
        txt = txt.replace( "$(RECENT_FILES)", "\n".join( r ) )
        
        self.ui.LBL_FIRST_MESSAGE.setText( txt )
        self.actions.bind_to_label( self.ui.LBL_FIRST_MESSAGE )
