from PyQt5.QtWidgets import QTreeWidgetItem
from groot.frontends.gui.forms.designer import frm_view_splits_designer

from groot import LegoSplit
from groot.frontends.gui.forms.frm_base import FrmSelectingToolbar
from groot.frontends.gui.gui_view_utils import ESelect
from mhelper import string_helper
from mhelper_qt import exceptToGui, exqtSlot, tree_helper


class FrmViewSplits( FrmSelectingToolbar ):
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_view_splits_designer.Ui_Dialog( self )
        self.setWindowTitle( "Splits" )
        
        self.bind_to_workflow_box( self.ui.FRA_TOOLBAR, ESelect.IS_SPLIT )
        
        self.ui.LST_MAIN.itemSelectionChanged.connect( self.__on_widget_itemSelectionChanged )
        
        self.on_refresh_data()
        self.__on_widget_itemSelectionChanged()
    
    
    def __on_widget_itemSelectionChanged( self ):
        data: LegoSplit = tree_helper.get_selected_data( self.ui.LST_MAIN )
        
        r = []
        
        model = self.get_model()
        
        evt = set( model.sequences ).union( model.fusion_points )
        
        for s in sorted( evt, key = str ):
            if data is None:
                colour = "#8080FF"
            elif s in data.split.inside:
                colour = "#00FF00"
            elif s in data.split.outside:
                colour = "#FF0000"
            else:
                colour = "#808080"
            
            r.append( '<a style="background:{0};color:#FFFFFF;" href="{1}">{1}</a>'.format( colour, s ) )
        
        self.ui.LBL_SELECTION_INFO.setText( " ".join( r ) )
    
    
    @exqtSlot()
    def on_BTN_REFRESH_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.on_refresh_data()
    
    
    def describe_filter( self ):
        sel = self.get_selection()
        r = []
        
        if sel.components:
            r.append( "(ᴄᴏᴍᴩ, ꜰᴏʀ) ⊇ {{{0}}}".format( string_helper.format_array( sel.components ) ) )
        
        if sel.sequences:
            r.append( "ᴀʟʟ ⊇ {{{0}}}".format( string_helper.format_array( sel.sequences ) ) )
        
        if sel.fusions:
            r.append( "ᴀʟʟ ⊇ {{{0}}}".format( string_helper.format_array( sel.fusions ) ) )
        
        if sel.fusions:
            r.append( "ꜱᴩʟɪᴛ ∈ {{{0}}}".format( string_helper.format_array( sel.splits ) ) )
        
        text = self.ui.TXT_ADDFILTER.text()
        if text:
            r.append( '"{0}" ∈ ꜱᴩʟɪᴛ' )
        
        return " ∧ ".join( r )
    
    
    def check_filter( self, split: LegoSplit ):
        sel = self.get_selection()
        
        if sel.components:
            if (not sel.components.issubset( split.components )
                    and not set( sel.components ).issuperset( split.evidence_for )):
                return False
        
        if sel.sequences:
            if not sel.sequences.issubset( split.split.all ):
                return False
        
        if sel.fusions:
            if not sel.fusions.issubset( split.split.all ):
                return False
        
        if sel.splits:
            if split not in sel.splits:
                return False
        
        text = self.ui.TXT_ADDFILTER.text()
        if text:
            if text.upper() not in str( split ).upper():
                return False
        
        return True
    
    
    def on_refresh_data( self ):
        tvw = self.ui.LST_MAIN
        
        tvw.clear()
        model = self.get_model()
        accepted = 0
        rejected = 0
        
        for split in model.splits:
            if not self.check_filter( split ):
                rejected += 1
                continue
            
            accepted += 1
            
            assert isinstance( split, LegoSplit )
            item = QTreeWidgetItem()
            
            col = tree_helper.get_or_create_column( tvw, "Inside" )
            txt = string_helper.format_array( split.split.inside )
            item.setText( col, txt )
            
            col = tree_helper.get_or_create_column( tvw, "Outside" )
            txt = string_helper.format_array( split.split.outside )
            item.setText( col, txt )
            
            col = tree_helper.get_or_create_column( tvw, "Components" )
            txt = string_helper.format_array( split.components )
            item.setText( col, txt )
            
            col = tree_helper.get_or_create_column( tvw, "For" )
            txt = string_helper.format_array( split.evidence_for )
            item.setText( col, txt )
            
            col = tree_helper.get_or_create_column( tvw, "Against" )
            txt = string_helper.format_array( split.evidence_against )
            item.setText( col, txt )
            
            col = tree_helper.get_or_create_column( tvw, "Unused" )
            txt = string_helper.format_array( split.evidence_unused )
            item.setText( col, txt )
            
            tree_helper.set_data( item, split )
            
            tvw.addTopLevelItem( item )
        
        self.ui.LBL_TITLE.setText( "{} splits, {} rejected due to filter {}".format( accepted, rejected, self.describe_filter() ) )
