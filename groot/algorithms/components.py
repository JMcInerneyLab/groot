"""
Components algorithms.

The only one publicly exposed is `detect`, so start there.
"""
from collections import defaultdict
from typing import Tuple, Set, cast, List

from groot.data.lego_model import LegoModel, LegoSequence, LegoComponent, LegoEdge, LegoSubsequence
from intermake.engine.environment import MCMD
from mhelper import Logger, ImplementationError, array_helper
from mhelper.component_helper import ComponentFinder


LOG_MAJOR = Logger( "component.major", False )
LOG_MINOR = Logger( "component.minor", False )


def detect( model: LegoModel, tolerance: int ) -> None:
    """
    Detects sequence and subsequence components.
    """
    if not model.sequences:
        raise ValueError( "Cannot perform component detection because the model has no sequences." )
    
    __clear( model )
    __detect_major( model, tolerance )
    __detect_minor( model, tolerance )


def drop( model: LegoModel ) -> int:
    """
    Drops all components from the model.
    """
    if model.fusion_events:
        raise ValueError( "Refusing to drop the components because there are already fusion events which depend on them. Did you mean to drop the fusion events first?" )
    
    if model.nrfg:
        raise ValueError( "Refusing to drop the components because there is already an NRFG which depends on them. Did you mean to drop the NRFG first?" )
    
    previous = len( model.components )
    __clear( model )
    return previous


def __clear( model: LegoModel ) -> None:
    """
    Clears the components from the model.
    """
    model.components.clear()


def __detect_major( model: LegoModel, tolerance: int ) -> None:
    """
    Finds the sequence components, here termed the "major" elements.
    
    Defined as genes (sequences) that share a similarity path between them, where each edge between elements ALPHA and BETA in that path:
        * Is sourced from no less than ALPHA's length, less the tolerance
        * Is targeted to no less than BETA's length, less the tolerance
        * The difference between ALPHA and beta's length is less than the tolerance 
    
    :param tolerance: Tolerance value. 
    """
    # Create new components
    components = ComponentFinder()
    
    LOG_MAJOR( "There are {} sequences.", len( model.sequences ) )
    
    # Iterate sequences
    for sequence_alpha in model.sequences:
        assert isinstance( sequence_alpha, LegoSequence )
        
        alpha_edges = model.edges.find_sequence( sequence_alpha )
        
        LOG_MAJOR( "Sequence {} contains {} edges.", sequence_alpha, len( alpha_edges ) )
        
        for edge in alpha_edges:
            source_difference = abs( edge.left.length - edge.left.sequence.length )
            destination_difference = abs( edge.right.length - edge.right.sequence.length )
            total_difference = abs( edge.left.sequence.length - edge.right.sequence.length )
            
            LOG_MAJOR( "{}", edge )
            LOG_MAJOR( "-- Source difference (={} e={} s={})", source_difference, edge.left.length, edge.left.sequence.length )
            LOG_MAJOR( "-- Destination difference (l={} e={} s={})", destination_difference, edge.right.length, edge.right.sequence.length )
            LOG_MAJOR( "-- Total difference (l={} s={} d={})", total_difference, edge.left.sequence.length, edge.right.sequence.length )
            
            if source_difference > tolerance \
                    or destination_difference > tolerance \
                    or total_difference > tolerance:
                LOG_MAJOR( "-- ==> REJECTED" )
                continue
            else:
                LOG_MAJOR( "-- ==> ACCEPTED" )
            
            beta = edge.opposite( sequence_alpha ).sequence
            LOG_MAJOR( "-- LINKS {} AND {}", sequence_alpha, beta )
            components.join( sequence_alpha, beta )
    
    # Create the components!
    totality = set()
    
    for index, sequence_list in enumerate( components.tabulate() ):
        model.components.add( LegoComponent( model, index, cast( List[LegoSequence], sequence_list ) ) )
        totality.update( sequence_list )
    
    # Create components for orphans
    for sequence in model.sequences:
        if sequence not in totality:
            LOG_MAJOR( "ORPHAN: {}", sequence )
            model.components.add( LegoComponent( model, len( model.components ), [sequence] ) )


def __detect_minor( model: LegoModel, tolerance: int ) -> None:
    """
    Finds the subsequence components, here termed the "minor" elements.
    
    Clause 1:
        Subsequences belong to the component of the sequence in which they reside.
        
    Clause 2:
        When one sequence of a component possesses an edge to a sequence of another component (an "entry").
        Subsequences of all sequences in that second component receive the first component, at the position of the entry.
    """
    sc = model.components
    
    if not sc:
        raise ValueError( "Cannot detect subsequence components because sequence components have not yet been calculated. Please calculate sequence components first." )
    
    entry_dict = defaultdict( dict )
    
    average_lengths = average_component_lengths( model )
    
    assert average_lengths
    
    for component in model.components:
        component.minor_subsequences = []
        
        for sequence in component.major_sequences:
            
            # Add the origin-al components
            component.minor_subsequences.append(LegoSubsequence(sequence, 1, sequence.length))
            
            for entering_edge in model.edges.find_sequence(sequence):
                opposite_side = entering_edge.opposite( sequence )
                opposite_sequence = opposite_side.sequence
                opposite_component = model.components.find_component_for_major_sequence(opposite_sequence)
                
                if opposite_component is None:
                    raise ImplementationError( "Sequence '{}' has no component!".format( opposite_sequence ) )
                
                if opposite_component != component:
                    # Entry from `component` into `opposite_component`
                    
                    # We'll get both ways around, but we're only interested in big to little transitions
                    if average_lengths[opposite_component] < average_lengths[component]:
                        continue
                    
                    # If we have an edge already, we use the larger one
                    # (We just use the side in the opposite component - we assume the side in the origin component will be roughly similar so ignore it)
                    existing_edge = entry_dict[component].get( opposite_component )
                    
                    if existing_edge is not None:
                        new_length = opposite_side.length
                        existing_length = existing_edge.side( opposite_component ).length
                        
                        if new_length > existing_length:
                            existing_edge = None
                    
                    if existing_edge is None:
                        LOG_MINOR( "FROM {} TO {} ACROSS {}", component, opposite_component, entering_edge )
                        entry_dict[component][opposite_component] = entering_edge
    
    # Now slice those sequences up!
    # Unfortunately we can't just relay the positions, since there will be shifts.
    # We need to use BLAST to work out the relationship between the genes.
    for component, opposing_dict in entry_dict.items():
        assert isinstance( component, LegoComponent )
        
        for other_component, entering_edge in opposing_dict.items():
            # `component` enters `other_component` via `edge`
            assert isinstance( other_component, LegoComponent )
            
            opposite_side: LegoSubsequence = entering_edge.opposite( component )
            
            # Flag the entry point into `other component`
            component.minor_subsequences.append( opposite_side )
            
            # Now iterate over the rest of the `other_component`
            to_do = set( other_component.major_sequences )
            
            # We did the first one though :)
            to_do.remove( opposite_side.sequence )
            done = set()
            done.add( opposite_side.sequence )
            
            LOG_MINOR( "flw. FOR {}".format( entering_edge ) )
            LOG_MINOR( "flw. ENTRY POINT IS {}".format( opposite_side ) )
            
            while to_do:
                # First we need to find an edge between something in the "done" set and something in the "to_do" set.
                # If multiple relationships are present, we use the largest one.
                edge, origin_seq, destination_seq = __find_largest_relationship( model, to_do, done )
                
                LOG_MINOR( "flw. FOLLOWING {}", edge )
                
                # Now we have our relationship, we can use it to calculate the offset
                left : LegoSubsequence= edge.side( origin_seq )
                right : LegoSubsequence = edge.side( destination_seq )
                LOG_MINOR( "flw. -- LEFT {} {}", left.start, left.end )
                LOG_MINOR( "flw. -- RIGHT {} {}", right.start, right.end )
                
                # Our origin is the part of the leading side which comprises our component
                msi = LegoSubsequence.list_union([x for x in component.minor_subsequences if x.sequence is origin_seq])
                origin_subsequences = left.intersection(msi)
                origin_start = origin_subsequences.start
                origin_end = origin_subsequences.end
                LOG_MINOR( "flw. -- ORIGIN {} {}", origin_start, origin_end )
                assert origin_start >= left.start, "The origin start ({}) cannot be before the left start ({}), but it is: {}".format( origin_start, left.start, origin_subsequences )
                assert origin_end <= left.end, "The origin end ({}) cannot be beyond the left end ({}), but it is: {}".format( origin_end, left.end, origin_subsequences )
                
                # The offset is the position in the edge pertaining to our origin
                offset_start = origin_start - left.start
                offset_end = origin_end - left.start  # We use just the `start` of the edge (TODO: a possible improvement might be to use something more advanced)
                LOG_MINOR( "flw. -- OFFSET {} {}", offset_start, offset_end )
                
                # The destination is the is slice of the trailing side, adding our original offset
                destination_start = right.start + offset_start
                destination_end = right.start + offset_end
                LOG_MINOR( "flw. -- DESTINATION {} {}", offset_start, offset_end )
                
                # Fix any small discrepancies
                destination_end, destination_start = __fit_to_range( destination_seq.length, destination_start, destination_end, tolerance )
                
                subsequence_list = LegoSubsequence( destination_seq, destination_start, destination_end )
                
                LOG_MINOR( "flw. -- SHIFTED {} {}", offset_start, offset_end )
                
                component.minor_subsequences.append( subsequence_list )
                
                to_do.remove( destination_seq )
                done.add( destination_seq )


def __fit_to_range( max_value: int, start: int, end: int, tolerance: int ) -> Tuple[int, int]:
    """
    Given a range "start..end" this tries to shift it such that it does not lie outside "1..max_value".
    """
    if end > max_value:
        subtract = min( end - max_value, start - 1 )
        
        if subtract > tolerance:
            MCMD.warning( "Fitting the subsequence to the new range results in a concerning ({}>{}) shift in position.".format( subtract, tolerance ) )
        
        LOG_MINOR( "fix. {}...{} SLIPS PAST {}, SUBTRACTING {}", start, end, max_value, subtract )
        end -= subtract
        start -= subtract
        
        if end > max_value:
            if (end - max_value) > tolerance:
                MCMD.warning( "Fitting the subsequence to the new range results in a concerning ({}>{}) excess in length.".format( end - max_value, tolerance ) )
            
            LOG_MINOR( "fix. -- FIXING TAIL." )
            end = max_value
        
        LOG_MINOR( "fix. -- FIXED TO {} {} OF {}", start, end, max_value )
    
    return end, start


def average_component_lengths( model: LegoModel ):
    average_lengths = { }
    
    for component in model.components:
        average_lengths[component] = array_helper.average( [x.length for x in component.major_sequences] )
    
    return average_lengths


def __find_largest_relationship( model: LegoModel, to_do: Set[LegoSequence], done: Set[LegoSequence] ) -> Tuple[LegoEdge, LegoSequence, LegoSequence]:
    candidate = None
    candidate_length = 0
    
    for sequence in done:
        for edge in model.edges.find_sequence( sequence ):
            op: LegoSubsequence = edge.opposite( sequence )
            
            if op.sequence in to_do:
                # We use just the `opposite` length of the edge - ASSUMING the origin is roughly the same
                if op.length > candidate_length:
                    candidate = edge, sequence, op.sequence
                    candidate_length = op.length
    
    if candidate is None:
        raise ValueError( "find_largest_relationship cannot find a relationship between the following sets. Set 1: {}. Set 2: {}.".format( to_do, done ) )
    
    return candidate
