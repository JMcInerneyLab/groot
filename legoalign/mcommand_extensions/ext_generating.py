from typing import List, Optional

from legoalign.algorithms import alignment, components, consensus, fuse, tree
from legoalign.data import global_view
from legoalign.data.lego_model import LegoComponent
from legoalign.frontends.cli import cli_view_utils
from legoalign.frontends.gui.gui_view_utils import Changes
from mcommand import command
from mcommand.engine.environment import MCMD


@command()
def make_components( tolerance: int = 0 ) -> Changes:
    """
    Detects composites in the model.
    :param tolerance:   Tolerance on overlap, in sites.
    """
    model = global_view.current_model()
    
    with MCMD.action( "Component detection" ):
        components.detect( MCMD, model, tolerance )
    
    for component in model.components:
        if len( component.major_sequences() ) == 1:
            MCMD.warning( "There are components with just one sequence in them. Maybe you meant to use a tolerance higher than {}?".format( tolerance ) )
            break
    
    return Changes( Changes.COMPONENTS )


@command()
def make_alignment( component: Optional[ List[ LegoComponent ] ] = None ) -> Changes:
    """
    Aligns the component. If no component is specified, aligns all components.
    
    :param component: Component to align, or `None` for all.
    """
    to_do = cli_view_utils.get_component_list( component )
    
    for component_ in MCMD.iterate( to_do, "Aligning", interesting = True ):
        alignment.align( component_ )
    
    MCMD.print( "{} {} aligned.".format( len( to_do ), "components" if len( to_do ) != 1 else "component" ) )
    
    return Changes( Changes.COMP_DATA )


@command()
def make_tree( component: Optional[ List[ LegoComponent ] ] = None ):
    """
    Generates component trees.
    
    :param component:   Component, or `None` for all.
    :return: 
    """
    to_do = cli_view_utils.get_component_list( component )
    
    for component_ in MCMD.iterate( to_do, "Generating trees", interesting = True ):
        tree.generate_tree( component_ )
    
    return Changes( Changes.COMP_DATA )


@command()
def make_consensus( component: Optional[ List[ LegoComponent ] ] = None ):
    """
    Fuses the component trees to create the basis for our fusion graph.
    :param component:   Component, or `None` for all.
    :return: 
    """
    components = cli_view_utils.get_component_list( component )
    
    for component_ in MCMD.iterate( components, "Consensus" ):
        consensus.consensus( component_ )
    
    return Changes( Changes.COMP_DATA )


@command()
def make_fusions():
    """
    Makes the fusion points.
    """
    results = [ ]
    
    model = global_view.current_model()
    
    for fusion in fuse.find_all_fusion_points( model ):
        results.append( str( fusion ) )
    
    MCMD.information( "\n".join( results ) )
    
    return Changes( Changes.MODEL_DATA )


@command()
def make_nrfg():
    """
    Creates the N-rooted fusion graph.
    """
    model = global_view.current_model()
    
    nrfg = fuse.create_nrfg( model )
    
    MCMD.information( nrfg.to_ascii() )
    
    return Changes( Changes.MODEL_DATA )
