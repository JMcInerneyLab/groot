from typing import Dict, List, Set, cast, Sequence
from groot.data.graphing import MEdge, MGraph, MNode, FollowParams
from groot.data.lego_model import LegoComponent, LegoModel
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
    
    
    def __init__( self, component_a: LegoComponent, component_b: LegoComponent, intersections: Set[LegoComponent] ):
        self.component_a: LegoComponent = component_a
        self.component_b: LegoComponent = component_b
        self.intersections: Set[LegoComponent] = intersections
        self.orig_intersections: Set[LegoComponent] = set( intersections )
        self.points_a: List[FusionPoint] = None
        self.points_b: List[FusionPoint] = None
    
    
    def __str__( self ):
        intersections = ", ".join( x.__str__() for x in self.intersections )
        return "{} COMBINES WITH {} TO FORM {}".format( self.component_a, self.component_b, intersections )


def find_fusion_events( model: LegoModel ) -> List[FusionEvent]:
    """
    Finds the fusion events in the model.
    i.e. Which components fuse together to generate which other components.
    """
    results = []  # type: List[FusionEvent]
    
    for i, a in enumerate( model.components ):
        for b in model.components[i + 1:]:
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
    r: List[FusionEvent] = []
    
    for event in find_fusion_events( model ):
        event.points_a = __get_fusion_points( event, event.component_a )
        event.points_b = __get_fusion_points( event, event.component_b )
        r.append( event )
    
    model.fusion_events = r


class FusionPoint:
    def __init__( self, node: MNode, event: FusionEvent, count: int, component: LegoComponent, opposite_component: LegoComponent ):
        self.node = node
        self.opposite_component = opposite_component
        self.component = component
        self.event = event
        self.count = count
    
    
    def __str__( self ):
        return "EVENT JOINING {} GENES IN {} TO {}".format( self.count, self.component, self.opposite_component )


class _FusionPointCandidate:
    def __init__( self, edge: MEdge, node_1: MNode, node_2: MNode, count: int ) -> None:
        self.edge: MEdge = edge
        self.node_a: MNode = node_1
        self.node_b: MNode = node_2
        self.count: int = count


def __get_fusion_points( fusion_event: FusionEvent,
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
    graph = component.tree
    
    intersection_roots = fusion_event.intersections
    intersection_aliases = set()
    
    for intersection_root in intersection_roots:
        for intersection_alias in intersection_root.outgoing_components():
            intersection_aliases.add( intersection_alias )
    
    # Iterate over all the edges to make a list of `candidate` edges
    # - those separating βγδ from everything else
    candidates: List[_FusionPointCandidate] = []
    
    for edge in graph.get_edges():
        for node in cast( Sequence[MNode], (edge.a, edge.b) ):
            params = FollowParams( root = node, exclude_edges = [edge] )
            graph.follow( params )
            count = 0
            
            # Count the number of fusion sequences in the subgraph
            for relative in params.visited_nodes:
                if relative.sequence is not None:
                    count += 1
                    
                    if relative.sequence.component not in intersection_aliases:
                        # Fusion sequence are not alone - disregard
                        count = 0
                        break
            
            if count != 0:
                candidates.append( _FusionPointCandidate( edge, node, edge.opposite( node ), count ) )
    
    # Connected candidates (such as 1,2,3 in the diagram above) need to be reduced to just the one encompassing them all
    # - To do this, make a CC set of the candidates
    cc_finder = ComponentFinder()
    
    for candidate_1 in candidates:
        for candidate_2 in candidates:
            if candidate_1.node_a is candidate_2.node_a or candidate_1.node_b is candidate_2.node_a:
                cc_finder.join( candidate_1, candidate_2 )
    
    # - Now for each CC, just use the candidate encompassing the most composites
    fusions_refined = []  # type: List[_FusionPointCandidate]
    
    for component_ in cc_finder.tabulate():  # type: List[_FusionPointCandidate]
        fusions_refined.append( max( component_, key = lambda x: x.count ) )
    
    results = []
    
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
    
    lookup_table: Dict[MNode, MNode] = { }
    
    for c in model.components:
        lookup_table.update( result.import_graph( c.tree ) )
    
    for fe in model.fusion_events:
        join = [lookup_table[x.node] for x in fe.points_a + fe.points_b]
        
        if len( join ) == 2:
            MEdge( result, join[0], join[1] )
        else:
            centre = MNode( result )
            
            for x in join:
                MEdge( result, centre, x )
    
    return result
