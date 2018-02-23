from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QMessageBox

from groot.data import global_view
from groot.frontends.gui.gui_menu import GuiActions
from groot.frontends.gui.gui_view_utils import EChanges, LegoSelection
from intermake import intermake_gui
from mhelper_qt import menu_helper, exceptToGui


class FrmBase( QDialog ):
    @exceptToGui()
    def __init__( self, parent ):
        from groot.frontends.gui.forms.frm_main import FrmMain
        assert isinstance( parent, FrmMain )
        self.frm_main: FrmMain = parent
        super().__init__( parent )
        self.setStyleSheet( intermake_gui.default_style_sheet() )
        self.actions: GuiActions = GuiActions( self.frm_main, self )
    
    
    def on_plugin_completed( self, change: EChanges ):
        self.on_refresh_data()
        self.on_fusions_changed()  # TODO
    
    
    def on_selection_changed( self ):
        self.on_refresh_data()
    
    
    def on_refresh_data( self ):
        pass
    
    
    def on_fusions_changed( self ):
        pass
    
    
    def alert( self, message: str ):
        msg = QMessageBox()
        msg.setText( message )
        msg.setWindowTitle( self.windowTitle() )
        msg.setIcon( QMessageBox.Warning )
        msg.exec_()
    
    
    def set_selected( self, item, selected ):
        selection: LegoSelection = self.get_selection()
        existing = item in selection
        
        if selected == existing:
            return
        
        if selected:
            if selection.is_empty() or selection.selection_type() != type( item ):
                self.actions.set_selection( LegoSelection( frozenset( { item } ) ) )
            else:
                self.actions.set_selection( LegoSelection( selection.items.union( { item } ) ) )
        else:
            self.actions.set_selection( LegoSelection( selection.items - { item } ) )
    
    
    def get_selection( self ) -> LegoSelection:
        return global_view.current_selection()
    
    
    def get_model( self ):
        return global_view.current_model()
    
    
    def closeEvent( self, event: QCloseEvent ):
        self.frm_main.remove_form( self )
    
    
    def show_menu( self, *args ):
        return menu_helper.show( self.sender(), *args )
    
    
    def show_form( self, form_class ):
        self.frm_main.show_form( form_class )
