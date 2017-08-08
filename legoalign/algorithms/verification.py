"""
Verifies the integrity of the model.

See `verify`.
"""

from legoalign.LegoModels import LOG, LegoSequence, LegoSubsequence, LegoEdge, LegoModel
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
        
        if not edge.source or not edge.destination:
            return
        
        if len(edge.source)==0:
            raise ImplementationError( "An edge has no source." )
        
        if len(edge.destination)==0:
            raise ImplementationError( "An edge has no destination." )
        
        for x in edge.source:
            if x.sequence is not edge.source[ 0 ].sequence:
                raise ImplementationError( "The source subsequences in the edge '{}' do not all reference the same sequence, e.g. '{}' and '{}'.".format( x, x, edge.source[ 0 ] ) )
        
        for x in edge.destination:
            if x.sequence is not edge.destination[ 0 ].sequence:
                raise ImplementationError( "The destination subsequences in the edge '{}' do not all reference the same sequence, e.g. '{}' and '{}'.".format( x, x, edge.destination[ 0 ] ) )
        
        if edge.source[ 0 ].sequence is edge.destination[ 0 ].sequence:
            # Don't allow this, it's unnecessary and just causes problems further down the line
            raise ImplementationError( "The source and destination sequences of the edge '{}' are the same ('{}').".format( edge, edge.source[ 0 ].sequence ) )
        
        for x in edge.source:
            if x.is_destroyed:
                raise ImplementationError( "Edge '{}' source contains a destroyed subsequence '{}'".format( edge, x ) )
            
        for x in edge.destination:
            if x.is_destroyed:
                raise ImplementationError( "Edge '{}' destination contains a destroyed subsequence '{}'".format( edge, x ) )