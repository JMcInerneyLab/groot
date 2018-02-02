from groot.frontends.gui.forms.designer import frm_workflow_designer

from groot.data import global_view
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import EChanges
from mhelper_qt import exceptToGui, exqtSlot


class FrmWorkflow( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_workflow_designer.Ui_Dialog( self )
        self.setWindowTitle( "Workflow" )
        
        self._refresh_labels()
    
    
    def on_plugin_completed( self, change: EChanges ):
        self._refresh_labels()
    
    
    def _refresh_labels( self ):
        model = global_view.current_model()
        status = global_view.current_status()
        
        self.ui.LBL_TITLE_MODEL.setText( str( model ) )
        self.ui.LBL_INFO_MODEL.setVisible( status.data and not status.file )
        self.ui.BTN_MODEL_LOAD.setEnabled( not status.file and not status.data )
        self.ui.BTN_MODEL_NEW.setEnabled( status.file )
        self.ui.BTN_MODEL_SAVE.setEnabled( status.data )
        
        self.ui.LBL_TITLE_DATA.setText( "{} sequences".format( status.num_sequences ) )
        self.ui.LBL_INFO_DATA.setVisible( status.file and (not status.blast or not status.fasta) )
        self.ui.BTN_DATA_IMPORT.setEnabled( not status.comps )
        self.ui.BTN_DATA_VIEW.setEnabled( status.blast or status.fasta )
        
        self.ui.LBL_TITLE_COMPONENTS.setText( "{} components".format( status.num_components ) )
        self.ui.LBL_INFO_COMPONENTS.setVisible( status.blast and not status.comps )
        self.ui.BTN_COMPONENTS_CREATE.setEnabled( status.blast and not status.comps )
        self.ui.BTN_COMPONENTS_DELETE.setEnabled( status.comps and not status.trees )
        self.ui.BTN_COMPONENTS_VIEW.setEnabled( status.comps )
        
        self.ui.LBL_TITLE_ALIGNMENT.setText( "{} alignments".format( status.num_alignments ) )
        self.ui.LBL_INFO_ALIGN.setVisible( status.comps and not status.align )
        self.ui.BTN_ALIGNMENT_CREATE.setEnabled( status.comps and not status.align )
        self.ui.BTN_ALIGNMENT_DELETE.setEnabled( status.align and not status.trees )
        self.ui.BTN_ALIGNMENT_VIEW.setEnabled( status.align )
        
        self.ui.LBL_TITLE_TREES.setText( "{} trees".format( status.num_trees ) )
        self.ui.LBL_INFO_TREES.setVisible( status.align and not status.trees )
        self.ui.BTN_TREES_CREATE.setEnabled( status.align and not status.trees )
        self.ui.BTN_TREES_DELETE.setEnabled( status.trees and not status.fusions )
        self.ui.BTN_TREES_VIEW.setEnabled( status.trees )
        
        self.ui.LBL_TITLE_FUSIONS.setText( "{} fusions".format( status.num_fusions ) )
        self.ui.LBL_INFO_FUSIONS.setVisible( status.trees and not status.fusions )
        self.ui.BTN_FUSIONS_CREATE.setEnabled( status.trees and not status.fusions )
        self.ui.BTN_FUSIONS_DELETE.setEnabled( status.fusions and not status.nrfg )
        self.ui.BTN_FUSIONS_VIEW.setEnabled( status.fusions )
        
        self.ui.LBL_TITLE_NRFG.setText( "{} graphs".format( "1" if status.nrfg else "0" ) )
        self.ui.LBL_INFO_NRFG.setVisible( status.fusions and not status.nrfg )
        self.ui.BTN_NRFG_CREATE.setEnabled( status.fusions and not status.nrfg )
        self.ui.BTN_NRFG_DELETE.setEnabled( status.nrfg )
        self.ui.BTN_NRFG_VIEW.setEnabled( status.nrfg )
    
    
    @exqtSlot()
    def on_BTN_MODEL_NEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.new_model()
    
    
    @exqtSlot()
    def on_BTN_MODEL_LOAD_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_samples_form()
    
    
    @exqtSlot()
    def on_BTN_MODEL_SAVE_clicked( self ) -> None:
        """
        Signal handler:
        """
        model = self.get_model()
        OPTION_1 = "Save"
        OPTION_2 = "Save as..."
        
        if not model.file_name:
            choice = OPTION_2
        else:
            choice = self.show_menu( OPTION_1, OPTION_2 )
        
        if choice == OPTION_1:
            self.actions.save_model()
        elif choice == OPTION_2:
            self.actions.save_model_as()
    
    
    @exqtSlot()
    def on_BTN_DATA_IMPORT_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.import_file()
    
    
    @exqtSlot()
    def on_BTN_DATA_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_text_form()
    
    
    @exqtSlot()
    def on_BTN_COMPONENTS_CREATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.create_components()
    
    
    @exqtSlot()
    def on_BTN_COMPONENTS_DELETE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.drop_components()
    
    
    @exqtSlot()
    def on_BTN_COMPONENTS_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_lego_form()
    
    
    @exqtSlot()
    def on_BTN_ALIGNMENT_CREATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.create_alignments()
    
    
    @exqtSlot()
    def on_BTN_ALIGNMENT_DELETE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.drop_alignments()
    
    
    @exqtSlot()
    def on_BTN_ALIGNMENT_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_alignments_form()
    
    
    @exqtSlot()
    def on_BTN_TREES_CREATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.create_trees()
    
    
    @exqtSlot()
    def on_BTN_TREES_DELETE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.drop_trees()
    
    
    @exqtSlot()
    def on_BTN_TREES_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_tree_form()
    
    
    @exqtSlot()
    def on_BTN_FUSIONS_CREATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.create_fusions()
    
    
    @exqtSlot()
    def on_BTN_FUSIONS_DELETE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.drop_fusions()
    
    
    @exqtSlot()
    def on_BTN_FUSIONS_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_fusion_form()
    
    
    @exqtSlot()
    def on_BTN_NRFG_CREATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.create_nrfg()
    
    
    @exqtSlot()
    def on_BTN_NRFG_DELETE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.drop_nrfg()
    
    
    @exqtSlot()
    def on_BTN_NRFG_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_tree_form()
