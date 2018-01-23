"""
Model for finding fusion events.
"""

from typing import List, Set

from groot.algorithms import graph_viewing
from groot.algorithms.classes import FusionEvent, FusionPoint, IFusion
from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence
from intermake.engine.environment import MCMD
from mgraph import MGraph, MNode
from mhelper import Logger, array_helper


__LOG = Logger( "fusion", True )


def find_fusion_events( model: LegoModel ) -> List[FusionEvent]:
    """
    Finds the fusion events in the model.
    i.e. Which components fuse together to generate which other components.
    """
    MCMD.autoquestion( "begin fusion" )
    results = []  # type: List[FusionEvent]
    index = 0
    
    for component_a, component_b in array_helper.triangular_comparison( model.components ):
        assert isinstance( component_a, LegoComponent )
        assert isinstance( component_b, LegoComponent )
        
        a_outgoing = set( component_a.outgoing_components() )
        b_outgoing = set( component_b.outgoing_components() )
        
        a_alone = a_outgoing - b_outgoing
        b_alone = b_outgoing - a_outgoing
        ab_ints = a_outgoing.intersection( b_outgoing )
        
        __LOG( "" )
        __LOG( "{} VS {}", component_a, component_b )
        __LOG( "A outg  {}", a_outgoing )
        __LOG( "B outg  {}", b_outgoing )
        __LOG( "A alone {}", a_alone )
        __LOG( "B alone {}", b_alone )
        __LOG( "AB toge {}", ab_ints )
        
        if a_outgoing == b_outgoing:
            results.append( FusionEvent( index, component_a, component_b, ab_ints ) )
            index += 1
    
    continue_ = True
    
    while continue_:
        continue_ = False
        
        for event in results:
            if len( event.intersections ) > 1:
                for event_b in results:
                    f = array_helper.first_or_none( event_b.intersections )
                    if len( event_b.intersections ) == 1 and f in event.intersections:
                        for component in (event_b.component_a, event_b.component_b):
                            if component in event.intersections:
                                event.intersections.remove( f )
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
        event.points_a = __get_fusion_points( True, event, event.component_a )
        event.points_b = __get_fusion_points( False, event, event.component_b )
        r.append( event )
    
    model.fusion_events = r


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
                assert node.num_edges() == 1
                
                # Remove the old node
                to_delete.append( node )
        
        for node in to_delete:
            node.remove_node()
        
        removed_count += len( to_delete )
    
    return removed_count


def __get_fusion_points( is_left: bool,
                         fusion_event: FusionEvent,
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
    
    __LOG( "--Processing event = {}, side = {}, component = {}, intersections = {}", fusion_event, "L" if is_left else "R", component, fusion_event.intersections )
    
    # Get the component tree
    # The `intersection_aliases` correspond to βγδ in the above diagram
    graph: MGraph = component.tree
    
    inside: Set[LegoSequence] = set()
    ignored: Set[LegoSequence] = set()
    
    for outgoing_component in fusion_event.intersections:  # intersections is what the event GOES TOWARDS (e.g. B in A --> B)
        inside.update( outgoing_component.major_sequences )
        ignored.update( outgoing_component.minor_sequences )
    
    ignored -= inside
    outside = [node.data for node in graph if isinstance( node.data, LegoSequence ) and node.data not in inside and node.data not in ignored]
    
    __LOG( "I WANT INSIDE  {}", inside )
    __LOG( "I WANT OUTSIDE {}", outside )
    __LOG( "I WANT IGNORED {}", ignored )  # TODO: not sure whether to have an ignored set makes any sense 
    
    # Iterate over all the edges to make a list of `candidate` edges
    # - those separating βγδ from everything else
    __LOG( graph.to_ascii( graph_viewing.create_user_formatter() ) )
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
        graph.add_edge( isolation_point.internal_node, fusion_node )
        
        genes = set( x.data for x in isolation_point.pure_inside_nodes if isinstance( x.data, LegoSequence ) )
        fusion_point = FusionPoint( is_left,
                                    fusion_node.uid,
                                    isolation_point.internal_node.uid,
                                    fusion_event,
                                    genes,
                                    component,
                                    fusion_event.component_a if (fusion_event.component_a is not component) else fusion_event.component_b )
        fusion_node.data = fusion_point.event
        results.append( fusion_point )
    
    __LOG( "----{} results", len( results ) )
    
    return results
