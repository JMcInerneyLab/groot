from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog
from typing import Optional

from groot.frontends.gui.gui_view_utils import EChanges
from intermake import intermake_gui, ArgsKwargs
from intermake.engine.plugin import Plugin
from intermake.hosts.frontends.gui_qt.frm_arguments import FrmArguments
from mhelper_qt import menu_helper


class FrmBase( QDialog ):
    def __init__( self, parent ):
        super().__init__( parent )
        self.parent = parent
        self.setStyleSheet( intermake_gui.default_style_sheet() )
        
    def on_plugin_completed( self, change : EChanges ):
        pass
    
    
    def closeEvent( self, event: QCloseEvent ):
        self.parent.remove_form( self )
    
    
    def show_menu( self, *args ):
        return menu_helper.show( self.sender(), *args )
    
    
    def show_form( self, form_class ):
        from groot.frontends.gui.forms.frm_main import FrmMain
        frm_main: FrmMain = self.parent
        frm_main.show_form( form_class )
    
    
    def request( self, plugin: Plugin, *args, **kwargs ):
        if args is None:
            args = ()
        
        arguments: Optional[ArgsKwargs] = FrmArguments.request( self, plugin, *args, **kwargs )
        
        if arguments is not None:
            plugin.run( *arguments.args, **arguments.kwargs )  # --> self.plugin_completed
