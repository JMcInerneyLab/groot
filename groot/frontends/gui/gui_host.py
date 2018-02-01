from typing import cast

from PyQt5.QtCore import QCoreApplication, Qt

from intermake.hosts.base import RunHostArgs
from intermake.hosts.gui import GuiHost
from mhelper import ignore


class LegoGuiHost( GuiHost ):
    def run_host( self, args: RunHostArgs ):
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        ignore( QWebEngineView )
        QCoreApplication.setAttribute( Qt.AA_ShareOpenGLContexts )
        super().run_host( args )
    
    
    def create_window( self, args ):
        from groot.frontends.gui.forms.resources import resources_rc as groot_resources_rc
        from intermake.hosts.frontends.gui_qt.designer.resource_files import resources_rc as intermake_resources_rc
        cast( None, groot_resources_rc )
        cast( None, intermake_resources_rc )
        from groot.frontends.gui.forms.frm_main import FrmMain
        return FrmMain()
