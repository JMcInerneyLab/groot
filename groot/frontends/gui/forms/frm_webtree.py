from os import path, system

from PyQt5.QtCore import QUrl
from PyQt5.QtWidgets import QGridLayout
from groot.frontends.gui.forms.designer import frm_webtree_designer

import intermake
from groot.algorithms import graph_viewing
from groot.data.lego_model import LegoComponent, LegoNrfg
from groot.frontends.gui.forms.frm_base import ESelMenu, FrmBase
from intermake.engine.environment import MENV
from mhelper import file_helper
from mhelper_qt import exceptToGui, exqtSlot


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
        
        self.is_browser = False
        self.__file_name = None
        self.browser = None
        
        self.update_trees()
    
    
    @property
    def file_name( self ):
        return self.__file_name
    
    
    @file_name.setter
    def file_name( self, value ):
        self.__file_name = value
        self.ui.BTN_SYSTEM_BROWSER.setEnabled( bool( value ) )
        self.ui.BTN_BROWSE_HERE.setEnabled( bool( value ) )
    
    
    def update_trees( self ):
        selection = self.get_selection()
        sel_text = str( selection )
        model = self.get_model()
        trees = []
        
        for item in selection:
            if isinstance( item, LegoComponent ):
                trees.append( item.tree )
            elif isinstance( item, LegoNrfg ):
                trees.append( item.graph )
            else:
                self.ui.BTN_SELECTION.setText( sel_text + " (no trees)" )
                self.file_name = None
                return
        
        if not trees:
            self.ui.BTN_SELECTION.setText( sel_text + " (no trees)" )
            self.file_name = None
            return
        
        self.ui.BTN_SELECTION.setText( sel_text + " ({} trees)".format( len( trees ) ) )
        
        visjs = graph_viewing.create_vis_js( None, trees, model, title = False )
        self.file_name = path.join( MENV.local_data.local_folder( intermake.constants.FOLDER_TEMPORARY ), "temporary_visjs.html" )
        
        file_helper.write_all_text( self.file_name, visjs )
        
        if self.is_browser:
            self.browser.load( QUrl.fromLocalFile( self.file_name ) )  # nb. setHtml doesn't work with visjs, so we still need to use a temporary file
    
    
    def on_selection_changed( self ):
        self.update_trees()
    
    
    @exqtSlot()
    def on_BTN_OPTIONS_clicked( self ) -> None: #TODO: BAD_HANDLER - The widget 'BTN_OPTIONS' does not appear in the designer file.
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_SYSTEM_BROWSER_clicked( self ) -> None:
        """
        Signal handler:
        """
        if self.file_name:
            system( 'open "{}"'.format( self.file_name ) )
    
    
    @exqtSlot()
    def on_BTN_BROWSE_HERE_clicked( self ) -> None:
        """
        Signal handler:
        """
        if self.is_browser:
            return
        
        self.ui.WIDGET_OPEN.setVisible( False )
        self.ui.WIDGET_MAIN.setVisible( True )
        
        layout = QGridLayout()
        self.ui.WIDGET_MAIN.setLayout( layout )
        from PyQt5.QtWebEngineWidgets import QWebEngineView
        self.browser = QWebEngineView()
        layout.addWidget( self.browser )
    
    
    @exqtSlot()
    def on_BTN_SELECTION_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_selection_menu( ESelMenu.META_GRAPHS )
