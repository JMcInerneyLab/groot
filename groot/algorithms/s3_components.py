"""
Components algorithms.

The only one publicly exposed is `detect`, so start there.
"""
from collections import defaultdict
from typing import Tuple, Set, cast, List, Dict

from groot.data.lego_model import LegoModel, LegoSequence, LegoComponent, LegoEdge, LegoSubsequence
from intermake.engine.environment import MCMD
from mhelper import Logger, ImplementationError, array_helper, string_helper, ansi, NotFoundError
from mhelper.component_helper import ComponentFinder


LOG_MAJOR = Logger( "comp.major", False )
LOG_MAJOR_V = Logger( "comp.major.v", False )
LOG_MINOR = Logger( "comp.minor", False )
LOG_GRAPH = Logger( "comp.graph", False )


def detect( model: LegoModel, major_tol: int, minor_tol: int, debug: bool ) -> None:
    """
    Detects model components.
    See :function:`ext_generating.create_components` for parameter details.
    
    :returns: nothing, the components are written to :attr:`model.components`.
    """
    if not model.sequences:
        raise ValueError( "Cannot perform component detection because the model has no sequences." )
    
    __clear( model )
    __detect_major( model, major_tol, debug )
    __detect_minor( model, minor_tol, debug )


def drop( model: LegoModel ) -> int:
    """
    Drops all components from the model.
    The components are removed from :attr:`model.components`.
    
    :returns: Number of components removed.
    """
    if model.fusion_events:
        raise ValueError( "Refusing to drop the components because there are already fusion events which depend on them. Did you mean to drop the fusion events first?" )
    
    if model.nrfg:
        raise ValueError( "Refusing to drop the components because there is already an NRFG which depends on them. Did you mean to drop the NRFG first?" )
    
    previous_count = len( model.components )
    __clear( model )
    return previous_count


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


def __clear( model: LegoModel ) -> None:
    """
    Clears the components from the model.
    """
    model.components.clear()


def __detect_major( model: LegoModel, tolerance: int, debug: bool ) -> None:
    """
    First step of finding the components.
    
    We classify each component as a set of "major" genes.
    
    Components are defined as sets of genes that share a similarity path between them, where each edge between element 𝓧 and 𝓨 in that path:
        * Is sourced from no less than 𝓧's length, less the tolerance
        * Is targeted to no less than 𝓨's length, less the tolerance
        * The difference between 𝓧 and 𝓨's length is less than the tolerance
        
    We'll grab the minor domains that this component extends into in the next step. 
    
    :param model:       Model
    :param tolerance:   Tolerance value 
    """
    # Find connected components
    components = ComponentFinder()
    
    # Basic assertions
    LOG_MAJOR( "There are {} sequences.", len( model.sequences ) )
    missing_edges = []
    
    for sequence in model.sequences:
        edges = model.edges.find_sequence( sequence )
        
        if not edges:
            missing_edges.append( sequence )
    
    if missing_edges:
        raise ValueError( "Refusing to detect components because some sequences have no edges: «{}»".format( string_helper.format_array( missing_edges ) ) )
    
    # Iterate sequences
    for sequence_alpha in model.sequences:
        assert isinstance( sequence_alpha, LegoSequence )
        
        alpha_edges = model.edges.find_sequence( sequence_alpha )
        any_accept = False
        
        LOG_MAJOR( "Sequence {} contains {} edges.", sequence_alpha, len( alpha_edges ) )
        
        for edge in alpha_edges:
            source_difference = abs( edge.left.length - edge.left.sequence.length )
            destination_difference = abs( edge.right.length - edge.right.sequence.length )
            total_difference = abs( edge.left.sequence.length - edge.right.sequence.length )
            
            LOG_MAJOR_V( "{}", edge )
            LOG_MAJOR_V( "-- Source difference ({})", source_difference )
            LOG_MAJOR_V( "-- Destination difference ({})", destination_difference )
            LOG_MAJOR_V( "-- Total difference ({})", total_difference )
            
            if source_difference > tolerance:
                LOG_MAJOR_V( "-- ==> REJECTED (SOURCE)" )
                continue
            elif destination_difference > tolerance:
                LOG_MAJOR_V( "-- ==> REJECTED (DEST)" )
                continue
            elif total_difference > tolerance:
                LOG_MAJOR_V( "-- ==> REJECTED (TOTAL)" )
                continue
            else:
                LOG_MAJOR_V( "-- ==> ACCEPTED" )
            
            if debug and edge.left.sequence.accession[0] != edge.right.sequence.accession[0]:
                raise ValueError( "Debug assertion failed. This edge not rejected: {}".format( edge ) )
            
            any_accept = True
            beta = edge.opposite( sequence_alpha ).sequence
            LOG_MAJOR( "-- {:<40} LINKS {:<5} AND {:<5}", edge, sequence_alpha, beta )
            components.join( sequence_alpha, beta )
        
        if debug and not any_accept:
            raise ValueError( "Debug assertion failed. This sequence has no good edges: {}".format( sequence_alpha ) )
    
    # Create the components!
    sequences_in_components = set()
    
    for index, sequence_list in enumerate( components.tabulate() ):
        model.components.add( LegoComponent( model, index, cast( List[LegoSequence], sequence_list ) ) )
        LOG_MAJOR( "COMPONENT MAJOR: {}", sequence_list )
        sequences_in_components.update( sequence_list )
    
    # Create components for orphans
    for sequence in model.sequences:
        if sequence not in sequences_in_components:
            LOG_MAJOR( "ORPHAN: {}", sequence )
            model.components.add( LegoComponent( model, len( model.components ), [sequence] ) )


def __detect_minor( model: LegoModel, tolerance: int, debug: bool ) -> None:
    """
    Finds the subsequence components, here termed the "minor" elements.
    
    Clause 1:
        Subsequences belong to the component of the sequence in which they reside.
        
    Clause 2:
        When one sequence of a component possesses an edge to a sequence of another component (an "entry").
        Subsequences of all sequences in that second component receive the first component, at the position of the entry.
    """
    
    if not model.components:
        raise ValueError( "Cannot detect subsequence components because sequence components have not yet been calculated. Please calculate sequence components first." )
    
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
