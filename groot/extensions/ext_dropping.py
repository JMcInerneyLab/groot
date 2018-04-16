from typing import List, Optional
from intermake import command, MCMD

from groot import algorithms
from groot.data import global_view, LegoSequence, LegoComponent, INamedGraph, FixedUserGraph
from groot.utilities import cli_view_utils
from groot.frontends.gui.gui_view_utils import EChanges


__mcmd_folder_name__ = "Removing"


@command()
def drop_graph( graph: INamedGraph ):
    """
    Removes a graph created with `import_graph`.
    :param graph:   Graph to remove. See `format_help`.
    """
    model = global_view.current_model()
    
    if not isinstance(graph, FixedUserGraph):
        raise ValueError( "The specified graph is not a user-graph and cannot be removed. Please specify an _existing_ user-graph." )
    
    model.user_graphs.remove( graph )


@command()
def drop_sequences( sequences: List[LegoSequence] ):
    """
    Removes one or more sequences from the model.
    
    !THIS ACTION CANNOT BE UNDONE!
    YOU WILL HAVE TO RELOAD YOUR DATA IF YOU WANT TO GET THE SEQUENCE(S) BACK.
    
    :param sequences:    One or more sequences to drop.
    """
    algorithms.s999_editor.remove_sequences( sequences, False )


@command()
def drop_components() -> EChanges:
    """
    Removes all the components from the model.
    """
    model = global_view.current_model()
    count = algorithms.s040_major.drop_major( model )
    
    MCMD.progress( "Dropped all {} components from the model.".format( count ) )
    
    return EChanges.COMPONENTS


@command()
def drop_alignment( component: Optional[List[LegoComponent]] = None ) -> EChanges:
    """
    Removes the alignment data from the component. If no component is specified, drops all alignments.
    :param component: Component to drop the alignment for, or `None` for all.
    """
    to_do = cli_view_utils.get_component_list( component )
    count = 0
    
    for component_ in to_do:
        if algorithms.s070_alignment.drop_alignments( component_ ):
            count += 1
    
    MCMD.progress( "{} alignments removed across {} components.".format( count, len( to_do ) ) )
    
    return EChanges.COMP_DATA


@command( names = ["drop_tree", "drop_trees"] )
def drop_tree( component: Optional[List[LegoComponent]] = None ) -> EChanges:
    """
    Removes component tree(s).
    
    :param component:   Component, or `None` for all. 
    """
    to_do = cli_view_utils.get_component_list( component )
    count = 0
    
    for component_ in to_do:
        if algorithms.s080_tree.drop_tree( component_ ):
            count += 1
    
    MCMD.progress( "{} trees removed across {} components.".format( count, len( to_do ) ) )
    
    return EChanges.COMP_DATA


@command()
def drop_fusions() -> EChanges:
    """
    Removes the fusion events from the model.
    """
    model = global_view.current_model()
    previous = len( model.fusion_events )
    removed = algorithms.s090_fusion_events.drop_fusions( model )
    
    MCMD.progress( "Removed {} fusion events and {} fusion points from the model.".format( previous, removed ) )
    
    return EChanges.COMP_DATA


@command()
def drop_candidates() -> EChanges:
    """
    Removes data from the model.
    """
    algorithms.s100_splits.drop_splits( global_view.current_model() )
    return EChanges.COMP_DATA


@command()
def drop_viable() -> EChanges:
    """
    Removes data from the model.
    """
    algorithms.s110_consensus.drop_consensus( global_view.current_model() )
    return EChanges.COMP_DATA

@command()
def drop_pregraphs() -> EChanges:
    """
    Removes data from the model.
    """
    algorithms.s130_pregraphs.drop_pregraphs( global_view.current_model() )
    return EChanges.COMP_DATA

@command()
def drop_subsets() -> EChanges:
    """
    Removes data from the model.
    """
    algorithms.s120_subsets.drop_subsets( global_view.current_model() )
    return EChanges.COMP_DATA


@command()
def drop_subgraphs() -> EChanges:
    """
    Removes data from the model.
    """
    algorithms.s140_supertrees.drop_supertrees( global_view.current_model() )
    return EChanges.COMP_DATA


@command()
def drop_fused() -> EChanges:
    """
    Removes data from the model.
    """
    algorithms.s150_fuse.drop_fused( global_view.current_model() )
    return EChanges.COMP_DATA


@command()
def drop_cleaned() -> EChanges:
    """
    Removes data from the model.
    """
    algorithms.s160_clean.drop_cleaned( global_view.current_model() )
    return EChanges.COMP_DATA


@command()
def drop_checked() -> EChanges:
    """
    Removes data from the model.
    """
    algorithms.s170_checked.drop_checked( global_view.current_model() )
    return EChanges.COMP_DATA
