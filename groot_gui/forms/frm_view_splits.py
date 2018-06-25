import groot
import mhelper
from PyQt5.QtWidgets import QTreeWidgetItem
from groot_gui.forms.designer import frm_view_splits_designer

from groot import Split
from groot_gui.forms.frm_base import FrmBaseWithSelection
from mhelper import string_helper
import mhelper_qt as qt


class _Filter:
    def __init__( self ):
        self.components = set()
        self.genes = set()
        self.fusions = set()
        self.splits = set()
        self.text = ""


class FrmViewSplits( FrmBaseWithSelection ):
    """
    The splits screen allows you to view the various splits in your trees.
    
    Clicking individual splits displays their matrix notation at the bottom of the screen.
    
    The splits can be searched and filtered using the options at the top.
    """
    
    
    @qt.exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_view_splits_designer.Ui_Dialog( self )
        self.setWindowTitle( "Splits" )
        self.filter = _Filter()
        self.add_select_button( self.ui.FRA_TOOLBAR )
        
        self.ui.LST_MAIN.itemSelectionChanged.connect( self.__on_widget_itemSelectionChanged )

        
        self.on_refresh_data()
        self.__on_widget_itemSelectionChanged()
    
    
    def _on_gene( self, name: str ):
        if name == "none":
            return
        
        gene = groot.current_model().genes[name]
        self.inspect_elsewhere( gene )
    
    
    def __on_widget_itemSelectionChanged( self ):
        data: Split = qt.tree_helper.get_selected_data( self.ui.LST_MAIN )
        
        qt.layout_helper.delete_children( self.ui.LAY_BBAR )
        
        model = self.get_model()
        
        vector = sorted( set( model.genes ).union( model.fusion_points ), key = str )
        
        for s in vector:
            if data is None:
                colour = "#8080FF"
            elif s in data.split.inside:
                colour = "#00FF00"
            elif s in data.split.outside:
                colour = "#FF0000"
            else:
                colour = "#808080"
            
            if isinstance( s, groot.Gene ):
                acc = s.accession
            else:
                acc = "none"
            
            label = qt.QLabel()
            label.setText( '<a style="background:{};color:#FFFFFF;" href="x">{}</a>'.format( colour, s ) )
            label.linkActivated[str].connect( self._on_link )
            label.setSizePolicy( qt.QSizePolicy.Fixed, qt.QSizePolicy.Fixed )
            setattr( label, "tag", s )
            self.ui.LAY_BBAR.addWidget( label )
        
    
    
    def _on_link( self, x ):
        self.inspect_elsewhere( getattr( self.sender(), "tag" ) )
    
    
    @qt.exqtSlot()
    def on_BTN_REFRESH_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.on_refresh_data()
    
    
    @qt.exqtSlot()
    def on_BTN_HELP_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_my_help()
    
    
    @qt.exqtSlot()
    def on_BTN_VIEW_ELSEWHERE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.inspect_elsewhere()
    
    
    @qt.exqtSlot()
    def on_BTN_ADD_TEXT_TO_FILTER_clicked( self ) -> None:
        """
        Signal handler:
        """
        txt = qt.FrmGenericText.request( self, message = "Filter", text = self.filter.text, editable = True )
        
        if txt is None:
            return
        
        self.filter.text = txt
        self.on_refresh_data()
    
    
    @qt.exqtSlot()
    def on_BTN_ADD_TO_FILTER_clicked( self ) -> None:
        """
        Signal handler:
        """
        s = self.selection
        
        if isinstance( s, groot.Gene ):
            self.filter.genes.add( s )
        elif isinstance( s, groot.Component ):
            self.filter.components.add( s )
        elif isinstance( s, groot.Fusion ):
            self.filter.fusions.add( s )
        elif isinstance( s, groot.Split ):
            self.filter.splits.add( s )
        else:
            raise mhelper.SwitchError( "selection", s, instance = True )
        
        self.on_refresh_data()
    
    
    @qt.exqtSlot()
    def on_BTN_REMOVE_FROM_FILTER_clicked( self ) -> None:
        """
        Signal handler:
        """
        s = self.selection
        
        try:
            if isinstance( s, groot.Gene ):
                self.filter.genes.remove( s )
            elif isinstance( s, groot.Component ):
                self.filter.components.remove( s )
            elif isinstance( s, groot.Fusion ):
                self.filter.fusions.remove( s )
            elif isinstance( s, groot.Split ):
                self.filter.splits.remove( s )
            else:
                raise mhelper.SwitchError( "selection", s, instance = True )
        except ValueError:
            pass
        
        self.on_refresh_data()
    
    
    def describe_filter( self ):
        sel = self.filter
        r = []
        
        if sel.components:
            r.append( "(ᴄᴏᴍᴩ, ꜰᴏʀ) ⊇ {{{0}}}".format( string_helper.format_array( sel.components ) ) )
        
        if sel.genes:
            r.append( "ᴀʟʟ ⊇ {{{0}}}".format( string_helper.format_array( sel.genes ) ) )
        
        if sel.fusions:
            r.append( "ᴀʟʟ ⊇ {{{0}}}".format( string_helper.format_array( sel.fusions ) ) )
        
        if sel.splits:
            r.append( "ꜱᴩʟɪᴛ ∈ {{{0}}}".format( string_helper.format_array( sel.splits ) ) )
        
        if sel.text:
            r.append( '"{0}" ∈ ꜱᴩʟɪᴛ'.format( sel.text ) )
        
        if not r:
            return "No filter"
        
        return " ∧ ".join( r )
    
    
    def check_filter( self, split: Split ):
        sel = self.filter
        
        if sel.components:
            if (not sel.components.issubset( split.components )
                    and not set( sel.components ).issuperset( split.evidence_for )):
                return False
        
        if sel.genes:
            if not sel.genes.issubset( split.split.all ):
                return False
        
        if sel.fusions:
            if not sel.fusions.issubset( split.split.all ):
                return False
        
        if sel.splits:
            if split not in sel.splits:
                return False
        
        if sel.text:
            if sel.text.upper() not in str( split ).upper():
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
            
            assert isinstance( split, Split )
            item = QTreeWidgetItem()
            
            col = qt.tree_helper.get_or_create_column( tvw, "Inside" )
            txt = string_helper.format_array( split.split.inside )
            item.setText( col, txt )
            
            col = qt.tree_helper.get_or_create_column( tvw, "Outside" )
            txt = string_helper.format_array( split.split.outside )
            item.setText( col, txt )
            
            col = qt.tree_helper.get_or_create_column( tvw, "Components" )
            txt = string_helper.format_array( split.components )
            item.setText( col, txt )
            
            col = qt.tree_helper.get_or_create_column( tvw, "For" )
            txt = string_helper.format_array( split.evidence_for )
            item.setText( col, txt )
            
            col = qt.tree_helper.get_or_create_column( tvw, "Against" )
            txt = string_helper.format_array( split.evidence_against )
            item.setText( col, txt )
            
            col = qt.tree_helper.get_or_create_column( tvw, "Unused" )
            txt = string_helper.format_array( split.evidence_unused )
            item.setText( col, txt )
            
            qt.tree_helper.set_data( item, split )
            
            tvw.addTopLevelItem( item )
        
        if rejected:
            self.ui.LBL_TITLE.setText( "{} splits, {} rejected due to filter".format( accepted, rejected ) )
        else:
            self.ui.LBL_TITLE.setText( "{} splits".format( accepted ) )
        
        self.ui.LBL_FILTER.setText( self.describe_filter() )
