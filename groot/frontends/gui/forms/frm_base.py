from typing import Optional

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QAction, QDialog, QMenu

from groot.data import global_view
from groot.data.lego_model import ILegoSelectable, LegoSequence
from groot.frontends.gui.gui_menu import GuiActions
from groot.frontends.gui.gui_view_utils import EChanges, LegoSelection
from intermake import ArgsKwargs, intermake_gui
from intermake.engine.plugin import Plugin
from intermake.hosts.frontends.gui_qt.frm_arguments import FrmArguments
from mhelper import MFlags, SwitchError
from mhelper_qt import menu_helper





class FrmBase( QDialog ):
    def __init__( self, parent ):
        from groot.frontends.gui.forms.frm_main import FrmMain
        super().__init__( parent )
        self.parent: FrmMain = parent
        self.setStyleSheet( intermake_gui.default_style_sheet() )
        self.actions : GuiActions = GuiActions( self.parent, self )
    
    
    def on_plugin_completed( self, change: EChanges ):
        self.on_refresh_data()
        self.on_fusions_changed()  # TODO
    
    
    def on_selection_changed( self ):
        self.on_refresh_data()
    
    
    def on_refresh_data( self ):
        pass
    
    
    def on_fusions_changed( self ):
        pass
    
    
    def set_selected( self, item, selected ):
        selection: LegoSelection = self.get_selection()
        existing = item in selection
        
        if selected == existing:
            return
        
        if selected:
            if selection.is_empty() or selection.selection_type() != type( item ):
                self.set_selection( LegoSelection( frozenset( { item } ) ) )
            else:
                self.set_selection( LegoSelection( selection.items.union( { item } ) ) )
        else:
            self.set_selection( LegoSelection( selection.items - { item } ) )
    
    
    
    
    
    def get_selection( self ) -> LegoSelection:
        return global_view.current_selection()
    
    
    
    
    
    def get_model( self ):
        return global_view.current_model()
    
    
    def closeEvent( self, event: QCloseEvent ):
        self.parent.remove_form( self )
    
    
    def show_menu( self, *args ):
        return menu_helper.show( self.sender(), *args )
    
    
    def show_form( self, form_class ):
        self.parent.show_form( form_class )
    
    
    def close_form( self, form ):
        self.parent.close_form( form )
    
    
    
