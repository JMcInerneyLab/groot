from typing import Dict

from groot.constants import STAGES
from groot.data import LegoModel, LegoSplit, ILegoNode
from groot.utilities import lego_graph
from mgraph import Split, MGraph, exporting
from mhelper import Logger


__LOG_SPLITS = Logger( "nrfg.splits", False )

def drop_splits( model: LegoModel ):
    model.get_status( STAGES.SPLITS_8 ).assert_drop()
    
    model.splits = frozenset()
    
    for component in model.components:
        component.splits = None
        component.leaves = None


def create_splits( model: LegoModel ):
    """
    NRFG Stage I.
    
    Collects the splits present in the component trees.

    :remarks:
    --------------------------------------------------------------------------------------------------------------    
    | Some of our graphs may have contradictory information.                                                     |
    | To resolve this we perform a consensus.                                                                    |
    | We define all the graphs by their splits, then see whether the splits are supported by the majority.       |
    |                                                                                                            |
    | A couple of implementation notes:                                                                          |
    | 1. I've not used the most efficient algorithm, however this is fast enough for the purpose and it is much  |
    |    easier to explain what we're doing. For a fast algorithm see Jansson 2013, which runs in O(nk) time.    |
    | 2. We're calculating much more data than we need to, since we only reconstruct the subsets of the graphs   |
    |    pertinent to the domains of the composite gene. However, again, this allows us to get the consensus     |
    |    stuff out of the way early so we can perform the more relevant composite stage independent from the     |
    |    consensus.                                                                                              |
    --------------------------------------------------------------------------------------------------------------
    
    :param model:   Model to find the components in
    :return:        Tuple of:
                        1. Set of splits
                        2. Dictionary of:
                            K. Component
                            V. Tuple of:
                                1. Splits for this component
                                2. Leaves for this component
    """
    
    # Status check
    model.get_status( STAGES.SPLITS_8 ).assert_create()
    
    all_splits: Dict[Split, LegoSplit] = { }
    
    for component in model.components:
        __LOG_SPLITS( "FOR COMPONENT {}", component )
        
        tree: MGraph = component.tree
        tree.any_root.make_root()  # ensure root is root-like
        
        component_sequences = lego_graph.get_ileaf_data( tree.get_nodes() )
        
        # Split the tree, `ILeaf` is a strange definition of a "leaf", since we'll pull out clades too (`FusionPoint`s).
        # We fix this when we reconstruct the NRFG.
        component_splits = exporting.export_splits( tree, filter = lambda x: isinstance( x.data, ILegoNode ) )
        component_splits_r = []
        
        for split in component_splits:
            __LOG_SPLITS( "---- FOUND SPLIT {}", str( split ) )
            
            exi = all_splits.get( split )
            
            if exi is None:
                exi = LegoSplit( split, len( all_splits ) )
                all_splits[split] = exi
            
            exi.components.add( component )
            component_splits_r.append( exi )
        
        component.splits = frozenset( component_splits_r )
        component.leaves = frozenset( component_sequences )
    
    model.splits = frozenset( all_splits.values() )