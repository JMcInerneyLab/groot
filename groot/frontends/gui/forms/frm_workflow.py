from PyQt5.QtWidgets import QLineEdit, QMenu, QToolButton, QWidget
from groot.frontends.gui.forms.designer import frm_workflow_designer

from groot import constants
from groot.algorithms.walkthrough import Walkthrough
from groot.constants import LegoStage
from groot.data import global_view
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui import gui_workflow
from mhelper_qt import exceptToGui, exqtSlot, menu_helper


class FrmWorkflow( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_workflow_designer.Ui_Dialog( self )
        self.setWindowTitle( "Workflow" )
        self.bind_to_label( self.ui.LBL_NEXT )
        self.bind_to_label( self.ui.LBL_CLOSE )
        self._refresh_labels()
        self.gray_indicator = False
    
    
    def on_plugin_completed( self ):
        self._refresh_labels()
    
    
    def _refresh_label( self, stage: LegoStage, indicator: QWidget, label: QLineEdit ):
        suffix = " margin-top: 2px; margin-bottom: 2px;"
        
        status = global_view.current_model().get_status( stage )
        
        if status.is_complete:
            indicator.setStyleSheet( "background:green;" + suffix )
        elif status.is_partial:
            indicator.setStyleSheet( "background:orange;" + suffix )
        elif not self.gray_indicator:
            indicator.setStyleSheet( "background:red;" + suffix )
            self.gray_indicator = True
        else:
            indicator.setStyleSheet( "background:silver;" + suffix )
        
        label.setText( str( status ) )
    
    
    def _refresh_labels( self ):
        wt = Walkthrough.get_active()
        
        if wt is not None and wt.is_paused:
            self.ui.FRA_PAUSED.setVisible( True )
            self.ui.LBL_NEXT.setText( wt.get_stage_name() )
        else:
            self.ui.FRA_PAUSED.setVisible( False )
        
        self.gray_indicator = False
        
        self._refresh_label( constants.STAGES.FILE_0,
                             self.ui.LBL_WARNI_FILENAME,
                             self.ui.TXT_FILENAME )
        
        self.gray_indicator = False
        
        self._refresh_label( constants.STAGES.FASTA_2,
                             self.ui.LBL_WARNI_SEQUENCES,
                             self.ui.TXT_SEQUENCES )
        
        self._refresh_label( constants.STAGES.BLAST_1,
                             self.ui.LBL_WARNI_EDGES,
                             self.ui.TXT_EDGES )
        
        self._refresh_label( constants.STAGES.COMPONENTS_3,
                             self.ui.LBL_WARNI_COMPONENTS,
                             self.ui.TXT_COMPONENTS )
        
        self._refresh_label( constants.STAGES.ALIGNMENTS_5,
                             self.ui.LBL_WARNI_ALIGNMENTS,
                             self.ui.TXT_ALIGNMENTS )
        
        self._refresh_label( constants.STAGES.TREES_6,
                             self.ui.LBL_WARNI_TREES,
                             self.ui.TXT_TREES )
        
        self._refresh_label( constants.STAGES.FUSIONS_7,
                             self.ui.LBL_WARNI_FUSIONS,
                             self.ui.TXT_FUSIONS )
        
        self._refresh_label( constants.STAGES.SPLITS_8,
                             self.ui.LBL_WARNI_SPLITS,
                             self.ui.TXT_SPLITS )
        
        self._refresh_label( constants.STAGES.CONSENSUS_9,
                             self.ui.LBL_WARNI_CONSENSUS,
                             self.ui.TXT_CONSENSUS )
        
        self._refresh_label( constants.STAGES.SUBSETS_10,
                             self.ui.LBL_WARNI_SUBSETS,
                             self.ui.TXT_SUBSETS )
        
        self._refresh_label( constants.STAGES.SUBGRAPHS_11,
                             self.ui.LBL_WARNI_SUBGRAPHS,
                             self.ui.TXT_SUBGRAPHS )
        
        self._refresh_label( constants.STAGES.FUSED_12,
                             self.ui.LBL_WARNI_STITCHED,
                             self.ui.TXT_STITCHED )
        
        self._refresh_label( constants.STAGES.CLEANED_13,
                             self.ui.LBL_WARNI_CLEANED,
                             self.ui.TXT_CLEANED )
        
        self._refresh_label( constants.STAGES.CHECKED_14,
                             self.ui.LBL_WARNI_CHECKED,
                             self.ui.TXT_CHECKED )
        
        self.gray_indicator = True
        
        self._refresh_label( constants.STAGES.DOMAINS_4,
                             self.ui.LBL_WARNI_DOMAINS,
                             self.ui.TXT_DOMAINS )
    
    
    def __show_menu( self, menu: QMenu ):
        control: QToolButton = self.sender()
        ot = control.text()
        control.setText( menu.title() )
        control.parent().updateGeometry()
        menu_helper.show_menu( self, menu )
        control.setText( ot )
    
    
    @exqtSlot()
    def on_BTN_FILENAME_clicked( self ) -> None:
        """
        Signal handler:
        """
        menu_helper.show_menu( self.window, self.actions.frm_main.menu_handler.mnu_file )
    
    
    @exqtSlot()
    def on_BTN_SEQUENCES_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.FASTA_2 )
    
    
    @exqtSlot()
    def on_BTN_SUBSETS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.SUBSETS_10 )
    
    
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
    def on_BTN_EDGES_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.BLAST_1 )
    
    
    @exqtSlot()
    def on_BTN_SUBGRAPHS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.SUBGRAPHS_11 )
    
    
    @exqtSlot()
    def on_BTN_CONTINUE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.launch( gui_workflow.VISUALISERS.ACT_WIZARD_NEXT )
    
    
    @exqtSlot()
    def on_BTN_COMPONENTS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.COMPONENTS_3 )
    
    
    @exqtSlot()
    def on_BTN_CLEANED_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.CLEANED_13 )
    
    
    @exqtSlot()
    def on_BTN_STITCHED_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.FUSED_12 )
    
    
    @exqtSlot()
    def on_BTN_CHECKED_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.CHECKED_14 )
    
    
    @exqtSlot()
    def on_BTN_DOMAINS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.menu( gui_workflow.STAGES.DOMAINS_4 )
    
    
    @exqtSlot()
    def on_BTN_ALIGNMENTS_clicked( self ) -> None:
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
