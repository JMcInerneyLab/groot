from PyQt5.QtWidgets import QFileDialog, QTreeWidgetItem

from typing import List, Dict

import groot
from groot_gui.forms.frm_base import FrmBase
from groot_gui.forms.frm_sample_browser import FrmSampleBrowser
from groot_gui.forms.designer import frm_wizard_designer
from groot_gui.utilities import gui_workflow
from groot_gui.utilities.gui_workflow import handlers, EIntent
from intermake.engine.environment import MENV
from mhelper import array_helper, file_helper
from mhelper_qt import exceptToGui, exqtSlot


SETTINGS_KEY = "walkthroughs"


class FrmWizard( FrmBase ):
    """
    The wizard screen allows the user to set up a Groot wizard, that will run through the entire process of
    creating an n-rooted fusion graph automatically.
    
    For finer control, the user is directed to the Workflow screen instead, which allows each stage to
    be configured and advanced manually, with more control. 
    """
    
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_wizard_designer.Ui_Dialog( self )
        self.setWindowTitle( "Wizard" )
        self.is_enabled = True
        
        for key in groot.alignment_algorithms.keys():
            self.ui.CMB_ALIGNMENT_METHOD.addItem( key )
        
        for key in groot.tree_algorithms.keys():
            self.ui.CMB_TREE_METHOD.addItem( key )
        
        for key in groot.supertree_algorithms.keys():
            self.ui.CMB_SUPERTREE_METHOD.addItem( key )
        
        self.bind_to_label( self.ui.LBL_HELP_TITLE )
        self.bind_to_label( self.ui.LBL_WRN_ACTIVE )
        self.bind_to_label( self.ui.LBL_WRN_MODEL )
        self.on_command_completed()
        self.ui.stackedWidget.setCurrentIndex( 0 )
        self.ui.stackedWidget.currentChanged.connect( self.on_current_changed )
        self.on_current_changed( 0 )
    
    
    def on_current_changed( self, _: int ):
        end = self.ui.stackedWidget.count() - 1
        index = self.ui.stackedWidget.currentIndex()
        self.ui.stackedWidget.setVisible( self.is_enabled )
        self.ui.SPC_ERROR.setVisible( not self.is_enabled )
        self.ui.BTN_NEXT.setEnabled( index != end and self.is_enabled )
        self.ui.BTN_OK.setEnabled( index == end and self.is_enabled )
        self.ui.BTN_BACK.setEnabled( index != 0 and self.is_enabled )
    
    
    @exqtSlot()
    def on_BTN_ADD_FILE_clicked( self ) -> None:
        """
        Signal handler:
        """
        filters = "Valid files (*.fasta *.fa *.faa *.blast *.tsv *.composites *.txt *.comp)", "FASTA files (*.fasta *.fa *.faa)", "BLAST output (*.blast *.tsv)", "Composite finder output (*.composites)"
        
        file_name, filter = QFileDialog.getOpenFileName( self, "Select file", None, ";;".join( filters ), options = QFileDialog.DontUseNativeDialog )
        
        if not file_name:
            return
        
        item = QTreeWidgetItem()
        item.setText( 0, file_name )
        self.ui.LST_FILES.addTopLevelItem( item )
    
    
    @exqtSlot()
    def on_BTN_REMOVE_FILE_clicked( self ) -> None:
        """
        Signal handler:
        """
        
        indexes = self.ui.LST_FILES.selectedIndexes()
        
        for index in sorted( indexes, key = lambda x: -x.row() ):
            self.ui.LST_FILES.takeTopLevelItem( index.row() )
    
    
    @exqtSlot()
    def on_BTN_OK_clicked( self ) -> None:
        """
        Signal handler:
        """
        
        walkthrough = self.write_walkthrough()
        
        walkthrough.make_active()
        
        handlers().VIEW_WORKFLOW.execute( self, EIntent.DIRECT, None )
        self.close()
    
    
    @exqtSlot()
    def on_BTN_HELP_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_my_help()
    
    
    @exqtSlot()
    def on_BTN_CANCEL_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.close_window()
    
    
    @exqtSlot()
    def on_BTN_BACK_clicked( self ) -> None:
        """
        Signal handler:
        """
        if self.ui.stackedWidget.currentIndex() == 0:
            return
        
        self.ui.stackedWidget.setCurrentIndex( self.ui.stackedWidget.currentIndex() - 1 )
    
    
    @exqtSlot()
    def on_BTN_NEXT_clicked( self ) -> None:
        """
        Signal handler:
        """
        if self.ui.stackedWidget.currentIndex() == self.ui.stackedWidget.count() - 1:
            return
        
        self.ui.stackedWidget.setCurrentIndex( self.ui.stackedWidget.currentIndex() + 1 )
    
    
    def on_command_completed( self ):
        w = groot.Wizard.get_active()
        m = groot.current_model()
        
        if w is not None and not w.is_completed:
            self.read_walkthrough( w )
            self.ui.LBL_WRN_ACTIVE.setVisible( True )
            self.ui.LBL_WRN_MODEL.setVisible( False )
            self.is_enabled = False
        elif not m.get_status( groot.constants.STAGES._DATA_0 ).is_none:
            self.ui.LBL_WRN_ACTIVE.setVisible( False )
            self.ui.LBL_WRN_MODEL.setVisible( True )
            self.is_enabled = False
        else:
            self.ui.LBL_WRN_ACTIVE.setVisible( False )
            self.ui.LBL_WRN_MODEL.setVisible( False )
            self.is_enabled = True
        
        if not self.is_enabled:
            self.ui.stackedWidget.setCurrentIndex( 0 )
        
        self.on_current_changed( 0 )
    
    
    def write_walkthrough( self ):
        """
        Creates a wizard.
        """
        imports = []
        
        for i in range( self.ui.LST_FILES.topLevelItemCount() ):
            item: QTreeWidgetItem = self.ui.LST_FILES.topLevelItem( i )
            imports.append( item.text( 0 ) )
        
        walkthrough = groot.Wizard(
                new = True,
                name = self.ui.TXT_FILENAME.text(),
                imports = imports,
                tolerance = self.ui.SPN_COMPONENT_TOLERANCE.value(),
                alignment = self.ui.CMB_ALIGNMENT_METHOD.currentText(),
                tree = self.ui.CMB_TREE_METHOD.currentText(),
                pause_align = self.ui.CHK_PAUSE_ALIGNMENTS.isChecked(),
                pause_tree = self.ui.CHK_PAUSE_TREES.isChecked(),
                pause_fusion = self.ui.CHK_PAUSE_FUSIONS.isChecked(),
                pause_splits = self.ui.CHK_PAUSE_SPLITS.isChecked(),
                pause_consensus = self.ui.CHK_PAUSE_CONSENSUS.isChecked(),
                pause_subset = self.ui.CHK_PAUSE_SUBSETS.isChecked(),
                pause_pregraphs = self.ui.CHK_PAUSE_PREGRAPHS.isChecked(),
                pause_minigraph = self.ui.CHK_PAUSE_MINIGRAPHS.isChecked(),
                pause_sew = self.ui.CHK_PAUSE_RAW_NRFG.isChecked(),
                pause_clean = self.ui.CHK_PAUSE_CLEANED_NRFG.isChecked(),
                pause_check = self.ui.CHK_PAUSE_CHECKED_NRFG.isChecked(),
                pause_components = self.ui.CHK_PAUSE_COMPONENTS.isChecked(),
                pause_import = self.ui.CHK_PAUSE_DATA.isChecked(),
                save = self.ui.CHK_SAVE.isChecked(),
                view = False,
                supertree = self.ui.CMB_SUPERTREE_METHOD.currentText(),
                outgroups = [x.strip() for x in self.ui.TXT_OUTGROUPS.text().split( "," )] )  # TODO
        
        return walkthrough
    
    
    def read_walkthrough( self, w: groot.Wizard ):
        """
        Loads a previous wizard.
        """
        self.ui.TXT_FILENAME.setText( w.name )
        self.ui.SPN_COMPONENT_TOLERANCE.setValue( w.tolerance )
        self.ui.CMB_ALIGNMENT_METHOD.setCurrentText( w.alignment )
        self.ui.CMB_TREE_METHOD.setCurrentText( w.alignment )
        self.ui.CHK_PAUSE_ALIGNMENTS.setChecked( w.pause_align )
        self.ui.CHK_PAUSE_TREES.setChecked( w.pause_tree )
        self.ui.CHK_PAUSE_FUSIONS.setChecked( w.pause_fusion )
        self.ui.CHK_PAUSE_COMPONENTS.setChecked( w.pause_components )
        self.ui.CHK_PAUSE_DATA.setChecked( w.pause_import )
        self.ui.CHK_PAUSE_SPLITS.setChecked( w.pause_splits )
        self.ui.CHK_PAUSE_CONSENSUS.setChecked( w.pause_consensus )
        self.ui.CHK_PAUSE_SUBSETS.setChecked( w.pause_subsets )
        self.ui.CHK_PAUSE_MINIGRAPHS.setChecked( w.pause_minigraph )
        self.ui.CHK_PAUSE_RAW_NRFG.setChecked( w.pause_sew )
        self.ui.CHK_PAUSE_CLEANED_NRFG.setChecked( w.pause_clean )
        self.ui.CHK_PAUSE_CHECKED_NRFG.setChecked( w.pause_check )
        self.ui.CHK_SAVE.setChecked( w.save )
        
        self.ui.TXT_OUTGROUPS.setText( ", ".join( w.outgroups ) )
        
        self.ui.LST_FILES.clear()
        
        for file_name in w.imports:
            item = QTreeWidgetItem()
            item.setText( 0, file_name )
            self.ui.LST_FILES.addTopLevelItem( item )
    
    
    @exqtSlot()
    def on_BTN_RECENT_clicked( self ) -> None:
        """
        Signal handler: Load wizard
        """
        walkthroughs_: List[groot.Wizard] = MENV.local_data.store.retrieve( SETTINGS_KEY, [] )
        
        if not walkthroughs_:
            self.alert( "You don't have any saved walkthroughs." )
            return
        
        walkthroughs: Dict[str, groot.Wizard] = dict( (x.name, x) for x in walkthroughs_ )
        
        selected = self.show_menu( *sorted( walkthroughs.keys() ) )
        
        if selected:
            self.read_walkthrough( walkthroughs[selected] )
    
    
    @exqtSlot()
    def on_BTN_SAVE_clicked( self ) -> None:
        """
        Signal handler: Save wizard
        """
        walkthrough: groot.Wizard = self.write_walkthrough()
        
        if not walkthrough.name:
            self.alert( "You must name your wizard before saving it." )
            return
        
        walkthroughs: List[groot.Wizard] = MENV.local_data.store.retrieve( SETTINGS_KEY, [] )
        
        array_helper.remove_where( walkthroughs, lambda x: x.name == walkthrough.name )
        walkthroughs.append( walkthrough )
        
        MENV.local_data.store.commit( SETTINGS_KEY )
    
    
    @exqtSlot()
    def on_BTN_SAMPLES_clicked( self ) -> None:
        """
        Signal handler:
        """
        sample = FrmSampleBrowser.request( self )
        
        if sample:
            self.ui.LST_FILES.clear()
            
            for file in file_helper.list_dir( sample ):
                if file.endswith( ".blast" ) or file.endswith( ".fasta" ):
                    item = QTreeWidgetItem()
                    item.setText( 0, file )
                    self.ui.LST_FILES.addTopLevelItem( item )
