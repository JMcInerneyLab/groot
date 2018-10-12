import typing
import intermake_qt


class LegoGuiController( intermake_qt.GuiControllerWithBrowser ):
    """
    Wraps the GUI as an Intermake host.
    """
    
    
    def on_start( self ):
        """
        OVERRIDE to apply our Open GL settings before the window opens.
        """
        from PyQt5.QtCore import QCoreApplication, Qt
        import groot.data.config
        
        if groot.data.config.options().share_opengl:
            QCoreApplication.setAttribute( Qt.AA_ShareOpenGLContexts )
        
        super().on_start()
    
    
    def on_create_window( self, args ):
        """
        OVERRIDE to show our custom window (`FrmMain`)
        """
        from groot_gui.forms.resources import resources_rc as groot_resources_rc
        from intermake_qt.forms.designer.resource_files import resources_rc as intermake_resources_rc
        typing.cast( None, groot_resources_rc )
        typing.cast( None, intermake_resources_rc )
        from groot_gui.forms.frm_main import FrmMain
        return FrmMain()
