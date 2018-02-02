from typing import List

from PyQt5.QtWidgets import QCommandLinkButton, QGridLayout, QPushButton
from groot.frontends.gui.forms.designer import frm_samples_designer
from groot.frontends.gui.forms.resources import resources

import groot.data.global_view
from groot.data import global_view
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import EChanges
from mhelper import file_helper
from mhelper_qt import exceptToGui, exqtSlot


class FrmSamples( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_samples_designer.Ui_Dialog( self )
        self.setWindowTitle( "Load diagram" )
        self._buttons: List[QPushButton] = []
        
        layout: QGridLayout = QGridLayout()
        self.ui.FRA_SAMPLES.setLayout( layout )
        x, y = 0, 0
        
        for sample_dir in global_view.get_samples():
            button = QCommandLinkButton()
            button.setText( file_helper.get_filename( sample_dir ) )
            button.setStatusTip( sample_dir )
            button.setAutoDefault( False )
            button.clicked[bool].connect( self._select_sample_data )
            button.setIcon( resources.samples_file.icon() )
            self._buttons.append( button )
            layout.addWidget( button, y, x )
            x += 1
            if x > 3:
                x = 0
                y += 1
        
        layout: QGridLayout = QGridLayout()
        self.ui.FRA_RECENT.setLayout( layout )
        x, y = 0, 0
        
        for recent_file in reversed( groot.data.global_view.options().recent_files ):
            button = QCommandLinkButton()
            button.setText( file_helper.get_filename_without_extension( recent_file ) )
            button.setStatusTip( recent_file )
            button.setIcon( resources.groot_file.icon() )
            button.setAutoDefault( False )
            button.clicked[bool].connect( self._select_recent_file )
            self._buttons.append( button )
            layout.addWidget( button, y, x )
            x += 1
            if x > 3:
                x = 0
                y += 1
        
        self.update_buttons()
        self.actions.bind_to_label(self.ui.LBL_HAS_DATA_WARNING)
    
    
    def _select_sample_data( self, _: bool ):
        sender: QPushButton = self.sender()
        self.actions.load_sample(sender.text())
    
    
    def _select_recent_file( self, _: bool ):
        sender: QPushButton = self.sender()
        self.actions.load_file(sender.statusTip())
    
    
    def on_plugin_completed( self, change: EChanges ):
        status = self.update_buttons()
        
        if not status.empty:
            from groot.frontends.gui.forms.frm_workflow import FrmWorkflow
            self.show_form( FrmWorkflow )
            self.close_form( self )
    
    
    def update_buttons( self ):
        status = global_view.current_status()
        for button in self._buttons:
            button.setEnabled( status.empty )
        self.ui.BTN_BROWSE.setEnabled( status.empty )
        self.ui.LBL_HAS_DATA_WARNING.setVisible( not status.empty )
        return status
    
    
    @exqtSlot()
    def on_BTN_BROWSE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.browse_open()
