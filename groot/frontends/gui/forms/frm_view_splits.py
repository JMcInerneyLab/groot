from groot.frontends.gui.forms.designer import frm_view_splits_designer

from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui import gui_workflow
from mhelper_qt import exceptToGui, exqtSlot


class FrmViewSplits( FrmBase ):
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_view_splits_designer.Ui_Dialog( self )
        self.setWindowTitle( "Data" )
        
        self.bind_to_workflow_box( self.ui.GRP_WORKFLOW,
                                   self.ui.BTN_WORKFLOW,
                                   self.ui.BTN_CREATE,
                                   self.ui.BTN_REMOVE,
                                   self.ui.BTN_VIEW,
                                   gui_workflow.VISUALISERS.VIEW_ALIGNMENT,
                                   gui_workflow.STAGES.SPLITS_8 )
        
    @exqtSlot()
    def on_BTN_WORKFLOW_clicked(self) -> None:
        """
        Signal handler:
        """
        pass
    
    @exqtSlot()
    def on_BTN_CREATE_clicked(self) -> None:
        """
        Signal handler:
        """
        pass
    
    @exqtSlot()
    def on_BTN_REMOVE_clicked(self) -> None:
        """
        Signal handler:
        """
        pass
    
    @exqtSlot()
    def on_BTN_VIEW_clicked(self) -> None:
        """
        Signal handler:
        """
        pass
    
    @exqtSlot()
    def on_BTN_CHANGE_SELECTION_clicked(self) -> None:
        """
        Signal handler:
        """
        pass
