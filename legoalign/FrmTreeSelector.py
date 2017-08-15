from PyQt5.QtWidgets import QDialog, QSizePolicy

from mhelper.QtGuiHelper import exqtSlot
from legoalign.Designer.FrmTreeSelector_designer import Ui_Dialog
from matplotlib import pyplot
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg

from legoalign import LegoFunctions
from legoalign.LegoFunctions import EFuse, ERoot
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
        
        self.ui.LST_ROOT.addItems(x.name for x in ERoot)
        self.ui.LST_TYPE.addItems(x.name for x in EFuse)
        
        self.ui.LST_ROOT.setCurrentIndex(0)
        self.ui.LST_TYPE.setCurrentIndex(0)
        
        self.figure = pyplot.figure()
        self.canvas = FigureCanvasQTAgg(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding)
        
        self.layout().addWidget( self.canvas )
            
        
        
    @staticmethod
    def request(parent, model : LegoModel):
        self = FrmTreeSelector(parent, model)
        
        self.exec_()
            
                  
    @exqtSlot()
    def on_BTNBOX_MAIN_accepted(self) -> None:
        """
        Signal handler:
        """
        root_mode = ERoot(self.ui.LST_ROOT.currentIndex())
        fuse_mode = EFuse(self.ui.LST_TYPE.currentIndex())
            
        self.figure.clear()
        
        LegoFunctions.fuse_trees( self._model, root_mode, fuse_mode )
        
        self.canvas.draw()
            
    @exqtSlot()
    def on_BTNBOX_MAIN_rejected(self) -> None:
        """
        Signal handler:
        """
        self.reject()
            