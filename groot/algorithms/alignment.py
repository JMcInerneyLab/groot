from typing import Callable

import groot.algorithms.external_runner
from groot.data.extendable_algorithm import AlgorithmCollection
from groot.data.lego_model import LegoComponent, LegoModel


DAlgorithm = Callable[[LegoModel, str], str]
"""A delegate for a function that takes a model and unaligned FASTA data, and produces an aligned result, in FASTA format."""

algorithms = AlgorithmCollection[DAlgorithm]( "Alignment" )


def clear( component: LegoComponent ):
    component.alignment = None


def align( algorithm: str, component: LegoComponent ):
    fasta = component.to_legacy_fasta()
    
    component.alignment = groot.algorithms.external_runner.run_in_temporary( algorithms[algorithm], component.model, fasta )


def drop( component: LegoComponent ):
    if component.tree:
        raise ValueError( "Refusing to drop the alignment because there is already a tree for this component. Did you mean to drop the tree first?" )
    
    if component.alignment is not None:
        component.alignment = None
        return True
    
    return False
