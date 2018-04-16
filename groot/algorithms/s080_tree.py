from typing import Callable, List, Optional

from mgraph import MGraph
from mhelper import SwitchError

from groot.utilities import AlgorithmCollection, external_runner
from groot import algorithms, constants
from groot.data import LegoModel, LegoSequence, LegoComponent, EPosition, ESiteType



DAlgorithm = Callable[[LegoModel, str], str]
"""A delegate for a function that takes a model and aligned FASTA data, and produces a tree, in Newick format."""

tree_algorithms = AlgorithmCollection[DAlgorithm]( "Tree" )


def drop_tree( component: LegoComponent ) -> bool:
    if component.model.get_status( constants.STAGES.FUSIONS_7 ):
        raise ValueError( "Refusing to drop the tree because fusions have already been recorded. Did you mean to drop the fusions first?" )
    
    if component.tree is not None:
        component.tree = None
        component.tree_unrooted = None
        component.tree_newick = None
        return True
    
    return False


def create_tree( algorithm: Optional[str], component: LegoComponent ) -> None:
    """
    Creates a tree from the component.
    
    :returns: Nothing, the tree is set as the component's `tree` field. 
    """
    if component.alignment is None:
        raise ValueError( "Cannot generate the tree because the alignment has not yet been specified." )
    
    if component.model.site_type == ESiteType.DNA:
        site_type = "n"
    elif component.model.site_type == ESiteType.PROTEIN:
        site_type = "p"
    else:
        raise SwitchError( "component.model.site_type", component.model.site_type )
    
    # Read the result
    newick = external_runner.run_in_temporary( tree_algorithms[algorithm], site_type, component.alignment )
    component.tree_unrooted = algorithms.s020_importation.import_newick( newick, component.model )
    component.tree = component.tree_unrooted.copy()
    component.tree_newick = newick
    reposition_tree( component.tree )


def reposition_all( model: LegoModel, component: Optional[LegoComponent] = None ) -> List[LegoComponent]:
    """
    Repositions a component tree based on node.position data.
    """
    if model.fusion_events:
        raise ValueError( "Cannot reposition trees because they already have assigned fusion events. Maybe you meant to drop the fusion events first?" )
    
    components = [component] if component is not None else model.components
    changes = []
    
    for component_ in components:
        if component_.tree is None:
            continue
        
        if component_.tree is not None and reposition_tree( component_.tree ):
            changes.append( component_ )
    
    return changes


def reposition_tree( tree: MGraph ) -> bool:
    """
    Re-lays out a tree using `LegoSequence.position`.
    """
    for node in tree:
        d = node.data
        if isinstance( d, LegoSequence ):
            if d.position == EPosition.OUTGROUP:
                node.make_outgroup()
                return True
            elif d.position == EPosition.ROOT:
                node.make_root()
                return True
            elif d.position == EPosition.NONE:
                pass
            else:
                raise SwitchError( "node.data.position", d.position )
    
    return False
