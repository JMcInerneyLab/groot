from typing import List, Optional

from groot.algorithms import alignment, components, consensus, fuse, tree
from groot.data import global_view
from groot.data.lego_model import LegoComponent
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.gui_view_utils import Changes
from intermake import command
from intermake.engine.environment import MCMD


__mcmd_folder_name__ = "Generating"


@command()
def drop_components() -> Changes:
    """
    Removes all the components from the model.
    """
    model = global_view.current_model()
    count = components.drop( model )
    
    MCMD.information( "Dropped all {} components from the model.".format( count ) )
    
    return Changes( Changes.COMPONENTS )


@command()
def drop_alignment( component: Optional[List[LegoComponent]] = None ) -> Changes:
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
    
    return Changes( Changes.COMP_DATA )


@command()
def drop_tree( component: Optional[List[LegoComponent]] = None ) -> Changes:
    """
    Removes component trees.
    
    :param component:   Component, or `None` for all.
    :return: 
    """
    to_do = cli_view_utils.get_component_list( component )
    count = 0
    
    for component_ in to_do:
        if tree.drop( component_ ):
            count += 1
    
    MCMD.print( "{} trees removed across {} components.".format( count, len( to_do ) ) )
    
    return Changes( Changes.COMP_DATA )


@command()
def drop_consensus( component: Optional[List[LegoComponent]] = None ) -> Changes:
    """
    Drops the consensus trees.
    :param component:   Component, or `None` for all.
    :return: 
    """
    to_do = cli_view_utils.get_component_list( component )
    count = 0
    
    for component_ in to_do:
        if consensus.drop( component_ ):
            count += 1
    
    MCMD.print( "{} consensus trees removed across {} components.".format( count, len( to_do ) ) )
    
    return Changes( Changes.COMP_DATA )


@command()
def drop_fusions() -> Changes:
    """
    Removes the fusion events from the model.
    """
    model = global_view.current_model()
    previous = len( model.fusion_events )
    removed = fuse.remove_fusions( model )
    
    MCMD.information( "Removed {} fusion events and {} fusion points from the model.".format( previous, removed ) )
    
    return Changes( Changes.COMP_DATA )


@command()
def drop_nrfg() -> Changes:
    """
    Removes the NRFG from the model.
    """
    model = global_view.current_model()
    
    if model.nrfg is None:
        MCMD.information( "The model doesn't have an NRFG. No action performed." )
        return Changes( Changes.NONE )
    
    model.nrfg = None
    
    MCMD.information( "The NRFG has been removed from the model." )
    
    return Changes( Changes.COMP_DATA )
