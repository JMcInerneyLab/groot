"""
Functions that actually edit the model.

In order to maintain correct within-model relationships, the model should only be edited via these functions.
"""

from typing import List, Iterable
from uuid import uuid4

from groot.data.lego_model import LegoModel, LegoSequence, LegoSubsequence, LegoEdge
from mhelper import Logger, array_helper, ImplementationError


LOG = Logger( False )
LOG_MAKE_SS = Logger( "make.subsequence", False )


def make_sequence( model: LegoModel,
                   accession: str,
                   obtain_only: bool,
                   initial_length: int,
                   extra_data: object,
                   no_fresh: bool ) -> LegoSequence:
    """
    Creates the specified sequence, or returns it if it already exists.
    """
    assert_model_freshness( model, no_fresh )
    
    assert isinstance( initial_length, int )
    
    if "|" in accession:
        accession = accession.split( "|" )[3]
    
    if "." in accession:
        accession = accession.split( ".", 1 )[0]
    
    accession = accession.strip()
    
    result = None
    
    for sequence in model.sequences:
        if sequence.accession == accession:
            result = sequence
    
    if result is None and not obtain_only:
        result = LegoSequence( model, accession, model._get_incremental_id() )
        array_helper.ordered_insert( model.sequences, result, lambda x: x.accession )
    
    if result is not None:
        result._ensure_length( initial_length )
        result.comments.append( extra_data )
    
    return result


def make_edge( model: LegoModel, source: List[LegoSubsequence], destination: List[LegoSubsequence], extra_data, no_fresh: bool ) -> LegoEdge:
    """
    Creates the specified edge, or returns it if it already exists.
    """
    assert_model_freshness( model, no_fresh )
    
    assert source != destination
    
    ss = set( source )
    sd = set( destination )
    
    for edge in model.all_edges:
        if (set( edge.left ) == ss and set( edge.right ) == sd) \
                or (set( edge.left ) == sd and set( edge.right ) == ss):
            edge.comments.append( extra_data )
            return edge
    
    assert not any( x in source for x in destination )
    assert not any( x in destination for x in source )
    
    result = LegoEdge()
    
    link_edge( result, False, source, no_fresh )
    link_edge( result, True, destination, no_fresh )
    result.comments.append( extra_data )
    
    return result


def make_subsequence( sequence: LegoSequence,
                      start: int,
                      end: int,
                      extra_data: object,
                      allow_resize: bool,
                      no_fresh: bool ) -> List[LegoSubsequence]:
    """
    Creates the specified subsequence, or returns it if it already exists.
    The result may encompass more than one subsequence, if the specified range spans existing subsequences.
    
    :param allow_resize:    Allow resizing of the parent sequence
    :param sequence:        Sequence to create the subsequence within 
    :param start:           Starting position (inclusive) of the new subsequence 
    :param end:             Ending position (inclusive) of the new subsequence 
    :param extra_data:      Extra data to attach to the subsequence 
    :param no_fresh:        Skip the freshness check (not recommended)
    :return:                A list containing the subsequence from start to end. 
    """
    assert_model_freshness( sequence.model, no_fresh )
    
    assert start > 0, start
    assert end > 0, end
    
    if start > end:
        raise ImplementationError( "Cannot make a subsequence in '{0}' which has a start ({1}) > end ({2}) because that doesn't make sense.".format( sequence, start, end ) )
    
    if not allow_resize:
        if start > sequence.length or end > sequence.length:
            raise ImplementationError( "make_subsequence called with start = {} and end = {} but the sequence length is {} and allow_resize is set to False.".format( start, end, sequence.length ) )
    
    with LOG_MAKE_SS( "REQUEST TO MAKE SUBSEQUENCE IN {} FROM {} TO {}".format( sequence, start, end ) ):
        if sequence.length < end:
            sequence._ensure_length( end )
        
        r = []
        
        for subsequence in sequence.subsequences:
            if subsequence.end >= start:
                if subsequence.start == start:
                    LOG_MAKE_SS( "FIRST - {}".format( subsequence ) )
                    first = subsequence
                else:
                    with LOG_MAKE_SS( "FIRST - {} - ¡SPLIT!".format( subsequence ) ):
                        _, first = split_subsequence( subsequence, start, no_fresh )
                        LOG_MAKE_SS( "SPLIT ABOUT {} GIVING RIGHT {}".format( start, first ) )
                
                if first.end > end:
                    first, _ = split_subsequence( first, end + 1, no_fresh )
                    LOG_MAKE_SS( "THEN SPLIT ABOUT {} GIVING LEFT {}".format( end + 1, first ) )
                
                LOG_MAKE_SS( "#### {}".format( first ) )
                r.append( first )
                break
        
        for subsequence in sequence.subsequences:
            if subsequence.start > start:
                if subsequence.end > end:
                    if subsequence.start != end + 1:
                        with LOG_MAKE_SS( "LAST - {} - ¡SPLIT!".format( subsequence ) ):
                            last, _ = split_subsequence( subsequence, end + 1, no_fresh )
                            LOG_MAKE_SS( "SPLIT ABOUT {} GIVING LEFT {}".format( end + 1, last ) )
                        
                        LOG_MAKE_SS( "#### {}".format( last ) )
                        r.append( last )
                    
                    break
                else:
                    LOG_MAKE_SS( "MIDDLE - {}".format( subsequence ) )
                    LOG_MAKE_SS( "#### {}".format( subsequence ) )
                    r.append( subsequence )
        
        for left, right in array_helper.lagged_iterate( sequence.subsequences ):
            assert left.end + 1 == right.start
        
        assert not any( x.is_destroyed for x in r )
        
        for subsequence in r:
            assert r.count( subsequence ) == 1, "Multiple copies of {} in result.".format( subsequence )
        
        for ss in r:
            ss.comments.append( extra_data )
        
        return r


def split_sequence( sequence: LegoSequence, split_point: int, no_fresh: bool ):
    """
    Splits a sequence about the `split_point`.
    See `split_subsequence`.
    """
    assert_model_freshness( sequence.model, no_fresh )
    
    for ss in sequence.subsequences:
        if ss.start <= split_point <= ss.end:
            split_subsequence( ss, split_point, no_fresh )
            break


def __inherit_subsequence( target: LegoSubsequence, original: LegoSubsequence, no_fresh: bool ):
    LOG( "INHERIT SUBSEQUENCE {} --> {}".format( original, target ) )
    assert original != target
    
    for edge in original.edges:
        link_edge( edge, edge.position( original ), [target], no_fresh )


def split_subsequence( subsequence: LegoSubsequence, p: int, no_fresh: bool ):
    """
    Splits the subsequence into s..p-1 and p..e, i.e.:

    ---------------------
    |       |p          |
    | 1 2 3 4|5 6 7 8 9 |
    ---------------------
    """
    assert_model_freshness( subsequence.sequence.model, no_fresh )
    
    with LOG( "SPLIT {} AT {}".format( subsequence, p ) ):
        if p <= subsequence.start or p > subsequence.end:
            raise ValueError( "Cannot split a subsequence from {0} to {1} about a point {2}".format( subsequence.start, subsequence.end, p ) )
        
        left = LegoSubsequence( subsequence.sequence, subsequence.start, p - 1, subsequence.components )
        right = LegoSubsequence( subsequence.sequence, p, subsequence.end, subsequence.components )
        
        __inherit_subsequence( left, subsequence, no_fresh )
        __inherit_subsequence( right, subsequence, no_fresh )
        
        index = subsequence.sequence.subsequences.index( subsequence )
        subsequence.sequence.subsequences.remove( subsequence )
        subsequence.sequence.subsequences.insert( index, right )
        subsequence.sequence.subsequences.insert( index, left )
        __destroy_subsequence( subsequence, no_fresh )
        return left, right


def unlink_all_edges( model: LegoModel, edge: LegoEdge, no_fresh: bool ):
    """
    Removes all references to this edge.
    """
    assert_model_freshness( model, no_fresh )
    
    for x in edge.left:
        x.edges.remove( edge )
    
    for x in edge.right:
        x.edges.remove( edge )
    
    edge.is_destroyed = True


def unlink_edge( edge: LegoEdge, subsequence: "LegoSubsequence", no_fresh: bool ):
    """
    Removes the specified subsequence from the edge.
    
    Warning: If this empties the edge, the edge is automatically destroyed.
    """
    assert_model_freshness( subsequence.sequence.model, no_fresh )
    
    the_list = edge.right if edge.position( subsequence ) else edge.left
    
    subsequence.edges.remove( edge )
    the_list.remove( subsequence )
    
    if len( the_list ) == 0:
        unlink_all_edges( subsequence.sequence.model, edge, no_fresh )


def link_edge( edge: LegoEdge, position: bool, subsequences: "List[LegoSubsequence]", no_fresh: bool ):
    """
    Adds the specified subsequences to the edge.
    """
    assert_model_freshness( subsequences[0].sequence.model, no_fresh )
    
    with LOG( "LINK EDGE #{}".format( id( edge ) ) ):
        pfx = "-D->" if position else "-S->"
        for x in subsequences:
            LOG( "{} {}".format( pfx, x ) )
        
        the_list = edge.right if position else edge.left
        
        for subsequence in subsequences:
            assert not subsequence.is_destroyed
            
            if subsequence not in the_list:
                the_list.add( subsequence )
                subsequence.edges.append( edge )


def merge_subsequences( model: LegoModel, all: Iterable[LegoSubsequence], no_fresh: bool ):
    assert_model_freshness( model, no_fresh )
    
    all = sorted( all, key = lambda x: x.start )
    
    if len( all ) <= 1:
        raise ValueError( "Cannot merge a list '{}' of less than two elements.".format( all ) )
    
    for left, right in array_helper.lagged_iterate( all ):
        if left.sequence != right.sequence:
            raise ValueError( "merge_subsequences attempted but the subsequences '{}' and '{}' are not in the same sequence.".format( left, right ) )
        
        if right.start != left.end + 1:
            raise ValueError( "merge_subsequences attempted but the subsequences '{}' and '{}' are not adjacent.".format( left, right ) )
    
    first = all[0]
    first.end = all[-1].end
    
    for other in all[1:]:
        __inherit_subsequence( first, other, no_fresh )
        other.sequence.subsequences.remove( other )
        __destroy_subsequence( other, no_fresh )


def __destroy_subsequence( subsequence: LegoSubsequence, no_fresh: bool ):
    LOG( "DESTROY SUBSEQUENCE {}".format( subsequence ) )
    
    for edge in list( subsequence.edges ):
        unlink_edge( edge, subsequence, no_fresh )
    
    assert len( subsequence.edges ) == 0, subsequence.edges
    subsequence.is_destroyed = True


def add_new_sequence( model: LegoModel, no_fresh: bool ) -> LegoSequence:
    """
    Creates a new sequence
    """
    assert_model_freshness( model, no_fresh )
    return make_sequence( model, str( uuid4() ), False, 10, "user-created", no_fresh )


def add_new_edge( subsequences: List[LegoSubsequence], no_fresh: bool ) -> LegoEdge:
    """
    Creates a new edge between the specified subsequences.
    The specified subsequences should span two, and only two, sequences.
    """
    assert_model_freshness( subsequences[0].sequence.model, no_fresh )
    
    sequences = list( set( subsequence.sequence for subsequence in subsequences ) )
    
    if len( sequences ) != 2:
        raise ValueError( "Need two sequences to create an edge, but {0} have been specified: {1}".format( len( subsequences ), subsequences ) )
    
    left_sequence = sequences[0]
    right_sequence = sequences[0]
    
    left_subsequences = [subsequence for subsequence in subsequences if subsequence.sequence is left_sequence]
    right_subsequences = [subsequence for subsequence in subsequences if subsequence.sequence is right_sequence]
    
    edge = LegoEdge()
    
    link_edge( edge, False, left_subsequences, no_fresh )
    link_edge( edge, True, right_subsequences, no_fresh )
    
    return edge


def add_new_subsequence( sequence: LegoSequence, split_point: int, no_fresh: bool ) -> None:
    """
    Splits a sequence, creating a new subsequence
    """
    split_sequence( sequence, split_point, no_fresh )


def remove_sequences( sequences: List[LegoSequence], no_fresh: bool ):
    """
    Removes the specified sequences
    """
    assert_model_freshness( sequences[0].model, no_fresh )
    
    for sequence in sequences:
        for subsequence in sequence.subsequences:
            __destroy_subsequence( subsequence, no_fresh )
        
        sequence.model.sequences.remove( sequence )


def assert_model_freshness( model, no_fresh: bool ):
    if no_fresh:
        return
    
    if model.components:
        raise ValueError( "Refusing to modify the model whilst it is in use. Did you mean to drop the components first?" )
    
    if model.fusion_events:
        raise ValueError( "Refusing to modify the model whilst it is in use. Did you mean to drop the fusion_events first?" )
    
    if model.nrfg:
        raise ValueError( "Refusing to modify the model whilst it is in use. Did you mean to drop the NRFG first?" )


def remove_edges( subsequences: List[LegoSubsequence], edges: List[LegoEdge], no_fresh: bool ):
    """
    Removes the specified edges from the specified subsequences
    """
    assert_model_freshness( subsequences[0].sequence.model, no_fresh )
    
    for subsequence in subsequences:
        for edge in edges:
            if not edge.is_destroyed:
                unlink_edge( edge, subsequence, no_fresh )
