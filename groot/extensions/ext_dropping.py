from typing import List, Optional

from groot.algorithms import alignment, components, tree, fuse, editor, nrfg
from groot.data import global_view
from groot.data.lego_model import LegoComponent, LegoSequence
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import command
from intermake.engine.environment import MCMD


__mcmd_folder_name__ = "Generating"


@command()
def drop_sequences( sequences: List[LegoSequence] ):
    """
    Removes one or more sequences from the model.
    
    !THIS ACTION CANNOT BE UNDONE!
    YOU WILL HAVE TO RELOAD YOUR DATA IF YOU WANT TO GET THE SEQUENCE(S) BACK.
    
    :param sequences:    One or more sequences to drop.
    """
    editor.remove_sequences( sequences, False )


@command()
def drop_components() -> EChanges:
    """
    Removes all the components from the model.
    """
    model = global_view.current_model()
    count = components.drop( model )
    
    MCMD.information( "Dropped all {} components from the model.".format( count ) )
    
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
        if alignment.drop( component_ ):
            count += 1
    
    MCMD.print( "{} alignments removed across {} components.".format( count, len( to_do ) ) )
    
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
        if tree.drop( component_ ):
            count += 1
    
    MCMD.print( "{} trees removed across {} components.".format( count, len( to_do ) ) )
    
    return EChanges.COMP_DATA


@command()
def drop_fusions() -> EChanges:
    """
    Removes the fusion events from the model.
    """
    model = global_view.current_model()
    previous = len( model.fusion_events )
    removed = fuse.remove_fusions( model )
    
    MCMD.information( "Removed {} fusion events and {} fusion points from the model.".format( previous, removed ) )
    
    return EChanges.COMP_DATA


@command()
def drop_candidates() -> EChanges:
    """
    Removes data from the model.
    """
    nrfg.s1_drop_candidates( global_view.current_model() )
    return EChanges.COMP_DATA


@command()
def drop_viable() -> EChanges:
    """
    Removes data from the model.
    """
    nrfg.s2_drop_viable( global_view.current_model() )
    return EChanges.COMP_DATA


@command()
def drop_subsets() -> EChanges:
    """
    Removes data from the model.
    """
    nrfg.s3_drop_subsets( global_view.current_model() )
    return EChanges.COMP_DATA


@command()
def drop_minigraphs() -> EChanges:
    """
    Removes data from the model.
    """
    nrfg.s4_drop_minigraphs( global_view.current_model() )
    return EChanges.COMP_DATA


@command()
def drop_fused() -> EChanges:
    """
    Removes data from the model.
    """
    nrfg.s5_drop_sewed( global_view.current_model() )
    return EChanges.COMP_DATA

@command()
def drop_cleaned() -> EChanges:
    """
    Removes data from the model.
    """
    nrfg.s6_drop_cleaned( global_view.current_model() )
    return EChanges.COMP_DATA


@command()
def drop_checked() -> EChanges:
    """
    Removes data from the model.
    """
    nrfg.s7_drop_checked( global_view.current_model() )
    return EChanges.COMP_DATA


