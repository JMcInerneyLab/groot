from groot_gui.forms.designer import frm_startup_designer
from groot.data import global_view
from groot.data.global_view import RecentFile
from groot_gui.forms.frm_base import FrmBase
from groot_gui.utilities import gui_workflow
from intermake.engine.environment import MENV
from mhelper import file_helper
from mhelper_qt import exceptToGui


class FrmStartup( FrmBase ):
    """
    This screen is displayed by default when the Groot GUI starts.
    """
    
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
            assert isinstance(file, RecentFile)
            r.append( '<li><a href="file_load:{}">{}</a></li>'.format( file.file_name, file_helper.get_filename_without_extension( file.file_name ) ) )
        
        r.append( '<li><a href="action:{}"><i>browse...</i></a></li>'.format( gui_workflow.handlers().ACT_FILE_OPEN ) )
        r.append( "</ul>" )
        
        r.append( "<h3>Sample data</h3><ul>" )
        
        for file in global_view.get_samples():
            r.append( '<li><a href="file_sample:{}">{}</a><li/>'.format( file, file_helper.get_filename_without_extension( file ) ) )
        
        r.append( '<li><a href="action:{}"><i>browse...</i></a></li>'.format( gui_workflow.handlers().VIEW_OPEN_FILE ) )
        r.append( "</ul>" )
        
        txt = txt.replace( "$(RECENT_FILES)", "\n".join( r ) )
        
        self.ui.LBL_FIRST_MESSAGE.setText( txt )
        self.bind_to_label( self.ui.LBL_FIRST_MESSAGE )
