from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QDialogButtonBox
from typing import Optional


from mhelper import file_helper, get_basic_documentation
from mhelper_qt import exceptToGui, exqtSlot, FrmGenericText
from groot_gui.forms.designer import frm_sample_browser_designer
from groot.data import global_view


class FrmSampleBrowser( QDialog ):
    """
    This screen allows the user to browse and load the sample datasets that ship with Groot.
    
    Information on the samples is also provided here.
    
    The CLI/Python equivalent of this screen is the `file_sample` command.
    """
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_sample_browser_designer.Ui_Dialog( self )
        self.setWindowTitle( "Sample browser" )
        self.update_files()
        self.ui.TVW_SAMPLES.itemSelectionChanged.connect( self.__on_item_selection_changed )
        self.ui.CMB_FILES.currentIndexChanged[int].connect( self.__on_current_index_changed )
        self.ui.BTNBOX_MAIN.button(QDialogButtonBox.Help).clicked[bool].connect(self.on_help_clicked)
        self.sample = None
        
    def on_help_clicked( self, _:bool ):
        FrmGenericText.request( self, text = get_basic_documentation( self ) )
    
    
    def __on_current_index_changed( self, _: int ):
        data = self.ui.CMB_FILES.currentData( Qt.UserRole )
        
        if data:
            try:
                text = file_helper.read_all_text( data )
                
                self.ui.TXT_DATA.setText( text )
            except Exception as ex:
                self.ui.TXT_DATA.setText( str( ex ) )
        else:
            self.ui.TXT_DATA.setText( "(no selection)" )
    
    
    def __on_item_selection_changed( self ):
        items = self.ui.TVW_SAMPLES.selectedItems()
        
        if len( items ) != 1:
            self.sample = None
        else:
            item: QTreeWidgetItem = items[0]
            self.sample = item.data( 0, Qt.UserRole )
        
        self.ui.LBL_SAMPLE.setText( file_helper.get_filename( self.sample ) if self.sample else "(no selection)" )
        self.ui.CMB_FILES.clear()
        
        if self.sample:
            files = file_helper.list_dir( self.sample )
            num_relevant = sum( x.endswith( ".fasta" ) or x.endswith( ".blast" ) for x in files )
            
            self.ui.CMB_FILES.addItem( "({} files, {} relevant)".format( len( files ), num_relevant ), None )
            
            for file in files:
                self.ui.CMB_FILES.addItem( file_helper.get_filename( file ), file )
    
    
    def update_files( self ):
        for sample_dir in global_view.get_samples():
            item = QTreeWidgetItem()
            item.setText( 0, file_helper.get_filename( sample_dir ) )
            item.setData( 0, Qt.UserRole, sample_dir )
            self.ui.TVW_SAMPLES.addTopLevelItem( item )
    
    
    @staticmethod
    def request( parent ) -> Optional[str]:
        frm = FrmSampleBrowser( parent )
        
        if frm.exec_():
            return frm.sample
        else:
            return None
    
    
    @exqtSlot()
    def on_BTNBOX_MAIN_accepted( self ) -> None:
        """
        Signal handler:
        """
        self.accept()
    
    
    @exqtSlot()
    def on_BTNBOX_MAIN_rejected( self ) -> None:
        """
        Signal handler:
        """
        self.reject()
