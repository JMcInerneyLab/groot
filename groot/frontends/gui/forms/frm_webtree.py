import shutil
from os import path, system
from typing import List, Tuple

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QGridLayout
from groot.frontends.gui.forms.designer import frm_webtree_designer

import intermake
from groot import constants
from groot.algorithms import graph_viewing
from groot.frontends.gui import gui_workflow
from groot.data import global_view
from groot.data.global_view import EBrowseMode
from groot.data.lego_model import INamedGraph, LegoModel
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import LegoSelection
from intermake.engine.environment import MENV
from mgraph import MGraph
from mhelper import SwitchError, file_helper
from mhelper_qt import exceptToGui, exqtSlot, qt_gui_helper


class FrmWebtree( FrmBase ):
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
        
        self.bind_to_select( self.ui.BTN_SELECTION )
        self.bind_to_label( self.ui.LBL_NO_TREES_WARNING )
        self.bind_to_label( self.ui.LBL_SELECTION_WARNING )
        self.bind_to_label( self.ui.LBL_NO_INBUILT )
        self.bind_to_workflow_box( self.ui.GRP_WORKFLOW,
                                   self.ui.BTN_WORKFLOW,
                                   self.ui.BTN_CREATE,
                                   self.ui.BTN_REMOVE,
                                   self.ui.BTN_VIEW,
                                   gui_workflow.VISUALISERS.VIEW_TREE,
                                   gui_workflow.STAGES.TREES_6 )
        
        self.update_trees()
        
        switch = global_view.options().browse_mode
        
        if switch == EBrowseMode.ASK:
            pass
        elif switch == EBrowseMode.INBUILT:
            self.enable_inbuilt_browser()
            self.ui.BTN_SYSTEM_BROWSER.setVisible( False )
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
        names_and_graphs: List[Tuple[str, MGraph]] = []
        self.file_name = path.join( MENV.local_data.local_folder( intermake.constants.FOLDER_TEMPORARY ), "temporary_visjs.html" )
        
        self.ui.LBL_NO_TREES_WARNING.setVisible( model.get_status(constants.STAGES.TREES_6).is_none )
        
        for item in selection:
            if isinstance( item, INamedGraph ) and item.graph is not None:
                names_and_graphs.append( (str( item ), item.graph) )
            else:
                names_and_graphs.clear()
                break
        
        error = not names_and_graphs
        self.ui.LBL_SELECTION_WARNING.setVisible( error )
        
        if error:
            visjs = ""
        else:
            visjs = graph_viewing.create_vis_js( graph = names_and_graphs,
                                                 inline_title = False,
                                                 title = "{} - {} - {}".format( MENV.name, model.name, str( selection ) ) )
        
        file_helper.write_all_text( self.file_name, visjs )
        
        self.__update_browser()
    
    
    def on_selection_changed( self ):
        self.update_trees()
    
    
    @exqtSlot()
    def on_BTN_SYSTEM_BROWSER_clicked( self ) -> None: #TODO: BAD_HANDLER - The widget 'BTN_SYSTEM_BROWSER' does not appear in the designer file.
        """
        Signal handler:
        """
        if self.file_name:
            system( 'open "{}"'.format( self.file_name ) )
    
    
    @exqtSlot()
    def on_BTN_SAVE_TO_FILE_clicked( self ) -> None: #TODO: BAD_HANDLER - The widget 'BTN_SAVE_TO_FILE' does not appear in the designer file.
        """
        Signal handler:
        """
        if self.file_name:
            new_file_name = qt_gui_helper.browse_save( self, "HTML files (*.html)" )
            
            if new_file_name:
                shutil.copy( self.file_name, new_file_name )
    
    
    @exqtSlot()
    def on_BTN_BROWSE_HERE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.enable_inbuilt_browser()
    
    
    @exqtSlot()
    def on_BTN_WORKFLOW_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_CREATE_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_REMOVE_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_VIEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_SELECTION_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass  # intentional
    
    
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
