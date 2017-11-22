"""
Components algorithms.

The only one publicly exposed is `detect`, so start there.
"""
from collections import defaultdict
from typing import Tuple, Set

from groot.algorithms import editor
from groot.data.lego_model import LegoModel, LegoSequence, LegoComponent, LegoSide, LegoEdge
from intermake.engine.mandate import Mandate
from mhelper import Logger, ImplementationError, array_helper
from mhelper.component_helper import ComponentFinder


LOG_MAJOR = Logger( "component.major", False )
LOG_MINOR = Logger( "component.minor", False ) 

def detect( e:Mandate,model: LegoModel, tolerance: int ) -> None:
    """
    Detects sequence and subsequence components.
    """
    if not model.sequences:
        raise ValueError("Cannot perform component detection because the model has no sequences.")
    
    __clear( e,model )
    __detect_major(e, model, tolerance )
    __detect_minor( e,model, tolerance )


def __clear( _:Mandate,model: LegoModel ):
    """
    Clears the components from the model.
    """
    model.components.clear()
    
    for sequence in model.sequences:
        sequence.component = None
    
    for subsequence in model.all_subsequences():
        subsequence.components.clear()


def __detect_major(_:Mandate, model: LegoModel, tolerance: int ) -> None:
    """
    Finds the sequence components, here termed the "major" elements.
    
    Defined as genes that share a similarity path between them, where each edge between elements ALPHA and BETA in that path:
        * Is sourced from no less than ALPHA's length, less the tolerance
        * Is targeted to no less than BETA's length, less the tolerance
        * The difference between ALPHA and beta's length is less than the tolerance 
    
    :param tolerance: Tolerance value. 
    """
    # Create new components
    components = ComponentFinder()
    
    LOG_MAJOR( "There are {} sequences.", len( model.sequences ) )
    
    for sequence_alpha in model.sequences:
        
        LOG_MAJOR( "Sequence {} contains {} edges.", sequence_alpha, len( sequence_alpha.all_edges() ) )
        
        for edge in sequence_alpha.all_edges():
            source_difference       = abs( edge.left.length - edge.left.sequence.length )
            destination_difference  = abs( edge.right.length - edge.right.sequence.length )
            total_difference        = abs( edge.left.sequence.length - edge.right.sequence.length )

            LOG_MAJOR( "{}", edge )
            LOG_MAJOR( "-- Source difference (={} e={} s={})", source_difference, edge.left.length, edge.left.sequence.length )
            LOG_MAJOR( "-- Destination difference (l={} e={} s={})", destination_difference, edge.right.length, edge.right.sequence.length )
            LOG_MAJOR( "-- Total difference (l={} s={} d={})", total_difference, edge.left.sequence.length, edge.right.sequence.length )
            
            if                                              \
                       source_difference      > tolerance   \
                    or destination_difference > tolerance   \
                    or total_difference       > tolerance:
                
                LOG_MAJOR( "-- ==> REJECTED" )
                continue
            else:
                LOG_MAJOR( "-- ==> ACCEPTED" )


            beta = edge.opposite( sequence_alpha ).sequence
            LOG_MAJOR( "-- LINKS {} AND {}", sequence_alpha, beta )
            components.join( sequence_alpha, beta )

    for index, sequence_list in enumerate( components.tabulate() ):
        component = LegoComponent( model, index )
        model.components.append( component )
    
        for sequence in sequence_list:  # type: LegoSequence
            sequence.component = component
            
    # Create components for orphans
    for sequence in model.sequences:
        if sequence.component is None:
            LOG_MAJOR( "ORPHAN: {}", sequence )
            component = LegoComponent( model, len(model.components) )
            model.components.append( component )
            sequence.component = component


def __detect_minor( e:Mandate,model: LegoModel, tolerance : int ) -> None:
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
    
    for sequence in model.sequences:
        component = sequence.component
        
        # Add the original components
        for subsequence in sequence.subsequences:
            subsequence.components.add( component )
        
        for entering_edge in sequence.all_edges():
            opposite_side       = entering_edge.opposite(sequence)
            opposite_sequence   = opposite_side.sequence
            opposite_component  = opposite_sequence.component
            
            if opposite_component is None:
                raise ImplementationError("Sequence '{}' has no component!".format(opposite_sequence))

            if opposite_component != component:
                # Entry from `component` into `opposite_component`
    
                # We'll get both ways around, but we're only interested in big to little transitions
                if average_lengths[ opposite_component ] < average_lengths[ component ]:
                    continue
    
                # If we have an edge already, we use the larger one
                # (We just use the side in the opposite component - we assume the side in the origin component will be roughly similar so ignore it)
                existing_edge = entry_dict[ component ].get( opposite_component )
    
                if existing_edge is not None:
                    new_length = opposite_side.length
                    existing_length = existing_edge.side( opposite_component ).length
        
                    if new_length > existing_length:
                        existing_edge = None
    
                if existing_edge is None:
                    LOG_MINOR("FROM {} TO {} ACROSS {}", component, opposite_component, entering_edge)
                    entry_dict[ component ][ opposite_component ] = entering_edge

    # Now slice those sequences up!
    # Unfortunately we can't just relay the positions, since there will be shifts.
    # We need to use BLAST to work out the relationship between the genes.
    for component, opposing_dict in entry_dict.items():
        for other_component, entering_edge in opposing_dict.items():
            # `component` enters `other_component` via `edge`
            assert isinstance( other_component, LegoComponent )
        
            opposite_side = entering_edge.opposite( component )  # type: LegoSide
        
            # Flag the entry point into `other component`
            for subsequence in opposite_side:
                subsequence.components.add( component )
        
            # Now iterate over the rest of the `other_component`
            to_do = set( other_component.major_sequences() )
        
            # We did the first one though :)
            to_do.remove( opposite_side.sequence )
            done = set()
            done.add( opposite_side.sequence )
            
            LOG_MINOR("flw. FOR {}".format(entering_edge))
            LOG_MINOR("flw. ENTRY POINT IS {}".format(opposite_side))
        
            while to_do:
                # First we need to find an edge between something in the "done" set and something in the "to_do" set.
                # If multiple relationships are present, we use the largest one.
                edge, origin_seq, destination_seq = __find_largest_relationship( to_do, done )
                
                LOG_MINOR("flw. FOLLOWING {}",edge)
            
                # Now we have our relationship, we can use it to calculate the offset
                left  = edge.side( origin_seq )
                right = edge.side( destination_seq )
                LOG_MINOR("flw. -- LEFT {} {}",left.start, left.end)
                LOG_MINOR("flw. -- RIGHT {} {}",right.start, right.end)
                
                # Our origin is the part of the leading side which comprises our component
                origin_subsequences     = [x for x in left if component in x.components]  # TODO: "left" or "left.subsequences"?
                origin_start            = origin_subsequences[0].start
                origin_end              = origin_subsequences[-1].end
                LOG_MINOR("flw. -- ORIGIN {} {}",origin_start, origin_end)
                assert origin_start >= left.start, "The origin start ({}) cannot be before the left start ({}), but it is: {}".format(origin_start, left.start, origin_subsequences) 
                assert origin_end <= left.end, "The origin end ({}) cannot be beyond the left end ({}), but it is: {}".format(origin_end, left.end, origin_subsequences)
                
                # The offset is the position in the edge pertaining to our origin
                offset_start                   = origin_start - left.start
                offset_end                     = origin_end   - left.start # We use just the `start` of the edge (TODO: a possible improvement might be to use something more advanced)
                LOG_MINOR("flw. -- OFFSET {} {}",offset_start, offset_end)
                
                # The destination is the is slice of the trailing side, adding our original offset
                destination_start   = right.start + offset_start
                destination_end     = right.start + offset_end
                LOG_MINOR("flw. -- DESTINATION {} {}",offset_start, offset_end)
                
                # Fix any small discrepancies
                destination_end, destination_start = __fit_to_range( e, destination_seq.length, destination_start, destination_end, tolerance )
                
                subsequence_list = editor.make_subsequence( destination_seq, destination_start, destination_end, None, allow_resize = False )
                
                LOG_MINOR("flw. -- SHIFTED {} {}",offset_start, offset_end)

                for subsequence in subsequence_list:
                    subsequence.components.add( component )

                to_do.remove( destination_seq )
                done.add( destination_seq )


def __fit_to_range( e:Mandate,max_value:int, start:int, end :int,tolerance:int)->Tuple[int,int]:
    """
    Given a range "start..end" this tries to shift it such that it does not lie outside "1..max_value".
    """
    if end > max_value:
        subtract = min(end - max_value, start-1)
        
        if subtract > tolerance:
            e.warning("Fitting the subsequence to the new range results in a concerning ({}>{}) shift in position.".format(subtract,tolerance))
        
        LOG_MINOR("fix. {}...{} SLIPS PAST {}, SUBTRACTING {}",start,end,max_value,subtract)
        end -= subtract
        start -= subtract
        
        if end > max_value:
            if (end - max_value) > tolerance:
                e.warning("Fitting the subsequence to the new range results in a concerning ({}>{}) excess in length.".format(end - max_value,tolerance))
            
            LOG_MINOR("fix. -- FIXING TAIL.")
            end = max_value
            
        LOG_MINOR("fix. -- FIXED TO {} {} OF {}",start,end,max_value)
                
    return end, start


def average_component_lengths( model: LegoModel ):
    average_lengths = { }
    
    for component in model.components:
        average_lengths[ component ] = array_helper.average( [ x.length for x in component.major_sequences() ] )
    
    return average_lengths


def __find_largest_relationship( to_do: Set[ LegoSequence ], done: Set[ LegoSequence ] ) -> Tuple[ LegoEdge, LegoSequence, LegoSequence ]:
    candidate = None
    candidate_length = 0
    
    for sequence in done:
        for edge in sequence.all_edges():
            op = edge.opposite( sequence )
            if op.sequence in to_do:
                # We use just the `opposite` length of the edge - ASSUMING the origin is roughly the same
                if op.length > candidate_length:
                    candidate = edge, sequence, op.sequence
                    candidate_length = op.length
    
    if candidate is None:
        raise ValueError( "find_largest_relationship cannot find a relationship between the following sets. Set 1: {}. Set 2: {}.".format( to_do, done ) )
    
    return candidate
