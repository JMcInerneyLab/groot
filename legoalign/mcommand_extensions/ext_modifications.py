from legoalign.algorithms import deconvolution, quantisation, verification
from legoalign.data import global_view
from legoalign.data.lego_model import LegoComponent
from legoalign.frontends.gui.gui_view_utils import Changes, Changes
from mcommand import command
from mcommand.engine.environment import MCMD


@command()
def clean( edges: bool = True, subsequences: bool = True ) -> Changes:
    """
    Removes redundancies (duplicates) from the model.
    
    :param subsequences: When `True`, redundant subsequences are removed. 
    :param edges:        When `True`, redundant edges are removed.
    :return: 
    """
    model = global_view.current_model()
    
    if not edges and not subsequences:
        raise ValueError( "You must specify at least one item to clean." )
    
    if edges:
        with MCMD.action( "Removing redundant edges" ):
            deconvolution.remove_redundant_edges( model )
    
    if subsequences:
        with MCMD.action( "Removing redundant subsequences" ):
            deconvolution.remove_redundant_subsequences( model )
    
    return Changes( Changes.MODEL_ENTITIES )


@command()
def verify() -> Changes:
    """
    Verifies the integrity of the model.
    """
    verification.verify( global_view.current_model() )
    MCMD.print( "Verified OK." )
    
    return Changes( Changes.NONE )


@command()
def set_tree( component: LegoComponent, tree: str ) -> Changes:
    """
    Sets a component tree manually.
    
    :param component:   Component 
    :param tree:        Tree to set. In newick format. 
    """
    component.tree = tree
    
    return Changes( Changes.COMP_DATA )


@command()
def set_alignment( component: LegoComponent, alignment: str )->Changes:
    """
    Sets a component tree manually.
    
    :param component:        Component. 
    :param alignment:        Alignment to set. 
    """
    component.alignment = alignment
    
    return Changes( Changes.COMP_DATA )

@command()
def quantise( level: int ) -> Changes:
    """
    Quantises the model.
    
    :param level:   Quantisation level, in sites 
    :return: 
    """
    
    before, after = quantisation.quantise( global_view.current_model(), level )
    
    MCMD.print( "Quantised applied. Reduced the model from {} to {} subsequences.".format( before, after ) )
    
    return Changes( Changes.MODEL_ENTITIES )


def new_subsequence( sequence, split_point )->Changes:
    return None


def new_edge( subsequences )->Changes:
    return None


def new_sequence()->Changes:
    return None


def merge_subsequences( subsequences )->Changes:
    return None


def remove_sequence( sequences )->Changes:
    return None


def remove_edges( subsequences, edges )->Changes:
    return None