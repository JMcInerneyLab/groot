from typing import Dict, Type
from mhelper_qt import exceptToGui, exqtSlot, qt_gui_helper
from intermake import AsyncResult, IGuiPluginHostWindow, intermake_gui
from intermake.hosts.frontends.gui_qt.frm_intermake_main import FrmIntermakeMain
from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QColor, QCloseEvent
from PyQt5.QtWidgets import QMainWindow, QMdiSubWindow

from groot.data import global_view
from groot.frontends.gui.forms.designer import frm_main_designer
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import EChanges


class FrmMain( QMainWindow, IGuiPluginHostWindow ):
    """
    Main window
    """
    
    
    @exceptToGui()
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        # QT stuff
        QCoreApplication.setAttribute( Qt.AA_DontUseNativeMenuBar )
        QMainWindow.__init__( self )
        self.ui = frm_main_designer.Ui_MainWindow()
        self.ui.setupUi( self )
        self.setWindowTitle( "Lego Model Creator" )
        self.setStyleSheet( intermake_gui.default_style_sheet() )
        
        self._mdi: Dict[Type[FrmBase], FrmBase] = { }
        
        self.COLOUR_EMPTY = QColor( intermake_gui.parse_style_sheet().get( 'QMdiArea[style="empty"].background', "#C0C0C0" ) )
        self.COLOUR_NOT_EMPTY = QColor( intermake_gui.parse_style_sheet().get( 'QMdiArea.background', "#C0C0C0" ) )
        
        self.ui.MDI_AREA.setBackground( self.COLOUR_EMPTY )
        
        self.showMaximized()
        
        self.mdi_mode = False
        
        global_view.subscribe_to_selection_changed( self.on_selection_changed )
    
    
    def closeEvent( self, e : QCloseEvent ):
        global_view.unsubscribe_from_selection_changed( self.on_selection_changed )
    
    
    def on_selection_changed( self ):
        for form in self.iter_forms():
            form.on_selection_changed()
    
    
    def plugin_completed( self, result: AsyncResult ) -> None:
        self.statusBar().showMessage( str( result ) )
        
        if result.is_error:
            qt_gui_helper.show_exception( self, "The operation did not complete.", result.exception )
        elif result.is_success and isinstance( result.result, EChanges ):
            for form in self.iter_forms():
                print( form )
                form.on_plugin_completed( result.result )
    
    
    def iter_forms( self ):
        return [x for x in self._mdi.values() if isinstance( x, FrmBase )]
    
    
    def remove_form( self, form ):
        del self._mdi[type( form )]
        
        if not self._mdi:
            self.ui.MDI_AREA.setBackground( self.COLOUR_EMPTY )
    
    
    def close_form( self, form: FrmBase ):
        if self.mdi_mode:
            form.parentWidget().close()
        else:
            form.close()
    
    
    def show_form( self, form_class ):
        if form_class in self._mdi:
            form = self._mdi[form_class]
            form.setFocus()
            return
        
        form: FrmBase = form_class( self )
        
        if self.mdi_mode:
            mdi: QMdiSubWindow = self.ui.MDI_AREA.addSubWindow( form )
            mdi.setSizePolicy( form.sizePolicy() )
        
        form.setWindowFlag( Qt.Tool, True )
        form.show()
        self._mdi[form_class] = form
        self.ui.MDI_AREA.setBackground( self.COLOUR_NOT_EMPTY )
    
    
    @exqtSlot()
    def on_ACT_WORKFLOW_triggered( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_workflow import FrmWorkflow
        self.show_form( FrmWorkflow )
    
    
    @exqtSlot()
    def on_ACT_WIZARD_triggered( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_wizard import FrmWizard
        self.show_form( FrmWizard )
    
    
    @exqtSlot()
    def on_ACT_LEGO_triggered( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_lego import FrmLego
        self.show_form( FrmLego )
    
    
    @exqtSlot()
    def on_ACT_TREE_triggered( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_webtree import FrmWebtree
        self.show_form( FrmWebtree )
    
    
    @exqtSlot()
    def on_ACT_TEXT_triggered( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_big_text import FrmBigText
        self.show_form( FrmBigText )
    
    
    @exqtSlot()
    def on_ACT_ENTITIES_triggered( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_selection_list import FrmSelectionList
        self.show_form( FrmSelectionList )
    
    
    @exqtSlot()
    def on_ACT_ALIGNMENTS_triggered( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_alignment import FrmAlignment
        self.show_form( FrmAlignment )
    
    
    @exqtSlot()
    def on_ACT_FUSION_triggered( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_fusions import FrmFusions
        self.show_form( FrmFusions )
    
    
    @exqtSlot()
    def on_ACT_SAMPLES_triggered( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_samples import FrmSamples
        self.show_form( FrmSamples )
    
    
    @exqtSlot()
    def on_ACT_INTERMAKE_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmIntermakeMain )
    
    
    @exqtSlot()
    def on_ACT_DOMAIN_triggered( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_domain import FrmDomain
        self.show_form( FrmDomain )
    
    
    @exqtSlot()
    def on_ACT_DEBUG_triggered( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_debug import FrmDebug
        self.show_form( FrmDebug )
