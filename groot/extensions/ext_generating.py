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
def make_components( tolerance: int = 0 ) -> Changes:
    """
    Detects composites in the model.
    :param tolerance:   Tolerance on overlap, in sites.
    """
    model = global_view.current_model()
    
    with MCMD.action( "Component detection" ):
        components.detect( model, tolerance )
    
    for component in model.components:
        if len( component.major_sequences() ) == 1:
            MCMD.warning( "There are components with just one sequence in them. Maybe you meant to use a tolerance higher than {}?".format( tolerance ) )
            break
    
    return Changes( Changes.COMPONENTS )


@command()
def make_alignments( component: Optional[List[LegoComponent]] = None ) -> Changes:
    """
    Aligns the component. If no component is specified, aligns all components.
    
    Requisites: The FASTA sequences. You must have called `load_fasta` first.
    
    :param component: Component to align, or `None` for all.
    """
    to_do = cli_view_utils.get_component_list( component )
    
    for component_ in MCMD.iterate( to_do, "Aligning", text = True ):
        alignment.align( component_ )
    
    MCMD.print( "{} components aligned.".format( len( to_do ) ) )
    
    return Changes( Changes.COMP_DATA )


@command()
def make_trees( component: Optional[List[LegoComponent]] = None ):
    """
    Generates component trees.
    
    Requisites: The alignments. You must have called `make_alignments` first.
    
    :param component:   Component, or `None` for all.
    :return: 
    """
    to_do = cli_view_utils.get_component_list( component )
    
    for component_ in MCMD.iterate( to_do, "Generating trees", text = True ):
        tree.generate_tree( component_ )
    
    return Changes( Changes.COMP_DATA )


@command()
def make_consensus( component: Optional[List[LegoComponent]] = None ):
    """
    Fuses the component trees to create the basis for our fusion graph.
    :param component:   Component, or `None` for all.
    :return: 
    """
    to_do = cli_view_utils.get_component_list( component )
    
    for component_ in MCMD.iterate( to_do, "Consensus" ):
        consensus.consensus( component_ )
    
    return Changes( Changes.COMP_DATA )


@command()
def make_fusions() -> Changes:
    """
    Makes the fusion points.
    
    Requisites: The trees. You must have called `make_trees` first.
    """
    model = global_view.current_model()
    fuse.find_all_fusion_points( model )
    
    n = len( model.fusion_events )
    MCMD.progress( "{} {} detected".format( n, "fusion" if n == 1 else "fusions" ) )
    
    return Changes( Changes.MODEL_DATA )


@command()
def make_nrfg( format_str: str = "t" ) -> Changes:
    """
    Creates the N-rooted fusion graph.
    
    Requisites: The fusions. You must have called `make_fusions` first.
    
    :param format_str: Format for output
    """
    model = global_view.current_model()
    
    nrfg = fuse.create_nrfg( model )
    
    MCMD.information( nrfg.to_csv( format_str ) )
    
    return Changes( Changes.MODEL_DATA )
