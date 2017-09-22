from legoalign.algorithms import deconvolution, verification, quantisation
from legoalign.data.hints import EChanges
from legoalign.data.lego_model import LegoComponent
from legoalign.frontends.cli import cli_view
from mcommand import command
from mcommand.engine.environment import MCMD

@command()
def clean_edges( edges: bool = True, subsequences: bool = True ) -> EChanges:
    """
    Removes redundancies (duplicates) from the model.
    
    :param subsequences: When `True`, redundant subsequences are removed. 
    :param edges:        When `True`, redundant edges are removed.
    :return: 
    """
    model = cli_view.current_model()
    
    if not edges and not subsequences:
        raise ValueError( "You must specify at least one item to clean." )
    
    if edges:
        with MCMD.action( "Removing redundant edges" ):
            deconvolution.remove_redundant_edges( model )
    
    if subsequences:
        with MCMD.action( "Removing redundant subsequences" ):
            deconvolution.remove_redundant_subsequences( model )
    
    return EChanges.ATTRS


@command()
def verify() -> None:
    """
    Verifies the integrity of the model.
    """
    verification.verify( cli_view.current_model() )
    MCMD.print( "Verified OK." )


@command()
def set_tree( component: LegoComponent, tree: str ):
    """
    Sets a component tree manually.
    
    :param component:   Component 
    :param tree:        Tree to set. In newick format. 
    """
    component.tree = tree


@command()
def set_alignment( component: LegoComponent, alignment: str ):
    """
    Sets a component tree manually.
    
    :param component:        Component. 
    :param alignment:        Alignment to set. 
    """
    component.alignment = alignment

@command()
def quantise( level: int ) -> EChanges:
    """
    Quantises the model.
    
    :param level:   Quantisation level, in sites 
    :return: 
    """
    
    before, after = quantisation.quantise( cli_view.current_model(), level )
    
    MCMD.print( "Quantised applied. Reduced the model from {} to {} subsequences.".format( before, after ) )
    
    return EChanges.ATTRS