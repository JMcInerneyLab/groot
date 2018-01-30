from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtWidgets import QMainWindow, QStatusBar
from typing import Type

from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.forms.frm_samples import FrmSamples
from groot.frontends.gui.forms.frm_workflow import FrmWorkflow
from groot.frontends.gui.gui_view import ILegoViewModelObserver
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import intermake_gui, IGuiPluginHostWindow, AsyncResult
from groot.frontends.gui.forms.designer import frm_main_designer

from mhelper_qt import exceptToGui


class FrmMain( QMainWindow, ILegoViewModelObserver, IGuiPluginHostWindow ):
    """
    Main window
    """
    
    
    @exceptToGui()
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        # QT stuff
        QCoreApplication.setAttribute( Qt.AA_DontUseNativeMenuBar )
        QMainWindow.__init__( self )
        self.ui = frm_main_designer.Ui_MainWindow()
        self.ui.setupUi( self )
        self.setWindowTitle( "Lego Model Creator" )
        self.setStyleSheet( intermake_gui.default_style_sheet() )
        
        self._mdi = { }
        
        self.show_form( FrmWorkflow )
    
    
    def plugin_completed( self, result: AsyncResult ) -> None:
        self.statusBar().showMessage( str( result ) )
        
        if result.is_success and isinstance(result.result, EChanges):
            for form in self._mdi.values():
                form.on_plugin_completed(result.result)
    
    
    def remove_form( self, form ):
        del self._mdi[type( form )]
    
    
    def show_form( self, form_class: Type[FrmBase] ):
        if form_class in self._mdi:
            form: FrmBase = self._mdi[form_class]
            form.setFocus()
            return
        
        form = form_class( self )
        self.ui.MDI_AREA.addSubWindow( form )
        form.show()
        self._mdi[form_class] = form
