from typing import Optional, Callable, Dict, List

import groot.algorithms.external_runner
from groot.algorithms import importation
from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence, EPosition
from mgraph import MGraph
from mhelper import SwitchError


DAlgorithm = Callable[[LegoModel, str], str]
"""A delegate for a function that takes a model and aligned FASTA data, and produces a tree, in Newick format."""

algorithms: Dict[str, DAlgorithm] = { }
default_algorithm = None


def register_algorithm( fn: DAlgorithm ) -> DAlgorithm:
    """
    Registers a tree algorithm.
    Can be used as a decorator.
    
    :param fn:  Function matching the `DAlgorithm` delegate.
    :return:    `fn` 
    """
    global default_algorithm
    
    name: str = fn.__name__
    
    if name.startswith( "tree_" ):
        name = name[5:]
    
    if default_algorithm is None:
        default_algorithm = name
    
    algorithms[name] = fn
    
    return fn


def generate_tree( algorithm: Optional[str], component: LegoComponent ) -> None:
    """
    Creates a tree from the component.
    
    The tree is set as the component's `tree` field. 
    """
    if component.alignment is None:
        raise ValueError( "Cannot generate the tree because the alignment has not yet been specified." )
    
    if not algorithm:
        algorithm = default_algorithm
    
    if not algorithm in algorithms:
        raise ValueError( "No such tree algorithm as «{}».".format( algorithm ) )
    
    fn = algorithms[algorithm]
    
    # Read the result
    newick = groot.algorithms.external_runner.run_in_temporary( fn, component.model, component.alignment )
    component.tree = importation.import_newick( newick, component.model )
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
                node.relation.make_root()
                return True
            elif d.position == EPosition.ROOT:
                node.make_root()
                return True
            elif d.position == EPosition.NONE:
                pass
            else:
                raise SwitchError( "node.data.position", d.position )
    
    return False


def drop( component: LegoComponent ) -> bool:
    if component.model.fusion_events:
        raise ValueError( "Refusing to drop the tree because there are fusion events which may be using it. Did you mean to drop the fusion events first?" )
    
    if component.model.nrfg:
        raise ValueError( "Refusing to drop the tree because there is an NRFG which may be using it. Did you mean to drop the NRFG first?" )
    
    if component.tree is not None:
        component.tree = None
        return True
    
    return False
