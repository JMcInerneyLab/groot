"""
Collection of miscellany for dealing with the GUI in GROOT.
"""

from typing import FrozenSet, Iterable

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QAction, QGraphicsView, QMenu, QToolButton

from groot.data import global_view
from groot.data.lego_model import ComponentAsAlignment, ComponentAsGraph, ILegoSelectable, LegoComponent, LegoEdge, LegoModel, LegoSequence, LegoUserDomain
from groot.frontends.gui.gui_workflow import LegoStage
from groot.frontends.gui import gui_workflow
from mhelper import MFlags, array_helper, string_helper


class LegoSelection:
    """
    IMMUTABLE
    Represents the selection made by the user.
    """
    
    
    def __init__( self, items: Iterable[ILegoSelectable] = None ):
        if items is None:
            items = frozenset()
        
        if not isinstance( items, FrozenSet ):
            items = frozenset( items )
        
        self.items: FrozenSet[ILegoSelectable] = items
        self.sequences = frozenset( x for x in self.items if isinstance( x, LegoSequence ) )
        self.user_domains = frozenset( x for x in self.items if isinstance( x, LegoUserDomain ) )
        self.components = frozenset( x for x in self.items if isinstance( x, LegoComponent ) )
        self.edges = frozenset( x for x in self.items if isinstance( x, LegoEdge ) )
    
    
    def is_empty( self ):
        return not self.items
    
    
    def selection_type( self ):
        return type( array_helper.first_or_none( self.items ) )
    
    
    def __iter__( self ):
        return iter( self.items )
    
    
    def __contains__( self, item ):
        return item in self.items
    
    
    def __str__( self ):
        if len( self.items ) == 0:
            return "No selection"
        elif len( self.items ) == 1:
            return str( array_helper.first_or_error( self.items ) )
        
        r = []
        
        if self.sequences:
            r.append( "{} genes".format( len( self.sequences ) ) )
        
        if self.user_domains:
            r.append( "{} domains".format( len( self.user_domains ) ) )
        
        if self.components:
            r.append( "{} components".format( len( self.components ) ) )
        
        if self.edges:
            r.append( "{} edges".format( len( self.edges ) ) )
        
        return string_helper.format_array( r, final = " and " )


class MyView( QGraphicsView ):
    """
    Subclasses QGraphicsView to provide mouse zooming. 
    """
    
    
    def wheelEvent( self, event: QWheelEvent ):
        """
        Zoom in or out of the view.
        """
        if event.modifiers() & Qt.ControlModifier or event.modifiers() & Qt.MetaModifier:
            zoomInFactor = 1.25
            zoomOutFactor = 1 / zoomInFactor
            
            # Save the scene pos
            oldPos = self.mapToScene( event.pos() )
            
            # Zoom
            if event.angleDelta().y() > 0:
                zoomFactor = zoomInFactor
            else:
                zoomFactor = zoomOutFactor
            self.scale( zoomFactor, zoomFactor )
            
            # Get the new position
            newPos = self.mapToScene( event.pos() )
            
            # Move scene to old position
            delta = newPos - oldPos
            self.translate( delta.x(), delta.y() )


class EChanges( MFlags ):
    """
    Describes the changes after a command has been issued.
    These are returned by most of the GROOT user-commands.
    When the GUI receives an EChanges object, it updates the pertinent data.
    The CLI does nothing with the object.
    
    :data MODEL_OBJECT:     The model object itself has changed.
                            Implies FILE_NAME, MODEL_ENTITIES
    :data FILE_NAME:        The filename of the model has changed and/or the recent files list.
    :data MODEL_ENTITIES:   The entities within the model have changed.
    :data COMPONENTS:       The components within the model have changed.
    :data COMP_DATA:        Meta-data (e.g. trees) on the components have changed
    :data MODEL_DATA:       Meta-data (e.g. the NRFG) on the model has changed
    :data INFORMATION:      The text printed during the command's execution is of primary concern to the user.
    """
    __no_flags_name__ = "NONE"
    
    MODEL_OBJECT = 1 << 0
    FILE_NAME = 1 << 1
    MODEL_ENTITIES = 1 << 2
    COMPONENTS = 1 << 3
    COMP_DATA = 1 << 4
    MODEL_DATA = 1 << 5
    INFORMATION = 1 << 6
    DOMAINS = 1 << 7


class SelectionManipulator:
    """
    Manipulates a selection.
    
    """
    
    
    def select_left( self, model: LegoModel, selection: LegoSelection ) -> LegoSelection:
        select = set()
        
        for domain1 in model.user_domains:
            for domain2 in selection.user_domains:
                if domain1.sequence is domain2.sequence and domain1.start <= domain2.start:
                    select.add( domain1 )
                    break
        
        return LegoSelection( select )
    
    
    def select_right( self, model: LegoModel, selection: LegoSelection ) -> LegoSelection:
        select = set()
        
        for domain1 in model.user_domains:
            for domain2 in selection.user_domains:
                if domain1.sequence is domain2.sequence and domain1.start <= domain2.start:
                    select.add( domain1 )
                    break
        
        return LegoSelection( select )
    
    
    def select_direct_connections( self, model: LegoModel, selection: LegoSelection ) -> LegoSelection:
        edges = set()
        
        for domain in selection.user_domains:
            for edge in model.edges:
                if edge.left.has_overlap( domain ) or edge.right.has_overlap( domain ):
                    edges.add( edge )
        
        select = set()
        
        for edge in edges:
            select.add( edge.start )
            select.add( edge.end )
        
        return LegoSelection( select )
    
    
    def select_all( self, model: LegoModel, _: LegoSelection ) -> LegoSelection:
        """
        Selects everything.
        """
        return LegoSelection( model.user_domains )


def show_selection_menu( control: QToolButton, actions, workflow: LegoStage = None ):
    model = global_view.current_model()
    selection = global_view.current_selection()
    alive = []
    roots = []
    
    root = QMenu()
    root.setTitle( "Make selection" )
    
    # Meta
    if workflow in (None,):
        relational = QMenu()
        relational.setTitle( "Relational" )
        OPTION_1 = "Select all"
        OPTION_2 = "Select none"
        OPTION_3 = "Invert selection"
        OPTION_4 = "Select sequences with no site data"
        OPTION_5 = "Select domains to left of selected domains"
        OPTION_6 = "Select domains to right of selected domains"
        OPTION_7 = "Select domains connected to selected domains"
        OPTIONS = (OPTION_1, OPTION_2, OPTION_3, OPTION_4, OPTION_5, OPTION_6, OPTION_7)
        
        _add_submenu( alive, OPTIONS, root, roots, selection, "Relational" )
    
    # Sequences
    if workflow in (None, gui_workflow.STAGES.FASTA_2) and model.sequences:
        _add_submenu( alive, model.sequences, root, roots, selection, "Genes" )
    
    # Domains
    if workflow in (None, gui_workflow.STAGES.DOMAINS_4) and model.user_domains:
        _add_submenu( alive, model.user_domains, root, roots, selection, "Domains" )
    
    # Edges
    if workflow in (None, gui_workflow.STAGES.BLAST_1) and model.edges:
        edges = QMenu()
        edges.setTitle( "Edges" )
        
        for sequence in model.sequences:
            assert isinstance( sequence, LegoSequence )
            sequence_edges = QMenu()
            sequence_edges.setTitle( str( sequence ) )
            
            for edge in model.edges:
                if edge.left.sequence is not sequence and edge.right.sequence is not sequence:
                    continue
                
                _add_action( alive, edge, selection, sequence_edges )
            
            alive.append( sequence_edges )
            edges.addMenu( sequence_edges )
        
        roots.append( edges )
        root.addMenu( edges )
    
    # Components
    if workflow in (None, gui_workflow.STAGES.COMPONENTS_3):
        _add_submenu( alive, model.components, root, roots, selection, "Components" )
    
    # Components - alignments
    if workflow in (None, gui_workflow.STAGES.ALIGNMENTS_5):
        _add_submenu( alive, [ComponentAsAlignment( x ) for x in model.components], root, roots, selection, "Alignments" )
    
    # Components - trees
    if workflow in (None, gui_workflow.STAGES.TREES_6):
        _add_submenu( alive, [ComponentAsGraph( x ) for x in model.components], root, roots, selection, "Trees" )
    
    # Fusions
    if workflow in (None, gui_workflow.STAGES.FUSIONS_7):
        _add_submenu( alive, model.fusion_events, root, roots, selection, "Fusions" )
    
    # Fusion points
    if workflow in (None, gui_workflow.STAGES.POINTS_7b):
        fusion_points = QMenu()
        fusion_points.setTitle( "Fusion points" )
        
        for fusion in model.fusion_events:
            fusions_points = QMenu()
            fusions_points.setTitle( str( fusion ) )
            
            for fusion_point in fusion.points:
                _add_action( alive, fusion_point, selection, fusions_points )
            
            alive.append( fusions_points )
            fusion_points.addMenu( fusions_points )
        
        roots.append( fusion_points )
        root.addMenu( fusion_points )
    
    #  Splits
    if workflow in (None, gui_workflow.STAGES.SPLITS_8):
        _add_submenu( alive, model.nrfg.splits, root, roots, selection, "Splits (candidates)" )
    
    # Consensus
    if workflow in (None, gui_workflow.STAGES.CONSENSUS_9):
        _add_submenu( alive, model.nrfg.consensus, root, roots, selection, "Splits (consensus)" )
        
    # Subgraphs
    if workflow in (None, gui_workflow.STAGES.SUBSETS_10):
        _add_submenu( alive, model.nrfg.subsets, root, roots, selection, "Subsets" )
    
    # Subgraphs
    if workflow in (None, gui_workflow.STAGES.SUBGRAPHS_11):
        _add_submenu( alive, model.nrfg.minigraphs, root, roots, selection, "Subgraphs" )
    
    # NRFG - unclean
    graphs = None
    
    if workflow in (None, gui_workflow.STAGES.FUSED_12):
        if model.nrfg.fusion_graph_unclean:
            graphs = QMenu()
            _add_action( alive, model.nrfg.fusion_graph_unclean, selection, graphs )
    
    # NRFG - clean        
    if workflow in (None, gui_workflow.STAGES.CLEANED_13):
        if model.nrfg.fusion_graph_clean:
            graphs = graphs or QMenu()
            _add_action( alive, model.nrfg.fusion_graph_clean, selection, graphs )
        
    
        
    # NRFG - report
    if workflow in (None, gui_workflow.STAGES.CHECKED_14):
        if model.nrfg.report:
            graphs = graphs or QMenu()
            _add_action( alive, model.nrfg.report, selection, graphs )
        
    if graphs is not None:
        graphs.setTitle( "Graphs" )
        roots.append( graphs )
        root.addMenu( graphs )
    
    # Special
    if not roots:
        act = QAction()
        act.setText( "List is empty" )
        act.setEnabled( False )
        act.tag = None
        alive.append( act )
        root.addAction( act )
    elif len( roots ) == 1:
        root = roots[0]
    
    # Show menu
    orig = control.text()
    control.setText( root.title() )
    selected = root.exec_( control.mapToGlobal( QPoint( 0, control.height() ) ) )
    control.setText( orig )
    
    if selected is None:
        return
    
    tag = selected.tag
    
    from groot.frontends.gui.gui_menu import GuiActions
    assert isinstance( actions, GuiActions )
    
    if tag is not None:
        actions.set_selection( LegoSelection( frozenset( { tag } ) ) )


def _add_submenu( alive, e, root, roots, selection, text ):
    if not e:
        return
    
    fusions = QMenu()
    fusions.setTitle( text )
    for x in e:
        _add_action( alive, x, selection, fusions )
    roots.append( fusions )
    root.addMenu( fusions )


def _add_action( alive, minigraph, selection, sub ):
    act = QAction()
    act.setCheckable( True )
    act.setChecked( minigraph in selection )
    act.setText( str( minigraph ) )
    act.tag = minigraph
    alive.append( act )
    sub.addAction( act )
