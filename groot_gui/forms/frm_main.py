import warnings
from typing import Dict, Type

import mhelper as mh
import mhelper_qt as qt
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtWidgets import QMainWindow, QMdiArea, QMenu, QToolButton
from groot import constants
from groot.constants import EChanges
from groot.data import global_view
from groot.data.global_view import EStartupMode, EWindowMode, GlobalOptions
from groot_gui.forms.designer import frm_main_designer
from groot_gui.forms.frm_base import FrmBase
from groot_gui.utilities.gui_workflow import Intent, handlers, EIntent
from intermake import AsyncResult
from intermake.engine.environment import MCMD, MENV
from intermake_qt import IGuiHostMainWindow, intermake_gui, resources


class FrmMain( QMainWindow, IGuiHostMainWindow ):
    """
    This is Groot's main window; one window to control them all.
    
    Sub-windows can be shown in MDI, TDI or basic overlapping mode, depending on the user's preferences.
    
    There are three toolbars at the top:
        * File controls
        * Window controls
        * Workflow controls
        
    The file and window controls have multicolour icons, the workflow controls have black, red or green icons, depending on their status.
        * Green = complete
        * Black = incomplete, not ready
        * Red = incomplete, ready
        
    Additional and advanced functionality can be accessed from the menu bar and status bar.
    """
    INSTANCE = None
    
    
    @qt.exceptToGui()
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
        
        self.mdi: Dict[str, FrmBase] = { }
        
        self.COLOUR_EMPTY = QColor( intermake_gui.parse_style_sheet().get( 'QMdiArea[style="empty"].background', "#E0E0E0" ) )
        self.COLOUR_NOT_EMPTY = QColor( intermake_gui.parse_style_sheet().get( 'QMdiArea.background', "#E0E0E0" ) )
        
        self.ui.MDI_AREA.setBackground( self.COLOUR_EMPTY )
        
        self.showMaximized()
        
        global_options: GlobalOptions = global_view.options()
        self.mdi_mode = global_options.window_mode != EWindowMode.BASIC
        self.ui.FRA_FILE.setVisible( global_options.tool_file )
        self.ui.FRA_VISUALISERS.setVisible( global_options.tool_visualisers )
        self.ui.FRA_WORKFLOW.setVisible( global_options.tool_workflow )
        
        if global_options.window_mode == EWindowMode.TDI:
            self.ui.MDI_AREA.setViewMode( QMdiArea.TabbedView )
            self.ui.MDI_AREA.setDocumentMode( True )
        
        from groot_gui.utilities.gui_menu import GuiMenu
        self.menu_handler = GuiMenu( self )
        self.actions = self.menu_handler.gui_actions
        
        view = global_view.options().startup_mode
        
        if global_view.current_model().get_status( constants.STAGES._DATA_0 ).is_none:
            if view == EStartupMode.STARTUP:
                handlers().VIEW_STARTUP.execute( self, EIntent.DIRECT, None )
            elif view == EStartupMode.WORKFLOW:
                handlers().VIEW_WORKFLOW.execute( self, EIntent.DIRECT, None )
            elif view == EStartupMode.SAMPLES:
                handlers().VIEW_OPEN_FILE.execute( self, EIntent.DIRECT, None )
            elif view == EStartupMode.NOTHING:
                pass
            else:
                raise mh.SwitchError( "view", view )
        
        self.completed_changes = None
        self.completed_plugin = None
        self.update_title()
        self.menu_handler.update_buttons()
    
    
    def update_title( self ):
        self.setWindowTitle( MENV.name + " - " + str( MENV.root ) )
        self.ui.LBL_FILENAME.setText( str( MENV.root ) )
    
    
    def command_completed( self, result: AsyncResult ) -> None:
        self.update_title()
        self.menu_handler.gui_actions.dismiss_startup_screen()
        self.menu_handler.update_buttons()
        
        if result.is_error:
            self.ui.LBL_STATUS.setText( "OPERATION FAILED TO COMPLETE: " + result.title )
            self.ui.BTN_STATUS.setIcon( resources.failure.icon() )
        elif result.is_success and isinstance( result.result, EChanges ):
            self.ui.LBL_STATUS.setText( "GROOT OPERATION COMPLETED: " + result.title )
            self.ui.BTN_STATUS.setIcon( resources.success.icon() )
            self.completed_changes = result.result
            self.completed_plugin = result.command
            for form in self.iter_forms():
                form.on_command_completed()
            self.completed_changes = None
            self.completed_plugin = None
        else:
            self.ui.LBL_STATUS.setText( "EXTERNAL OPERATION COMPLETED: " + str( result ) )
            self.ui.BTN_STATUS.setIcon( resources.success.icon() )
    
    
    def iter_forms( self ):
        return [x for x in self.mdi.values() if isinstance( x, FrmBase )]
    
    
    def remove_form( self, form ):
        try:
            del self.mdi[type( form ).__name__]
        except KeyError as ex:
            warnings.warn( str( ex ), UserWarning )
            pass
        
        if not self.mdi:
            self.ui.MDI_AREA.setBackground( self.COLOUR_EMPTY )
    
    
    def adjust_window_size( self, form ):
        form = self.mdi.get( type( form ).__name__ )
        
        if form:
            if self.mdi_mode:
                form.parent().adjustSize()
    
    
    def close_form( self, form_type: Type[FrmBase] ):
        form = self.mdi.get( form_type.__name__ )
        
        if form is None:
            return
        
        if self.mdi_mode:
            form.parentWidget().close()
        else:
            form.close()
    
    
    def show_form( self, form_class: Type[qt.QWidget], intent: Intent ):
        self.menu_handler.gui_actions.dismiss_startup_screen()
        
        if form_class.__name__ in self.mdi:
            form = self.mdi[form_class.__name__]
            form.setFocus()
            return
        
        form: FrmBase = form_class( self )
        
        if self.mdi_mode:
            self.ui.MDI_AREA.addSubWindow( form )
            # mdi.setSizePolicy( form.sizePolicy() )
        else:
            form.setWindowFlag( Qt.Tool, True )
        
        form.show()
        
        if isinstance( form, FrmBase ):
            form.on_apply_request( intent )
        
        self.mdi[form_class.__name__] = form
        self.ui.MDI_AREA.setBackground( self.COLOUR_NOT_EMPTY )
    
    
    @qt.exqtSlot()
    def on_BTN_STATUS_clicked( self ) -> None:
        """
        Signal handler:
        """
        from intermake_qt import FrmTreeView
        
        FrmTreeView.request( parent = self,
                             root = MCMD.host.result_history,
                             message = "Results",
                             flat = True )
    
    
    def __show_menu( self, menu: QMenu ):
        control: QToolButton = self.sender()
        ot = control.text()
        control.setText( menu.title() )
        control.parent().updateGeometry()
        qt.menu_helper.show_menu( self, menu )
        control.setText( ot )
    
    
    def return_to_console( self ):
        return True
