
from intermake.hosts.base import DMultiHostProvider


def __create_lego_gui_host():
    from typing import cast
    
    from intermake.hosts.base import RunHostArgs
    from intermake.hosts.gui import GuiHost
    from mhelper import ignore
    
    
    class LegoGuiHost( GuiHost ):
        def on_run_host( self, args: RunHostArgs ):
            from PyQt5.QtCore import QCoreApplication, Qt
            from PyQt5.QtWebEngineWidgets import QWebEngineView
            ignore( QWebEngineView )
            QCoreApplication.setAttribute( Qt.AA_ShareOpenGLContexts )
            from groot.frontends.gui import gui_workflow
            gui_workflow.init()
            super().on_run_host( args )
        
        
        def on_create_window( self, args ):
            from groot.frontends.gui.forms.resources import resources_rc as groot_resources_rc
            from intermake.hosts.frontends.gui_qt.designer.resource_files import resources_rc as intermake_resources_rc
            cast( None, groot_resources_rc )
            cast( None, intermake_resources_rc )
            from groot.frontends.gui.forms.frm_main import FrmMain
            return FrmMain()
    
    
    return LegoGuiHost()


def setup() -> DMultiHostProvider:
    from intermake import create_simple_host_provider_from_class
    from intermake.hosts.console import ConsoleHost
    return create_simple_host_provider_from_class( ConsoleHost, __create_lego_gui_host )
