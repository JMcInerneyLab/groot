from typing import List, Iterable
from groot import LegoSequence, LegoUserDomain, LegoModel, domain_algorithms
from groot.data.model_core import LegoSubsequence
from mhelper import array_helper


@domain_algorithms.register( "Fixed width" )
def sequence_fixed_width( sequence: LegoSequence, width: int = 25 ) -> List[LegoUserDomain]:
    """
    Sequences are split up into fixed width domains. 
    """
    r = []
    
    for i in range( 1, sequence.length + 1, width ):
        r.append( LegoUserDomain( sequence, i, min( i + width, sequence.length ) ) )
    
    return r


@domain_algorithms.register( "Fixed count" )
def sequence_fixed_count( sequence: LegoSequence, count: int = 4 ) -> List[LegoUserDomain]:
    """
    Sequences are split up into a fixed number of equal width domains.
    """
    r = []
    
    for s, e in array_helper.divide_workload( sequence.length, count ):
        r.append( LegoUserDomain( sequence, s + 1, e + 1 ) )
    
    return r


@domain_algorithms.register( "Component" )
def sequence_by_component( sequence: LegoSequence, _: int ) -> List[LegoUserDomain]:
    """
    Sequences are split at the component boundaries. This usually provides the best view.
    """
    model: LegoModel = sequence.model
    
    components = model.components.find_components_for_minor_sequence( sequence )
    todo = []
    
    for component in components:
        for subsequence in component.minor_subsequences:
            if subsequence.sequence is not sequence:
                continue
            
            todo.append( subsequence )
    
    if not todo:
        return [LegoUserDomain( sequence, 1, sequence.length )]
    
    return __sequence_by_predefined( todo )


def __sequence_by_predefined( subsequences: List[LegoSubsequence] ) -> List[LegoUserDomain]:
    cuts = set()
    
    for subsequence in subsequences:
        cuts.add( subsequence.start )
        cuts.add( subsequence.end + 1 )
    
    return __sequence_by_cuts( subsequences[0].sequence, cuts )


def __sequence_by_cuts( sequence: LegoSequence, cuts: Iterable[int] ):
    """
    Creates domains by cutting up the sequence at the cut points.
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
