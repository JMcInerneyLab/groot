from typing import Dict, List, Set, cast, Sequence, Iterator, Tuple
from groot.data.graphing import MEdge, MGraph, MNode, FollowParams
from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence
from mhelper import Logger, array_helper
from mhelper.component_helper import ComponentFinder


__LOG = Logger( "fusion", False )


class NotCommensurateError( Exception ):
    pass


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
    
    
    def get_commensurate_points( self ) -> List[Tuple[FusionPoint, FusionPoint]]:
        """
        Gets tuples of points that look like they are commensurate, or raises a `NotCommensurateError`. 
        """
        if len( self.points_a ) != len( self.points_b ):
            raise NotCommensurateError( "The two sets of fusion points for this event are not the same length, so at least one will be non-commensurate.".format( len( self.points_a ), len( self.points_b ) ) )
        
        results = []
        
        for point_a in self.points_a:
            found = False
            
            for point_b in self.points_b:
                if point_a.genes == point_b.genes:
                    if found:
                        raise NotCommensurateError( "In the fusion point A «{}» there are multiple commensurate points in the B set «{}».".format( point_a, self.points_b ) )
                    
                    results.append( (point_a, point_b) )
                    found = True
            
            if not found:
                raise NotCommensurateError( "In the fusion point A «{}» there is no commensurate point in the B set «{}».".format( point_a, self.points_b ) )
        
        return results
    
    
    @property
    def component_c( self ) -> LegoComponent:
        return array_helper.extract_single_item_or_error( self.intersections )
    
    
    def __str__( self ) -> str:
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
    
    remove_fusions( model )
    
    for event in find_fusion_events( model ):
        event.points_a = __get_fusion_points( event, event.component_a )
        event.points_b = __get_fusion_points( event, event.component_b )
        r.append( event )
    
    model.fusion_events = r


class FusionPoint:
    def __init__( self, node: MNode, direction: MNode, event: FusionEvent, genes: List[LegoSequence], component: LegoComponent, opposite_component: LegoComponent ):
        self.node = node
        self.direction = direction
        self.opposite_component = opposite_component
        self.component = component
        self.event = event
        self.genes = genes
    
    
    @property
    def count( self ):
        return len( self.genes )
    
    
    def __str__( self ):
        return "EVENT JOINING {} GENES IN {} TO {} FORMING {} : {}".format( self.count, self.component, self.opposite_component, ", ".join( sorted( str( x ) for x in self.event.intersections ) ), ", ".join( sorted( str( x ) for x in self.genes ) ) )


class _FusionPointCandidate:
    def __init__( self, edge: MEdge, node_1: MNode, node_2: MNode, genes: List[LegoSequence] ) -> None:
        self.edge: MEdge = edge
        self.node_a: MNode = node_1
        self.node_b: MNode = node_2
        self.genes: List[LegoSequence] = genes
    
    
    @property
    def count( self ):
        return len( self.genes )


def remove_fusions( model: LegoModel ) -> int:
    """
    Removes all fusion points from the specified component.
    """
    removed_count = 0
    
    model.fusion_events.clear()
    
    for component in model.components:
        graph = component.tree
        to_delete: List[MNode] = []
        
        for node in graph.get_nodes():
            if node.fusion_comment is not None:
                assert node.num_edges() == 2
                edges = list( node.iter_edges() )
                
                d1 = edges[0].opposite( node )
                d2 = edges[1].opposite( node )
                
                # Create the new edge
                MEdge( graph, d1, d2 )
                
                # Remove the old node
                to_delete.append( node )
        
        for node in to_delete:
            node.remove()
        
        removed_count += len( to_delete )
    
    return removed_count


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
            count = []
            
            # Count the number of fusion sequences in the subgraph
            for relative in params.visited_nodes:
                if relative.sequence is not None:
                    count.append( relative.sequence )
                    
                    if relative.sequence.component not in intersection_aliases:
                        # Fusion sequence are not alone - disregard
                        count.clear()
                        break
            
            if count:
                candidates.append( _FusionPointCandidate( edge, node, edge.opposite( node ), count ) )
    
    # Connected candidates (such as 1,2,3 in the diagram above) need to be reduced to just the one encompassing them all
    # - To do this, make a CC set of the candidates
    cc_finder = ComponentFinder()
    
    for candidate_1 in candidates:
        for candidate_2 in candidates:
            if candidate_1.node_a is candidate_2.node_a or candidate_1.node_b is candidate_2.node_a:
                cc_finder.join( candidate_1, candidate_2 )
    
    # - Now for each CC, just use the candidate encompassing the most composites
    fusions_refined: List[_FusionPointCandidate] = []
    tabulation: List[List[_FusionPointCandidate]] = cc_finder.tabulate()
    
    for component_ in tabulation:
        fusions_refined.append( max( component_, key = lambda x: x.count ) )
    
    results = []
    
    # Add the fusions to the graph
    
    # Replace the edge :              #
    #   Ⓧ───🅰───Ⓨ                   #
    #                                 #
    # with:                           #
    #   Ⓧ───🅱───Ⓐ───🅲───Ⓨ         #
    #                                 #
    for fusion in fusions_refined:
        # Remove the existing edge
        fusion.edge.remove()
        
        # Create the fusion-point node
        fusion_node = MNode( graph )
        
        # Create the edges
        MEdge( graph, fusion_node, fusion.node_a )
        MEdge( graph, fusion_node, fusion.node_b )
        
        fusion = FusionPoint( fusion_node, fusion.node_a, fusion_event, fusion.genes, component, fusion_event.component_a if (fusion_event.component_a is not component) else fusion_event.component_b )
        fusion_node.fusion_comment = fusion
        results.append( fusion )
    
    return results


def create_nrfg( model: LegoModel ) -> MGraph:
    """
    Creates the N-rooted fusion graph. Huzzah!
    
    :param model:   Model to create the graph for.
    """
    result = MGraph()
    
    for fusion_event in model.fusion_events:
        a = fusion_event.component_a.tree
        b = fusion_event.component_b.tree
        c = fusion_event.component_c.tree
        
        for point_a, point_b in fusion_event.get_commensurate_points():
            genes = point_a.genes
            aʹ, ca = a.cut( point_a.node, point_a.direction )
            bʹ, cb = b.cut( point_b.node, point_b.direction )
            cs = c.slice( genes )
            
            cʹ = MGraph.consensus( (ca, cb, cs) )
            
            result.incorporate( aʹ )
            result.incorporate( bʹ )
            result.incorporate( cʹ )
            
            MEdge( result, result.find_node( point_a.node ), result.find_node( point_a.direction ) )
            MEdge( result, result.find_node( point_b.node ), result.find_node( point_b.direction ) )
    
    return result
