from typing import List, Optional

from PyQt5.QtWidgets import QCommandLinkButton, QGridLayout, QPushButton, QLabel, QWidget
from groot_gui.forms.designer import frm_samples_designer
from groot_gui.forms.resources import resources

import groot.data.global_view
import groot
from groot import constants
from groot.data import global_view
from groot.data.global_view import RecentFile
from groot_gui.forms.frm_base import FrmBase
from mhelper import file_helper
from mhelper_qt import exceptToGui, exqtSlot


_MAX_DISPLAYED_FILES = 20


class FrmSamples( FrmBase ):
    """
    This screen allows the user to load or save Groot models (depending on the mode).
    
    Additionally, the sample data that ships with Groot may also be loaded from here.
    
    The CLI/Python equivalents of this screen are the `file_load`, `file_save` and `file_sample` commands.
    """
    
    @exceptToGui()
    def __init__( self,
                  parent: QWidget,
                  title: str,
                  file_action: str,
                  sample_action: Optional[str],
                  browse_action: str,
                  data_warn: bool ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_samples_designer.Ui_Dialog( self )
        self.browse_action = browse_action
        self.setWindowTitle( "Load model" )
        self.__controls: List[QWidget] = []
        self.data_warn = data_warn
        self.ui.LBL_TITLE_MAIN.setText( title )
        self.setWindowTitle( title )
        self.file_action = file_action
        self.sample_action = sample_action
        
        # UPDATE
        self.bind_to_label( self.ui.LBL_HAS_DATA_WARNING )
        self.ui.LBL_HAS_DATA_WARNING.setVisible( False )
        self.view_mode = 1
        self.update_files()
        self.update_view()
    
    
    def update_files( self ):
        # Remove existing buttons
        for control in self.__controls:
            control.setParent( None )
            
        self.__controls.clear()
        
        sample_dirs = global_view.get_samples()
        recent_files = reversed( groot.data.global_view.options().recent_files )
        workspace_files = groot.data.global_view.get_workspace_files()
        
        # SAMPLES
        for sample_dir in sample_dirs:
            self.add_button( self.ui.LAY_SAMPLE, sample_dir, self.sample_action, resources.samples_file )
        
        if not sample_dirs:
            lbl = QLabel()
            lbl.setText( "No samples available." )
            self.ui.LAY_SAMPLE.addWidget( lbl )
            self.__controls.append(lbl)
        
        # RECENT
        for file in recent_files:
            assert isinstance( file, RecentFile )
            self.add_button( self.ui.LAY_RECENT, file.file_name, self.file_action, resources.groot_file )
        
        if not recent_files:
            lbl = QLabel()
            lbl.setText( "No recent files." )
            self.ui.LAY_RECENT.addWidget( lbl )
            self.__controls.append(lbl)
        
        # WORKSPACE
        if len( workspace_files ) <= _MAX_DISPLAYED_FILES:
            for file in workspace_files:
                self.add_button( self.ui.LAY_WORKSPACE, file, self.file_action, resources.groot_file )
        
        if not workspace_files:
            lbl = QLabel()
            lbl.setText( "No workspace files." )
            self.ui.LAY_WORKSPACE.addWidget( lbl )
            self.__controls.append(lbl)
        elif len( workspace_files ) > _MAX_DISPLAYED_FILES:
            lbl = QLabel()
            lbl.setText( "Too many ({}) files to list.".format( len( workspace_files ) ) )
            self.ui.LAY_WORKSPACE.addWidget( lbl )
            self.__controls.append(lbl)
            
        self.update_buttons()
    
    
    def add_button( self, layout: QGridLayout, sample_dir, action, icon ):
        act = (action or "") + sample_dir
        
        button = QCommandLinkButton()
        button.setText( file_helper.get_filename_without_extension( sample_dir ) )
        button.setStatusTip( act )
        if not action:
            button.setEnabled( False )
        button.setToolTip( button.statusTip() )
        button.setAutoDefault( False )
        button.clicked[bool].connect( self.__on_button_clicked )
        button.setIcon( icon.icon() )
        self.__controls.append( button )
        i = layout.count()
        x = i % 3
        y = i // 3
        layout.addWidget( button, y, x )
    
    
    def __on_button_clicked( self, _: bool ):
        sender: QPushButton = self.sender()
        self.actions.by_url( sender.toolTip() )
    
    
    def on_command_completed( self ):
        if self.actions.frm_main.completed_plugin in (groot.file_save, groot.file_load, groot.file_new, groot.file_sample, groot.file_recent, groot.file_load_last):
            self.actions.close_window()
            return
        
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
            status = global_view.current_model().get_status( constants.STAGES._DATA_0 )
            
            for button in self.__controls:
                button.setEnabled( status.is_none )
            
            self.ui.BTN_BROWSE.setEnabled( status.is_none )
            self.ui.LBL_HAS_DATA_WARNING.setVisible( status.is_partial )
    
    
    @exqtSlot()
    def on_BTN_BROWSE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.by_url( self.browse_action )
    
    @exqtSlot()
    def on_BTN_HELP_clicked(self) -> None:
        """
        Signal handler:
        """
        self.actions.show_my_help()
            
    @exqtSlot()
    def on_BTN_REFRESH_clicked( self ) -> None:
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
            self.actions.by_url( self.file_action + self.ui.TXT_WORKSPACE.text() )
    
    
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
        super().__init__( parent, "Load model", "file_load:", "file_sample:", "action:file_open", True )


class FrmSaveFile( FrmSamples ):
    def __init__( self, parent ):
        super().__init__( parent, "Save model", "file_save:", None, "action:file_save_as", False )
