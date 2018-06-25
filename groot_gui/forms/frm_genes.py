from typing import Dict, Tuple, Callable

from groot_gui.forms.resources import resources

import groot
import intermake
import intermake_qt
import mhelper_qt as qt
from groot_gui.forms.frm_base import FrmBase
import mhelper as mh


class _LineEdit( qt.QLineEdit ):
    def focusInEvent( self, QFocusEvent ):
        super().focusInEvent( QFocusEvent )
        self.setStyleSheet( "QLineEdit {border: 2px solid red;}" )
    
    
    def focusOutEvent( self, QFocusEvent ):
        super().focusOutEvent( QFocusEvent )
        self.setStyleSheet( "" )


class FrmGenes( FrmBase ):
    """
    The gene list screen displays the genes in the current model.
    
    A table of genes and their information is displayed.
    
    From this screen, genes can be renamed, set as outgroups, or deleted from the model.
    
    This screen does _not_ display sequence data or domain arrangement, please use the alignment
    viewer or lego diagram editor for these features.
    """
    
    txt_to_rename = "txt_to_rename"
    orig_text = "orig_text"
    
    
    def __init__( self, parent ):
        super().__init__( parent )
        self.setWindowTitle( "Genes" )
        
        self.queue = []
        
        root_layout = qt.QVBoxLayout()
        self.setLayout( root_layout )
        
        toolbar = qt.QFrame()
        root_layout.addWidget( toolbar )
        
        self.tool_layout = qt.QHBoxLayout()
        self.tool_layout.setContentsMargins( qt.QMargins( 0, 0, 0, 0 ) )
        toolbar.setLayout( self.tool_layout )
        self.add_select_button( toolbar )
        
        self.add_toolbar_item( "Import\nnames", resources.rename.icon(), self.on_mnu_rename )
        
        qt.toolbar_helper.add_spacer( toolbar )
        self.add_toolbar_item( "Refresh", resources.refresh.icon(), self.refresh_data )
        self.add_toolbar_item( "Help", resources.help.icon(), self.on_mnu_help )
        
        self.scroll_area = qt.QScrollArea()
        self.scroll_area.setWidgetResizable( True )
        self.scroll_area.setSizePolicy( qt.QSizePolicy.MinimumExpanding, qt.QSizePolicy.Expanding )
        self.scroll_area.setHorizontalScrollBarPolicy( qt.Qt.ScrollBarAlwaysOff )
        self.scroll_area.setMinimumWidth( 1024 )
        root_layout.addWidget( self.scroll_area )
        
        frame = qt.QWidget()
        self.scroll_area.setWidget( frame )
        
        self.layout = qt.QGridLayout()
        self.layout.setContentsMargins( qt.QMargins( 0, 0, 0, 0 ) )
        frame.setLayout( self.layout )
        
        self.model = groot.current_model()
        
        self.setStyleSheet( """
        QAbstractButton[style="custom"]
        {
            background: white;
            border: 2px solid white;
            border-radius: 4px;
        }
        
        QAbstractButton[style="custom"]:hover
        {
            border: 2px solid black;
        }
        
        QAbstractButton[style="custom"]:pressed
        {
            border: 2px solid silver;
        }
        
        QAbstractButton[style="custom"]:checked
        {
            background: #03A9F4;
        }
        """ )
        
        self.lut: Dict[groot.Gene, Tuple[qt.QLineEdit, qt.QAbstractButton, qt.QAbstractButton, qt.QAbstractButton]] = { }
        self.refresh_data()
        
        btn_box = qt.QDialogButtonBox()
        btn_box.setStandardButtons( qt.QDialogButtonBox.Apply | qt.QDialogButtonBox.Ok | qt.QDialogButtonBox.Cancel )
        btn_box.button( qt.QDialogButtonBox.Apply ).clicked.connect( self.on_apply )
        btn_box.button( qt.QDialogButtonBox.Ok ).clicked.connect( self.on_ok )
        btn_box.button( qt.QDialogButtonBox.Cancel ).clicked.connect( self.on_cancel )
        root_layout.addWidget( btn_box )
    
    
    def on_refresh_data( self ):
        qt.layout_helper.delete_children( self.layout )
        x = mh.ByRef[int]( 0 )
        for header in (("Accession", "Accession"),
                       ("Name", "Display name"),
                       ("Length", "Length in sites"),
                       ("Maj.", "Major component"),
                       ("Min.", "Minor components"),
                       ("Dom.", "User-defined domains"),
                       ("RN", "Click to toggle renaming this gene"),
                       ("OG", "Click to toggle setting this gene as an outgroup"),
                       ("Del", "Click to toggle deleting this gene"),
                       ("View", "Click to view")):
            self.__add_header( *header, x )
        
        self.lut.clear()
        
        for row, gene in enumerate( self.model.genes ):
            row += 1
            label = qt.QLabel()
            label.setText( gene.accession )
            self.layout.addWidget( label, row, 0 )
            
            txt_nam = _LineEdit()
            txt_nam.setText( gene.display_name )
            txt_nam.textChanged.connect( self.__on_text_changed )
            setattr( txt_nam, self.orig_text, gene.display_name )
            self.layout.addWidget( txt_nam, row, 1 )
            
            label = qt.QLabel()
            label.setText( str( gene.length ) )
            self.layout.addWidget( label, row, 2 )
            
            label = qt.QLabel()
            label.setText( str( self.model.components.find_component_for_major_gene( gene ) ) )
            self.layout.addWidget( label, row, 3 )
            
            label = qt.QLabel()
            label.setText( mh.string_helper.format_array( self.model.components.find_components_for_minor_gene( gene ) ) )
            self.layout.addWidget( label, row, 4 )
            
            label = qt.QLabel()
            label.setText( str( len( self.model.user_domains.by_gene( gene ) ) ) )
            self.layout.addWidget( label, row, 5 )
            
            btn_nam = self.__mk_button()
            btn_nam.setIcon( resources.rename.icon() )
            self.layout.addWidget( btn_nam, row, 6 )
            
            btn_out = self.__mk_button()
            btn_out.setIcon( resources.outgroup.icon() )
            btn_out.setChecked( gene.is_outgroup )
            
            self.layout.addWidget( btn_out, row, 7 )
            
            btn_rem = self.__mk_button()
            btn_rem.setIcon( resources.remove.icon() )
            self.layout.addWidget( btn_rem, row, 8 )
            
            btn_view = self.__mk_button()
            btn_view.setIcon( resources.view.icon() )
            btn_view.clicked[bool].connect( self.__view_gene )
            setattr( btn_view, "gene", gene )
            self.layout.addWidget( btn_view, row, 9 )
            
            self.lut[gene] = (txt_nam, btn_nam, btn_out, btn_rem)
            
            setattr( txt_nam, self.txt_to_rename, btn_nam )
    
    
    def on_inspect( self, item: object ):
        super().on_inspect( item )
        
        if isinstance( item, groot.Gene ):
            line_edit = self.lut[item][0]
            line_edit.setFocus()
            self.scroll_area.ensureWidgetVisible( line_edit )
    
    
    def __view_gene( self ):
        gene = getattr( self.sender(), "gene" )
        self.inspect_elsewhere( gene )
    
    
    def add_toolbar_item( self, title: str, icon: qt.QIcon, callback: Callable[[], None] ):
        mnu_name = qt.QToolButton()
        mnu_name.setText( title )
        mnu_name.setIcon( icon )
        mnu_name.setIconSize( qt.QSize( 32, 32 ) )
        mnu_name.setFixedSize( qt.QSize( 64, 64 ) )
        mnu_name.setToolButtonStyle( qt.Qt.ToolButtonTextUnderIcon )
        mnu_name.clicked.connect( callback )
        self.tool_layout.addWidget( mnu_name )
    
    
    def on_apply( self, exit: bool = False ):
        self.queue = []
        
        for gene, (txt_nam, btn_nam, btn_out, btn_rem) in self.lut.items():
            assert isinstance( btn_nam, qt.QAbstractButton )
            assert isinstance( btn_out, qt.QAbstractButton )
            assert isinstance( btn_rem, qt.QAbstractButton )
            assert isinstance( txt_nam, qt.QLineEdit )
            
            name = txt_nam.text()
            
            if btn_nam.isChecked() and gene.name != name:
                self.queue.append( (groot.set_gene_name, { "gene": gene, "name": name }) )
            
            out = btn_out.isChecked()
            
            if out != gene.is_outgroup:
                self.queue.append( (groot.set_outgroups, { "genes": [gene], "position": out }) )
            
            if btn_rem.isChecked():
                self.queue.append( (groot.drop_genes, { "genes": [gene] }) )
        
        if not qt.FrmGenericText.request( self,
                                          confirm = True,
                                          message = "The following changes will be made",
                                          text = "<html><body><ul>" + "\n".join
                                                  (
                                                  ("<li><b>{}</b> {}</li>".format
                                                          (
                                                          f.__name__,
                                                          ", ".join(
                                                                  "<i>{}</i>='{}'".format
                                                                          (
                                                                          arg_name, arg_value
                                                                  )
                                                                  for arg_name, arg_value in a.items()
                                                          )
                                                  )
                                                          for f, a in self.queue
                                                  )
                                          ) + "</ul></body></html>"
                                          ):
            self.queue.clear()
            return
        
        if exit:
            self.queue.append( (None, None) )
        
        self.run_queue()
    
    
    def run_queue( self ):
        if not self.queue:
            return
        
        next_cmd, next_args = self.queue.pop( 0 )
        
        if next_cmd is None:
            self.close()
            return
        
        intermake.acquire( next_cmd, parent = self ).run( **next_args ).listen( self.on_run_queue )
    
    
    def on_run_queue( self, result: intermake.AsyncResult ):
        if result.is_success:
            self.run_queue()
        else:
            self.queue.clear()
    
    
    def on_ok( self ):
        self.on_apply( True )
    
    
    def on_cancel( self ):
        self.reject()
    
    
    def __add_header( self, txt, tt, x: mh.ByRef[int] ):
        label = qt.QLabel()
        label.setProperty( "style", "heading" )
        label.setText( txt )
        label.setToolTip( tt )
        self.layout.addWidget( label, 0, x.value )
        x.value += 1
    
    
    def __mk_button( self ):
        btn = qt.QToolButton()
        btn.setCheckable( True )
        btn.setProperty( "style", "custom" )
        btn.setSizePolicy( qt.QSizePolicy.Preferred, qt.QSizePolicy.Preferred )
        return btn
    
    
    def __on_text_changed( self ):
        text: qt.QLineEdit = self.sender()
        button: qt.QAbstractButton = getattr( text, self.txt_to_rename )
        orig = getattr( text, self.orig_text )
        button.setChecked( text.text() != orig )
    
    
    def on_mnu_rename( self ):
        intermake_qt.FrmArguments.request( self, groot.import_gene_names )
    
    
    def on_mnu_help( self ):
        self.actions.show_my_help()
