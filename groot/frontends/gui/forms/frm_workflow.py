from PyQt5.QtWidgets import QFileDialog
from groot.frontends.gui.forms.designer import frm_workflow_designer

from groot import extensions, constants
from groot.data import global_view
from groot.frontends.gui.forms.frm_alignment import FrmAlignment
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.forms.frm_big_text import FrmBigText
from groot.frontends.gui.forms.frm_fusions import FrmFusions
from groot.frontends.gui.forms.frm_lego import FrmLego
from groot.frontends.gui.forms.frm_samples import FrmSamples
from groot.frontends.gui.forms.frm_webtree import FrmWebtree
from groot.frontends.gui.gui_view_utils import EChanges
from mhelper import SwitchError
from mhelper_qt import exceptToGui, exqtSlot, qt_gui_helper


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
        extensions.ext_files.file_new.run()
    
    
    @exqtSlot()
    def on_BTN_MODEL_LOAD_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmSamples )
    
    
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
            extensions.ext_files.file_save( model.file_name )
        elif choice == OPTION_2:
            file_name = qt_gui_helper.browse_save( self, constants.DIALOGUE_FILTER )
            
            if file_name:
                extensions.ext_files.file_save( file_name )
    
    
    @exqtSlot()
    def on_BTN_DATA_IMPORT_clicked( self ) -> None:
        """
        Signal handler:
        """
        filters = "Valid files (*.fasta *.fa *.faa *.blast *.tsv *.composites *.txt *.comp)", "FASTA files (*.fasta *.fa *.faa)", "BLAST output (*.blast *.tsv)", "Composite finder output (*.composites)"
        
        file_name, filter = QFileDialog.getOpenFileName( self, "Select file", None, ";;".join( filters ), options = QFileDialog.DontUseNativeDialog )
        
        if not file_name:
            return
        
        filter_index = filters.index( filter )
        
        if filter_index == 0:
            extensions.ext_files.import_file( self._model, file_name )
        elif filter_index == 0:
            extensions.ext_files.import_fasta( self._model, file_name )
        elif filter_index == 1:
            extensions.ext_files.import_blast( self._model, file_name )
        elif filter_index == 2:
            extensions.ext_files.import_composites( self._model, file_name )
        else:
            raise SwitchError( "filter_index", filter_index )
    
    
    @exqtSlot()
    def on_BTN_DATA_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmBigText )
    
    
    @exqtSlot()
    def on_BTN_COMPONENTS_CREATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.request( extensions.ext_generating.make_components )
    
    
    @exqtSlot()
    def on_BTN_COMPONENTS_DELETE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.request( extensions.ext_dropping.drop_components )
    
    
    @exqtSlot()
    def on_BTN_COMPONENTS_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmLego )
    
    
    @exqtSlot()
    def on_BTN_ALIGNMENT_CREATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.request( extensions.ext_generating.make_alignments )
    
    
    @exqtSlot()
    def on_BTN_ALIGNMENT_DELETE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.request( extensions.ext_dropping.drop_alignment )
    
    
    @exqtSlot()
    def on_BTN_ALIGNMENT_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmAlignment )
    
    
    @exqtSlot()
    def on_BTN_TREES_CREATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.request( extensions.ext_generating.make_trees )
    
    
    @exqtSlot()
    def on_BTN_TREES_DELETE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.request( extensions.ext_dropping.drop_tree )
    
    
    @exqtSlot()
    def on_BTN_TREES_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmWebtree )
    
    
    @exqtSlot()
    def on_BTN_FUSIONS_CREATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.request( extensions.ext_generating.make_fusions )
    
    
    @exqtSlot()
    def on_BTN_FUSIONS_DELETE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.request( extensions.ext_dropping.drop_fusions )
    
    
    @exqtSlot()
    def on_BTN_FUSIONS_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmFusions )
    
    
    @exqtSlot()
    def on_BTN_NRFG_CREATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.request( extensions.ext_generating.make_nrfg )
    
    
    @exqtSlot()
    def on_BTN_NRFG_DELETE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.request( extensions.ext_dropping.drop_nrfg )
    
    
    @exqtSlot()
    def on_BTN_NRFG_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_form( FrmWebtree )
