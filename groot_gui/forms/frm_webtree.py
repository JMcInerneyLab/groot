"""
Allows the user to select an entity and display information on it (including the tree).

Despite the name, FrmWebtree does everything report (HTML) based.
"""

from os import path
from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QGridLayout
from mhelper import OpeningWriter, SwitchError, file_helper, string_helper
from mhelper_qt import exceptToGui, exqtSlot, qt_gui_helper
from intermake import MENV, constants as im_constants

import groot
from groot import LegoModel, LegoSequence
from groot.data import global_view, EPosition
from groot.data.global_view import EBrowseMode
from groot_gui.forms.designer import frm_webtree_designer
from groot_gui.forms.frm_base import FrmSelectingToolbar
from groot_gui.utilities.gui_view_utils import ESelect
from groot.utilities import entity_to_html


class FrmWebtree( FrmSelectingToolbar ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_webtree_designer.Ui_Dialog( self )
        self.setWindowTitle( "Tree Viewer" )
        
        # Disable the browser host until its enabled
        self.ui.WIDGET_MAIN.setVisible( False )
        self.is_browser = False
        self.browser_ctrl = None
        self.html = ""
        
        # Setup the base class
        self.bind_to_label( self.ui.LBL_BROWSER_WARNING )
        self.bind_to_workflow_box( self.ui.FRA_TOOLBAR, ESelect.ALL )
        
        # Enable our browser?
        switch = global_view.options().browse_mode
        
        if switch == EBrowseMode.ASK:
            pass
        elif switch == EBrowseMode.INBUILT:
            self.enable_inbuilt_browser()
        elif switch == EBrowseMode.SYSTEM:
            self.ui.BTN_BROWSE_HERE.setVisible( False )
        else:
            raise SwitchError( "FrmWebtree.__init__.switch", switch )
        
        # Show the selection
        self.update_page()
    
    
    def update_page( self ):
        selection = self.get_selection()
        s = selection.single
        model: LegoModel = self.get_model()
        self.html = entity_to_html.render( s, model ) if s else ""
        self.__update_browser()
        
        if isinstance( s, LegoSequence ):
            self.ui.BTN_OUTGROUP.setEnabled( True )
            self.ui.BTN_OUTGROUP.setChecked( s.position == EPosition.OUTGROUP )
        else:
            self.ui.BTN_OUTGROUP.setEnabled( False )
    
    
    def on_selection_changed( self ):
        self.update_page()
    
    
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
        with OpeningWriter() as ow:
            ow.write( self.html )
    
    
    @exqtSlot()
    def on_BTN_SAVE_TO_FILE_clicked( self ) -> None:
        """
        Signal handler:
        """
        file_name: str = qt_gui_helper.browse_save( self, "HTML (*.html)" )
        
        if file_name:
            file_helper.write_all_text( file_name, self.html )
    
    
    @exqtSlot()
    def on_BTN_OUTGROUP_clicked( self ) -> None:
        """
        Signal handler:
        """
        selection = self.get_selection()
        s = selection.single
        
        if isinstance( s, LegoSequence ):
            # We'll get a callback when the plugin completes so we don't need to confirm the button's status
            groot.set_outgroups( [s], not s.is_outgroup )
    
    
    @exqtSlot()
    def on_BTN_REFRESH_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.update_trees()
    
    
    def enable_inbuilt_browser( self ):
        if self.is_browser:
            return
        
        self.is_browser = True
        self.ui.BTN_BROWSE_HERE.setVisible( False )
        self.ui.WIDGET_OTHER.setVisible( False )
        self.ui.WIDGET_MAIN.setVisible( True )
        self.ui.TXT_BROWSER.setHtml( "" )
        
        layout = QGridLayout()
        self.ui.WIDGET_MAIN.setLayout( layout )
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        self.browser_ctrl = QWebEngineView()
        self.browser_ctrl.setVisible( True )
        self.browser_ctrl.titleChanged[str].connect( self.__on_title_changed )
        layout.addWidget( self.browser_ctrl )
        
        self.__update_browser()
    
    
    def __update_browser( self ):
        if self.is_browser:
            file_name = path.join( MENV.local_data.local_folder( im_constants.FOLDER_TEMPORARY ), "groot_temp.html" )
            file_helper.write_all_text( file_name, self.html )
            self.browser_ctrl.load( QUrl.fromLocalFile( file_name ) )  # nb. setHtml doesn't work with visjs, so we always need to use a temporary file
            self.ui.LBL_TITLE.setToolTip( self.browser_ctrl.url().toString() )
        else:
            title = string_helper.regex_extract( "<title>(.*?)</title>", self.html )
            self.__on_title_changed( title )
            self.ui.TXT_BROWSER.setHtml( self.html )
            self.ui.LBL_BROWSER_WARNING.setVisible( "<script" in self.html )
    
    
    def __on_title_changed( self, title: str ):
        self.ui.LBL_TITLE.setText( title )
