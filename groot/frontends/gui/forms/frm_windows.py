from PyQt5.QtCore import Qt
from PyQt5.QtGui import QCloseEvent
from groot.frontends.gui.forms.designer import frm_windows_designer

from groot.frontends.gui.forms.frm_alignment import FrmAlignment
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.forms.frm_big_text import FrmBigText
from groot.frontends.gui.forms.frm_fusions import FrmFusions
from groot.frontends.gui.forms.frm_lego import FrmLego
from groot.frontends.gui.forms.frm_samples import FrmSamples
from groot.frontends.gui.forms.frm_selection_list import FrmSelectionList
from groot.frontends.gui.forms.frm_view_options import FrmViewOptions
from groot.frontends.gui.forms.frm_webtree import FrmWebtree
from groot.frontends.gui.forms.frm_wizard import FrmWizard
from groot.frontends.gui.forms.frm_workflow import FrmWorkflow
from mhelper_qt import exceptToGui, exqtSlot


class FrmWindows( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_windows_designer.Ui_Dialog( self )
        self.setWindowTitle( "Windows" )
        self.setWindowFlags(self.windowFlags() & ~Qt.WindowCloseButtonHint)

    
    
    def closeEvent( self, event: QCloseEvent ):
        event.ignore()
    
    
    @exqtSlot()
    def on_BTN_WORKFLOW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmWorkflow )
    
    
    @exqtSlot()
    def on_BTN_WIZARD_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmWizard )
    
    
    @exqtSlot()
    def on_BTN_ENTITIES_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmSelectionList )
    
    
    @exqtSlot()
    def on_BTN_TEXT_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmBigText )
    
    
    @exqtSlot()
    def on_BTN_ALIGNMENTS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmAlignment )
    
    
    @exqtSlot()
    def on_BTN_FUSIONS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmFusions )
    
    
    @exqtSlot()
    def on_BTN_LEGO_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmLego )
    
    
    @exqtSlot()
    def on_BTN_LOAD_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmSamples )
    
    
    @exqtSlot()
    def on_BTN_LEGOOPTS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmViewOptions )
    
    
    @exqtSlot()
    def on_BTN_TREE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmWebtree )
