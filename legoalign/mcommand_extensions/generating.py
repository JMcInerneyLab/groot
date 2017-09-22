from typing import Optional

from legoalign.algorithms import alignment, components, consensus, fuse, quantisation, tree
from legoalign.data.hints import EChanges
from legoalign.data.lego_model import LegoComponent
from mcommand import command
from mcommand.engine.environment import MCMD
from legoalign.frontends.cli import cli_view, cli_view_utils


@command()
def make_components( tolerance: int = 0 ) -> EChanges:
    """
    Detects composites in the model.
    :param tolerance:   Tolerance on overlap, in sites.
    """
    model = cli_view.current_model()
    
    with MCMD.action( "Component detection" ):
        components.detect( MCMD, model, tolerance )
    
    for component in model.components:
        if len( component.major_sequences() ) == 1:
            MCMD.warning( "There are components with just one sequence in them. Maybe you meant to use a tolerance higher than {}?".format( tolerance ) )
            break
    
    return EChanges.ATTRS


@command()
def make_alignment( component: Optional[ LegoComponent ] = None ):
    """
    Aligns the component. If no component is specified, aligns all components.
    
    :param component: Component to align, or `None` for all.
    """
    to_do = cli_view_utils.get_component_list( component )
    
    for component_ in MCMD.iterate( to_do, "Aligning", interesting = True ):
        alignment.align( component_ )
    
    MCMD.print( "{} {} aligned.".format( len( to_do ), "components" if len( to_do ) != 1 else "component" ) )


@command()
def make_tree( component: Optional[ LegoComponent ] = None ):
    """
    Generates component trees.
    
    :param component:   Component, or `None` for all.
    :return: 
    """
    to_do = cli_view_utils.get_component_list( component )
    
    for component_ in MCMD.iterate( to_do, "Generating trees", interesting = True ):
        tree.generate_tree( component_ )


@command()
def make_consensus( component: Optional[ LegoComponent ] = None ):
    """
    Fuses the component trees to create the basis for our fusion graph.
    :param component:   Component, or `None` for all.
    :return: 
    """
    components = cli_view_utils.get_component_list( component )
    
    for component_ in MCMD.iterate( components, "Consensus" ):
        consensus.consensus( component_ )



@command( names = [ "print_fusions", "fusions" ] )
def make_fusions():
    """
    Makes the fusion points.
    """
    results = [ ]
    
    model = cli_view.current_model()
    
    for fusion in fuse.find_points( model ):
        results.append( str( fusion ) )
    
    MCMD.information( "\n".join( results ) )