from typing import Callable, Set

from PyQt5.QtCore import QEvent, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from PyQt5.QtWidgets import QAction, QGraphicsScene, QGridLayout, QMenu, QSizePolicy, QAbstractButton
from groot_gui.forms.designer import frm_lego_designer

import intermake
import groot
from groot_gui.forms.frm_base import FrmBaseWithSelection
from groot_gui.lego import InteractiveGraphicsView, ModelView, lay_colour, lay_position, lay_selection
from groot_gui.utilities.gui_workflow import handlers, EIntent, Intent
from groot_gui.utilities.selection import show_selection_menu
from intermake.engine.environment import MCMD
from mhelper import array_helper, FunctionInspector, ignore
import mhelper_qt as qt


_BIT = "TAG_info"


class FrmLego( FrmBaseWithSelection ):
    """
    The Lego diagram editor allows the user to construct and view Lego diagrams from the current model.
    
    For good diagrams, a suitably defined set of Domains should have been generated first.
    
    The sidebar allows the user to quickly define domains and organise the diagram automatically.
    
    Double clicking elements in the diagram toggles edit mode.
    
    Settings for viewing the diagram are available from the Preferences window.
    """
    
    
    @qt.exceptToGui()
    def __init__( self, parent ) -> None:
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_lego_designer.Ui_Dialog( self )
        self.setWindowTitle( "Lego Diagram Editor" )
        
        #
        # Graphics view
        # 
        self.ctrl_graphics_view = InteractiveGraphicsView()
        v = self.ctrl_graphics_view
        sizePolicy = QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        sizePolicy.setHeightForWidth( v.sizePolicy().hasHeightForWidth() )
        v.setSizePolicy( sizePolicy )
        v.setObjectName( "graphicsView" )
        v.setBackgroundBrush( QBrush( QColor( 255, 255, 255 ) ) )
        v.setInteractive( True )
        layout = QGridLayout()
        self.ui.FRA_MAIN.setLayout( layout )
        layout.addWidget( v )
        
        # Open GL rendering
        if groot.global_view.options().opengl:
            v.setViewport( QGLWidget( QGLFormat( QGL.SampleBuffers ) ) )
        
        # Default (empty) scene
        scene = QGraphicsScene()
        scene.addRect( QRectF( -10, -10, 20, 20 ) )
        
        v.setScene( scene )
        
        #
        # Create our model view!
        #
        self.model_view: ModelView = None
        self.update_view()
        
        self.toggle_show_edit( False )
        
        # Button clicks
        for x in (self.ui.BTN_S_EDGES_,
                  self.ui.BTN_S_COMPS_,
                  self.ui.BTN_S_GENES_,
                  self.ui.BTN_S_MINCOMPS_,
                  self.ui.BTN_S_DOMAINS_):
            x.clicked[bool].connect( self.on_btn_click )
    
    
    def on_apply_request( self, request: Intent ):
        if request.is_inspect:
            lay_selection.select_by_entity( self.model_view, request.target )
    
    
    def on_btn_click( self, _ ):
        s: QAbstractButton = self.sender()
        msg = getattr( s, _BIT, None )
        self.inspect_elsewhere( msg )
    
    
    def event( self, e: QEvent ) -> bool:
        if e.type() == QEvent.WindowStateChange:
            self.ctrl_graphics_view.setVisible( bool( self.windowState() & Qt.WindowActive or self.windowState() & Qt.WindowMaximized ) )  # Maximised is for TDI mode
        
        return super().event( e )
    
    
    def update_view( self, changes = groot.EChanges.MODEL_OBJECT ) -> None:
        """
        Update the view with changes from the model.
        """
        if changes.MODEL_OBJECT or changes.MODEL_ENTITIES or changes.COMPONENTS or changes.DOMAINS:
            if self.model_view:
                self.model_view.scene.setParent( None )
            
            self.model_view = ModelView( self, self.ctrl_graphics_view, self.get_model() )
            self.model_view.on_selection_changed += self.__on_selection_changed
            self.ctrl_graphics_view.setScene( self.model_view.scene )
            self.refresh_view()
    
    
    def __on_selection_changed( self, domains: Set[groot.Domain] ):
        model = self.model_view.model
        genes = set( x.gene for x in domains )
        major = set( model.components.find_component_for_major_gene( x, default = None ) for x in genes )
        minor = set( y for x in domains for y in model.components.find_components_for_minor_domain( x ) )
        edges = set( y for y in model.edges.iter_touching( domains ) )
        
        self.ui.BTN_S_DOMAINS_.setText( "{} domains".format( len( domains ) ) if len( domains ) != 1 else str( array_helper.single( domains ) ) )
        self.ui.BTN_S_COMPS_.setText( "{} maj. comps.".format( len( major ) ) if len( major ) != 1 else str( array_helper.single( major ) ) )
        self.ui.BTN_S_MINCOMPS_.setText( "{} min. comps.".format( len( minor ) ) if len( minor ) != 1 else str( array_helper.single( minor ) ) )
        self.ui.BTN_S_EDGES_.setText( "{} edges".format( len( edges ) ) if len( edges ) != 1 else str( array_helper.single( edges ) ) )
        self.ui.BTN_S_GENES_.setText( "{} genes".format( len( genes ) ) if len( genes ) != 1 else str( array_helper.single( genes ) ) )
        
        setattr( self.ui.BTN_S_DOMAINS_, _BIT, domains )
        setattr( self.ui.BTN_S_COMPS_, _BIT, major )
        setattr( self.ui.BTN_S_MINCOMPS_, _BIT, minor )
        setattr( self.ui.BTN_S_EDGES_, _BIT, edges )
        setattr( self.ui.BTN_S_GENES_, _BIT, genes )
    
    
    @qt.exqtSlot()
    def on_BTN_ALIGN_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_intent_menu( lay_position.apply_position, lay_position.position_algorithms )
    
    
    @qt.exqtSlot()
    def on_BTN_OPTIONS_clicked( self ) -> None:
        """
        Signal handler:
        """
        handlers().VIEW_PREFERENCES.execute( self, EIntent.DIRECT, None )
    
    
    @qt.exqtSlot()
    def on_BTN_COLOUR_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_intent_menu( lay_colour.apply_colour, lay_colour.colour_algorithms )
    
    
    def show_intent_menu( self, apply_function: Callable[[ModelView, groot.AbstractAlgorithm], None], algo_collection: groot.AlgorithmCollection ) -> None:
        """
        Shows a drop down menu listing the available algorithms, calling `apply_function` if the user makes a choice.
        """
        menu = QMenu()
        map = { }
        
        for key, value in algo_collection.items():
            act = QAction()
            act.setText( MCMD.host.translate_name( key ) )
            act.setToolTip( value.__doc__ )
            map[act] = key
            menu.addAction( act )
        
        a: QAction = qt.menu_helper.show_menu( self, menu )
        
        if a is None:
            return
        
        algo_name = map[a]
        
        algo = algo_collection.get_algorithm( algo_name )
        
        apply_function( self.model_view, algo )
        self.refresh_view()
    
    
    def domain_fake_fn( self, model_view: ModelView, algo: groot.domain_algorithms.Algorithm ):
        """
        Wraps `groot.create_domains` into a method suitable for calling via `show_intent_menu`.
        """
        ignore( model_view )
        
        # Any extra args
        if len( FunctionInspector( algo.function ).args ) > groot.domain_algorithms.num_expected_args:
            handlers().CREATE_DOMAINS.execute( self, EIntent.INSPECT, algo )
        else:
            self.actions.run( groot.create_domains, algorithm = algo )
    
    
    @qt.exqtSlot()
    def on_BTN_REFRESH_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.update_view()
    
    
    @qt.exqtSlot()
    def on_BTN_SHOW_EDIT_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.toggle_show_edit()
    
    
    def toggle_show_edit( self, value = None ):
        v = value if value is not None else not self.ui.BTN_DELETE_GENE.isVisible()
        self.ui.BTN_DELETE_GENE.setVisible( v )
        self.ui.BTN_OUTGROUP_GENE.setVisible( v )
        self.ui.BTN_COMPONENT_GENE.setVisible( v )
        self.ui.BTN_RENAME_GENE.setVisible( v )
    
    
    @qt.exqtSlot()
    def on_BTN_DELETE_GENE_clicked( self ) -> None:
        """
        Signal handler:
        """
        genes = self.__get_selected_genes()
        handlers().DROP_GENES.execute( self, EIntent.INSPECT, list( genes ) )
    
    
    def __get_selected_genes( self ):
        genes = set()
        
        for domain in self.model_view.selection:
            genes.add( domain.gene )
        
        return genes
    
    
    @qt.exqtSlot()
    def on_BTN_OUTGROUP_GENE_clicked( self ) -> None:
        """
        Signal handler:
        """
        genes = self.__get_selected_genes()
        intermake.acquire( groot.set_outgroups, parent = self ).run( genes = list( genes ) )
    
    
    @qt.exqtSlot()
    def on_BTN_RENAME_GENE_clicked( self ) -> None:
        """
        Signal handler:
        """
        genes = self.__get_selected_genes()
        gene: groot.Gene = array_helper.first_or_none( genes )
        
        name = qt.FrmGenericText( self, message = "Rename the gene with accession '{}'".format( gene.accession ), text = gene.display_name, editable = True )
        
        if name:
            intermake.acquire( groot.set_gene_name, parent = self ).run( gene = gene, name = name )
    
    
    @qt.exqtSlot()
    def on_BTN_COMPONENT_GENE_clicked( self ) -> None:
        """
        Signal handler:
        """
        genes = self.__get_selected_genes()
        intermake.acquire( groot.set_major, parent = self ).run( genes = genes )
    
    
    @qt.exqtSlot()
    def on_BTN_HELP_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.actions.show_my_help()
    
    
    @qt.exqtSlot()
    def on_BTN_DOMAINS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_intent_menu( self.domain_fake_fn, groot.domain_algorithms )
    
    
    @qt.exqtSlot()
    def on_BTN_FIND_clicked( self ) -> None:
        """
        Signal handler:
        """
        sel = show_selection_menu( self.ui.BTN_FIND, None, self.__selecting_mode )
        
        if sel is not None:
            lay_selection.select_by_entity( self.model_view, sel )
            self.refresh_view()
    
    
    @qt.exqtSlot()
    def on_BTN_LEGEND_clicked( self ) -> None:
        """
        Signal handler: Show legend button
        """
        qt.FrmGenericText.request( self, title = "Legend", text = "".join( lay_colour.get_legend( self.model_view ) ) )
    
    
    @qt.exqtSlot()
    def on_BTN_SELECT_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.show_intent_menu( lay_selection.apply_select, lay_selection.selection_algorithms )
    
    
    def on_command_completed( self ) -> None:
        self.update_view( self.actions.frm_main.completed_changes )
    
    
    def refresh_view( self ) -> None:
        self.model_view.scene.update()
