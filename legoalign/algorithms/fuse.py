from typing import Set, List, Dict, Tuple, Iterable, cast

from collections import Counter

from legoalign.data.graphing import MGraph, MNode, MEdge
from legoalign.data.lego_model import LegoComponent, LegoModel, LegoSequence
from mcommand.engine.environment import MCMD
from mhelper import Logger, array_helper
from mhelper.component_helper import ComponentFinder


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
        self.points_a = None #type: List[ FusionPoint ]
        self.points_b = None #type: List[ FusionPoint ]
    
    
    def __str__( self ):
        intr = ", ".join( str( x ) for x in self.intersections )
        
        if self.orig_intersections != self.intersections:
            xintr = " ({})".format( "+".join( str( x ) for x in self.orig_intersections ) )
        else:
            xintr = ""
        
        return "{} ({} points) + {} ({} points) = {}{}".format( self.component_a, len( self.points_a ), self.component_b, len( self.points_b ), intr, xintr )


def find_fusion_events( model: LegoModel ) -> List[ FusionEvent ]:
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


def find_all_fusion_points( model: LegoModel ) -> None:
    """
    Finds the fusion points in the model.
    i.e. Given the events (see `find_events`), find the exact points at which the fusion(s) occur.
    """
    r = [ ]
    
    for event in find_fusion_events( model ):
        event.points_a = __get_fusion_points( event, event.component_a )
        event.points_b = __get_fusion_points( event, event.component_b )
        r.append( event )
    
    model.fusion_events = r
    
    return model.fusion_events


class FusionPoint:
    def __init__( self, node: MNode, event: FusionEvent, count: int, component: LegoComponent, opposite_component: LegoComponent ):
        self.node = node
        self.opposite_component = opposite_component
        self.component = component
        self.event = event
        self.count = count


class _FusionPointCandidate:
    def __init__( self, edge: MEdge, node_1: MNode, node_2: MNode, count ):
        self.edge = edge
        self.node_a = node_1
        self.node_b = node_2
        self.count = count


def __get_fusion_points( fusion_event: FusionEvent,
                         component: LegoComponent ) -> List[ FusionPoint ]:
    """
    In the tree of `component` we look for the node separating the event's intersections from everything else.
    """
    graph = component.tree
    
    for node in graph.get_nodes():
        if node.fusion is not None:
            if node.fusion.event.component_a == fusion_event.component_a and node.fusion.event.component_b == fusion_event.component_b:
                node.fusion = None
    
    lower = fusion_event.intersections
    subset = set()
    
    for x in lower:
        for y in x.outgoing_components():
            subset.add( y )
    
    fusions = cast( List[ _FusionPointCandidate ], [ ] )
    
    for edge in graph.get_edges():
        for node in (edge.a, edge.b):
            relations = node.follow( exclude_edges = [ edge ] )
            count = 0
            
            for relative in relations:
                if relative.sequence is not None:
                    count += 1
                    
                    if relative.sequence.component not in subset:
                        count = 0
                        break
            
            if count == 0:
                continue
            
            fusions.append( _FusionPointCandidate( edge, node, edge.opposite( node ), count ) )
    
    comp = ComponentFinder()
    
    for fp1 in fusions:
        for fp2 in fusions:
            if fp1.node_a is fp2.node_a or fp1.node_b is fp2.node_a:
                comp.equate( fp1, fp2 )
    
    fusions_refined = [ ]  # type: List[_FusionPointCandidate]
    
    for component_ in comp.tabulate():  # type: List[_FusionPointCandidate]
        fusions_refined.append( max( component_, key = lambda x: x.count ) )
    
    results = [ ]
    
    for fusion in fusions_refined:
        if fusion.node_a.num_edges() == 2:
            fusion_node = fusion.node_a
        elif fusion.node_b.num_edges() == 2:
            fusion_node = fusion.node_b
        else:
            fusion_node = MNode( graph )
            
            MEdge( graph, fusion_node, fusion.node_a )
            MEdge( graph, fusion_node, fusion.node_b )
            
            fusion.edge.remove()
        
        fusion = FusionPoint( fusion_node, fusion_event, fusion.count, component, fusion_event.component_a if (fusion_event.component_a is not component) else fusion_event.component_b )
        fusion_node.fusion_comment = fusion
        results.append( fusion )
    
    return results


def create_nrfg( model: LegoModel ) -> MGraph:
    result = MGraph()
    
    lookup_table = cast( Dict[ MNode, MNode ], { } )
    
    for c in model.components:
        lookup_table.update( result.import_graph( c.tree ) )
    
    for fe in model.fusion_events:
        join = [ lookup_table[ x.node ] for x in fe.points_a + fe.points_b ]
        
        if len( join ) == 2:
            MEdge( result, join[ 0 ], join[ 1 ] )
        else:
            centre = MNode( result )
            
            for x in join:
                MEdge( result, centre, x )
                
    return result
