"""
Model for finding fusion events.
"""

from typing import List, Set

from groot.algorithms import graph_viewing
from groot.algorithms.classes import FusionEvent, FusionPoint, IFusion
from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence
from mgraph import MGraph, MNode
from mgraph.graphing import EDirection
from mhelper import Logger, array_helper


__LOG = Logger( "fusion", True )


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
            if isinstance( node.data, IFusion ):
                assert len( node.edges ) == 2
                
                # Remove the old node
                graph.add_edge( node.parent, node.child )
                to_delete.append( node )
        
        for node in to_delete:
            node.remove_node()
        
        removed_count += len( to_delete )
    
    return removed_count


def find_fusion_events( model: LegoModel ) -> List[FusionEvent]:
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
                                __LOG( "INTERSECTIONS {} SHOULD LOSE {} BECAUSE THATS ALREADY IN {}", event, f, event_b )
                                event.products.remove( f )
                                __LOG( "NOW INTERSECTIONS ARE {}", event )
                                continue_ = True
    
    return results


def __fusions_exist( model: LegoModel ):
    if model.fusion_events:
        return True
    
    for component in model.components:
        for node in component.tree:
            if isinstance( node.data, IFusion ):
                return True
    
    return False


def find_all_fusion_points( model: LegoModel ) -> None:
    """
    Finds the fusion points in the model.
    i.e. Given the events (see `find_events`), find the exact points at which the fusion(s) occur.
    """
    r: List[FusionEvent] = []
    
    if __fusions_exist( model ):
        raise ValueError( "Cannot find fusion points because fusion points for this model already exist. Did you mean to remove the existing fusions first?" )
    
    for event in find_fusion_events( model ):
        __LOG( "Processing fusion event: {}", event )
        event.points = []
        
        for component in model.components:
            for point in __find_fusion_points( event, component ):
                event.points.append( point )
        
        r.append( event )
    
    model.fusion_events = r


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
        first: MNode = graph.first_node
        root = first.add_parent()
        root.make_root()
        result = FusionPoint( fusion_event, component )
        root.data = result.event
        return [result]
    
    # The `intersection_aliases` correspond to βγδ in the above diagram
    
    
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
    isolation_points = graph.find_isolation_points( is_inside = lambda node: isinstance( node.data, LegoSequence ) and node.data in inside,
                                                    is_outside = lambda node: isinstance( node.data, LegoSequence ) and node.data in outside )
    
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
        
        genes = set( x.data for x in isolation_point.pure_inside_nodes if isinstance( x.data, LegoSequence ) )
        fusion_point = FusionPoint( fusion_event, component )
        fusion_node.data = fusion_point.event
        results.append( fusion_point )
    
    __LOG( "----{} results", len( results ) )
    
    return results
