from PyQt5.QtWidgets import QWidget, QMessageBox, QCheckBox, QGroupBox
from groot.frontends.gui.forms.designer.frm_view_options_designer import Ui_Dialog

from groot.constants import EFormat
from groot.data import global_view
from groot.data.global_view import EBrowseMode, EStartupMode, GlobalOptions, EWindowMode
from groot.frontends.gui.forms.frm_base import FrmBase
from intermake import common_commands
from intermake_qt.forms.frm_arguments import FrmArguments
from mhelper_qt import exqtSlot


class FrmViewOptions( FrmBase ):
    def __init__( self, parent: QWidget ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = Ui_Dialog( self )
        self.setWindowTitle( "Options" )
        
        self.ignore_map = False
        
        radios = (self.ui.RAD_COMPONENTS_IND,
                  self.ui.RAD_COMPONENTS_NO,
                  self.ui.RAD_COMPONENTS_YES,
                  self.ui.RAD_MOVE_IND,
                  self.ui.RAD_MOVE_NO,
                  self.ui.RAD_MOVE_YES,
                  self.ui.RAD_NAME_IND,
                  self.ui.RAD_NAME_NO,
                  self.ui.RAD_NAME_YES,
                  self.ui.RAD_PIANO_IND,
                  self.ui.RAD_PIANO_NO,
                  self.ui.RAD_PIANO_YES,
                  self.ui.RAD_POS_IND,
                  self.ui.RAD_POS_NO,
                  self.ui.RAD_POS_YES,
                  self.ui.RAD_XSNAP_IND,
                  self.ui.RAD_XSNAP_NO,
                  self.ui.RAD_XSNAP_YES,
                  self.ui.RAD_YSNAP_IND,
                  self.ui.RAD_YSNAP_NO,
                  self.ui.RAD_YSNAP_YES,
                  self.ui.RAD_STARTUP_MESSAGE,
                  self.ui.RAD_STARTUP_WORKFLOW,
                  self.ui.RAD_STARTUP_NOTHING,
                  self.ui.RAD_STARTUP_SAMPLES,
                  self.ui.RAD_TREE_ASK,
                  self.ui.RAD_TREE_INBUILT,
                  self.ui.RAD_TREE_SYSTEM,
                  self.ui.RAD_WIN_MDI,
                  self.ui.RAD_WIN_NORMAL,
                  self.ui.RAD_WIN_TDI,
                  self.ui.RAD_JS_NONE,
                  self.ui.RAD_JS_VIS,
                  self.ui.RAD_JS_CY,
                  self.ui.CHKTOOL_FILE,
                  self.ui.CHKTOOL_VIS,
                  self.ui.CHKTOOL_WORKFLOW)
        
        for ctrl in radios:
            ctrl.toggled[bool].connect( self.__on_radio_changed )
        
        self.map( False )
    
    
    def __on_radio_changed( self, _: object ):
        self.map( True )
    
    
    def map( self, write ):
        if self.ignore_map:
            return
        
        self.ignore_map = True
        
        # Global options
        global_options: GlobalOptions = global_view.options()
        
        self.__map_check( write, global_options, "tool_file", self.ui.CHKTOOL_FILE, self.actions.frm_main.ui.FRA_FILE )
        self.__map_check( write, global_options, "tool_visualisers", self.ui.CHKTOOL_VIS, self.actions.frm_main.ui.FRA_VISUALISERS )
        self.__map_check( write, global_options, "tool_workflow", self.ui.CHKTOOL_WORKFLOW, self.actions.frm_main.ui.FRA_WORKFLOW )
        
        self.__map( write, global_options, "browse_mode", { EBrowseMode.ASK    : self.ui.RAD_TREE_ASK,
                                                            EBrowseMode.INBUILT: self.ui.RAD_TREE_INBUILT,
                                                            EBrowseMode.SYSTEM : self.ui.RAD_TREE_SYSTEM } )
        
        self.__map( write, global_options, "startup_mode", { EStartupMode.STARTUP : self.ui.RAD_STARTUP_MESSAGE,
                                                             EStartupMode.NOTHING : self.ui.RAD_STARTUP_NOTHING,
                                                             EStartupMode.WORKFLOW: self.ui.RAD_STARTUP_WORKFLOW,
                                                             EStartupMode.SAMPLES : self.ui.RAD_STARTUP_SAMPLES } )
        
        self.__map( write, global_options, "window_mode", { EWindowMode.BASIC: self.ui.RAD_WIN_NORMAL,
                                                            EWindowMode.MDI  : self.ui.RAD_WIN_MDI,
                                                            EWindowMode.TDI  : self.ui.RAD_WIN_TDI } )
        
        self.__map( write, global_options, "gui_tree_view", { EFormat.VISJS: self.ui.RAD_JS_VIS,
                                                              EFormat.CYJS : self.ui.RAD_JS_CY,
                                                              EFormat.SVG  : self.ui.RAD_JS_NONE } )
        
        # Model options
        model_options = self.get_model().ui_options
        
        self.__map( write, model_options, "move_enabled", { True : self.ui.RAD_MOVE_YES,
                                                            None : self.ui.RAD_MOVE_IND,
                                                            False: self.ui.RAD_MOVE_NO } )
        
        self.__map( write, model_options, "view_names", { True : self.ui.RAD_NAME_YES,
                                                          None : self.ui.RAD_NAME_IND,
                                                          False: self.ui.RAD_NAME_NO } )
        
        self.__map( write, model_options, "view_piano_roll", { True : self.ui.RAD_PIANO_YES,
                                                               None : self.ui.RAD_PIANO_IND,
                                                               False: self.ui.RAD_PIANO_NO } )
        
        self.__map( write, model_options, "view_positions", { True : self.ui.RAD_POS_YES,
                                                              None : self.ui.RAD_POS_IND,
                                                              False: self.ui.RAD_POS_NO } )
        
        self.__map( write, model_options, "x_snap", { True : self.ui.RAD_XSNAP_YES,
                                                      None : self.ui.RAD_XSNAP_IND,
                                                      False: self.ui.RAD_XSNAP_NO } )
        
        self.__map( write, model_options, "y_snap", { True : self.ui.RAD_YSNAP_YES,
                                                      None : self.ui.RAD_YSNAP_IND,
                                                      False: self.ui.RAD_YSNAP_NO } )
        
        self.__map( write, model_options, "view_components", { True : self.ui.RAD_COMPONENTS_YES,
                                                               None : self.ui.RAD_COMPONENTS_IND,
                                                               False: self.ui.RAD_COMPONENTS_NO } )
        
        self.ignore_map = False
    
    
    def __map_check( self, write, target, field, checkbox: QCheckBox, tool: QGroupBox ):
        if write:
            setattr( target, field, checkbox.isChecked() )
            
            if tool:
                tool.setVisible( checkbox.isChecked() )
        
        else:
            checkbox.setChecked( getattr( target, field ) )
    
    
    def __map( self, write, object_, field, mapping ):
        if write:
            for k, v in mapping.items():
                if v.isChecked():
                    setattr( object_, field, k )
                    return
        else:
            value = getattr( object_, field )
            
            for k, v in mapping.items():
                v.setChecked( value == k )
    
    
    @exqtSlot()
    def on_BTN_CLEAR_RECENT_clicked( self ) -> None:
        """
        Signal handler:
        """
        global_view.options().recent_files.clear()
        global_view.save_global_options()
        QMessageBox.information( self, self.windowTitle(), "Recent files list cleared." )
    
    
    @exqtSlot()
    def on_BTN_INTERMAKE_clicked( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, common_commands.LOCAL_DATA_PLUGIN )
    
    
    @exqtSlot()
    def on_BTN_INTERMAKE_EXP_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_intermake()
