"""
Allows the user to select an entity and display information on it (including the tree).

Despite the name, FrmWebtree does everything report (HTML) based.
"""

from os import path

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QGridLayout
from groot_gui.forms.designer import frm_webtree_designer

from groot import Model
from groot.utilities import entity_to_html
from groot_gui import LegoGuiHost
from groot_gui.forms.frm_base import FrmBaseWithSelection
from groot_gui.forms.frm_view_options import BROWSE_MODE
from intermake import MENV, constants as im_constants
from mhelper import OpeningWriter, SwitchError, file_helper, string_helper
from mhelper_qt import exceptToGui, exqtSlot, qt_gui_helper


class FrmWebtree( FrmBaseWithSelection ):
    """
    The reports screen generates HTML (webpage) reports on various elements of your Groot model.

    Groot will attempt to find a suitable engine to render HTML in this window, which can be
    configured from the preferences screen, or, if this doesn't work, you can opt for using your
    external web browser.
    
    Note that, aside from trees visualised using Javascript, the reports are not interactive,
    the various other Groot screens provide interaction more specific to specific elements.
    """
    
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_webtree_designer.Ui_Dialog( self )
        self.setWindowTitle( "Reports" )
        
        # Disable the browser host until its enabled
        self.ui.WIDGET_MAIN.setVisible( False )
        self.is_browser = False
        self.browser_ctrl = None
        self.html = ""
        
        # Setup the base class
        self.bind_to_label( self.ui.LBL_BROWSER_WARNING )
        self.add_select_button( self.ui.FRA_TOOLBAR )
        
        # Enable our browser?
        switch = LegoGuiHost.get_settings().enable_browser
        
        if switch == BROWSE_MODE.ASK:
            pass
        elif switch == BROWSE_MODE.INBUILT:
            self.enable_inbuilt_browser()
        elif switch == BROWSE_MODE.SYSTEM:
            self.ui.BTN_BROWSE_HERE.setVisible( False )
        else:
            raise SwitchError( "LegoGuiHost.get_settings().enable_browser", switch )
        
        # Show the selection
        self.update_page()
    
    
    def update_page( self ):
        model: Model = self.get_model()
        self.html = entity_to_html.render( self.selection, model ) if self.selection else ""
        self.__update_browser()
    
    
    def on_inspect( self, item: object ):
        super().on_inspect( item )
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
        with OpeningWriter( extension = ".html" ) as ow:
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
    def on_BTN_HELP_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_my_help()
    
    
    @exqtSlot()
    def on_BTN_VIEW_ELSEWHERE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.inspect_elsewhere()
    
    
    @exqtSlot()
    def on_BTN_REFRESH_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.__update_browser()
    
    
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
