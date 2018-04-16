"""
Algorithms for user-domains

Used for display, nothing to do with the model.
"""
from typing import Callable

from groot.utilities.extendable_algorithm import AlgorithmCollection
from groot.data import LegoModel, LegoSequence


DAlgorithm = Callable[[LegoSequence, int], str]
"""A delegate for a function that takes a sequence and an arbitrary parameter, and produces an list of domains."""

domain_algorithms = AlgorithmCollection[DAlgorithm]( "Domain" )


def drop_userdomains( model: LegoModel ):
    model.user_domains.clear()


def create_userdomains( model: LegoModel, algorithm: str, param: int ):
    if not model.sequences:
        raise ValueError( "Cannot generate domains because there are no sequences." )
    
    model.user_domains.clear()
    
    fn = domain_algorithms[algorithm]
    
    for sequence in model.sequences:
        for domain in fn( sequence, param ):
            model.user_domains.add( domain )


def list_userdomains( sequence: LegoSequence, algorithm: str, param: int ):
    fn = domain_algorithms[algorithm]
    return fn( sequence, param )
