"""
Algorithms for user-domains

Used for display, nothing to do with the model.
"""
from typing import List, Iterable

from groot.frontends.gui.gui_view_support import EDomainFunction
from mhelper import array_helper, SwitchError

from groot.data.lego_model import LegoSequence, LegoModel, LegoSubsequence, LegoUserDomain


def create_userdomains( model: LegoModel, switch: EDomainFunction, param: int ):
    if not model.sequences:
        raise ValueError( "Cannot generate domains because there are no sequences." )
    
    model.user_domains.clear()
    
    for sequence in model.sequences:
        for domain in sequence_by_enum( sequence, switch, param ):
            model.user_domains.add( domain )


def sequence_fixed_width( sequence: LegoSequence, width: int = 25 ) -> List[LegoUserDomain]:
    r = []
    
    for i in range( 1, sequence.length + 1, width ):
        r.append( LegoUserDomain( sequence, i, min( i + width, sequence.length ) ) )
    
    return r


def sequence_fixed_count( sequence: LegoSequence, count: int = 4 ) -> List[LegoUserDomain]:
    r = []
    
    for s, e in array_helper.divide_workload( sequence.length, count ):
        r.append( LegoUserDomain( sequence, s + 1, e + 1 ) )
    
    return r


def sequence_by_predefined( subsequences: List[LegoSubsequence] ) -> List[LegoUserDomain]:
    cuts = set()
    
    for subsequence in subsequences:
        cuts.add( subsequence.start )
        cuts.add( subsequence.end + 1 )
    
    return sequence_by_cuts( subsequences[0].sequence, cuts )


def sequence_by_cuts( sequence: LegoSequence, cuts: Iterable[int] ):
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


def sequence_by_component( sequence: LegoSequence ) -> List[LegoUserDomain]:
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
    
    return sequence_by_predefined( todo )


def sequence_by_enum( sequence, switch, param ):
    if switch == EDomainFunction.NONE:
        return [LegoUserDomain( sequence, 1, sequence.length )]
    if switch == EDomainFunction.COMPONENT:
        return sequence_by_component( sequence )
    elif switch == EDomainFunction.FIXED_COUNT:
        return sequence_fixed_count( sequence, param )
    elif switch == EDomainFunction.FIXED_WIDTH:
        return sequence_fixed_width( sequence, param )
    else:
        raise SwitchError( "self.owner_model_view.options.domain_function", switch )
