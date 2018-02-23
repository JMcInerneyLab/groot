from groot.frontends.gui.forms.designer import frm_workflow_designer

from groot.data import global_view
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import EChanges
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
        
        self._refresh_labels()
        
        self.actions.bind_to_label( self.ui.LBL_WARN_ALIGNMENTS )
        self.actions.bind_to_label( self.ui.LBL_WARN_COMPONENTS )
        self.actions.bind_to_label( self.ui.LBL_WARN_DOMAINS )
        self.actions.bind_to_label( self.ui.LBL_WARN_FILENAME )
        self.actions.bind_to_label( self.ui.LBL_WARN_FUSIONS )
        self.actions.bind_to_label( self.ui.LBL_WARN_GRAPH )
        self.actions.bind_to_label( self.ui.LBL_WARN_NRFG )
        self.actions.bind_to_label( self.ui.LBL_WARN_SEQUENCES )
        self.actions.bind_to_label( self.ui.LBL_WARN_TREES )
    
    
    def on_plugin_completed( self, change: EChanges ):
        self._refresh_labels()
    
    
    def _refresh_labels( self ):
        status = global_view.current_status()
        
        self.ui.TXT_FILENAME.setText( status.file_name if status.is_file else "-" )
        self.ui.TXT_DOMAINS.setText( "{} domains".format( status.num_domains ) if status.is_any_data else "-" )
        self.ui.TXT_COMPONENTS.setText( "{} components".format( status.num_components ) if status.is_comps else "-" )
        self.ui.TXT_ALIGNMENTS.setText( "{}/{} alignments".format( status.num_alignments, status.num_components ) if status.is_align else "-" )
        self.ui.TXT_FUSIONS.setText( "{} fusions".format( status.num_fusions ) if status.is_fusions else "-" )
        self.ui.TXT_NRFG.setText( "1 NRFG" if status.is_nrfg else "-" )
        self.ui.TXT_SEQUENCES.setText( "{} sequences".format( status.num_sequences ) if status.is_any_data else "-" )
        self.ui.TXT_TREES.setText( "{}/{} trees".format( status.num_trees, status.num_components ) if status.is_trees else "-" )
        
        self.ui.LBL_WARN_SEQUENCES.setVisible( not status.is_any_data )
        self.ui.LBL_WARN_TREES.setVisible( status.is_align and not status.is_trees )
        self.ui.LBL_WARN_DOMAINS.setVisible( status.is_comps and not status.domains )
        self.ui.LBL_WARN_ALIGNMENTS.setVisible( status.is_comps and not status.is_align )
        self.ui.LBL_WARN_COMPONENTS.setVisible( status.is_any_data and not status.is_comps )
        self.ui.LBL_WARN_FILENAME.setVisible( not status.is_empty and not status.is_file )
        self.ui.LBL_WARN_FUSIONS.setVisible( status.is_trees and not status.is_fusions )
        self.ui.LBL_WARN_NRFG.setVisible( status.is_fusions and not status.is_nrfg )
        self.ui.LBL_WARN_GRAPH.setVisible( status.is_nrfg )
    
    
    @exqtSlot()
    def on_BTN_FILENAME_clicked( self ) -> None:
        """
        Signal handler:
        """
        menu_helper.show_menu( self, self.frm_main.menu_handler.mnu_file )
    
    
    @exqtSlot()
    def on_BTN_SEQUENCES_clicked( self ) -> None:
        """
        Signal handler:
        """
        menu_helper.show_menu( self, self.frm_main.menu_handler.mnu_data )
    
    
    @exqtSlot()
    def on_BTN_COMPONENTS_clicked( self ) -> None:
        """
        Signal handler:
        """
        menu_helper.show_menu( self, self.frm_main.menu_handler.mnu_components )
    
    
    @exqtSlot()
    def on_BTN_DOMAINS_clicked( self ) -> None:
        """
        Signal handler:
        """
        menu_helper.show_menu( self, self.frm_main.menu_handler.mnu_domains )
    
    
    @exqtSlot()
    def on_BTN_ALIGNMENTS_clicked( self ) -> None:
        """
        Signal handler:
        """
        menu_helper.show_menu( self, self.frm_main.menu_handler.mnu_alignments )
    
    
    @exqtSlot()
    def on_BTN_TREES_clicked( self ) -> None:
        """
        Signal handler:
        """
        menu_helper.show_menu( self, self.frm_main.menu_handler.mnu_trees )
    
    
    @exqtSlot()
    def on_BTN_FUSIONS_clicked( self ) -> None:
        """
        Signal handler:
        """
        menu_helper.show_menu( self, self.frm_main.menu_handler.mnu_fusions )
    
    
    @exqtSlot()
    def on_BTN_NRFG_clicked( self ) -> None:
        """
        Signal handler:
        """
        menu_helper.show_menu( self, self.frm_main.menu_handler.mnu_nrfg )
