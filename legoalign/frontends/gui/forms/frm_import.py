from typing import List

from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem
from os import path

from Designer.FrmImport_designer import Ui_Dialog
from mhelper import FileHelper, QtGuiHelper


class LegoQueuedFile:
    BLAST = "Blast"
    COMPOSITES = "Composites"
    FASTA = "Fasta"
    
    
    def __init__( self, filename, filetype ):
        self.filename = filename
        self.filetype = filetype

class FrmImport( QDialog ):
    def __init__(self, parent):
        QDialog.__init__( self,parent )
        self.ui = Ui_Dialog( )
        self.ui.setupUi( self )
        self.setWindowTitle( "Lego Model Creator / Import" )
        self.result = [] #type:  List[LegoQueuedFile]
        
        self.ui.TVW_FILES.setColumnCount(2)
        self.ui.TVW_FILES.headerItem().setText(0, "Name")
        self.ui.TVW_FILES.headerItem().setText(0, "Type")
        
    @staticmethod
    def request(parent):
        form = FrmImport(parent)
        
        if form.exec():
            return form.result
    
    @pyqtSlot()
    def on_BTN_FILENAME_clicked(self) -> None:
        """
        Signal handler:
        """
        if QtGuiHelper.browse_open_on_textbox(self.ui.TXT_FILENAME):
            ext = FileHelper.get_extension( self.ui.TXT_FILENAME.text()).lower()
            
            if ext in (".fasta", ".fa"):
                self.ui.RAD_FASTA.setChecked(True)
            elif ext in(".blast", ".tsv"):
                self.ui.RAD_BLAST.setChecked(True)
            elif ext in (".composities", ".comp"):
                self.ui.RAD_COMPOSITES.setChecked(True)
        
    @pyqtSlot()
    def on_BTNBOX_MAIN_accepted(self) -> None:
        """
        Signal handler:
        """
        self.accept()
        
    @pyqtSlot()
    def on_BTNBOX_MAIN_rejected(self) -> None:
        """
        Signal handler:
        """
        self.reject()
        
    def refresh_view(self):
        self.ui.TVW_FILES.clear()
        
        for x in self.result:
            item = QTreeWidgetItem()
            item.setText(0, x.filename)
            item.setText(1, x.filetype)
            self.ui.TVW_FILES.addTopLevelItem(item)
            
        
    @pyqtSlot()
    def on_BTN_LOAD_clicked(self) -> None:
        """
        Signal handler:
        """
        file_name = self.ui.TXT_FILENAME.text()
        
        if path.isfile(file_name):
            if self.ui.RAD_BLAST.isChecked():
                self.result.append(LegoQueuedFile(file_name, LegoQueuedFile.BLAST)     )
            elif self.ui.RAD_COMPOSITES.isChecked():
                self.result.append(LegoQueuedFile(file_name, LegoQueuedFile.COMPOSITES))
            elif self.ui.RAD_FASTA.isChecked():
                self.result.append(LegoQueuedFile(file_name, LegoQueuedFile.FASTA)      )
                
            self.refresh_view()
    
    @pyqtSlot()
    def on_BTN_CLEAR_clicked(self) -> None:
        """
        Signal handler:
        """
        self.result=[]
        self.refresh_view()
    