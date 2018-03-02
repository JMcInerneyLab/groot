from PyQt5.QtWidgets import QFileDialog, QTreeWidgetItem
from groot.frontends.gui.forms.designer import frm_wizard_designer
from typing import List, Dict

from groot.algorithms import alignment, tree, walkthrough
from groot.algorithms.walkthrough import Walkthrough
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.forms.frm_sample_browser import FrmSampleBrowser
from intermake.engine.environment import MENV
from mhelper import array_helper, file_helper
from mhelper_qt import exceptToGui, exqtSlot


SETTINGS_KEY = "walkthroughs"


class FrmWizard( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_wizard_designer.Ui_Dialog( self )
        self.setWindowTitle( "Wizard" )
        
        for key in alignment.algorithms:
            self.ui.CMB_ALIGNMENT_METHOD.addItem( key )
        
        for key in tree.algorithms:
            self.ui.CMB_TREE_METHOD.addItem( key )
        
        self.actions.bind_to_label( self.ui.LBL_HELP_TITLE )
    
    
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
        
        self.actions.show_wizard_progress()
        self.close()
    
    
    def write_walkthrough( self ):
        """
        Creates a walkthrough.
        """
        imports = []
        
        for i in range( self.ui.LST_FILES.topLevelItemCount() ):
            item: QTreeWidgetItem = self.ui.LST_FILES.topLevelItem( i )
            imports.append( item.text( 0 ) )
        
        walkthrough = Walkthrough(
                new = True,
                name = self.ui.TXT_FILENAME.text(),
                imports = imports,
                tolerance = self.ui.SPN_COMPONENT_TOLERANCE.value(),
                alignment = self.ui.CMB_ALIGNMENT_METHOD.currentText(),
                tree = self.ui.CMB_TREE_METHOD.currentText(),
                pause_align = self.ui.CHK_PAUSE_ALIGNMENTS.isChecked(),
                pause_tree = self.ui.CHK_PAUSE_TREES.isChecked(),
                pause_fusion = self.ui.CHK_PAUSE_FUSIONS.isChecked(),
                pause_nrfg = False,
                pause_components = self.ui.CHK_PAUSE_COMPONENTS.isChecked(),
                pause_import = self.ui.CHK_PAUSE_DATA.isChecked(),
                view = False )
        return walkthrough
    
    
    def read_walkthrough( self, w: walkthrough.Walkthrough ):
        """
        Loads a previous walkthrough.
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
        
        self.ui.LST_FILES.clear()
        
        for file_name in w.imports:
            item = QTreeWidgetItem()
            item.setText( 0, file_name )
            self.ui.LST_FILES.addTopLevelItem( item )
    
    
    @exqtSlot()
    def on_BTN_RECENT_clicked( self ) -> None:
        """
        Signal handler: Load walkthrough
        """
        walkthroughs_: List[Walkthrough] = MENV.local_data.store.get( SETTINGS_KEY, [] )
        
        if not walkthroughs_:
            self.alert( "You don't have any saved walkthroughs." )
            return
        
        walkthroughs: Dict[str, Walkthrough] = dict( (x.name, x) for x in walkthroughs_ )
        
        selected = self.show_menu( *sorted( walkthroughs.keys() ) )
        
        if selected:
            self.read_walkthrough( walkthroughs[selected] )
    
    
    @exqtSlot()
    def on_BTN_SAVE_clicked( self ) -> None:
        """
        Signal handler: Save walkthrough
        """
        walkthrough: Walkthrough = self.write_walkthrough()
        
        if not walkthrough.name:
            self.alert( "You must name your walkthrough before saving it." )
            return
        
        walkthroughs: List[Walkthrough] = MENV.local_data.store.get( SETTINGS_KEY, [] )
        
        array_helper.remove_where( walkthroughs, lambda x: x.name == walkthrough.name )
        walkthroughs.append( walkthrough )
        
        MENV.local_data.store[SETTINGS_KEY] = walkthroughs
    
    
    @exqtSlot()
    def on_BTN_SAMPLES_clicked( self ) -> None:
        """
        Signal handler:
        """
        sample = FrmSampleBrowser.request( self )
        
        if sample:
            self.ui.LST_FILES.clear()
            
            for file in file_helper.list_dir( sample ):
                if file.endswith(".blast") or file.endswith(".fasta"):
                    item = QTreeWidgetItem()
                    item.setText( 0, file )
                    self.ui.LST_FILES.addTopLevelItem( item )
