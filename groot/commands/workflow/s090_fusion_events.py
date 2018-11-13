"""
Deals with the model's fusion events and fusion points.
"""
from typing import FrozenSet, List, Set, Iterator
from intermake import  pr
from mgraph import MEdge, MGraph, MNode
from mhelper import Logger, array_helper, string_helper

import itertools

from groot import constants
from groot.constants import EChanges
from groot.data.model_collections import FusionCollection
from groot.application import app
from groot.data import INode, Component, Fusion, Model, Point, Gene, global_view
from groot.data.model_core import Formation
from groot.utilities import lego_graph
from groot.commands.workflow import s080_tree


__LOG = Logger( "fusion", False )
__LOG_ISOLATION = Logger( "isolation", False )


@app.command( folder = constants.F_CREATE )
def create_fusions() -> EChanges:
    """
    Finds the fusion points in the model.
    i.e. Given the events (see `find_events`), find the exact points at which the fusion(s) occur.
    Requisites: `create_trees`
    """
    model = global_view.current_model()
    model.get_status( constants.STAGES.FUSIONS_9 ).assert_create()
    
    r: List[Fusion] = []
    
    for event in __find_fusion_events( model ):
        __LOG( "Processing fusion event: {}", event )
        event.points = []
        
        for component in model.components:
            __find_fusion_points( event, component )
        
        r.append( event )
    
    model.fusions = FusionCollection( r )
    n = len( model.fusions )
    pr.printx( "<verbose>{} {} detected</verbose>".format( n, "fusion" if n == 1 else "fusions" ) )
    return EChanges.MODEL_DATA


@app.command( folder = constants.F_DROP )
def drop_fusions() -> EChanges:
    """
    Removes all fusion points from the model.
    """
    model = global_view.current_model()
    previous = len( model.fusions )
    model.get_status( constants.STAGES.FUSIONS_9 ).assert_drop()
    
    removed_count = 0
    
    model.fusions.clear()
    
    # Reset trees
    for component in model.components:
        s080_tree.set_tree( component, component.tree )
    
    pr.printx( "<verbose>Removed {} fusion events and {} fusion points from the model.</verbose>".format( previous, removed_count ) )
    return EChanges.COMP_DATA


@app.command( names = ["print_fusions", "fusions"], folder = constants.F_PRINT )
def print_fusions() -> EChanges:
    """
    Prints model fusions.
    """
    results: List[str] = []
    
    model = global_view.current_model()
    
    for event in model.fusions:
        results.append( "- name               {}".format( event ) )
        results.append( "  components in      {}".format( event.components_in ) )
        results.append( "  component out      {}".format( event.component_out ) )
        results.append( "  index              {}".format( event.index ) )
        results.append( "  points             {}".format( string_helper.format_array( event.points ) ) )
        
        for point in event.points:
            results.append( "     -   name               {}".format( point ) )
            results.append( "         point_component    {}".format( point.point_component ) )
            results.append( "         count              {}".format( point.count ) )
            results.append( "         outer sequences    {}".format( string_helper.format_array( point.outer_sequences ) ) )
            results.append( "         pertinent inner    {}".format( string_helper.format_array( point.pertinent_inner ) ) )
            results.append( "         pertinent outer    {}".format( string_helper.format_array( point.pertinent_outer ) ) )
            results.append( "         sequences          {}".format( string_helper.format_array( point.genes ) ) )
            results.append( "" )
        
        results.append( "" )
    
    print( "\n".join( results ) )
    
    return EChanges.INFORMATION


def __find_fusion_events( model: Model ) -> List[Fusion]:
    """
    Finds the fusion events in the model.
    
    i.e. Which components fuse together to generate which other components.
    """
    results: List[Fusion] = []
    
    for outgoing in model.components:
        incoming = [x for x in model.components if outgoing in x.outgoing_components()]
        
        while __remove_causing( incoming ):
            pass
        
        if incoming:
            results.append( Fusion( len( results ), tuple( incoming ), outgoing ) )
    
    return results


def __remove_causing( the_list: List[Component] ) -> bool:
    """
    Removes an 𝓐 from `the_list` (𝕃) if 𝓑 is already in 𝕃 and 𝓐 forms 𝓑.
    :return: Was an 𝓐 removed?
    """
    for a, b in itertools.combinations( the_list, 2 ):
        assert isinstance( a, Component )
        assert isinstance( b, Component )
        
        if b in a.outgoing_components():
            the_list.remove( a )
            return True
    
    return False


def __find_or_create_point( event: Fusion,
                            component: Component,
                            inner: FrozenSet[INode],
                            outer: FrozenSet[INode] ):
    """
    Either retrieves the matching point or generates a new one.
    """
    formation = None
    
    pertinent_inner = frozenset( inner.intersection( event.component_out.major_genes ) )
    
    for x in event.formations:  # type: Formation
        if x.pertinent_inner == pertinent_inner:
            formation = x
            break
    
    if formation is None:
        formation = Formation( event, inner, len( event.formations ), pertinent_inner )
        event.formations.append( formation )
    
    p = Point( formation, outer, component, len( formation.points ) )
    
    formation.points.append( p )
    return p


def __find_fusion_points( fusion_event: Fusion,
                          component: Component ) -> None:
    """
    In the tree of `component` we look for the node separating the event's intersections from everything else.
    
    We have a tree (which hopefully looks something like...)
    
         ┌── ▒▒▒▒      α        ╗
         │                      ║
      ┌──┤                      ║ our non-composite genes
      │  │                      ║
      │  └── ▒▒▒▒      α        ╝
    ──┤
      │  ┌── ▒▒▒▒░░░░  αβγδ     ╗
      │1 │2                     ║
      └──┤                      ║ our composite genes
         │3                     ║
         └── ▒▒▒▒░░░░  αβγδ     ╝
    
    # `α` we are working on (which is in all nodes)
    # `β` is the component that identifies the "fusion" part of the tree
    # `β` itself may be made up of multiple other components (`βγδ`)
    """
    
    __LOG( "***** LOOKING FOR EVENT {} IN COMPONENT {} ***** ", fusion_event, component )
    
    graph: MGraph = component.tree
    
    if fusion_event.component_out is component:
        assert component is not None
        __LOG( "Base of graph" )
        first: MNode = graph.root
        root: MNode = first.add_parent()
        root.make_root()
        genes: FrozenSet[Gene] = frozenset( lego_graph.get_sequence_data( graph ).intersection( set( fusion_event.component_out.major_genes ) ) )
        result: Point = __find_or_create_point( fusion_event,
                                                component,
                                                inner = genes,
                                                outer = frozenset() )
        root.data = result
        return
    
    # The `intersection_aliases` correspond to βγδ in the above diagram
    
    __LOG( "component.minor_genes = {}", component.minor_genes )
    
    component_sequences = set( component.minor_genes )
    s = []
    insides: List[Set[Gene]] = []
    
    for i, com in enumerate( fusion_event.components_in ):
        __LOG( "fusion_event.component_{}.major_genes = {}", i, com.major_genes )
        st = set( com.major_genes )
        s.append( st )
        insides.append( component_sequences.intersection( st ) )
    
    outside: Set[Gene] = component_sequences.intersection( fusion_event.component_out.major_genes )
    
    if not any( x for x in insides ):
        __LOG( "THESE AREN'T THE COMPONENTS WE'RE LOOKING FOR" )
        return
    
    if sum( bool( x ) for x in insides ) != 1:
        raise ValueError( "What is happening?" )
    
    inside = array_helper.single( x for x in insides if x )
    
    __LOG( "I WANT INSIDE  {}", "            OR ".join( str( insides ) ) )
    __LOG( "I WANT OUTSIDE {}", outside )
    
    # Iterate over all the edges to make a list of `candidate` edges
    # - those separating βγδ from everything else
    inside_nodes = set( node for node in graph if (isinstance( node.data, Gene ) and node.data in inside) )
    outside_nodes = set( node for node in graph if (isinstance( node.data, Gene ) and node.data in outside) )
    
    __LOG( graph.to_ascii() )
    isolation_points = list( isolate( graph, inside_nodes, outside_nodes ) )
    
    __LOG( "----There are {} isolation points on {} ¦ {}", len( isolation_points ), inside, outside )
    
    # Add the fusions to the graph
    
    # Replace the edge :              #
    #   Ⓧ───🅰───Ⓨ                   #
    #                                 #
    # with:                           #
    #   Ⓧ───🅱───Ⓐ───🅲───Ⓨ         #
    #                                 #
    for isolation_point in isolation_points:
        # Create the fusion-point node
        fusion_node = MNode( graph )
        
        # Create the edges
        edge = graph.find_edge( isolation_point.internal_node, isolation_point.external_node )
        graph.add_edge( edge.left, fusion_node )
        graph.add_edge( fusion_node, edge.right )
        edge.remove_edge()
        
        genes = lego_graph.get_ileaf_data( isolation_point.outside_nodes )
        outer_sequences = frozenset( lego_graph.get_ileaf_data( isolation_point.inside_nodes ) )
        fusion_point = __find_or_create_point( fusion_event, component, genes, outer_sequences )
        fusion_node.data = fusion_point


class EdgeInfo:
    """
    Describes a fragment of a graph cut along an edge.
    
    :ivar edge:                The edge along which the graph was cut 
    :ivar flip_edge:           Whether the `inside_nodes` represent the edge's right (destination) set
    :ivar inside_nodes:        Nodes to one side of the edge 
    :ivar outside_nodes:       Nodes to the other side of the edge
    :ivar inside_request:      The set of nodes we want inside
    :ivar outside_request:     The set of nodes we want outside
    :ivar inside_count:        Length of `inside_nodes`
    :ivar outside_count:       Length of `outside_nodes`
    :ivar inside_incorrect:    Nodes in `inside_request` that appear in the `outside_nodes`
    :ivar outside_incorrect:   Nodes in the `outside_request` that appear in the `inside_nodes`
    :ivar internal_node:       Node to the designated "inside" of the edge
    :ivar external_node:       Node to the designated "outside" of the edge
    """
    
    
    def __init__( self,
                  edge: MEdge,
                  flip_edge: bool,
                  inside_nodes: Set[MNode],
                  outside_nodes: Set[MNode],
                  inside_request: Set[MNode],
                  outside_request: Set[MNode] ):
        self.edge = edge
        self.flip_edge = flip_edge
        self.inside_nodes = inside_nodes
        self.outside_nodes = outside_nodes
        
        self.inside_count = len( self.inside_nodes )
        self.outside_count = len( self.outside_nodes )
        self.inside_incorrect = [x for x in inside_request if x in outside_nodes]
        self.outside_incorrect = [x for x in outside_request if x in inside_nodes]
        
        if flip_edge:
            self.internal_node = edge.right
            self.external_node = edge.left
        else:
            self.internal_node = edge.left
            self.external_node = edge.right


def __cut_all_edges( graph: MGraph,
                     inside_request: Set[MNode],
                     outside_request: Set[MNode] ):
    """
    Cuts the graph along every edge, returning a list containing an `EdgeInfo` for each cut (see `EdgeInfo`).
    """
    results = []
    
    if not graph.edges:
        raise ValueError( "Cannot cut the graph because the graph has no edges." )
    
    for edge in graph.edges:
        left_nodes, right_nodes = edge.cut_nodes()
        # Each edge has two cuts, depending on which side is "inside" and which "outside"
        results.append( EdgeInfo( edge, False, left_nodes, right_nodes, inside_request, outside_request ) )
        results.append( EdgeInfo( edge, True, right_nodes, left_nodes, inside_request, outside_request ) )
    
    return results


def isolate( graph: MGraph,
             inside_request: Set[MNode],
             outside_request: Set[MNode],
             debug_level: int = 0
             ) -> Iterator[EdgeInfo]:
    __LOG_ISOLATION.indent = debug_level
    __LOG_ISOLATION( "READY TO ISOLATE" )
    __LOG_ISOLATION( "*ISOLATE* INSIDE:  (n={}) {}", len( inside_request ), inside_request, sort = True )
    __LOG_ISOLATION( "*ISOLATE* OUTSIDE: (n={}) {}", len( outside_request ), outside_request, sort = True )
    
    edges: List[EdgeInfo] = __cut_all_edges( graph, inside_request, outside_request )
    
    __LOG_ISOLATION( "{} EDGES", len( edges ) )
    
    valid_edges = [x for x in edges if not x.inside_incorrect]
    best_correct_score = min( len( x.outside_incorrect ) for x in valid_edges )
    best_correct = [x for x in valid_edges if len( x.outside_incorrect ) == best_correct_score]
    best_correct_count = min( x.inside_count for x in best_correct )
    best: EdgeInfo = array_helper.first_or_error( x for x in best_correct if x.inside_count == best_correct_count )
    
    __LOG_ISOLATION( "BEST ISOLATION:" )
    __LOG_ISOLATION( "*BEST* FLIP EDGE         {}", best.flip_edge )
    __LOG_ISOLATION( "*BEST* INSIDE INCORRECT  (n={}) {}", len( best.inside_incorrect ), best.inside_incorrect, sort = True )
    __LOG_ISOLATION( "*BEST* INSIDE            (n={}) {}", len( best.inside_nodes ), best.inside_nodes, sort = True )
    __LOG_ISOLATION( "*BEST* OUTSIDE INCORRECT (n={}) {}", len( best.outside_incorrect ), best.outside_incorrect, sort = True )
    __LOG_ISOLATION( "*BEST* OUTSIDE           (n={}) {}", len( best.outside_nodes ), best.outside_nodes, sort = True )
    
    yield best
    
    if best.outside_incorrect:
        __LOG_ISOLATION( "REMAINING" )
        yield from isolate( graph, inside_request, set( best.outside_incorrect ) )
    
    __LOG_ISOLATION.indent = 0
