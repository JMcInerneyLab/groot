from PyQt5.QtWidgets import QPushButton, QGridLayout, QCommandLinkButton
from groot.frontends.gui.forms.designer import frm_samples_designer
from typing import List

from groot.frontends.gui.forms.frm_base import FrmBase

from groot.frontends.gui.gui_view_utils import EChanges
from mhelper import file_helper
from mhelper_qt import exceptToGui, exqtSlot, qt_gui_helper
from groot.data import global_view, user_options
from groot import extensions, constants
from groot.frontends.gui.forms.resources import resources


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
        
        for recent_file in reversed( user_options.options().recent_files ):
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
    
    
    def _select_sample_data( self, _: bool ):
        sender: QPushButton = self.sender()
        
        extensions.ext_files.file_sample( sender.text() )
    
    
    def _select_recent_file( self, _: bool ):
        sender: QPushButton = self.sender()
        
        extensions.ext_files.file_load( sender.statusTip() )
    
    
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
    
    
    @exqtSlot( str )
    def on_LBL_HAS_DATA_WARNING_linkActivated( self, _: str ):
        from groot.frontends.gui.forms.frm_workflow import FrmWorkflow
        self.show_form( FrmWorkflow )
    
    
    @exqtSlot()
    def on_BTN_BROWSE_clicked( self ) -> None:
        """
        Signal handler:
        """
        file_name = qt_gui_helper.browse_open( self, constants.DIALOGUE_FILTER )
        
        if file_name:
            extensions.ext_files.file_load( file_name )
