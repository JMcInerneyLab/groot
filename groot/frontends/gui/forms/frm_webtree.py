from os import path
import os

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QGridLayout
from groot.frontends.gui.forms.designer import frm_webtree_designer

import intermake
from groot import constants, LegoModel
from groot.constants import EFormat
from groot.data import global_view
from groot.data.global_view import EBrowseMode
from groot.data.model_interfaces import INamedGraph
from groot.frontends.gui.forms.frm_base import FrmSelectingToolbar
from groot.frontends.gui.gui_view_utils import ESelect, LegoSelection
from groot.utilities import graph_viewing
from intermake.engine.environment import MENV
from mhelper import SwitchError, file_helper
from mhelper_qt import exceptToGui, exqtSlot


class FrmWebtree( FrmSelectingToolbar ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_webtree_designer.Ui_Dialog( self )
        self.setWindowTitle( "Tree Viewer" )
        
        self.ui.WIDGET_MAIN.setVisible( False )
        self.ui.LBL_TITLE.setVisible( False )
        
        self.is_browser = False
        self.__file_name = None
        self.browser = None
        
        self.bind_to_label( self.ui.LBL_NO_TREES_WARNING )
        self.bind_to_label( self.ui.LBL_SELECTION_WARNING )
        self.bind_to_label( self.ui.LBL_NO_INBUILT )
        self.bind_to_workflow_box( self.ui.FRA_TOOLBAR, ESelect.HAS_GRAPH )
        
        self.update_trees()
        
        switch = global_view.options().browse_mode
        
        if switch == EBrowseMode.ASK:
            pass
        elif switch == EBrowseMode.INBUILT:
            self.enable_inbuilt_browser()
        elif switch == EBrowseMode.SYSTEM:
            self.__disable_inbuilt_browser()
        else:
            raise SwitchError( "FrmWebtree.__init__.switch", switch )
    
    
    @property
    def file_name( self ):
        return self.__file_name
    
    
    @file_name.setter
    def file_name( self, value ):
        self.__file_name = value
        self.ui.BTN_SAVE_TO_FILE.setEnabled( bool( value ) )
        self.ui.BTN_SYSTEM_BROWSER.setEnabled( bool( value ) )
        self.ui.BTN_BROWSE_HERE.setEnabled( bool( value ) )
    
    
    def update_trees( self ):
        selection: LegoSelection = self.get_selection()
        model: LegoModel = self.get_model()
        self.file_name = path.join( MENV.local_data.local_folder( intermake.constants.FOLDER_TEMPORARY ), "temporary_visjs.html" )
        
        self.ui.LBL_NO_TREES_WARNING.setVisible( model.get_status( constants.STAGES.TREES_6 ).is_none )
        
        graph = None
        
        for item in selection:
            if isinstance( item, INamedGraph ) and item.graph is not None:
                graph = item
            else:
                graph = None
                break
        
        error = not graph
        self.ui.LBL_SELECTION_WARNING.setVisible( error )
        
        if error:
            visjs = ""
        else:
            visjs = graph_viewing.create( format_str = None,
                                          graph = graph,
                                          model = model,
                                          format = global_view.options().gui_tree_view )
        
        file_helper.write_all_text( self.file_name, visjs )
        
        self.__update_browser()
    
    
    def on_selection_changed( self ):
        self.update_trees()
    
    
    @exqtSlot()
    def on_BTN_BROWSE_HERE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.enable_inbuilt_browser()
    
    
    @exqtSlot()
    def on_BTN_SYSTEM_BROWSER_clicked( self ) -> None:
        """
        Signal handler:
        """
        from mhelper import io_helper
        io_helper.system_open(self.file_name)
        
    
    
    @exqtSlot()
    def on_BTN_SAVE_TO_FILE_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    def __disable_inbuilt_browser( self ):
        self.ui.BTN_BROWSE_HERE.setVisible( False )
        self.ui.LBL_NO_INBUILT.setVisible( False )
    
    
    def enable_inbuilt_browser( self ):
        if self.is_browser:
            return
        
        self.is_browser = True
        self.ui.BTN_BROWSE_HERE.setVisible( False )
        self.ui.WIDGET_OTHER.setVisible( False )
        self.ui.WIDGET_MAIN.setVisible( True )
        
        layout = QGridLayout()
        self.ui.WIDGET_MAIN.setLayout( layout )
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        self.browser = QWebEngineView()
        self.browser.setVisible( True )
        self.browser.titleChanged[str].connect( self.__on_title_changed )
        layout.addWidget( self.browser )
        
        self.__update_browser()
    
    
    def __update_browser( self ):
        if self.is_browser and self.file_name:
            self.browser.load( QUrl.fromLocalFile( self.file_name ) )  # nb. setHtml doesn't work with visjs, so we always need to use a temporary file
    
    
    def __on_title_changed( self, title: str ):
        self.ui.LBL_TITLE.setText( title )
        self.ui.LBL_TITLE.setToolTip( self.browser.url().toString() )
        self.ui.LBL_TITLE.setStatusTip( self.browser.url().toString() )
        self.ui.LBL_TITLE.setVisible( True )
