


def create_lego_gui_host():
    from typing import cast
    from intermake import RunHost
    from intermake_qt import GuiHost
    from mhelper import ignore
    
    
    class LegoGuiHost( GuiHost ):
        def on_run_host( self, args: RunHost ):
            from PyQt5.QtCore import QCoreApplication, Qt
            from PyQt5.QtWebEngineWidgets import QWebEngineView
            ignore( QWebEngineView )
            QCoreApplication.setAttribute( Qt.AA_ShareOpenGLContexts )
            from groot.frontends.gui import gui_workflow
            gui_workflow.init()
            super().on_run_host( args )
        
        
        def on_create_window( self, args ):
            from groot.frontends.gui.forms.resources import resources_rc as groot_resources_rc
            from intermake_qt.forms.designer.resource_files import resources_rc as intermake_resources_rc
            cast( None, groot_resources_rc )
            cast( None, intermake_resources_rc )
            from groot.frontends.gui.forms.frm_main import FrmMain
            return FrmMain()
    
    
    return LegoGuiHost()


