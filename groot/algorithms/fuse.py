from typing import List, Set, Tuple

from groot.algorithms import consensus
from groot.data.graphing import MEdge, MGraph, MNode, IsolationError, IsolationPoint
from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence
from intermake.engine.environment import MCMD
from mhelper import Logger, array_helper


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
    
    
    def get_commensurate_points( self ) -> List[Tuple[IsolationPoint, IsolationPoint]]:
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
                        raise NotCommensurateError( "In the fusion point A there are multiple commensurate points in the B set. A = «{}», B = «{}».".format( point_a, self.points_b ) )
                    
                    results.append( (point_a, point_b) )
                    found = True
            
            if not found:
                raise NotCommensurateError( "In the fusion point A there is no commensurate point in the B set. A = «{}», B = «{}».".format( point_a, self.points_b ) )
        
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
    
    if model.fusion_events:
        raise ValueError( "Cannot find fusion points because fusion points for this model already exist. Did you mean to remove the existing fusions first?" )
    
    for event in find_fusion_events( model ):
        event.points_a = __get_fusion_points( event, event.component_a )
        event.points_b = __get_fusion_points( event, event.component_b )
        r.append( event )
    
    model.fusion_events = r


class FusionPoint:
    def __init__( self, node: int, direction_uid: int, event: FusionEvent, genes: Set[LegoSequence], component: LegoComponent, opposite_component: LegoComponent ):
        self.node_uid = node
        self.direction_uid = direction_uid
        self.opposite_component = opposite_component
        self.component = component
        self.event = event
        self.genes = genes
    
    
    @property
    def count( self ):
        return len( self.genes )
    
    
    def __repr__( self ):
        return "({})-AND-({})-FORM-({}):{}_GENES=[{}]".format( self.component,
                                                               self.opposite_component,
                                                               ",".join( sorted( str( x ) for x in self.event.intersections ) ),
                                                               self.count,
                                                               ",".join( sorted( str( x ) for x in self.genes ) ) )


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
            if node.fusion is not None:
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
    graph: MGraph = component.tree
    
    intersection_roots = fusion_event.intersections
    intersection_aliases = set()
    
    for intersection_root in intersection_roots:
        for intersection_alias in intersection_root.outgoing_components():
            intersection_aliases.add( intersection_alias )
    
    # Iterate over all the edges to make a list of `candidate` edges
    # - those separating βγδ from everything else
    isolation_points = graph.find_isolation_points( is_inside = lambda node: isinstance( node.data, LegoSequence ) and node.data.component in intersection_aliases,
                                                    is_outside = lambda node: isinstance( node.data, LegoSequence ) is not None and node.data.component not in intersection_aliases )
    
    results = []
    
    # Add the fusions to the graph
    
    # Replace the edge :              #
    #   Ⓧ───🅰───Ⓨ                   #
    #                                 #
    # with:                           #
    #   Ⓧ───🅱───Ⓐ───🅲───Ⓨ         #
    #                                 #
    for isolation_point in isolation_points:
        # Remove the existing edge
        isolation_point.edge.remove()
        
        # Create the fusion-point node
        fusion_node = MNode( graph )
        
        # Create the edges
        MEdge( graph, fusion_node, isolation_point.internal_node )
        MEdge( graph, fusion_node, isolation_point.external_node )
        
        genes = set( x.sequence for x in isolation_point.inside_nodes if x.sequence is not None )
        fusion_point = FusionPoint( fusion_node.uid,
                                    isolation_point.internal_node.uid,
                                    fusion_event,
                                    genes,
                                    component,
                                    fusion_event.component_a if (fusion_event.component_a is not component) else fusion_event.component_b )
        fusion_node.fusion = fusion_point
        results.append( fusion_point )
    
    return results


def create_nrfg( model: LegoModel ) -> None:
    """
    Creates the N-rooted fusion graph. Huzzah!
    The graph is saved to the model's appropriate field.
    
    :param model:   Model to create the graph for.
    """
    if model.nrfg is not None:
        raise ValueError( "The model's NRFG already exists. If your intention was to replace it you should remove the existing NRFG first." )
    
    ωψ = MGraph()
    
    for fusion_event in model.fusion_events:
        aψ = fusion_event.component_a.tree
        bψ = fusion_event.component_b.tree
        cψ = fusion_event.component_c.tree
        dψ = fusion_event.component_c.consensus
        
        # Iterate our commensurate points 
        # - Points that isolate the same sequences in both graphs
        # - Ideally there will just be one of these points, but there might be more if multiple fusion events occurred
        for aπ, bπ in fusion_event.get_commensurate_points():
            MCMD.progress( "PROCESSING {} SUBSET [ ({})--({}) ]".format( fusion_event, aπ, bπ ) )
            
            assert isinstance( aπ, FusionPoint )
            assert isinstance( bπ, FusionPoint )
            
            #  Get the genes isolated by the fusion
            genes = aπ.genes
            
            # Create our sub-graphs by cutting the original graph at these points
            # aΛ/bΛ/cΛ : The graphs excluding our genes
            # aΔ/bΔ/cΔ : The graphs including our genes 
            aΛ, aΔ = aψ.cut( aπ.node_uid, aπ.direction_uid )
            bΛ, bΔ = bψ.cut( bπ.node_uid, bπ.direction_uid )
            
            # Attempt to pull the same slice out of our consensus graph
            try:
                dΛ, dΔ = dψ.cut_at_isolation( is_inside = lambda node: isinstance( node.data, LegoSequence ) and node.data in genes,
                                              is_outside = lambda node: isinstance( node.data, LegoSequence ) and node.data not in genes )
            except IsolationError:
                # If they can't be pulled out we can still make a new consensus
                dΔ = __make_new_consensus( model, aΔ, bΔ, cψ, genes )
            
            aΛ.copy_into( ωψ )
            bΛ.copy_into( ωψ )
            dΔ.copy_into( ωψ )
            
            ωψ.add_edge( aπ.node_uid, aπ.direction_uid )
            ωψ.add_edge( bπ.node_uid, bπ.direction_uid )
    
    model.nrfg = ωψ


def __make_new_consensus( model, aΔ, bΔ, cψ, genes ):
    # Show a warning
    MCMD.warning( "Cannot pull the fused gene subset out of the consensus tree. I'm going to have to create a new consensus using just the fused gene subset." )
    
    # Attempt to make the same slice in our graph of the fused part only
    cΛ, cΔ = cψ.cut_at_isolation( is_inside = lambda node: isinstance( node.data, LegoSequence ) and node.data in genes,
                                  is_outside = lambda node: isinstance( node.data, LegoSequence ) and node.data not in genes )
    
    # Make a consensus of the three graphs
    dΔ = consensus.tree_consensus( model, (aΔ, bΔ, cΔ) )
    return dΔ
