from groot.frontends.gui.forms.designer import frm_wizard_active_designer

from groot.extensions import ext_gimmicks
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.data import global_view
from groot.frontends.gui.gui_view_utils import EChanges
from groot.algorithms.walkthrough import Walkthrough
from mhelper_qt import exceptToGui, exqtSlot


class FrmWizardActive( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_wizard_active_designer.Ui_Dialog( self )
        self.setWindowTitle( "Wizard Progress" )
        
        self.actions.bind_to_label( self.ui.LBL_CLOSE )
        self.actions.bind_to_label( self.ui.LBL_COMPONENTS )
        self.actions.bind_to_label( self.ui.LBL_DATA )
        self.actions.bind_to_label( self.ui.LBL_FILENAME )
        self.actions.bind_to_label( self.ui.LBL_FUSIONS )
        self.actions.bind_to_label( self.ui.LBL_NEXT )
        self.actions.bind_to_label( self.ui.LBL_NRFG )
        self.actions.bind_to_label( self.ui.LBL_P_COMP )
        self.actions.bind_to_label( self.ui.LBL_P_DATA )
        self.actions.bind_to_label( self.ui.LBL_P_FUS )
        self.actions.bind_to_label( self.ui.LBL_P_NRFG )
        self.actions.bind_to_label( self.ui.LBL_P_SEQ )
        self.actions.bind_to_label( self.ui.LBL_P_TREE )
        self.actions.bind_to_label( self.ui.LBL_PAUSED )
        self.actions.bind_to_label( self.ui.LBL_SEQUENCES )
        self.actions.bind_to_label( self.ui.LBL_TREES )
        self.actions.bind_to_label( self.ui.LBL_WARN_INACTIVE )
        
        self.LBL_NEXT_TEXT = self.ui.LBL_NEXT.text()
        self.LBL_P_COMP_TEXT = self.ui.LBL_P_COMP.text()
        self.LBL_P_DATA_TEXT = self.ui.LBL_P_DATA.text()
        self.LBL_P_SEQ_TEXT = self.ui.LBL_P_SEQ.text()
        self.LBL_P_TREE_TEXT = self.ui.LBL_P_TREE.text()
        
        self.__update_labels()
    
    
    def on_plugin_completed( self, change: EChanges ):
        super().on_plugin_completed( change )
        self.__update_labels()
    
    
    def __update_labels( self ):
        status = global_view.current_status()
        wizard = Walkthrough.get_active()
        is_wizard = bool( wizard )
        
        self.ui.LBL_COMPONENTS.setVisible( is_wizard and status.is_comps )
        self.ui.LBL_P_COMP.setVisible( is_wizard and not status.is_comps )
        self.ui.LBL_SEQUENCES.setVisible( is_wizard and status.is_align )
        self.ui.LBL_P_SEQ.setVisible( is_wizard and not status.is_align )
        self.ui.LBL_TREES.setVisible( is_wizard and status.is_trees )
        self.ui.LBL_P_TREE.setVisible( is_wizard and not status.is_trees )
        self.ui.LBL_DATA.setVisible( is_wizard and status.is_any_data )
        self.ui.LBL_P_DATA.setVisible( is_wizard and not status.is_any_data )
        self.ui.LBL_NRFG.setVisible( is_wizard and status.is_nrfg )
        self.ui.LBL_P_NRFG.setVisible( is_wizard and not status.is_nrfg )
        self.ui.LBL_FUSIONS.setVisible( is_wizard and status.is_fusions )
        self.ui.LBL_P_FUS.setVisible( is_wizard and not status.is_fusions )
        self.ui.TXT_FILENAME.setVisible( is_wizard and status.is_file )
        self.ui.BTN_COPY_FILE.setVisible( is_wizard and status.is_file )
        self.ui.BTN_FILENAME.setVisible( is_wizard and status.is_file )
        self.ui.LBL_FILENAME.setVisible( is_wizard and status.is_file )
        
        self.ui.LBL_WARN_INACTIVE.setVisible( not is_wizard )
        self.ui.FRA_PAUSED.setVisible( is_wizard and wizard.is_paused )
        
        if is_wizard:
            self.ui.LBL_NEXT.setText( self.LBL_NEXT_TEXT.format( wizard.pause_reason ) )
            self.ui.LBL_P_COMP.setText( self.LBL_P_COMP_TEXT.format( wizard.tolerance ) )
            self.ui.LBL_P_DATA.setText( self.LBL_P_DATA_TEXT.format( len( wizard.imports ) ) )
            self.ui.LBL_P_SEQ.setText( self.LBL_P_SEQ_TEXT.format( wizard.alignment or "default" ) )
            self.ui.LBL_P_TREE.setText( self.LBL_P_TREE_TEXT.format( wizard.tree or "default" ) )
            self.ui.TXT_FILENAME.setText( status.file_name )
    
    
    def __check_current( self ):
        if global_view.current_model().file_name != self.ui.TXT_FILENAME.text():
            # This should never have happened, but just in case
            self.alert( "This model is no longer the active model. Click the refresh button to update the display." )
            return False
        
        return True
    
    
    @exqtSlot()
    def on_BTN_FILENAME_clicked( self ) -> None:
        """
        Signal handler: Show workflow
        """
        if not self.__check_current():
            return
        
        self.actions.show_workflow()
    
    
    @exqtSlot()
    def on_BTN_COPY_FILE_clicked( self ) -> None:
        """
        Signal handler:  Save file as
        """
        if not self.__check_current():
            return
        
        self.actions.save_model_as()
    
    
    @exqtSlot()
    def on_BTN_CONTINUE_clicked( self ) -> None:
        """
        Signal handler: Continue wizard
        """
        ext_gimmicks.continue_walkthrough()
    
    
    @exqtSlot()
    def on_BTN_REFRESH_clicked( self ) -> None:
        """
        Signal handler: Refresh form
        """
        self.__update_labels()
