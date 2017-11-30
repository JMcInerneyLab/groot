from typing import List

from groot.algorithms import consensus, graph_viewing
from groot.algorithms.classes import FusionEvent, FusionPoint, Nrfg, NrfgEvent
from groot.data.graphing import IsolationError, MEdge, MGraph, MNode
from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence
from intermake.engine.environment import MCMD
from mhelper import Logger, array_helper


__LOG = Logger( "fusion", False )


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
                                                    is_outside = lambda node: isinstance( node.data, LegoSequence ) and node.data.component not in intersection_aliases )
    
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
        
        genes = set( x.data for x in isolation_point.inside_nodes if isinstance( x.data, LegoSequence ) )
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
    
    zψ = MGraph()
    details = []
    
    for event in model.fusion_events:
        MCMD.information( "Processing event: {}".format( event ) )
        aψ = event.component_a.tree
        bψ = event.component_b.tree
        cψ = event.component_c.tree
        
        # Iterate our commensurate points 
        # - Points that isolate the same sequences in both graphs
        # - Ideally there will just be one of these points, but there might be more if multiple fusion events occurred
        for aπ, bπ in event.get_commensurate_points():
            MCMD.progress( "Fusing commensurate points: ({})--({})".format( aπ, bπ ) )
            
            assert isinstance( aπ, FusionPoint )
            assert isinstance( bπ, FusionPoint )
            
            #  Get the genes isolated by the fusion
            genes = aπ.genes
            
            # Create our sub-graphs by cutting the original graph at these points
            # aΛ/bΛ/cΛ : The graphs excluding our genes
            # aΔ/bΔ/cΔ : The graphs including our genes
            MCMD.progress( "Cutting out A: {} | {}".format( aπ.node_uid, aπ.direction_uid ) )
            MCMD.progress( aψ.to_ascii( graph_viewing.create_user_formatter( "[uid]" ) ) )
            aΛ, aΔ = aψ.cut( aπ.node_uid, aπ.direction_uid )
            
            MCMD.progress( "Cutting out B" )
            bΛ, bΔ = bψ.cut( bπ.node_uid, bπ.direction_uid )
            
            # Make consensus of our three trees
            dΔ = __make_new_consensus( model, aΔ, bΔ, cψ, genes )
            
            MCMD.progress( "Copying A, B, C into Z" )
            aΛ.copy_into( zψ )
            bΛ.copy_into( zψ )
            dΔ.copy_into( zψ )
            
            MCMD.progress( "Creating edges in Z" )
            zψ.add_edge( aπ.node_uid, aπ.direction_uid )
            zψ.add_edge( bπ.node_uid, bπ.direction_uid )
            
            details.append( NrfgEvent( event, aπ, bπ, aΛ, aΔ, bΛ, bΔ, dΔ ) )
    
    MCMD.progress( "Returning Z" )
    model.nrfg = Nrfg( zψ, details )


def __make_new_consensus( model, aΔ, bΔ, cψ, genes ):
    # Attempt to make the same slice in our graph of the fused part only
    MCMD.progress( "Isolating and cutting C" )
    cΛ, cΔ = cψ.cut_at_isolation( is_inside = lambda node: isinstance( node.data, LegoSequence ) and node.data in genes,
                                  is_outside = lambda node: isinstance( node.data, LegoSequence ) and node.data not in genes )
    
    # Make a consensus of the three graphs
    MCMD.progress( "Making consensus" )
    dΔ = consensus.tree_consensus( model, (aΔ, bΔ, cΔ) )
    return dΔ
