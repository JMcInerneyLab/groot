from typing import Any, Dict

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QTreeWidgetItem, QMessageBox
from groot.frontends.gui.forms.designer import frm_selection_list_designer

from groot import constants
from groot.data.lego_model import LegoSequence, EPosition
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import LegoSelection
from groot.frontends.gui import gui_workflow
from intermake.visualisables.visualisable import IVisualisable, VisualisablePath
from mhelper import ignore, array_helper, string_helper
from mhelper_qt import exceptToGui, exqtSlot


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
        
        self.bind_to_label( self.ui.LBL_NO_DATA_WARNING )
        self.bind_to_select( self.ui.BTN_CHANGE_SELECTION )
        self.bind_to_workflow_box( self.ui.GRP_WORKFLOW,
                                   self.ui.BTN_WORKFLOW,
                                   self.ui.BTN_CREATE,
                                   self.ui.BTN_REMOVE,
                                   self.ui.BTN_VIEW,
                                   gui_workflow.VISUALISERS.VIEW_ENTITIES,
                                   gui_workflow.STAGES.FASTA_2 )
        
        self.ui.LST_ALL.itemChanged[QTreeWidgetItem, int].connect( self.__on_item_changed )
        self.ui.LST_SELECTED.itemChanged[QTreeWidgetItem, int].connect( self.__on_item_changed )
        
        self.ui.LST_ALL.setHeaderHidden( False )
        self.ui.LST_SELECTED.setHeaderHidden( False )
        self.on_BTN_MAXIMISE_clicked()
    
    
    @exceptToGui()
    def __on_item_changed( self, list_item: Any, column: int ):
        ignore( column )
        item = list_item.tag
        checked = list_item.checkState( 0 ) == Qt.Checked
        self.set_selected( item, checked )
    
    
    def __add( self, item: IVisualisable, list = None ):
        if list is None:
            list = self.ui.LST_ALL
        
        selected = item in self.get_selection()
        
        list_item = QTreeWidgetItem()
        list_item.setCheckState( 0, Qt.Checked if selected else Qt.Unchecked )
        list_item.tag = item
        
        i = VisualisablePath.from_visualisable_temporary( item ).info()
        
        cols: Dict[str, int] = list.tag
        
        for x in i.iter_children():
            assert isinstance( x, VisualisablePath )
            v = x.get_raw_value()
            if array_helper.is_simple_iterable( v ):
                text = string_helper.format_array( v )
            else:
                text = str( v )
            
            if not text or len( text ) > 100:
                continue
            
            col_index = cols.get( x.key )
            
            if col_index is None:
                col_index = len( cols )
                cols[x.key] = col_index
                list.headerItem().setText( col_index, x.key )
            
            list_item.setText( col_index, text )
        
        list.addTopLevelItem( list_item )
    
    
    def __refresh_lists( self ):
        model = self.get_model()
        
        self.ui.LBL_NO_DATA_WARNING.setVisible( model.get_status( constants.STAGES.BLAST_1 ).is_none )
        
        self.ui.LST_SELECTED.clear()
        self.ui.LST_ALL.clear()
        
        self.ui.LST_SELECTED.tag = { }
        self.ui.LST_ALL.tag = { }
        
        self.ui.LST_SELECTED.setHeaderItem( QTreeWidgetItem() )
        self.ui.LST_ALL.setHeaderItem( QTreeWidgetItem() )
        
        for item in self.get_selection():
            self.__add( item, self.ui.LST_SELECTED )
        
        w = self.workflow
        
        if w == gui_workflow.STAGES.BLAST_1:
            title = "Edges"
            for item in model.edges:
                self.__add( item )
        elif w == gui_workflow.STAGES.FASTA_2:
            title = "Genes"
            for item in model.sequences:
                self.__add( item )
        elif w in (gui_workflow.STAGES.COMPONENTS_3, gui_workflow.STAGES.ALIGNMENTS_5, gui_workflow.STAGES.TREES_6):
            title = "Components"
            for item in model.components:
                self.__add( item )
        elif w == gui_workflow.STAGES.DOMAINS_4:
            title = "Domains"
            for item in model.user_domains:
                self.__add( item )
        elif w == gui_workflow.STAGES.FUSIONS_7:
            title = "Fusions"
            for item in model.fusion_events:
                self.__add( item )
        elif w == gui_workflow.STAGES.SPLITS_8:
            title = "Splits"
            for item in model.nrfg.splits:
                self.__add( item )
        elif w == gui_workflow.STAGES.CONSENSUS_9:
            title = "Consensus"
            for item in model.nrfg.consensus:
                self.__add( item )
        elif w == gui_workflow.STAGES.SUBSETS_10:
            title = "Subsets"
            for item in model.nrfg.subsets:
                self.__add( item )
        elif w == gui_workflow.STAGES.SUBGRAPHS_11:
            title = "Subgraphs"
            for item in model.nrfg.minigraphs:
                self.__add( item )
        elif w == gui_workflow.STAGES.FUSED_12:
            title = "Raw NRFG"
            if model.nrfg.fusion_graph_unclean:
                self.__add( model.nrfg.fusion_graph_unclean )
        elif w in (gui_workflow.STAGES.CLEANED_13, gui_workflow.STAGES.CHECKED_14):
            title = "NRFG"
            if model.nrfg.fusion_graph_unclean:
                self.__add( model.nrfg.fusion_graph_unclean )
        else:
            title = "No workflow mode"
        
        self.ui.LBL_ALL.setText( title )
    
    
    def on_plugin_completed( self ):
        self.__refresh_lists()
    
    
    def on_selection_changed( self ):
        self.__refresh_lists()
    
    
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
    def on_BTN_CHANGE_SELECTION_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_REFRESH_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.__refresh_lists()
    
    
    @exqtSlot()
    def on_BTN_SELECT_clicked( self ) -> None:
        """
        Signal handler:
        """
        items = self.ui.LST_ALL.selectedItems()
        
        if len( items ) == 1:
            item: QTreeWidgetItem = items[0].tag
            self.set_selected( item, True )
    
    
    @exqtSlot()
    def on_BTN_DESELECT_clicked( self ) -> None:
        """
        Signal handler:
        """
        items = self.ui.LST_SELECTED.selectedItems()
        
        if len( items ) == 1:
            item: QTreeWidgetItem = items[0].tag
            self.set_selected( item, False )
    
    
    @exqtSlot()
    def on_BTN_CLEAR_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.set_selection( LegoSelection() )
    
    
    @exqtSlot()
    def on_BTN_MAXIMISE_clicked( self ) -> None:
        """
        Signal handler:
        """
        v = not self.ui.LST_SELECTED.isVisible()
        self.ui.LST_SELECTED.setVisible( v )
        self.ui.LBL_SELECTED.setVisible( v )
        self.ui.BTN_SELECT.setVisible( v )
        self.ui.BTN_DESELECT.setVisible( v )
        self.ui.BTN_CLEAR.setVisible( v )
    
    
    @exqtSlot()
    def on_BTN_OUTGROUP_clicked( self ) -> None:
        """
        Signal handler:
        """
        message = []
        
        # TODO: We modify the model here, this breaks MVC architecture!
        
        if self.get_model().get_status( constants.STAGES.FUSIONS_7 ):
            QMessageBox.information( self, self.windowTitle(), "Cannot set outgroups once the trees are in use." )
            return
        
        for x in self.actions.get_selection():
            if isinstance( x, LegoSequence ):
                if x.position == EPosition.NONE:
                    message.append( "{} --> Outgroup".format( x ) )
                    x.position = EPosition.OUTGROUP
                else:
                    message.append( "{} --> Normal".format( x ) )
                    x.position = EPosition.NONE
        
        if not message:
            QMessageBox.information( self, self.windowTitle(), "Please select at least one gene to set outgroups." )
            return
        
        msg = QMessageBox()
        msg.setText( "Modified {} genes.".format( len( message ) ) )
        msg.setDetailedText( "\n".join( message ) )
        msg.setIcon( QMessageBox.Information )
        msg.exec_()
        
        self.__refresh_lists()
