from PyQt5.QtWidgets import QTreeWidgetItem
from groot.frontends.gui.forms.designer import frm_debug_designer

from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import EChanges
from mhelper_qt import exceptToGui


class FrmDebug( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_debug_designer.Ui_Dialog( self )
        self.setWindowTitle( "Debug" )
    
    
    def on_plugin_completed( self ):
        self.add( "COMPLETED" )
    
    
    def on_selection_changed( self ):
        self.add( "SELECTION: {}".format( self.get_selection() ) )
    
    
    def add( self, message ):
        item = QTreeWidgetItem()
        item.setText( 0, message )
        self.ui.LST_MAIN.addTopLevelItem( item )
        self.ui.LST_MAIN.scrollToBottom()
