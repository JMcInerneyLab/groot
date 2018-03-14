from typing import Callable, Dict

import groot.algorithms.external_runner
from groot.data.lego_model import LegoComponent, LegoModel


DAlgorithm = Callable[[LegoModel, str], str]
"""A delegate for a function that takes a model and unaligned FASTA data, and produces an aligned result, in FASTA format."""

algorithms: Dict[str, DAlgorithm] = { }
default_algorithm = None


def register_algorithm( fn: DAlgorithm ) -> DAlgorithm:
    """
    Registers an alignment algorithm.
    Can be used as a decorator.
    
    :param fn:  The function to register. Must match the `DAlgorithm` delegate. 
    :return:    `fn` 
    """
    global default_algorithm
    name: str = fn.__name__
    
    if name.startswith( "align_" ):
        name = name[6:]
    
    if not default_algorithm:
        default_algorithm = name
    
    algorithms[name] = fn
    return fn


def clear( component: LegoComponent ):
    component.alignment = None


def align( algorithm: str, component: LegoComponent ):
    fasta = component.to_legacy_fasta()
    
    if not algorithm:
        algorithm = default_algorithm
    
    if not algorithm in algorithms:
        raise ValueError( "No such alignment algorithm as «{}».".format( algorithm ) )
    
    fn = algorithms[algorithm]
    
    component.alignment = groot.algorithms.external_runner.run_in_temporary( fn, component.model, fasta )


def drop( component: LegoComponent ):
    if component.tree:
        raise ValueError( "Refusing to drop the alignment because there is already a tree for this component. Did you mean to drop the tree first?" )
    
    if component.alignment is not None:
        component.alignment = None
        return True
    
    return False
