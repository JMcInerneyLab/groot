from PyQt5.QtWidgets import QWidget, QMessageBox, QCheckBox, QGroupBox, QTreeWidgetItem
from groot_gui.forms.designer.frm_view_options_designer import Ui_Dialog

from groot.constants import EFormat, BROWSE_MODE
from groot.data import global_view
from groot.data.global_view import EStartupMode, GlobalOptions, EWindowMode
from groot_gui.forms.frm_base import FrmBase
from intermake import common_commands
from intermake_qt.forms.frm_arguments import FrmArguments
from mhelper_qt import exqtSlot





class FrmViewOptions( FrmBase ):
    """
    Groot's application-wide settings can be configured from this screen.
    
    The CLI/Python interactive equivalent of this screen is the `local` command.
    The Python script equivalent is the `groot.global_view.options()` object.
    """
    
    def __init__( self, parent: QWidget ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = Ui_Dialog( self )
        self.setWindowTitle( "Preferences" )
        
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
                  self.ui.CHK_OPENGL,
                  self.ui.CHK_SHARE_CONTEXTS,
                  self.ui.CHKTOOL_FILE,
                  self.ui.CHKTOOL_VIS,
                  self.ui.CHKTOOL_WORKFLOW)
        
        for ctrl in radios:
            ctrl.toggled[bool].connect( self.__on_radio_changed )
        
        self.map( False )
        
        for index in range( self.ui.stackedWidget.count() ):
            page: QWidget = self.ui.stackedWidget.widget( index )  # by index because `.children` isn't sorted 
            title = page.property( "page_title" )
            
            i = QTreeWidgetItem()
            i.setText( 0, title )
            self.ui.LST_PAGES.addTopLevelItem( i )
        
        self.ui.LST_PAGES.itemSelectionChanged.connect( self.__on_itemSelectionChanged )
    
    
    def __on_itemSelectionChanged( self ):
        self.ui.stackedWidget.setCurrentIndex( self.ui.LST_PAGES.currentIndex().row() )
    
    
    def __on_radio_changed( self, _: object ):
        self.map( True )
    
    
    def map( self, write ):
        from groot_gui import LegoGuiHost
        
        if self.ignore_map:
            return
        
        self.ignore_map = True
        
        # Global options
        global_options: GlobalOptions = global_view.options()
        host_options = LegoGuiHost.get_settings()
        
        if not isinstance( host_options.enable_browser, int ):
            host_options.enable_browser = BROWSE_MODE.ASK if host_options.enable_browser else BROWSE_MODE.SYSTEM
        
        self.__map_check( write, global_options, "tool_file", self.ui.CHKTOOL_FILE, self.actions.frm_main.ui.FRA_FILE )
        
        self.__map_check( write, global_options, "tool_visualisers", self.ui.CHKTOOL_VIS, self.actions.frm_main.ui.FRA_VISUALISERS )
        
        self.__map_check( write, global_options, "tool_workflow", self.ui.CHKTOOL_WORKFLOW, self.actions.frm_main.ui.FRA_WORKFLOW )
        
        self.__map_check( write, global_options, "opengl", self.ui.CHK_OPENGL )
        
        self.__map_check( write, global_options, "share_opengl", self.ui.CHK_SHARE_CONTEXTS )
        
        self.__map( write, host_options, "enable_browser", { BROWSE_MODE.ASK    : self.ui.RAD_TREE_ASK,
                                                             BROWSE_MODE.INBUILT: self.ui.RAD_TREE_INBUILT,
                                                             BROWSE_MODE.SYSTEM : self.ui.RAD_TREE_SYSTEM } )
        
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
        
        self.__map( write, global_options, "lego_move_enabled", { True : self.ui.RAD_MOVE_YES,
                                                                  None : self.ui.RAD_MOVE_IND,
                                                                  False: self.ui.RAD_MOVE_NO } )
        
        self.__map( write, global_options, "lego_view_names", { True : self.ui.RAD_NAME_YES,
                                                                None : self.ui.RAD_NAME_IND,
                                                                False: self.ui.RAD_NAME_NO } )
        
        self.__map( write, global_options, "lego_view_piano_roll", { True : self.ui.RAD_PIANO_YES,
                                                                     None : self.ui.RAD_PIANO_IND,
                                                                     False: self.ui.RAD_PIANO_NO } )
        
        self.__map( write, global_options, "lego_view_positions", { True : self.ui.RAD_POS_YES,
                                                                    None : self.ui.RAD_POS_IND,
                                                                    False: self.ui.RAD_POS_NO } )
        
        self.__map( write, global_options, "lego_x_snap", { True : self.ui.RAD_XSNAP_YES,
                                                            None : self.ui.RAD_XSNAP_IND,
                                                            False: self.ui.RAD_XSNAP_NO } )
        
        self.__map( write, global_options, "lego_y_snap", { True : self.ui.RAD_YSNAP_YES,
                                                            None : self.ui.RAD_YSNAP_IND,
                                                            False: self.ui.RAD_YSNAP_NO } )
        
        self.__map( write, global_options, "lego_view_components", { True : self.ui.RAD_COMPONENTS_YES,
                                                                     None : self.ui.RAD_COMPONENTS_IND,
                                                                     False: self.ui.RAD_COMPONENTS_NO } )
        
        self.ignore_map = False
    
    
    def __map_check( self, write, target, field, checkbox: QCheckBox, tool_box: QGroupBox = None ):
        if write:
            setattr( target, field, checkbox.isChecked() )
            
            if tool_box:
                tool_box.setVisible( checkbox.isChecked() )
        
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
        FrmArguments.request( self, common_commands.cmd_local_data )
