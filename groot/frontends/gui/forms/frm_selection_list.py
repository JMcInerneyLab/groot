from typing import Any

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItem
from groot.frontends.gui.forms.designer import frm_selection_list_designer

from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import EChanges
from mhelper import ignore
from mhelper_qt import exceptToGui


class FrmSelectionList( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_selection_list_designer.Ui_Dialog( self )
        self.setWindowTitle( "Selection" )
        self.__refresh_lists()
        
        self.ui.RAD_COMPONENTS.toggled[bool].connect( self.__on_radio_changed )
        self.ui.RAD_DOMAINS.toggled[bool].connect( self.__on_radio_changed )
        self.ui.RAD_EDGES.toggled[bool].connect( self.__on_radio_changed )
        self.ui.RAD_GENES.toggled[bool].connect( self.__on_radio_changed )
        self.ui.RAD_OTHER.toggled[bool].connect( self.__on_radio_changed )
        
        self.ui.LST_MAIN.itemChanged[QTreeWidgetItem, int].connect( self.__on_item_changed )
    
    
    def __on_item_changed( self, list_item: Any, column: int ):
        ignore( column )
        item = list_item.tag
        checked = list_item.checkState( 0 ) == Qt.Checked
        self.set_selected( item, checked )
    
    
    def __on_radio_changed( self, _: bool ):
        self.__refresh_lists()
        
    def on_LBL_NO_DATA_WARNING_linkActivated( self, _:str ):
        from groot.frontends.gui.forms.frm_workflow import FrmWorkflow
        self.show_form(FrmWorkflow)
    
    
    def __refresh_lists( self ):
        selection = self.get_selection()
        model = self.get_model()
        
        self.ui.LBL_NO_DATA_WARNING.setVisible(not model.sequences)
        
        self.ui.LST_MAIN.clear()
        self.ui.LBL_SELECTION_INFO.setText( str( selection ) )
        
        if self.ui.RAD_GENES.isChecked():
            for sequence in model.sequences:
                item = QTreeWidgetItem()
                item.setCheckState( 0, Qt.Checked if sequence in selection else Qt.Unchecked )
                item.setText( 0, str( sequence ) )
                item.tag = sequence
                self.ui.LST_MAIN.addTopLevelItem( item )
        
        if self.ui.RAD_COMPONENTS.isChecked():
            for component in model.components:
                item = QTreeWidgetItem()
                item.setCheckState( 0, Qt.Checked if component in selection else Qt.Unchecked )
                item.setText( 0, str( component ) )
                item.tag = component
                self.ui.LST_MAIN.addTopLevelItem( item )
        
        if self.ui.RAD_DOMAINS.isChecked():
            for user_domain in model.user_domains:
                item = QTreeWidgetItem()
                item.setCheckState( 0, Qt.Checked if user_domain in selection else Qt.Unchecked )
                item.setText( 0, str( user_domain ) )
                item.tag = user_domain
                self.ui.LST_MAIN.addTopLevelItem( item )
        
        if self.ui.RAD_EDGES.isChecked():
            for edge in model.edges:
                item = QTreeWidgetItem()
                item.setCheckState( 0, Qt.Checked if edge in selection else Qt.Unchecked )
                item.setText( 0, str( edge ) )
                item.tag = edge
                self.ui.LST_MAIN.addTopLevelItem( item )
        
        if self.ui.RAD_OTHER.isChecked():
            if model.nrfg:
                item = QTreeWidgetItem()
                item.setCheckState( 0, Qt.Checked if model.nrfg in selection else Qt.Unchecked )
                item.setText( 0, str( model.nrfg ) )
                item.tag = model.nrfg
                self.ui.LST_MAIN.addTopLevelItem( item )
            
            for fusion in model.fusion_events:
                item = QTreeWidgetItem()
                item.setCheckState( 0, Qt.Checked if fusion in selection else Qt.Unchecked )
                item.setText( 0, str( fusion ) )
                item.tag = fusion
                self.ui.LST_MAIN.addTopLevelItem( item )
                
                for point in fusion.points:
                    item2 = QTreeWidgetItem()
                    item2.setCheckState( 0, Qt.Checked if point in selection else Qt.Unchecked )
                    item2.setText( 0, str( point ) )
                    item.tag = point
                    item.addChild( item2 )
    
    
    def on_plugin_completed( self, change: EChanges ):
        self.__refresh_lists()
    
    
    def on_selection_changed( self ):
        self.__refresh_lists()
    
    
