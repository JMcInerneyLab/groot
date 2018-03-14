import warnings
from typing import Dict, Type

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QCloseEvent, QColor
from PyQt5.QtWidgets import QMainWindow, QMenu, QToolButton, QMdiArea
from groot.frontends.gui.forms.designer import frm_main_designer

from groot.data import global_view
from groot.data.global_view import EStartupMode
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import EChanges
from groot.frontends.gui import gui_workflow
from intermake import AsyncResult, IGuiPluginHostWindow, intermake_gui
from intermake.engine.environment import MENV
from mhelper import SwitchError
from mhelper_qt import exceptToGui, exqtSlot, menu_helper, qt_gui_helper


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
        
        self.mdi: Dict[str, FrmBase] = { }
        
        self.COLOUR_EMPTY = QColor( intermake_gui.parse_style_sheet().get( 'QMdiArea[style="empty"].background', "#E0E0E0" ) )
        self.COLOUR_NOT_EMPTY = QColor( intermake_gui.parse_style_sheet().get( 'QMdiArea.background', "#E0E0E0" ) )
        
        self.ui.MDI_AREA.setBackground( self.COLOUR_EMPTY )
        
        self.showMaximized()
        
        self.mdi_mode = False
        # self.ui.MDI_AREA.setViewMode( QMdiArea.TabbedView )
        
        global_view.subscribe_to_selection_changed( self.on_selection_changed )
        
        from groot.frontends.gui.gui_menu import GuiMenu
        self.menu_handler = GuiMenu( self )
        self.actions = self.menu_handler.gui_actions
        
        view = global_view.options().startup_mode
        
        if view == EStartupMode.STARTUP:
            self.menu_handler.gui_actions.launch( gui_workflow.VISUALISERS.VIEW_STARTUP )
        elif view == EStartupMode.WORKFLOW:
            self.menu_handler.gui_actions.launch( gui_workflow.VISUALISERS.VIEW_WORKFLOW )
        elif view == EStartupMode.SAMPLES:
            self.menu_handler.gui_actions.launch( gui_workflow.VISUALISERS.VIEW_OPEN_FILE )
        elif view == EStartupMode.NOTHING:
            pass
        else:
            raise SwitchError( "view", view )
        
        self.completed_changes = None
        self.completed_plugin = None
        self.update_title()
    
    
    def update_title( self ):
        self.setWindowTitle( MENV.name + " - " + MENV.root.visualisable_info().name )
    
    
    def closeEvent( self, e: QCloseEvent ):
        global_view.unsubscribe_from_selection_changed( self.on_selection_changed )
    
    
    def on_selection_changed( self ):
        for form in self.iter_forms():
            form.selection_changed()
    
    
    def plugin_completed( self, result: AsyncResult ) -> None:
        self.update_title()
        self.menu_handler.gui_actions.dismiss_startup_screen()
        
        if result.is_error:
            self.statusBar().showMessage( "OPERATION FAILED TO COMPLETE: " + result.title )
            qt_gui_helper.show_exception( self, "The operation did not complete.", result.exception )
        elif result.is_success and isinstance( result.result, EChanges ):
            self.statusBar().showMessage( "GROOT OPERATION COMPLETED: " + result.title )
            self.completed_changes = result.result
            self.completed_plugin = result.plugin
            for form in self.iter_forms():
                print( form )
                form.on_plugin_completed()
            self.completed_changes = None
            self.completed_plugin = None
        else:
            self.statusBar().showMessage( "EXTERNAL OPERATION COMPLETED: " + str( result ) )
    
    
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
    
    
    def show_form( self, form_class, *parameters ):
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
        self.mdi[form_class.__name__] = form
        self.ui.MDI_AREA.setBackground( self.COLOUR_NOT_EMPTY )
        
        if isinstance( form, FrmBase ):
            form.set_parameters( *parameters )
    
    
    @exqtSlot()
    def on_BTN_NEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.launch( gui_workflow.VISUALISERS.ACT_FILE_NEW )
    
    
    @exqtSlot()
    def on_BTN_OPEN_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.launch( gui_workflow.VISUALISERS.VIEW_OPEN_FILE )
    
    
    @exqtSlot()
    def on_BTN_SAVE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.launch( gui_workflow.VISUALISERS.ACT_FILE_SAVE )
    
    
    @exqtSlot()
    def on_BTN_WORKFLOW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.launch( gui_workflow.VISUALISERS.VIEW_WORKFLOW )
    
    
    @exqtSlot()
    def on_BTN_WIZARD_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.launch( gui_workflow.VISUALISERS.VIEW_WIZARD )
    
    
    @exqtSlot()
    def on_BTN_VIEW_TEXT_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.launch( gui_workflow.VISUALISERS.VIEW_TEXT )
    
    
    @exqtSlot()
    def on_BTN_VIEW_LEGO_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.launch( gui_workflow.VISUALISERS.VIEW_LEGO )
    
    
    @exqtSlot()
    def on_BTN_VIEW_ALIGNMENT_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.launch( gui_workflow.VISUALISERS.VIEW_ALIGNMENT )
    
    
    @exqtSlot()
    def on_BTN_VIEW_TREES_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.launch( gui_workflow.VISUALISERS.VIEW_TREE )
    
    
    @exqtSlot()
    def on_BTN_BLAST_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.BLAST_1 )
    
    
    @exqtSlot()
    def on_BTN_FASTA_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.FASTA_2 )
    
    
    @exqtSlot()
    def on_BTN_COMPONENTS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.COMPONENTS_3 )
    
    
    @exqtSlot()
    def on_BTN_DOMAINS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.DOMAINS_4 )
    
    
    @exqtSlot()
    def on_BTN_ALIGNMENT_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.ALIGNMENTS_5 )
    
    
    @exqtSlot()
    def on_BTN_TREES_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.TREES_6 )
    
    
    @exqtSlot()
    def on_BTN_FUSIONS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.FUSIONS_7 )
    
    
    @exqtSlot()
    def on_BTN_SPLITS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.SPLITS_8 )
    
    
    @exqtSlot()
    def on_BTN_CONSENSUS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.CONSENSUS_9 )
    
    
    @exqtSlot()
    def on_BTN_SUBSETS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.SUBSETS_10 )
    
    
    @exqtSlot()
    def on_BTN_SUBGRAPHS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.SUBGRAPHS_11 )
    
    
    @exqtSlot()
    def on_BTN_NRFG_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.FUSED_12 )
    
    
    @exqtSlot()
    def on_BTN_CLEAN_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.CLEANED_13 )
    
    
    @exqtSlot()
    def on_BTN_CHECK_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.CHECKED_14 )
    
    
    @exqtSlot()
    def on_BTN_DATABASE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.launch( gui_workflow.VISUALISERS.VIEW_ENTITIES )
    
    
    @exqtSlot()
    def on_BTN_SETTINGS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.launch( gui_workflow.VISUALISERS.VIEW_PREFERENCES )
    
    
    def __show_menu( self, menu: QMenu ):
        control: QToolButton = self.sender()
        ot = control.text()
        control.setText( menu.title() )
        control.parent().updateGeometry()
        menu_helper.show_menu( self, menu )
        control.setText( ot )
    
    
    def return_to_console( self ):
        return False
