from typing import Set, List, Dict, Tuple, Iterable

from legoalign.data.graphing import MGraph, MNode
from legoalign.data.lego_model import LegoComponent, LegoModel, LegoSequence
from mhelper import Logger, array_helper


__LOG = Logger( "fusion", False )


class FusionEvent:
    """
    Describes a fusion event
    
    :data component_a:          First component
    :data component_b:          Second component
    :data intersections:        Generated component (root)
    :data orig_intersections:   Generated component (all possibilities)
    :data point_a:              The name of the node on the first component which the fusion occurs
    :data point_b:              The name of the node on the second component which the fusion occurs
    """
    
    
    def __init__( self, component_a: LegoComponent, component_b: LegoComponent, intersections: Set[ LegoComponent ] ):
        self.component_a = component_a
        self.component_b = component_b
        self.intersections = intersections
        self.orig_intersections = set( intersections )
        self.points_a = None
        self.points_b = None
    
    
    def __str__( self ):
        if self.orig_intersections == self.intersections:
            return "In the trees of {} and {} I can see the fusion into {}.".format( self.component_a, self.component_b, ", ".join( str( x ) for x in self.intersections ) )
        else:
            return "In the trees of {} and {} I can see the fusion into {} ({}).".format( self.component_a, self.component_b, ", ".join( str( x ) for x in self.intersections ), "+".join( str( x ) for x in self.orig_intersections ) )


def find_events( model: LegoModel ) -> List[ FusionEvent ]:
    """
    Finds the fusion events in the model.
    i.e. Which components fuse together to generate which other components.
    """
    results = [ ]  # type: List[FusionEvent]
    
    for i, a in enumerate( model.components ):
        for b in model.components[ i + 1: ]:
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
                results.append( FusionEvent( a, b, ab_ints ) )
    
    continue_ = True
    
    while continue_:
        continue_ = False
        
        for event in results:
            if len( event.intersections ) > 1:
                for event_b in results:
                    f = array_helper.first( event_b.intersections )
                    if len( event_b.intersections ) == 1 and f in event.intersections:
                        for component in (event_b.component_a, event_b.component_b):
                            if component in event.intersections:
                                event.intersections.remove( f )
                                continue_ = True
    
    return results


def find_points( model: LegoModel ) -> List[FusionEvent]:
    """
    Finds the fusion points in the model.
    i.e. Given the events (see `find_events`), find the exact points at which the fusion(s) occur.
    
    """
    r = []
    
    for event in find_events( model ):
        event.points_a = __find_point( event.component_a, event.orig_intersections, array_helper.first( event.intersections ) )
        event.points_b = __find_point( event.component_b, event.orig_intersections, array_helper.first( event.intersections ) )
        r.append(event)
        
    return r


def __find_point( component: LegoComponent,
                  lower: Set[ LegoComponent ],
                  fusion_name: LegoComponent ) -> List[MNode]:
    """
    In the tree of `component` we look for the node separating `lower` from everything else.
    If there are multiple nodes, we consider the best match
    
    :param component:   Component who's tree to search 
    :param lower:       What to search for 
    :param fusion_name: Name of the fusion
    :return: 
    """
    model = component.model
    graph = MGraph()
    graph.import_newick( component.tree, model )
    all_nodes = list(graph.traverse())
    
    viables = { }  # type: Dict[MNode, Tuple[Set[MNode], int]]
    
    for node in all_nodes:
        for edge_1 in node.iter_edges():
            relations = node.follow( exclude = [ edge_1 ] )
            components, count = __get_components( relations )
            
            if component in relations:
                components.remove( component )
            
            if all( x in lower for x in components ):
                contender = edge_1.opposite( node )
                contention, contention_count = (viables.get( contender ) or (None, None))
                
                if contention is not None:
                    if count < contention_count:
                        continue
                    elif count > contention_count:
                        del viables[ contender ]
                    elif len( relations ) > len( contention ):
                        continue
                    else:
                        del viables[ contender ]
                
                viables[ node ] = relations, count
    
    for viable in viables:
        viable.sequence = fusion_name
    
    component.tree = graph.to_newick()
    
    return list( viables.keys() )


def __get_components( nodes: Iterable[ MNode ] ) -> Tuple[ Set[ LegoComponent ], int ]:
    r = set()
    count = 0
    
    for n in nodes:
        if isinstance( n.sequence, LegoSequence ):
            r.add( n.sequence.component )
            count += 1
    
    return r, count

