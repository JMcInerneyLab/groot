from typing import List, Iterable

from ete3 import Tree

from groot.algorithms import external_tools
from groot.data.graphing import MGraph
from groot.data.lego_model import LegoComponent, LegoModel
from groot.frontends import ete_providers
from intermake.engine.environment import MCMD


def consensus( component: LegoComponent ):
    if not component.tree:
        raise ValueError( "Trees not available. Cannot generate fusion, please generate trees first." )
    
    all_trees_ete = []  # type: List[Tree]
    
    incoming = component.incoming_components()
    intersection = set( (x.accession for x in component.major_sequences()) )
    
    for i, component_b in enumerate( incoming ):
        newick = component_b.tree.to_newick()
        tree_b = ete_providers.tree_from_newick( newick )
        
        all_nodes = [x.name for x in tree_b.traverse() if x.name]
        
        intersection.intersection_update( set( all_nodes ) )
        
        all_trees_ete.append( tree_b )
    
    FORMAT = 9
    
    component.consensus_intersection = intersection
    
    for ete_tree in all_trees_ete:
        assert isinstance( ete_tree, Tree )
        
        MCMD.print( "" )
        MCMD.print( "PRUNE: " + str( intersection ) )
        MCMD.print( "BEFORE PRUNE:" )
        MCMD.print( ete_tree.write( format = FORMAT ) )
        ete_tree.prune( intersection )
        MCMD.print( "AFTER PRUNE:" )
        MCMD.print( ete_tree.write( format = FORMAT ) )
    
    all_trees_newick = "\n".join( (x.write( format = FORMAT ) for x in all_trees_ete) )
    
    if not all_trees_newick:
        raise ValueError( "Cannot perform consensus, trees are empty." )
    
    if len( all_trees_ete ) != 1:
        consensus_newick = external_tools.run_in_temporary( external_tools.consensus, all_trees_newick )
    else:
        consensus_newick = all_trees_newick
    
    component.consensus = MGraph.from_newick( consensus_newick, component.model )


def tree_consensus( model: LegoModel, graphs: Iterable[MGraph] ) -> MGraph:
    newick = []
    
    for graph in graphs:
        newick.append( graph.to_newick() )
    
    consensus_newick = external_tools.run_in_temporary( external_tools.consensus, "\n".join( newick ) )
    
    return MGraph.from_newick( consensus_newick, model )


def drop( component: LegoComponent ):
    if component.consensus is not None:
        component.consensus = None
        return True
    
    return False
