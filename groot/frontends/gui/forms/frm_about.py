from PyQt5 import QtCore
from groot.frontends.gui.forms.designer import frm_about_designer

from groot.frontends.gui.forms.frm_base import FrmBase
from mhelper_qt import exceptToGui


class FrmAbout( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_about_designer.Ui_Dialog( self )
        self.setWindowTitle( "About" )
        
        import groot
        import intermake
        
        txt = self.ui.LBL_MAIN.text()
        txt = txt.replace( "$(GROOT)", groot.__version__ )
        txt = txt.replace( "$(INTERMAKE)", intermake.__version__ )
        txt = txt.replace( "$(PYQT)", QtCore.PYQT_VERSION_STR )
        txt = txt.replace( "$(QT)", QtCore.QT_VERSION_STR )
        self.ui.LBL_MAIN.setText( txt )
