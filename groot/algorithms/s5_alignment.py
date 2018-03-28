from typing import Callable

import groot.utilities.external_runner
from groot.data.extendable_algorithm import AlgorithmCollection
from groot.data.lego_model import LegoComponent, LegoModel


DAlgorithm = Callable[[LegoModel, str], str]
"""A delegate for a function that takes a model and unaligned FASTA data, and produces an aligned result, in FASTA format."""

alignment_algorithms = AlgorithmCollection[DAlgorithm]( "Alignment" )


def drop_alignments( component: LegoComponent ):
    if component.tree:
        raise ValueError( "Refusing to drop the alignment because there is already a tree for this component. Did you mean to drop the tree first?" )
    
    if component.alignment is not None:
        component.alignment = None
        return True
    
    return False



def create_alignments( algorithm: str, component: LegoComponent ):
    fasta = component.to_legacy_fasta()
    
    component.alignment = groot.utilities.external_runner.run_in_temporary( alignment_algorithms[algorithm], component.model, fasta )

