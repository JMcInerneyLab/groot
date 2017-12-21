"""
Algorithms for user-domains

Used for display, nothing to do with the model.
"""
from typing import List, Iterable

from mhelper import array_helper

from groot.data.lego_model import LegoSequence, LegoModel, LegoSubsequence, LegoUserDomain


def fixed_width( sequence: LegoSequence, width: int = 25 ) -> List[LegoUserDomain]:
    r = []
    
    for s, e in array_helper.divide_workload( sequence.length, width, expand = True ):
        r.append( LegoUserDomain( sequence, s + 1, e + 1 ) )
    
    return r

def fixed_count( sequence: LegoSequence, count: int = 4 ) -> List[LegoUserDomain]:
    r = []
    
    for s, e in array_helper.divide_workload( sequence.length, count ):
        r.append( LegoUserDomain( sequence, s + 1, e + 1 ) )
    
    return r


def by_predefined( subsequences: List[LegoSubsequence] ) -> List[LegoUserDomain]:
    cuts = set()
    
    for subsequence in subsequences:
        cuts.add( subsequence.start )
        cuts.add( subsequence.end + 1 )
    
    return by_cuts( subsequences[0].sequence, cuts )


def by_cuts( sequence: LegoSequence, cuts: Iterable[int] ):
    """
    Creates domains by cutting up the sequence
    
    :param sequence:        Sequence to generate domains for 
    :param cuts:            The START of the cuts, i.e. 5 = 1…4 ✂ 5…n
    """
    r = []
    
    for left, right in array_helper.lagged_iterate( sorted( cuts ), head = True, tail = True ):
        if left is None:
            left = 1
        
        if right is None:
            if left > sequence.length:
                continue
                
            right = sequence.length
        elif right == 1:
            continue
        else:
            right -= 1
        
        r.append( LegoUserDomain( sequence, left, right ) )
    
    return r


def by_component( sequence: LegoSequence ) -> List[LegoUserDomain]:
    model: LegoModel = sequence.model
    
    components = model.components.find_components_for_minor_sequence( sequence )
    todo = []
    
    for component in components:
        for subsequence in component.minor_subsequences:
            if subsequence.sequence is not sequence:
                continue
            
            todo.append( subsequence )
    
    return by_predefined( todo )
