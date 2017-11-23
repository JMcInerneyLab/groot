from typing import List

from ete3 import Tree

from groot.algorithms import external_tools
from groot.data.lego_model import LegoComponent
from groot.frontends import ete_providers
from intermake.engine.environment import MCMD


def consensus( component: LegoComponent ):
    if not component.tree:
        raise ValueError( "Trees not available. Cannot generate fusion, please generate trees first." )
    
    trees_list = []  # type: List[Tree]
    
    incoming = component.incoming_components()
    intersection = set( (x.accession for x in component.major_sequences()) )
    
    for i, component_b in enumerate( incoming ):
        newick = component_b.tree.to_newick()
        tree_b = ete_providers.tree_from_newick( newick )
        
        all_nodes = [x.name for x in tree_b.traverse() if x.name]
        
        intersection.intersection_update( set( all_nodes ) )
        
        trees_list.append( tree_b )
    
    FORMAT = 9
    
    component.consensus_intersection = intersection
    
    for tree_ in trees_list:
        assert isinstance( tree_, Tree )
        
        MCMD.print( "" )
        MCMD.print( "PRUNE: " + str( intersection ) )
        MCMD.print( "BEFORE PRUNE:" )
        MCMD.print( tree_.write( format = FORMAT ) )
        tree_.prune( intersection )
        MCMD.print( "AFTER PRUNE:" )
        MCMD.print( tree_.write( format = FORMAT ) )
    
    trees_text = "\n".join( (x.write( format = FORMAT ) for x in trees_list) )
    
    if not trees_text:
        raise ValueError( "Cannot perform consensus, trees are empty." )
    
    if len( trees_list ) != 1:
        component.consensus = external_tools.run_in_temporary( external_tools.consensus, trees_text )
    else:
        component.consensus = trees_text

def drop(component:LegoComponent):
    if component.consensus is not None:
        component.consensus = None
        return True
    
    return False