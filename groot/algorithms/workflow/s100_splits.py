from groot import Component, constants
from intermake import MCMD, command
from mgraph import MGraph, MSplit, exporting
from mhelper import Logger
from typing import Dict, Optional

from groot.constants import STAGES, EChanges
from groot.data import INode, Model, Split, global_view
from groot.utilities import lego_graph


__LOG_SPLITS = Logger( "nrfg.splits", False )
__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME

@command(folder = constants.F_CREATE)
def create_splits(  ):
    """
    Creates the candidate splits.
    
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

    Requisites: `create_fusions`
    """
    model: Model   =global_view.current_model()
    
    # Status check
    model.get_status( STAGES.SPLITS_8 ).assert_create()
    
    all_splits: Dict[MSplit, Split] = { }
    
    for component in model.components:
        __LOG_SPLITS( "FOR COMPONENT {}", component )
        
        tree: MGraph = component.tree
        tree.any_root.make_root()  # ensure root is root-like
        
        component_sequences = lego_graph.get_ileaf_data( tree.get_nodes() )
        
        # Split the tree, `ILeaf` is a strange definition of a "leaf", since we'll pull out clades too (`LegoPoint`s).
        # We fix this when we reconstruct the NRFG.
        component_splits = exporting.export_splits( tree, filter = lambda x: isinstance( x.data, INode ) )
        component_splits_r = []
        
        for split in component_splits:
            __LOG_SPLITS( "---- FOUND SPLIT {}", str( split ) )
            
            exi = all_splits.get( split )
            
            if exi is None:
                exi = Split( split, len( all_splits ) )
                all_splits[split] = exi
            
            exi.components.add( component )
            component_splits_r.append( exi )
        
        component.splits = frozenset( component_splits_r )
        component.leaves = frozenset( component_sequences )
    
    model.splits = frozenset( all_splits.values() )
    
    return EChanges.MODEL_DATA
    
@command(folder = constants.F_DROP)
def drop_splits( ):
    """
    Removes data from the model.
    """
    model: Model   =global_view.current_model()
    model.get_status( STAGES.SPLITS_8 ).assert_drop()
    
    model.splits = frozenset()
    
    for component in model.components:
        component.splits = None
        component.leaves = None
        
    return EChanges.COMP_DATA


@command( names = ["print_splits", "splits"], folder=constants.F_PRINT )
def print_splits( component: Optional[Component] = None ) -> EChanges:
    """
    Prints NRFG candidate splits.
    :param component:   Component, or `None` for the global split set.
    """
    model = global_view.current_model()
    
    if component:
        for x in component.splits:
            MCMD.information( str( x ) )
    else:
        for x in model.splits:
            MCMD.information( str( x ) )
    
    return EChanges.INFORMATION