"""
Components algorithms.

The only one publicly exposed is `detect`, so start there.
"""
import warnings
from collections import defaultdict
from typing import Dict, Set, Tuple
from mhelper import Logger, array_helper, string_helper

from groot.constants import STAGES
from groot.data import LegoSubsequence, LegoModel, LegoEdge, LegoSequence, LegoComponent


LOG_MINOR = Logger( "comp.minor", False )


def drop_minor( model: LegoModel ):
    model.get_status( STAGES.MINOR_3 ).assert_drop()
    
    for comp in model.components:
        comp.minor_subsequences = None


def create_minor( model: LegoModel, tolerance: int ) -> None:
    """
    Finds the subsequence components, here termed the "minor" elements.
    
    Clause 1:
        Subsequences belong to the component of the sequence in which they reside.
        
    Clause 2:
        When one sequence of a component possesses an edge to a sequence of another component (an "entry").
        Subsequences of all sequences in that second component receive the first component, at the position of the entry.
    """
    model.get_status( STAGES.MINOR_3 ).assert_create()
    
    average_lengths = get_average_component_lengths( model )
    
    #
    # PHASE I.
    # We complete an `entry_dict`
    # - this is a dict, for components v components, of their longest spanning edges
    #
    entry_dict: Dict[LegoComponent, Dict[LegoComponent, LegoEdge]] = defaultdict( dict )
    
    # Iterate the components
    for comp in model.components:
        LOG_MINOR( "~~~~~ {} ~~~~~", comp )
        comp.minor_subsequences = []
        
        # Iterate the major sequences
        for sequence in comp.major_sequences:
            # Add the origin-al sequence
            comp.minor_subsequences.append( LegoSubsequence( sequence, 1, sequence.length ) )
            
            # Iterate the edges of that sequence
            for edge in model.edges.find_sequence( sequence ):
                same_side, oppo_side = edge.sides( sequence )
                
                # Discard edges with a mismatch < tolerance
                if abs( sequence.length - same_side.length ) > tolerance:
                    LOG_MINOR( "IGNORING: {}", edge )
                    continue
                
                LOG_MINOR( "ATTEMPTING: {}", edge )
                
                oppo_comp = model.components.find_component_for_major_sequence( oppo_side.sequence )
                
                if oppo_comp != comp:
                    # We have found an entry from `comp` into `oppo_comp`
                    
                    # We'll get both ways around, so filter to deal with the big to little transitions
                    if average_lengths[oppo_comp] < average_lengths[comp]:
                        continue
                    
                    # If we have an edge already, we use the larger one
                    # (We just use the side in the opposite component - we assume the side in the origin component will be roughly similar so ignore it)
                    existing_edge = entry_dict[comp].get( oppo_comp )
                    
                    if existing_edge is not None:
                        new_length = oppo_side.length
                        existing_length = existing_edge.side( oppo_comp ).length
                        
                        if new_length > existing_length:
                            existing_edge = None
                    
                    if existing_edge is None:
                        LOG_MINOR( "FROM {} TO {} ACROSS {}", comp, oppo_comp, edge )
                        entry_dict[comp][oppo_comp] = edge
    
    #
    # PHASE II.
    # Now slice those sequences up!
    # Unfortunately we can't just relay the positions, since there will be small shifts.
    # We need to use BLAST to work out the relationship between the genes.
    #
    for comp, oppo_dict in entry_dict.items():
        assert isinstance( comp, LegoComponent )
        
        for oppo_comp, edge in oppo_dict.items():
            # `comp` enters `oppo_comp` via `edge`
            assert isinstance( oppo_comp, LegoComponent )
            assert isinstance( edge, LegoEdge )
            
            same_side, oppo_side = edge.sides( comp )
            
            # Grab the entry point
            comp.minor_subsequences.append( oppo_side )
            
            # Now iterate over the rest of the `other_component`
            to_do = set( oppo_comp.major_sequences )
            done = set()
            
            # We have added the entry point already
            to_do.remove( oppo_side.sequence )
            done.add( oppo_side.sequence )
            
            LOG_MINOR( "flw. FOR {}".format( edge ) )
            LOG_MINOR( "flw. ENTRY POINT IS {}".format( oppo_side ) )
            
            while to_do:
                # First we need to find an edge between something in the "done" set and something in the "to_do" set.
                # If multiple relationships are present, we use the largest one.
                edge, src_dom, dst_dom = __find_largest_relationship( model, done, to_do )
                to_do.remove( dst_dom.sequence )
                done.add( dst_dom.sequence )
                
                LOG_MINOR( "flw. FOLLOWING {}", edge )
                LOG_MINOR( "flw. -- SRC {} {}", src_dom.start, src_dom.end )
                LOG_MINOR( "flw. -- DST {} {}", dst_dom.start, dst_dom.end )
                
                # Now we have our relationship, we can use it to calculate the offset within the component
                src_comp_dom = comp.get_minor_subsequence_by_sequence( src_dom.sequence )
                LOG_MINOR( "flw. -- SRC-OWN {} {}", src_comp_dom.start, src_comp_dom.end )
                
                if src_comp_dom.start < src_dom.start - tolerance or src_comp_dom.end > src_dom.end + tolerance:
                    raise ValueError( "Cannot resolve components. The edge «{}» is smaller than the component boundary «{}» (less the tolerance «{}»). This is indicative of an earlier error in :func:`detect_major`. Component data follows:\n{}".format(
                            edge, src_comp_dom, tolerance, string_helper.dump_data( comp ) ) )
                
                # The offset is the position in the edge pertaining to our origin
                offset_start = src_comp_dom.start - src_dom.start
                offset_end = src_comp_dom.end - src_dom.start  # We use just the `start` of the edge (TODO: a possible improvement might be to use something more advanced)
                LOG_MINOR( "flw. -- OFFSET {} {}", offset_start, offset_end )
                
                # The destination is the is slice of the trailing side, adding our original offset
                destination_start = dst_dom.start + offset_start
                destination_end = dst_dom.start + offset_end
                LOG_MINOR( "flw. -- DESTINATION {} {}", offset_start, offset_end )
                
                # Fix any small discrepancies
                destination_end, destination_start = __fit_to_range( dst_dom.sequence.length, destination_start, destination_end, tolerance )
                
                subsequence_list = LegoSubsequence( dst_dom.sequence, destination_start, destination_end )
                
                LOG_MINOR( "flw. -- SHIFTED {} {}", offset_start, offset_end )
                comp.minor_subsequences.append( subsequence_list )


def get_average_component_lengths( model: LegoModel ):
    """
    Obtains a dictionary detailing the average lengths of the sequences in each component.
    :return: Dictionary:
                key:    component
                value:  average length 
    """
    average_lengths = { }
    
    for component in model.components:
        average_lengths[component] = array_helper.average( [x.length for x in component.major_sequences] )
    
    return average_lengths


def __find_largest_relationship( model: LegoModel, done: Set[LegoSequence], to_do: Set[LegoSequence] ) -> Tuple[LegoEdge, LegoSubsequence, LegoSubsequence]:
    """
    In the `done` set we search for the widest edge to the `to_do` set.
    
    We define "widest" as the longest side on the destination (`to_do` set), assuming the edge source (`done` set) is roughly similar.
    :param model:   Model 
    :param done:    Set 
    :param to_do:   Set 
    :return: A tuple:
                0: The longest edge
                1: The side of the edge in the `done` set
                2: The side of the edge in the `to_do` set 
    """
    candidate = None
    candidate_length = 0
    
    for sequence in done:
        for edge in model.edges.find_sequence( sequence ):
            ori, op = edge.sides( sequence )
            
            if op.sequence in to_do:
                if op.length > candidate_length:
                    candidate = edge, ori, op
                    candidate_length = op.length
    
    if candidate is None:
        raise ValueError( "find_largest_relationship cannot find a relationship between the following sets. Set 1: {}. Set 2: {}.".format( to_do, done ) )
    
    return candidate


def __fit_to_range( max_value: int, start: int, end: int, tolerance: int ) -> Tuple[int, int]:
    """
    Given a range "start..end" this tries to shift it such that it does not lie outside "1..max_value".
    """
    if end > max_value:
        subtract = min( end - max_value, start - 1 )
        
        if subtract > tolerance:
            warnings.warn( "Fitting the subsequence to the new range results in a concerning ({}>{}) shift in position.".format( subtract, tolerance ), UserWarning )
        
        LOG_MINOR( "fix. {}...{} SLIPS PAST {}, SUBTRACTING {}", start, end, max_value, subtract )
        end -= subtract
        start -= subtract
        
        if end > max_value:
            if (end - max_value) > tolerance:
                warnings.warn( "Fitting the subsequence to the new range results in a concerning ({}>{}) excess in length.".format( end - max_value, tolerance ), UserWarning )
            
            LOG_MINOR( "fix. -- FIXING TAIL." )
            end = max_value
        
        LOG_MINOR( "fix. -- FIXED TO {} {} OF {}", start, end, max_value )
    
    return end, start
