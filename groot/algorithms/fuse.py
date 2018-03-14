"""
Model for finding fusion events.
"""
from typing import List, Set
from mgraph import MGraph, MNode, MEdge
from mhelper import Logger, array_helper

from groot.algorithms import lego_graph
from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence, FusionPoint, FusionEvent


__LOG = Logger( "fusion", False )
__LOG_ISOLATION = Logger( "isolation", False )


def remove_fusions( model: LegoModel ) -> int:
    """
    Removes all fusion points from the specified component.
    """
    if model.nrfg:
        raise ValueError( "Refusing to drop fusions because they are in use by the NRFG. Did you mean to drop the NRFG first?" )
    
    removed_count = 0
    
    model.fusion_events.clear()
    
    for component in model.components:
        graph = component.tree
        to_delete: List[MNode] = []
        
        for node in graph.get_nodes():
            if isinstance( node.data, FusionPoint ):
                if len( node.edges ) == 1:
                    to_delete.append( node )
                    continue
                
                assert len( node.edges ) == 2, len( node.edges )
                
                # Remove the old node
                graph.add_edge( node.parent, node.child )
                to_delete.append( node )
        
        for node in to_delete:
            node.remove_node()
        
        removed_count += len( to_delete )
    
    return removed_count

def find_all_fusion_points( model: LegoModel ) -> None:
    """
    Finds the fusion points in the model.
    i.e. Given the events (see `find_events`), find the exact points at which the fusion(s) occur.
    """
    r: List[FusionEvent] = []
    
    if __fusions_exist( model ):
        raise ValueError( "Cannot find fusion points because fusion points for this model already exist. Did you mean to remove the existing fusions first?" )
        
    for event in __find_fusion_events( model ):
        __LOG( "Processing fusion event: {}", event )
        event.points = []
        
        for component in model.components:
            for point in __find_fusion_points( event, component ):
                event.points.append( point )
        
        r.append( event )
    
    for x in r:
        model.fusion_events.add(x)

def __find_fusion_events( model: LegoModel ) -> List[FusionEvent]:
    """
    Finds the fusion events in the model.
    
    i.e. Which components fuse together to generate which other components.
    """
    results = []  # type: List[FusionEvent]
    index = 0
    
    #
    # Our EVENTS are two components that produce the same set of components
    # e.g. if A --> C and B --> C then A and B join to form C
    #
    for component_a, component_b in array_helper.triangular_comparison( model.components ):
        assert isinstance( component_a, LegoComponent )
        assert isinstance( component_b, LegoComponent )
        
        a_outgoing = set( component_a.outgoing_components() )
        b_outgoing = set( component_b.outgoing_components() )
        
        ab_ints = a_outgoing.intersection( b_outgoing )
        
        if a_outgoing == b_outgoing:
            __LOG( "FUSION FOUND" )
            __LOG( "{} AND {}", component_a, component_b )
            __LOG( "FORMING {}", ab_ints )
            results.append( FusionEvent( index, component_a, component_b, ab_ints ) )
            index += 1
        else:
            __LOG( "NOT A FUSION:" )
            __LOG( "{} AND {}", component_a, component_b )
            __LOG( "FORMING {}", ab_ints )
    
    #
    # Some fusions will form things actually formed by other fusions
    # strip out subsequence formations from the fusions
    #
    continue_ = True
    
    while continue_:
        continue_ = False
        
        for event in results:
            if len( event.products ) > 1:
                for event_b in results:
                    f = array_helper.first_or_none( event_b.products )
                    if len( event_b.products ) == 1 and f in event.products:
                        for component in (event_b.component_a, event_b.component_b):
                            if component in event.products:
                                __LOG( "EVENT {} SHOULD LOSE PRODUCT {} BECAUSE THAT'S ALREADY IN EVENT {}", event, f, event_b )
                                event.products.remove( f )
                                __LOG( "NOW INTERSECTIONS ARE {}", event )
                                continue_ = True
    
    return results


def __fusions_exist( model: LegoModel ):
    if model.fusion_events:
        return True
    
    for component in model.components:
        for node in component.tree:
            if isinstance( node.data, FusionPoint ):
                return True
    
    return False





def __find_fusion_points( fusion_event: FusionEvent,
                          component: LegoComponent ) -> List[FusionPoint]:
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
    
    if fusion_event.component_c is component:
        __LOG( "Base of graph" )
        first: MNode = graph.root
        root = first.add_parent()
        root.make_root()
        assert isinstance( component, LegoComponent )
        sequences = lego_graph.get_sequence_data( graph ).intersection( set( fusion_event.component_c.major_sequences ) )
        result = FusionPoint( fusion_event, component, sequences, set() )
        root.data = result
        return [result]
    
    # The `intersection_aliases` correspond to βγδ in the above diagram
    
    __LOG( "component.minor_sequences = {}", component.minor_sequences )
    __LOG( "fusion_event.component_a.major_sequences = {}", fusion_event.component_a.major_sequences )
    __LOG( "fusion_event.component_b.major_sequences = {}", fusion_event.component_b.major_sequences )
    
    component_sequences = set( component.minor_sequences )
    
    inside_a: Set[LegoSequence] = component_sequences.intersection( fusion_event.component_a.major_sequences )
    inside_b: Set[LegoSequence] = component_sequences.intersection( fusion_event.component_b.major_sequences )
    outside: Set[LegoSequence] = component_sequences.intersection( [y for x in fusion_event.products for y in x.major_sequences] )
    ignored: Set[LegoSequence] = component_sequences - inside_a - inside_b - outside
    
    if not inside_a and not inside_b:
        __LOG( "THESE AREN'T THE COMPONENTS WE'RE LOOKING FOR" )
        return []
    
    if inside_a and inside_b:
        raise ValueError( "What is happening?" )
    
    inside = inside_a or inside_b
    
    __LOG( "I WANT INSIDE  {}", inside_a )
    __LOG( "            OR {}", inside_b )
    __LOG( "I WANT OUTSIDE {}", outside )
    __LOG( "I WANT IGNORED {}", ignored )  # TODO: not sure whether to have an ignored set makes any sense
    
    # Iterate over all the edges to make a list of `candidate` edges
    # - those separating βγδ from everything else
    inside_nodes = set( node for node in graph if (isinstance( node.data, LegoSequence ) and node.data in inside) )
    outside_nodes = set( node for node in graph if (isinstance( node.data, LegoSequence ) and node.data in outside) )
    
    __LOG( graph.to_ascii() )
    isolation_points = list( isolate( graph, inside_nodes, outside_nodes ) )
    
    __LOG( "----There are {} isolation points on {} ¦ {}", len( isolation_points ), inside, outside )
    
    results = []
    
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
        
        sequences = lego_graph.get_ileaf_data( isolation_point.outside_nodes )
        outer_sequences = lego_graph.get_ileaf_data( isolation_point.inside_nodes )
        fusion_point = FusionPoint( fusion_event, component, sequences, outer_sequences )
        fusion_node.data = fusion_point
        results.append( fusion_point )
    
    __LOG( "----{} results", len( results ) )
    
    return results


class EdgeInfo:
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


def prepare_graph( graph: MGraph,
                   inside_request: Set[MNode],
                   outside_request: Set[MNode] ):
    results = []
    for edge in graph.edges:
        assert isinstance( edge, MEdge )
        left_nodes, right_nodes = edge.cut_nodes()
        results.append( EdgeInfo( edge, False, left_nodes, right_nodes, inside_request, outside_request ) )
        results.append( EdgeInfo( edge, True, right_nodes, left_nodes, inside_request, outside_request ) )
    return results


def isolate( graph: MGraph,
             inside_request: Set[MNode],
             outside_request: Set[MNode],
             debug_level: int = 0 ):
    __LOG_ISOLATION.indent = debug_level
    __LOG_ISOLATION( "READY TO ISOLATE" )
    __LOG_ISOLATION( "*ISOLATE* INSIDE:  (n={}) {}", len( inside_request ), inside_request, sort = True )
    __LOG_ISOLATION( "*ISOLATE* OUTSIDE: (n={}) {}", len( outside_request ), outside_request, sort = True )
    
    edges: List[EdgeInfo] = prepare_graph( graph, inside_request, outside_request )
    
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
        yield from isolate( graph, inside_request, set(best.outside_incorrect) )
    
    __LOG_ISOLATION.indent = 0
