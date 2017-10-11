from ete3 import Tree

from legoalign.algorithms import external_tools
from legoalign.data.lego_model import LegoComponent


def generate_tree( component: LegoComponent ) -> None:
    """
    Creates a tree from the component.
    
    The tree is set as the component's `tree` field. 
    """
    try:
        # noinspection PyUnresolvedReferences
        from mhelper import BioHelper
        # noinspection PyUnresolvedReferences
        from Bio import Phylo
    except ImportError:
        raise ImportError( "Install BioPython if you want to generate NRFGs." )
    
    if component.alignment is None:
        raise ValueError( "Cannot generate the tree because the alignment has not yet been specified." )
    
    # Read the result
    component.tree = external_tools.run_in_temporary( external_tools.tree, component.alignment )
    
    # Fix the sequence names
    for sequence in component.minor_sequences():
        if "?" not in sequence.site_array:
            component.tree = component.tree.replace( "S{}:".format( sequence.id ), sequence.accession + ":" )



