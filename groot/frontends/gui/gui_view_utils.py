"""
Collection of miscellany for dealing with the GUI in GROOT.
"""

from typing import FrozenSet, Iterable, List, Optional, Callable
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QAction, QGraphicsView, QMenu, QAbstractButton
from mhelper import MFlags, array_helper, string_helper, ResourceIcon, identity

from groot.data import global_view, LegoModel, LegoEdge, LegoUserDomain, LegoSequence, LegoComponent, LegoSplit, LegoFusion
from groot.frontends.gui.forms.resources import resources


_MENUCSS = 'font-size: 18px; font-family: "Segoe UI";'


class ESelect( MFlags ):
    EX_SPECIAL = 1 << 1
    EX_SEQUENCES = 1 << 2
    EX_DOMAINS = 1 << 3
    EX_EDGES = 1 << 4
    EX_COMPONENTS = 1 << 5
    EX_ALIGNMENTS = 1 << 6
    EX_TREES_ROOTED = 1 << 7
    EX_TREES_UNROOTED = 1 << 8
    EX_FUSIONS = 1 << 9
    EX_POINTS = 1 << 10
    EX_SPLITS = 1 << 11
    EX_CONSENSUS = 1 << 12
    EX_SUBSETS = 1 << 13
    EX_SUBGRAPHS = 1 << 14
    EX_NRFGS = 1 << 15
    EX_CHECKED = 1 << 16
    EX_USERGRAPHS = 1 << 17
    
    HAS_FASTA = EX_SEQUENCES | EX_DOMAINS | EX_EDGES | EX_COMPONENTS | EX_ALIGNMENTS
    HAS_GRAPH = EX_TREES_ROOTED | EX_TREES_UNROOTED | EX_SUBGRAPHS | EX_NRFGS | EX_USERGRAPHS
    IS_SPLIT = EX_SPLITS | EX_CONSENSUS


class LegoSelection:
    """
    IMMUTABLE
    Represents the selection made by the user.
    """
    
    
    def __init__( self, items: Iterable[object] = None ):
        if items is None:
            items = frozenset()
        
        if not isinstance( items, FrozenSet ):
            items = frozenset( items )
        
        self.items: FrozenSet[object] = items
        self.sequences = frozenset( x for x in self.items if isinstance( x, LegoSequence ) )
        self.user_domains = frozenset( x for x in self.items if isinstance( x, LegoUserDomain ) )
        self.components = frozenset( x for x in self.items if isinstance( x, LegoComponent ) )
        self.edges = frozenset( x for x in self.items if isinstance( x, LegoEdge ) )
        self.fusions = frozenset( x for x in self.items if isinstance( x, LegoFusion ) )
        self.splits = frozenset( x for x in self.items if isinstance( x, LegoSplit ) )
    
    
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


def show_selection_menu( control: QAbstractButton, actions, mode: ESelect = ESelect.ALL ):
    from groot.frontends.gui.gui_menu import GuiActions
    assert isinstance( actions, GuiActions )
    
    model = global_view.current_model()
    selection = actions.get_selection()
    alive = []
    
    root = QMenu()
    root.setTitle( "Make selection" )
    
    # Meta
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
    
    _add_submenu( "(Selection)", mode & ESelect.EX_SPECIAL, alive, OPTIONS, root, selection, None )
    
    # Sequences
    _add_submenu( "1. Genes", mode & ESelect.EX_SEQUENCES, alive, model.sequences, root, selection, resources.black_gene )
    
    # Edges
    _add_submenu( "2. Edges", mode & ESelect.EX_EDGES, alive, model.sequences, root, selection, resources.black_edge, ex = [LegoSequence.iter_edges] )
    
    # Components
    _add_submenu( "3. Components", mode & ESelect.EX_COMPONENTS, alive, model.components, root, selection, resources.black_major )
    
    # Components - FASTA (unaligned)
    _add_submenu( "3b. Component FASTA (unaligned)", mode & ESelect.EX_ALIGNMENTS, alive, (x.named_unaligned_fasta for x in model.components), root, selection, resources.black_alignment )
    
    # Domains
    _add_submenu( "4. Domains", mode & ESelect.EX_DOMAINS, alive, model.sequences, root, selection, resources.black_domain, ex = [LegoSequence.iter_userdomains] )
    
    # Components - FASTA (aligned)
    _add_submenu( "5. Component FASTA (aligned)", mode & ESelect.EX_ALIGNMENTS, alive, (x.named_aligned_fasta for x in model.components), root, selection, resources.black_alignment )
    
    # Components - trees (rooted)
    _add_submenu( "6a. Component trees (rooted)", mode & ESelect.EX_TREES_ROOTED, alive, (x.named_tree for x in model.components), root, selection, resources.black_tree )
    
    # Components - trees (unrooted)
    _add_submenu( "6b. Component trees (unrooted)", mode & ESelect.EX_TREES_UNROOTED, alive, (x.named_tree_unrooted for x in model.components), root, selection, resources.black_tree )
    
    # Fusions
    _add_submenu( "7a. Fusion events", mode & ESelect.EX_FUSIONS, alive, model.fusion_events, root, selection, resources.black_fusion )
    
    # Fusion formations
    _add_submenu( "7b. Fusion formations", mode & ESelect.EX_POINTS, alive, model.fusion_events, root, selection, resources.black_fusion, ex = [lambda x: x.formations] )
    
    # Fusion points
    _add_submenu( "7c. Fusion points", mode & ESelect.EX_POINTS, alive, model.fusion_events, root, selection, resources.black_fusion, ex = [lambda x: x.formations, lambda x: x.points] )
    
    #  Splits
    _add_submenu( "8. Splits", mode & ESelect.EX_SPLITS, alive, model.splits, root, selection, resources.black_split, it = True )
    
    # Consensus
    _add_submenu( "9. Consensus", mode & ESelect.EX_CONSENSUS, alive, model.consensus, root, selection, resources.black_consensus, it = True )
    
    # Subsets
    _add_submenu( "10. Subsets", mode & ESelect.EX_SUBSETS, alive, model.subsets, root, selection, resources.black_subset )
    
    # Pregraphs
    _add_submenu( "11. Pregraphs", mode & ESelect.EX_SUBGRAPHS, alive, model.iter_pregraphs(), root, selection, resources.black_pregraph )
    
    # Subgraphs
    _add_submenu( "12. Supertrees", mode & ESelect.EX_SUBGRAPHS, alive, model.subgraphs, root, selection, resources.black_subgraph )
    
    # NRFG - clean
    _add_submenu( "13. Fusion graphs", mode & ESelect.EX_NRFGS, alive, (model.fusion_graph_unclean, model.fusion_graph_clean), root, selection, resources.black_nrfg )
    
    # NRFG - report
    _add_submenu( "14. Reports", mode & ESelect.EX_CHECKED, alive, (model.report,), root, selection, resources.black_check )
    
    # Usergraphs
    _add_submenu( "User graphs", mode & ESelect.EX_USERGRAPHS, alive, model.user_graphs, root, selection, resources.black_nrfg )
    
    # Special
    if len( root.actions() ) == 0:
        act = QAction()
        act.setText( "List is empty" )
        act.setEnabled( False )
        act.tag = None
        alive.append( act )
        root.addAction( act )
    elif len( root.actions() ) == 1:
        root = root.actions()[0].menu()
    
    # Show menu
    orig = control.text()
    control.setText( root.title() )
    root.setStyleSheet( _MENUCSS )
    selected = root.exec_( control.mapToGlobal( QPoint( 0, control.height() ) ) )
    control.setText( orig )
    
    if selected is None:
        return
    
    tag = selected.tag
    
    if tag is not None:
        actions.set_selection( LegoSelection( frozenset( { tag } ) ) )


def _add_submenu( text: str,
                  requirement: bool,
                  alive: List[object],
                  elements: Iterable[object],
                  root: QMenu,
                  selection: LegoSelection,
                  icon: Optional[ResourceIcon],
                  ex: Optional[List[Callable[[object], Iterable[object]]]] = None,
                  it: bool = False ) -> int:
    if it:
        lst = sorted( elements, key = str )
        ne = []
        for s in range( 0, len( lst ), 20 ):
            ne.append( (s, lst[s:s + 20]) )
        
        ex = ((lambda x: x[1]),)
        elements = ne
        fmt = lambda x: "{}-{}".format( x[0], x[0] + 20 )
    else:
        fmt = str
    
    sub_menu = QMenu()
    sub_menu.setTitle( text )
    sub_menu.setStyleSheet( _MENUCSS )
    count = 0
    
    for element in elements:
        if element is None:
            continue
        
        if not ex:
            if _add_action( requirement, alive, element, selection, sub_menu, icon ):
                count += 1
        else:
            count += _add_submenu( fmt( element ), requirement, alive, ex[0]( element ), sub_menu, selection, icon, ex = list( ex[1:] ) )
    
    if not count:
        # Nothing in the menu
        return 0
    
    alive.append( sub_menu )
    root.addMenu( sub_menu )
    return count


def _add_action( requirement: bool,
                 alive,
                 minigraph,
                 selection,
                 sub,
                 icon ):
    e = bool( requirement )
    act = QAction()
    act.setCheckable( True )
    act.setChecked( minigraph in selection )
    act.setText( str( minigraph ) )
    act.setEnabled( e )
    if icon:
        act.setIcon( icon.icon() )
    act.tag = minigraph
    alive.append( act )
    sub.addAction( act )
    return e
