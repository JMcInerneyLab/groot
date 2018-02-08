from typing import Dict, Type

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QCloseEvent, QColor
from PyQt5.QtWidgets import QMainWindow, QMdiSubWindow
from groot.frontends.gui.forms.designer import frm_main_designer

from groot.data import global_view
from groot.data.global_view import EStartupMode
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import AsyncResult, IGuiPluginHostWindow, intermake_gui
from mhelper import SwitchError
from mhelper_qt import exceptToGui, qt_gui_helper


class FrmMain( QMainWindow, IGuiPluginHostWindow ):
    """
    Main window
    """
    INSTANCE = None
    
    
    @exceptToGui()
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        # QT stuff
        FrmMain.INSTANCE = self
        QCoreApplication.setAttribute( Qt.AA_DontUseNativeMenuBar )
        QMainWindow.__init__( self )
        self.ui = frm_main_designer.Ui_MainWindow()
        self.ui.setupUi( self )
        self.setWindowTitle( "Lego Model Creator" )
        self.setStyleSheet( intermake_gui.default_style_sheet() )
        
        self.mdi: Dict[Type[FrmBase], FrmBase] = { }
        
        self.COLOUR_EMPTY = QColor( intermake_gui.parse_style_sheet().get( 'QMdiArea[style="empty"].background', "#000000" ) )
        self.COLOUR_NOT_EMPTY = QColor( intermake_gui.parse_style_sheet().get( 'QMdiArea.background', "#000000" ) )
        
        self.ui.MDI_AREA.setBackground( self.COLOUR_EMPTY )
        
        self.showMaximized()
        
        self.mdi_mode = False
        
        global_view.subscribe_to_selection_changed( self.on_selection_changed )
        
        from groot.frontends.gui.gui_menu import GuiMenu
        self.menu_handler = GuiMenu( self )
        
        view = global_view.options().startup_mode
        
        if view == EStartupMode.STARTUP:
            self.menu_handler.gui_actions.show_startup()
        elif view == EStartupMode.WORKFLOW:
            self.menu_handler.gui_actions.show_workflow()
        elif view == EStartupMode.SAMPLES:
            self.menu_handler.gui_actions.show_load_model()
        elif view == EStartupMode.NOTHING:
            pass
        else:
            raise SwitchError( "view", view )
    
    
    def closeEvent( self, e: QCloseEvent ):
        global_view.unsubscribe_from_selection_changed( self.on_selection_changed )
    
    
    def on_selection_changed( self ):
        for form in self.iter_forms():
            form.on_selection_changed()
            form.actions.on_selection_changed()
    
    
    def plugin_completed( self, result: AsyncResult ) -> None:
        self.menu_handler.gui_actions.dismiss_startup_screen()
        self.statusBar().showMessage( str( result ) )
        
        if result.is_error:
            qt_gui_helper.show_exception( self, "The operation did not complete.", result.exception )
        elif result.is_success and isinstance( result.result, EChanges ):
            for form in self.iter_forms():
                print( form )
                form.on_plugin_completed( result.result )
    
    
    def iter_forms( self ):
        return [x for x in self.mdi.values() if isinstance( x, FrmBase )]
    
    
    def remove_form( self, form ):
        del self.mdi[type( form )]
        
        if not self.mdi:
            self.ui.MDI_AREA.setBackground( self.COLOUR_EMPTY )
            self.statusBar().showMessage( "YEHR CLERSERD ERL DA WERNDERS. DA SCRERN ERS BLER. ERPERN ER WERNDER FRERM DA MAHN TER MAHK ERT LERS BLER." )
    
    
    def close_form( self, form_type: Type[FrmBase] ):
        form = self.mdi.get( form_type )
        
        if form is None:
            return
        
        if self.mdi_mode:
            form.parentWidget().close()
        else:
            form.close()
    
    
    def show_form( self, form_class ):
        self.menu_handler.gui_actions.dismiss_startup_screen()
        
        if form_class in self.mdi:
            form = self.mdi[form_class]
            form.setFocus()
            return
        
        form: FrmBase = form_class( self )
        
        if self.mdi_mode:
            mdi: QMdiSubWindow = self.ui.MDI_AREA.addSubWindow( form )
            mdi.setSizePolicy( form.sizePolicy() )
        
        form.setWindowFlag( Qt.Tool, True )
        form.show()
        self.mdi[form_class] = form
        self.ui.MDI_AREA.setBackground( self.COLOUR_NOT_EMPTY )
