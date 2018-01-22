"""
Model for finding fusion events.
"""

from typing import List, Set
from mgraph import MEdge, MGraph, MNode
from mhelper import Logger, array_helper

from groot.algorithms.classes import FusionEvent, FusionPoint
from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence


__LOG = Logger( "fusion", False )


def find_fusion_events( model: LegoModel ) -> List[FusionEvent]:
    """
    Finds the fusion events in the model.
    i.e. Which components fuse together to generate which other components.
    """ 
    results = []  # type: List[FusionEvent]
    index=0
    
    for a, b in array_helper.triangular_comparison(model.components):
        a_comps = set( a.outgoing_components() )
        b_comps = set( b.outgoing_components() )
        
        a_alone = a_comps - b_comps
        b_alone = b_comps - a_comps
        ab_ints = a_comps.intersection( b_comps )
        
        __LOG( "" )
        __LOG( "{} {}".format( a, b ) )
        __LOG( "A       {}".format( a_comps ) )
        __LOG( "B       {}".format( b_comps ) )
        __LOG( "A alone {}".format( a_alone ) )
        __LOG( "B alone {}".format( b_alone ) )
        __LOG( "AB toge {}".format( ab_ints ) )
        
        if len( a_alone ) == 1 and len( b_alone ) == 1 and len( ab_ints ) >= 1:
            results.append( FusionEvent( index, a, b, ab_ints ) )
            index+=1
    
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


def find_all_fusion_points( model: LegoModel ) -> None:
    """
    Finds the fusion points in the model.
    i.e. Given the events (see `find_events`), find the exact points at which the fusion(s) occur.
    """
    r: List[FusionEvent] = []
    
    if model.fusion_events:
        raise ValueError( "Cannot find fusion points because fusion points for this model already exist. Did you mean to remove the existing fusions first?" )
    
    for event in find_fusion_events( model ):
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
            if isinstance( node.data, FusionPoint ):
                assert node.num_edges() == 1
                
                # Remove the old node
                to_delete.append( node )
        
        for node in to_delete:
            node.remove_node()
        
        removed_count += len( to_delete )
    
    return removed_count


def __get_fusion_points( is_left:bool,
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
    
    # Get the component tree
    # The `intersection_aliases` correspond to βγδ in the above diagram
    graph: MGraph = component.tree
    
    intersection_roots: Set[LegoComponent] = fusion_event.intersections
    intersection_aliases: Set[LegoComponent] = set()
    
    for intersection_root in intersection_roots:
        for intersection_alias in intersection_root.outgoing_components():
            intersection_aliases.add( intersection_alias )
    
    # Iterate over all the edges to make a list of `candidate` edges
    # - those separating βγδ from everything else
    isolation_points = graph.find_isolation_points( is_inside = lambda node: isinstance( node.data, LegoSequence ) and any( (node.data in x.major_sequences) for x in intersection_aliases ),
                                                    is_outside = lambda node: isinstance( node.data, LegoSequence ) and not any( (node.data in x.major_sequences) for x in intersection_aliases ) )
    
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
        
        genes = set( x.data for x in isolation_point.inside_nodes if isinstance( x.data, LegoSequence ) )
        fusion_point = FusionPoint( is_left,
                                    fusion_node.uid,
                                    isolation_point.internal_node.uid,
                                    fusion_event,
                                    genes,
                                    component,
                                    fusion_event.component_a if (fusion_event.component_a is not component) else fusion_event.component_b )
        fusion_node.data = fusion_point
        results.append( fusion_point )
    
    return results
