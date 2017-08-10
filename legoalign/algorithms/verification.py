"""
Verifies the integrity of the model.

See `verify`.
"""

from legoalign.LegoModels import LOG, LegoSequence, LegoSubsequence, LegoEdge, LegoModel, LegoSide
from mhelper import ArrayHelper
from mhelper.ExceptionHelper import ImplementationError


def verify( model : LegoModel ):
    """
    Verifies the integrity of the model.
    """
    for edge in model.all_edges:
        __verify_edge(edge)
    
    for sequence in model.sequences:
        __verify_sequence( sequence )
            
def __verify_sequence( sequence : LegoSequence ):
        with LOG("{}".format(sequence)):
            for x in sequence.subsequences:
                LOG("{}".format(x))
                __verify_subsequence( x )
        
        if len(sequence.subsequences) == 0:
            raise ImplementationError( "The sequence '{}' has no subsequences.".format( sequence ) )
        
        for left, right in ArrayHelper.lagged_iterate( sequence.subsequences ):
            if left.end != right.start - 1:
                raise ImplementationError( "Subsequences '{}' and '{}' in sequence '{}' are not adjacent.".format( left, right, sequence ) )

        if sequence.subsequences[ 0 ].start != 1:
            raise ImplementationError( "The first subsequence '{}' in sequence '{}' is not at the start.".format( sequence.subsequences[ 0 ], sequence ) )
        
        if sequence.subsequences[ -1 ].end != sequence.length:
            raise ImplementationError( "The last subsequence '{}' in sequence '{}' is not at the end.".format( sequence.subsequences[ 0 ], sequence ) )
        

def __verify_subsequence( subsequence : LegoSubsequence ):
        if subsequence.start > subsequence.end:
            raise ImplementationError("Subsequence '{}' has start ({}) > end ({}).".format(subsequence, subsequence.start,subsequence.end))
        
        if subsequence.is_destroyed:
            raise ImplementationError("Subsequence '{}' has been flagged as destroyed, but it is still in use.".format(subsequence))
        
        assert subsequence in subsequence.sequence.subsequences
        

def __verify_edge( edge : LegoEdge ):
        if edge.is_destroyed:
            raise ImplementationError( "Edge '{}' has been destroyed.".format( edge ) )
        
        __verify_side( edge.left )
        __verify_side( edge.right )
        
        if edge.left.sequence is edge.right.sequence:
            # Don't allow this, it's unnecessary and just causes problems further down the line
            raise ImplementationError( "The source and destination sequences of the edge '{}' are the same ('{}').".format( edge, edge.left[ 0 ].sequence ) )
        
        
            
def __verify_side( side : LegoSide ):
    if side is None:
        raise ImplementationError( "A side '{}' is `None`.".format(side) )
    
    if len(side)==0:
        raise ImplementationError( "A side '{}' is empty.".format(side) )
    
    for a, b in ArrayHelper.lagged_iterate(side):
        if a.start >= b.start:
            raise ValueError("The subsequences '{}' and '{}' in the side '{}' are not in the correct order!")
        
        if a.end + 1 != b.start:
            raise ValueError("The subsequences '{}' and '{}' in the side '{}' are not adjacent!")
    
    for subsequence in side:
        if subsequence.is_destroyed:
            raise ImplementationError( "Side '{}' source contains a destroyed subsequence '{}'".format( side, subsequence ) )
        
        if subsequence.sequence is not side.sequence:
            raise ImplementationError( "The source subsequences in the side '{}' do not all reference the same sequence, e.g. '{}' and '{}'.".format( side, subsequence.sequence, side.sequence ) )
        
        if subsequence not in subsequence.sequence.subsequences:
            raise ImplementationError("The subsequence '{}' in side '{}' is not in its sequence '{}'.".format(subsequence, side, subsequence.sequence))
        
        