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
    def __init__( self, parent, title, file_action, sample_action, browse_action, data_warn, save_action ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_samples_designer.Ui_Dialog( self )
        self.browse_action = browse_action
        self.setWindowTitle( "Load diagram" )
        self._buttons: List[QPushButton] = []
        self.data_warn = data_warn
        self.save_action = save_action
        self.ui.LBL_TITLE_MAIN.setText( title )
        self.setWindowTitle( title )
        self.file_action = file_action
        self.sample_action = sample_action
        
        # UPDATE
        self.actions.bind_to_label( self.ui.LBL_HAS_DATA_WARNING )
        self.ui.LBL_HAS_DATA_WARNING.setVisible( False )
        self.view_mode = 0
        self.update_files()
        self.update_buttons()
        self.update_view()
    
    
    def update_files( self ):
        # Disable existing buttons
        for button in self._buttons:
            button.setEnabled( False )
        
        # SAMPLES
        for sample_dir in global_view.get_samples():
            self.add_button( self.ui.LAY_SAMPLE, sample_dir, self.sample_action, resources.samples_file )
        
        # RECENT
        for file in reversed( groot.data.global_view.options().recent_files ):
            self.add_button( self.ui.LAY_RECENT, file, self.file_action, resources.groot_file )
        
        # WORKSPACE
        wsf = groot.data.global_view.get_workspace_files()
        if len( wsf ) <= 10:
            for file in wsf:
                self.add_button( self.ui.LAY_WORKSPACE, file, self.file_action, resources.groot_file )
    
    
    def add_button( self, layout: QGridLayout, sample_dir, action, icon ):
        act = (action or "") + sample_dir
        
        for button in self._buttons:
            if button.parent().layout() is layout and button.statusTip() == act:
                if action:
                    button.setEnabled( True )
                return
        
        button = QCommandLinkButton()
        button.setText( file_helper.get_filename_without_extension( sample_dir ) )
        button.setStatusTip( act )
        if not action:
            button.setEnabled( False )
        button.setToolTip( button.statusTip() )
        button.setAutoDefault( False )
        button.clicked[bool].connect( self.__on_button_clicked )
        button.setIcon( icon.icon() )
        self._buttons.append( button )
        i = layout.count()
        x = i % 3
        y = i // 3
        layout.addWidget( button, y, x )
    
    
    def __on_button_clicked( self, _: bool ):
        sender: QPushButton = self.sender()
        self.actions.by_url( sender.toolTip() )
    
    
    def on_plugin_completed( self, change: EChanges ):
        self.update_buttons()
    
    
    def update_view( self ):
        self.ui.FRA_RECENT.setVisible( self.view_mode == 1 )
        self.ui.BTN_SHOW_RECENT.setVisible( self.view_mode != 1 )
        self.ui.FRA_WORKSPACE.setVisible( self.view_mode == 0 )
        self.ui.BTN_SHOW_WORKSPACE.setVisible( self.view_mode != 0 )
        self.ui.FRA_SAMPLE.setVisible( self.view_mode == 2 )
        self.ui.BTN_SHOW_SAMPLE.setVisible( self.view_mode != 2 )
        self.ui.TXT_WORKSPACE.setVisible( self.view_mode == 0 and not self.data_warn )
        self.ui.BTN_NEW_WORKSPACE.setVisible( self.view_mode == 0 and not self.data_warn )
    
    
    def update_buttons( self ):
        if self.data_warn:
            status = global_view.current_status()
            
            for button in self._buttons:
                button.setEnabled( status.is_empty )
            
            self.ui.BTN_BROWSE.setEnabled( status.is_empty )
            self.ui.LBL_HAS_DATA_WARNING.setVisible( not status.is_empty )
    
    
    @exqtSlot()
    def on_BTN_BROWSE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.by_url( self.browse_action )
    
    @exqtSlot()
    def on_BTN_REFRESH_clicked(self) -> None:
        """
        Signal handler:
        """
        self.update_files()
            
    @exqtSlot()
    def on_BTN_SHOW_WORKSPACE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.view_mode = 0
        self.update_view()
    
    
    @exqtSlot()
    def on_BTN_NEW_WORKSPACE_clicked( self ) -> None:
        """
        Signal handler:
        """
        if self.ui.TXT_WORKSPACE.text():
            self.actions.by_url( self.save_action + self.ui.TXT_WORKSPACE.text() )
    
    
    @exqtSlot()
    def on_BTN_SHOW_RECENT_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.view_mode = 1
        self.update_view()
    
    
    @exqtSlot()
    def on_BTN_SHOW_SAMPLE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.view_mode = 2
        self.update_view()


class FrmLoadFile( FrmSamples ):
    def __init__( self, parent ):
        super().__init__( parent, "Load model", "load_file:", "load_sample:", "action:browse_open", True, None )


class FrmSaveFile( FrmSamples ):
    def __init__( self, parent ):
        super().__init__( parent, "Save model", "save_file:", None, "action:save_model_as", False, "file_save:" )
