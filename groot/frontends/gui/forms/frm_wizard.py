from PyQt5.QtWidgets import QFileDialog, QTreeWidgetItem
from groot.frontends.gui.forms.designer import frm_wizard_designer

from groot import extensions
from groot.algorithms import tree, alignment
from groot.frontends.gui.forms.frm_base import FrmBase
from mhelper_qt import exceptToGui, exqtSlot, qt_gui_helper


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
    def on_BTN_BROWSE_FILE_clicked( self ) -> None:
        """
        Signal handler:
        """
        qt_gui_helper.browse_save_on_textbox( self.ui.TXT_FILENAME, "Groot models (*.groot)" )
    
    
    @exqtSlot()
    def on_BTN_OK_clicked( self ) -> None:
        """
        Signal handler:
        """
        imports = []
        
        for i in range( self.ui.LST_FILES.topLevelItemCount() ):
            item: QTreeWidgetItem = self.ui.LST_FILES.topLevelItem( i )
            imports.append( item.text( 0 ) )
        
        extensions.ext_gimmicks.walkthrough(
                new = True,
                name = self.ui.TXT_FILENAME.text(),
                imports = imports,
                review = False,
                tolerance = self.ui.SPN_COMPONENT_TOLERANCE.value(),
                alignment = self.ui.CMB_ALIGNMENT_METHOD.currentText(),
                tree = self.ui.CMB_TREE_METHOD.currentText(),
                fusion = True,
                nrfg = True,
                view = False )
