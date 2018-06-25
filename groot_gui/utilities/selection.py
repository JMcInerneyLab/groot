from typing import Callable, Iterable, List, Optional

import groot
from PyQt5.QtCore import QPoint
from PyQt5.QtWidgets import QAbstractButton, QAction, QMenu
from groot_gui.forms.resources import resources
from mhelper import ResourceIcon, AnnotationInspector


_MENU_CSS = 'font-size: 18px; font-family: "Segoe UI";'
_GuiActions_ = "groot_gui.utilities.gui_menu.GuiActions"


def show_selection_menu( control: QAbstractButton,
                         default: object,
                         mode: type = object,
                         ) -> object:
    """
    Shows the selection menu.
    
    :param control:     Button to drop the menu down from. 
    :param default:     Currently selected item
    :param mode:        What we are capable of selecting (as a `type`).
    :return:            The selection made. This will have already been committed to `actions` if `actions` is a `GuiActions` object. 
    """
    model = groot.global_view.current_model()
    
    selection = default
    
    alive = []
    
    root = QMenu()
    root.setTitle( "Make selection" )
    
    # Sequences
    _add_submenu( "Genes", mode, alive, model.genes, root, selection, resources.black_gene )
    
    # Edges
    _add_submenu( "Edges", mode, alive, model.genes, root, selection, resources.black_edge, expand_functions = [groot.Gene.iter_edges] )
    
    # Components
    _add_submenu( "Components", mode, alive, model.components, root, selection, resources.black_major )
    
    # Components - FASTA (unaligned)
    _add_submenu( "Component FASTA (unaligned)", mode, alive, (x.named_unaligned_fasta for x in model.components), root, selection, resources.black_alignment )
    
    # Domains
    _add_submenu( "Domains", mode, alive, model.genes, root, selection, resources.black_domain, expand_functions = [groot.Gene.iter_userdomains] )
    
    # Components - FASTA (aligned)
    _add_submenu( "Component FASTA (aligned)", mode, alive, (x.named_aligned_fasta for x in model.components), root, selection, resources.black_alignment )
    
    # Components - trees (rooted)
    _add_submenu( "Component trees (rooted)", mode, alive, (x.named_tree for x in model.components), root, selection, resources.black_tree )
    
    # Components - trees (unrooted)
    _add_submenu( "Component trees (unrooted)", mode, alive, (x.named_tree_unrooted for x in model.components), root, selection, resources.black_tree )
    
    # Fusions
    _add_submenu( "Fusion events", mode, alive, model.fusions, root, selection, resources.black_fusion )
    
    # Fusion formations
    _add_submenu( "Fusion formations", mode, alive, model.fusions, root, selection, resources.black_fusion, expand_functions = [lambda x: x.formations] )
    
    # Fusion points
    _add_submenu( "Fusion points", mode, alive, model.fusions, root, selection, resources.black_fusion, expand_functions = [lambda x: x.formations, lambda x: x.points] )
    
    #  Splits
    _add_submenu( "Splits", mode, alive, model.splits, root, selection, resources.black_split, create_index = True )
    
    # Consensus
    _add_submenu( "Consensus", mode, alive, model.consensus, root, selection, resources.black_consensus, create_index = True )
    
    # Subsets
    _add_submenu( "Subsets", mode, alive, model.subsets, root, selection, resources.black_subset )
    
    # Pregraphs
    _add_submenu( "Pregraphs", mode, alive, model.iter_pregraphs(), root, selection, resources.black_pregraph )
    
    # Subgraphs
    _add_submenu( "Supertrees", mode, alive, model.subgraphs, root, selection, resources.black_subgraph )
    
    # NRFG - clean
    _add_submenu( "Fusion graphs", mode, alive, (model.fusion_graph_unclean, model.fusion_graph_clean), root, selection, resources.black_nrfg )
    
    # NRFG - report
    _add_submenu( "Reports", mode, alive, (model.report,), root, selection, resources.black_check )
    
    # Usergraphs
    _add_submenu( "User graphs", mode, alive, model.user_graphs, root, selection, resources.black_nrfg )
    
    # Usergraphs
    _add_submenu( "User reports", mode, alive, model.user_reports, root, selection, resources.black_check )
    
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
    root.setStyleSheet( _MENU_CSS )
    selected = root.exec_( control.mapToGlobal( QPoint( 0, control.height() ) ) )
    control.setText( orig )
    
    if selected is None:
        return None
    
    return selected.tag


def _add_submenu( text: str,
                  mode: type,
                  live_list: List[object],
                  elements: Iterable[object],
                  root: QMenu,
                  selection: object,
                  icon: Optional[ResourceIcon],
                  expand_functions: Optional[List[Callable[[object], Iterable[object]]]] = None,
                  create_index: bool = False ) -> int:
    """
    
    :param text: 
    :param mode: 
    :param live_list: 
    :param elements: 
    :param root: 
    :param selection: 
    :param icon: 
    :param expand_functions:    When set, each of the `elements` is expanded into its own menu via this function.
                                This should be a list, the first element of which is used (the second element is used to expand the next set, and so forth)
    :param create_index:        Add an index page (overrides `ex`) 
    :return: 
    """
    if create_index:
        lst = sorted( elements, key = str )
        ne = []
        for s in range( 0, len( lst ), 20 ):
            ne.append( (s, lst[s:s + 20]) )
        
        expand_functions = ((lambda x: x[1]),)
        elements = ne
        fmt = lambda x: "{}-{}".format( x[0], x[0] + 20 )
    else:
        fmt = str
    
    sub_menu = QMenu()
    sub_menu.setTitle( text )
    sub_menu.setStyleSheet( _MENU_CSS )
    count = 0
    
    for element in elements:
        if element is None:
            continue
        
        if not expand_functions:
            count += _add_action( mode, live_list, element, selection, sub_menu, icon )
        else:
            count += _add_submenu( fmt( element ), mode, live_list, expand_functions[0]( element ), sub_menu, selection, icon, expand_functions = list( expand_functions[1:] ) )
    
    if not count:
        # Nothing in the menu
        return 0
    
    live_list.append( sub_menu )
    root.addMenu( sub_menu )
    return count


def _add_action( mode: type,
                 live_list: List[object],
                 element: object,
                 selection: object,
                 menu: QMenu,
                 icon: ResourceIcon ):
    e = AnnotationInspector( mode ).is_viable_instance( element )
    act = QAction()
    act.setCheckable( True )
    act.setChecked( element is selection )
    act.setText( str( element ) )
    act.setEnabled( e )
    if icon:
        act.setIcon( icon.icon() )
    act.tag = element
    live_list.append( act )
    menu.addAction( act )
    return bool( e )
