from PyQt5.QtCore import pyqtSlot
from PyQt5.QtWidgets import QDialog, QDialogButtonBox, QSizePolicy

from legoalign.Designer.FrmTreeSelector_designer import Ui_Dialog
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from legoalign import LegoFunctions
from legoalign.LegoModels import LegoModel


class FrmTreeSelector( QDialog ):
    def __init__( self, parent, model : LegoModel):
        """
        CONSTRUCTOR
        :param parent:          Parent form 
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        
        self._model = model
        
        rads = (self.ui.RAD_FUSEON_ANY,
            self.ui.RAD_FUSEON_ROOT,
            self.ui.RAD_PLOT_ROOTED,
            self.ui.RAD_PLOT_UNROOTED,
            self.ui.RAD_TYPE_FUSED,
            self.ui.RAD_TYPE_REGULAR)
        
        for rad in rads:
            rad.toggled[bool].connect(self.__on_rad_toggled)
            
        self.__on_rad_toggled(False)
        
        self.figure = pyplot.figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.layout().addWidget( self.canvas )
            
    def __on_rad_toggled(self, _ : bool):
        e = self.ui.RAD_TYPE_FUSED.isChecked() and self.ui.RAD_PLOT_ROOTED.isChecked()
        self.ui.RAD_FUSEON_ANY.setEnabled(e)
        self.ui.RAD_FUSEON_ROOT.setEnabled(e)
        
        
        ok = (self.ui.RAD_FUSEON_ANY.isChecked() or self.ui.RAD_FUSEON_ROOT.isChecked() or self.ui.RAD_TYPE_REGULAR.isChecked() or self.ui.RAD_PLOT_UNROOTED.isChecked()) and \
            (self.ui.RAD_PLOT_ROOTED.isChecked() or self.ui.RAD_PLOT_UNROOTED.isChecked()) and \
            (self.ui.RAD_TYPE_FUSED.isChecked() or self.ui.RAD_TYPE_REGULAR.isChecked())
        
        self.ui.BTNBOX_MAIN.button(QDialogButtonBox.Ok).setEnabled(ok)
        
        
    @staticmethod
    def request(parent, model : LegoModel):
        self = FrmTreeSelector(parent, model)
        
        self.exec_()
            
                  
    @pyqtSlot()
    def on_BTNBOX_MAIN_accepted(self) -> None:
        """
        Signal handler:
        """
        if self.ui.RAD_PLOT_ROOTED.isChecked():
            roots = [x for x in self._model.sequences if x.is_root]
        else:
            roots = []
            
        if self.ui.RAD_FUSEON_ANY.isChecked():
            roots = [x for x in roots if not x.is_composite]
            
        fused = self.ui.RAD_TYPE_FUSED.isChecked()
        
        self.figure.clear()
        
        LegoFunctions.process_trees(self._model, roots, fused)
        
        self.canvas.draw()
            
    @pyqtSlot()
    def on_BTNBOX_MAIN_rejected(self) -> None:
        """
        Signal handler:
        """
        self.reject()
            