"""
Components algorithms.

The only one publicly exposed is `detect`, so start there.
"""
from collections import defaultdict
from typing import Tuple, Set

from legoalign.algorithms import editor
from legoalign.LegoModels import LegoModel, LegoComponent, LegoSequence, LegoSide, LegoEdge
from mhelper import ArrayHelper
from mhelper.ExceptionHelper import ImplementationError
from mhelper.components import ComponentFinder


def detect( model: LegoModel, tolerance: int ) -> None:
    """
    Detects sequence and subsequence components.
    """
    __clear( model )
    __detect_major( model, tolerance )
    __detect_minor( model )


def __clear( model: LegoModel ):
    """
    Clears the components from the model.
    """
    model.components.clear()
    
    for sequence in model.sequences:
        sequence.component = None
    
    for subsequence in model.all_subsequences():
        subsequence.components.clear()


def __detect_major( model: LegoModel, tolerance: int ) -> None:
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
    
    for sequence_alpha in model.sequences:
        for edge in sequence_alpha.all_edges():
            source_difference       = abs( edge.source.length          - edge.source.sequence.length )
            destination_difference  = abs( edge.destination.length     - edge.destination.sequence.length )
            total_difference        = abs( edge.source.sequence.length - edge.destination.sequence.length )
            
            if                                              \
                       source_difference      > tolerance   \
                    or destination_difference > tolerance   \
                    or total_difference       > tolerance:
                
                continue

            beta = edge.opposite( sequence_alpha ).sequence
            print("{} and {}".format(sequence_alpha, beta))
            components.equate( sequence_alpha, beta )

    for index, sequence_list in enumerate( components.tabulate() ):
        component = LegoComponent( model, index )
        model.components.append( component )
    
        for sequence in sequence_list:  # type: LegoSequence
            sequence.component = component
            
    # Create components for orphans
    for sequence in model.sequences:
        if sequence.component is None:
            print("ORPHAN: {}".format(sequence))
            component = LegoComponent( model, len(model.components) )
            model.components.append( component )
            sequence.component = component


def __detect_minor( model: LegoModel ) -> None:
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
        
        for edge in sequence.all_edges():
            opposite_side       = edge.opposite(sequence)
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
                    entry_dict[ component ][ opposite_component ] = edge

    # Now slice those sequences up!
    # Unfortunately we can't just relay the positions, since there will be shifts.
    # We need to use BLAST to work out the relationship between the genes.
    for component, data in entry_dict.items():
        for other_component, edge in data.items():
            # `component` enters `other_component` via `edge`
            assert isinstance( other_component, LegoComponent )
        
            opposite_side = edge.opposite( component )  # type: LegoSide
        
            # Flag the entry point into `other component`
            for subsequence in opposite_side:
                subsequence.components.add( component )
        
            # Now iterate over the rest of the `other_component`
            to_do = set( other_component.major_sequences() )
        
            # We did the first one though :)
            to_do.remove( opposite_side.sequence )
            done = set()
            done.add( opposite_side.sequence )
        
            while to_do:
                # First we need to find an edge between something in the "done" set and something in the "to_do" set.
                # If multiple relationships are present, we use the largest one.
                edge_b, done_s, to_do_s = __find_largest_relationship( to_do, done )
            
                # Now we have our relationship, we can use it to calculate the offset
                # We use just the `start` of the edge (TODO: a possible improvement might be to use something more advanced)
                src = edge_b.side( done_s )
                dst = edge_b.side( to_do_s )
                
                source_subsequences             = [x for x in src.sequence.subsequences if component in x.components]
                source_entry_point_start        = source_subsequences[0].start
                source_offset                   = source_entry_point_start - src.start
                destination_entry_point_start   = dst.start + source_offset
                destination_entry_point_end     = dst.start + source_offset + source_subsequences[-1].end

                subsequence_list = editor.make_subsequence( to_do_s, destination_entry_point_start, destination_entry_point_end, None )

                for subsequence in subsequence_list:
                    subsequence.components.add( component )

                to_do.remove( to_do_s )
                done.add( to_do_s )


def average_component_lengths( model: LegoModel ):
    average_lengths = { }
    
    for component in model.components:
        average_lengths[ component ] = ArrayHelper.average( [ x.length for x in component.major_sequences() ] )
    
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
