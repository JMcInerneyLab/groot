from typing import Iterable, List

from ete3 import Tree

from groot.algorithms import external_tools, graph_viewing
from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence
from groot.frontends import ete_providers
from groot.graphing.graphing import MGraph, MNode
from mhelper import ByRef, array_helper


def consensus( component: LegoComponent ):
    """
    Generates the consensus tree for a component.
    """
    if not component.tree:
        raise ValueError( "Trees not available. Cannot generate fusion, please generate trees first." )
    
    if component.consensus:
        raise ValueError( "Refusing to generate a consensus because a consensus for this component already exists. Did you mean to drop the existing consensus first?" )
    
    # Get the IDs of of the genes we need the consensus for (`major_gene_ids`)
    all_trees_ete = []  # type: List[Tree]
    major_gene_ids = set( (x.id for x in component.major_sequences()) )
    
    for incoming_component in component.incoming_components():
        incoming_newick = incoming_component.tree.to_newick( graph_viewing.FORMATTER.prefixed_sequence_internal_id )
        incoming_tree = ete_providers.tree_from_newick( incoming_newick )
        incoming_genes = [λnode.data.id for λnode in incoming_component.tree.nodes if isinstance( λnode.data, LegoSequence )]
        
        major_gene_ids.intersection_update( set( incoming_genes ) )
        
        all_trees_ete.append( incoming_tree )
    
    component.consensus_intersection = major_gene_ids
    
    for ete_tree in all_trees_ete:
        assert isinstance( ete_tree, Tree )
        ete_tree.prune( [str( x ) for x in major_gene_ids] )
    
    all_trees_newick = "\n".join( (x.write( format = 9 ) for x in all_trees_ete) )
    
    if not all_trees_newick:
        raise ValueError( "Cannot perform consensus, trees are empty." )
    
    if len( all_trees_ete ) != 1:
        consensus_newick = external_tools.run_in_temporary( external_tools.consensus, all_trees_newick )
    else:
        consensus_newick = all_trees_newick
    
    component.consensus = MGraph.from_newick( consensus_newick, component.model )


def tree_consensus( model: LegoModel, graphs: Iterable[MGraph] ) -> (MGraph, MNode):
    """
    Generates a consensus tree.
    """
    newick = []
    
    for a, b in array_helper.lagged_iterate( graphs ):
        aa = set( x.data for x in a.nodes if isinstance( x.data, LegoSequence ) )
        bb = set( x.data for x in b.nodes if isinstance( x.data, LegoSequence ) )
        
        if aa != bb:
            raise ValueError( "Refusing to generate a consensus because the sets of at least two of the graphs are dissimilar. First set = «{}», second set = «{}», difference = «{}».".format( aa, bb, aa.difference( bb ) ) )
    
    for graph in graphs:
        aa = set( x for x in graph.nodes if isinstance( x.data, LegoSequence ) )
        
        if not aa:
            raise ValueError( "Refusing to generate a consensus because at least one graph has no sequence data: {}".format( graph ) )
        
        newick.append( graph.to_newick( graph_viewing.FORMATTER.prefixed_sequence_internal_id ) )
    
    consensus_newick = external_tools.run_in_temporary( external_tools.consensus, "\n".join( newick ) + "\n" )
    
    root_ref = ByRef[MNode]( None )
    result = MGraph.from_newick( consensus_newick, model, root_ref )
    return result, root_ref.value


def drop( component: LegoComponent ):
    if component.model.nrfg:
        raise ValueError( "Refusing to drop consensus because they may be in use by the NRFG. Did you mean to drop the NRFG first?" )
    
    if component.consensus is not None:
        component.consensus = None
        component.consensus_intersection = None
        return True
    
    return False
