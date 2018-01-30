from PyQt5.QtWidgets import QPushButton, QGridLayout
from groot.frontends.gui.forms.designer import frm_samples_designer
from typing import List

from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import EChanges
from mhelper import file_helper
from mhelper_qt import exceptToGui, exqtSlot, qt_gui_helper
from groot.data import global_view, user_options
from groot import extensions, constants


class FrmSamples( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_samples_designer.Ui_Dialog( self )
        self.setWindowTitle( "Samples" )
        self._buttons: List[QPushButton] = []
        
        layout: QGridLayout = QGridLayout()
        self.ui.FRA_SAMPLES.setLayout( layout )
        x, y = 0, 0
        
        for sample_dir in global_view.get_samples():
            button = QPushButton()
            button.setText( file_helper.get_filename( sample_dir ) )
            button.setStatusTip( sample_dir )
            button.clicked[bool].connect( self._select_sample_data )
            self._buttons.append( button )
            layout.addWidget( button, x, y )
            x += 1
            if x > 3:
                x = 0
                y += 1
        
        layout: QGridLayout = QGridLayout()
        self.ui.FRA_RECENT.setLayout( layout )
        x, y = 0, 0
        
        for recent_file in user_options.options().recent_files:
            button = QPushButton()
            button.setText( file_helper.get_filename_without_extension( recent_file ) )
            button.setStatusTip( recent_file )
            button.clicked[bool].connect( self._select_recent_file )
            self._buttons.append( button )
            layout.addWidget( button, x, y )
            x += 1
            if x > 3:
                x = 0
                y += 1
        
        print( "END" )
    
    
    def _select_sample_data( self, _: bool ):
        sender: QPushButton = self.sender()
        
        extensions.ext_files.file_sample( sender.text() )
    
    
    def _select_recent_file( self, _: bool ):
        sender: QPushButton = self.sender()
        
        extensions.ext_files.file_load( sender.statusTip() )
    
    
    def on_plugin_completed( self, change: EChanges ):
        status = global_view.current_status()
        
        for button in self._buttons:
            button.setEnabled( status.empty )
        
        self.ui.BTN_BROWSE.setEnabled( status.empty )
    
    
    @exqtSlot()
    def on_BTN_BROWSE_clicked( self ) -> None:
        """
        Signal handler:
        """
        file_name = qt_gui_helper.browse_open( self, constants.DIALOGUE_FILTER )
        
        if file_name:
            extensions.ext_files.file_load( file_name )
