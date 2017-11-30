"""
Quantise implementation.

See `quantise` function.
"""
from groot.algorithms import editor
from groot.data.lego_model import LegoModel, LegoSequence, LOG
from mhelper import array_helper


def quantise( model : LegoModel, level ):
    """
    Quantises the subsequence start/end positions in the model
    """
    editor.assert_model_freshness( model )
    
    before = model.count_subsequences()
    
    for sequence in model.sequences:
        # noinspection PyProtectedMember
        __quantise_sequence( sequence, level )
    
    after = model.count_subsequences()
    
    return before, after

def __quantise_sequence( sequence : LegoSequence, level: int ):
    with LOG("QUANTISING '{}'".format(sequence.accession)):
        while __quantise_iteration( sequence, level ):
            pass

    new_length = __quantise_int( level, sequence.length )
    __quantise_subsequence( sequence, new_length, sequence.subsequences[-1 ] )


def __quantise_iteration( sequence, level ):
    for previous, next in array_helper.lagged_iterate( list( sequence.subsequences ) ):
        new_start = __quantise_int( level, next.start )
    
        if new_start == next.start:
            continue
    
        if new_start > next.end:
            LOG( "'{}' START MOVES TO {} => disappeared.".format( next, new_start ) )
            sequence.subsequences.remove( next )
        else:
            LOG( "'{}' START MOVES TO {}".format( next, new_start ) )
            next.start = new_start
    
        __quantise_subsequence( sequence, new_start, previous )
        
        return True
    
    return False


def __quantise_subsequence( sequence : LegoSequence, new_start, previous ):
    LOG("{} --> {}".format(previous.end + 1, new_start))
    
    new_end = new_start - 1
    
    if new_end >= previous.start:
        LOG("'{}' END MOVES TO {}".format(previous, new_end))
        previous.end = new_end
    else:
        # "previous" has shrunk to nothing
        with LOG( "'{}' END MOVES TO {} => disappeared.".format( previous, new_end ) ):
            sequence.subsequences.remove( previous )
            
def __quantise_int( level, position ):
    half_level = (level // 2)
    position = position + half_level
    position = max( position - position % level, 1 )
    return position