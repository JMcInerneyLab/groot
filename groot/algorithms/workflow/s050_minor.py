"""
Components algorithms.

The only one publicly exposed is `detect`, so start there.
"""
import warnings
from collections import defaultdict
from typing import Dict, Optional, Set, Tuple, List

from groot import constants
from intermake import MCMD, Table, command
from mhelper import Logger, array_helper, string_helper

from groot.constants import STAGES, EChanges
from groot.data import Component, Edge, Model, Gene, Domain, global_view


LOG_MINOR = Logger( "comp.minor", False )
__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME

@command(folder = constants.F_CREATE)
def create_minor( tol: int ) -> EChanges:
    """
    Finds the subsequence components, here termed the "minor" elements.
    
    Clause 1:
        Subsequences belong to the component of the sequence in which they reside.
        
    Clause 2:
        When one sequence of a component possesses an edge to a sequence of another component (an "entry").
        Subsequences of all sequences in that second component receive the first component, at the position of the entry.
        
    Requisites: `create_major`
    
    :param tol:         Tolerance on overlap, in sites.
    """
    model = global_view.current_model()
    model.get_status( STAGES.MINOR_3 ).assert_create()
    
    average_lengths = __get_average_component_lengths( model )
    
    #
    # PHASE I.
    # We complete an `entry_dict`
    # - this is a dict, for components v components, of their longest spanning edges
    #
    entry_dict: Dict[Component, Dict[Component, Edge]] = defaultdict( dict )
    
    # Iterate the components
    for comp in model.components:
        LOG_MINOR( "~~~~~ {} ~~~~~", comp )
        comp.minor_domains = []
        
        # Iterate the major sequences
        for sequence in comp.major_genes:
            # Add the origin-al sequence
            comp.minor_domains.append( Domain( sequence, 1, sequence.length ) )
            
            # Iterate the edges of that sequence
            for edge in model.edges.find_gene( sequence ):
                same_side, oppo_side = edge.sides( sequence )
                
                # Discard edges with a mismatch < tolerance
                if abs( sequence.length - same_side.length ) > tol:
                    LOG_MINOR( "IGNORING: {}", edge )
                    continue
                
                LOG_MINOR( "ATTEMPTING: {}", edge )
                
                oppo_comp = model.components.find_component_for_major_gene( oppo_side.gene )
                
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
        assert isinstance( comp, Component )
        
        for oppo_comp, edge in oppo_dict.items():
            # `comp` enters `oppo_comp` via `edge`
            assert isinstance( oppo_comp, Component )
            assert isinstance( edge, Edge )
            
            same_side, oppo_side = edge.sides( comp )
            
            # Grab the entry point
            comp.minor_domains.append( oppo_side )
            
            # Now iterate over the rest of the `other_component`
            to_do = set( oppo_comp.major_genes )
            done = set()
            
            # We have added the entry point already
            to_do.remove( oppo_side.gene )
            done.add( oppo_side.gene )
            
            LOG_MINOR( "flw. FOR {}".format( edge ) )
            LOG_MINOR( "flw. ENTRY POINT IS {}".format( oppo_side ) )
            
            while to_do:
                # First we need to find an edge between something in the "done" set and something in the "to_do" set.
                # If multiple relationships are present, we use the largest one.
                edge, src_dom, dst_dom = __find_largest_relationship( model, done, to_do )
                to_do.remove( dst_dom.gene )
                done.add( dst_dom.gene )
                
                LOG_MINOR( "flw. FOLLOWING {}", edge )
                LOG_MINOR( "flw. -- SRC {} {}", src_dom.start, src_dom.end )
                LOG_MINOR( "flw. -- DST {} {}", dst_dom.start, dst_dom.end )
                
                # Now we have our relationship, we can use it to calculate the offset within the component
                src_comp_dom = comp.get_minor_domain_by_gene( src_dom.gene )
                LOG_MINOR( "flw. -- SRC-OWN {} {}", src_comp_dom.start, src_comp_dom.end )
                
                if src_comp_dom.start < src_dom.start - tol or src_comp_dom.end > src_dom.end + tol:
                    raise ValueError( "Cannot resolve components. The edge «{}» is smaller than the component boundary «{}» (less the tolerance «{}»). This is indicative of an earlier error in :func:`detect_major`. Component data follows:\n{}".format(
                            edge, src_comp_dom, tol, string_helper.dump_data( comp ) ) )
                
                # The offset is the position in the edge pertaining to our origin
                offset_start = src_comp_dom.start - src_dom.start
                offset_end = src_comp_dom.end - src_dom.start  # We use just the `start` of the edge (TODO: a possible improvement might be to use something more advanced)
                LOG_MINOR( "flw. -- OFFSET {} {}", offset_start, offset_end )
                
                # The destination is the is slice of the trailing side, adding our original offset
                destination_start = dst_dom.start + offset_start
                destination_end = dst_dom.start + offset_end
                LOG_MINOR( "flw. -- DESTINATION {} {}", offset_start, offset_end )
                
                # Fix any small discrepancies
                destination_end, destination_start = __fit_to_range( dst_dom.gene.length, destination_start, destination_end, tol )
                
                subsequence_list = Domain( dst_dom.gene, destination_start, destination_end )
                
                LOG_MINOR( "flw. -- SHIFTED {} {}", offset_start, offset_end )
                comp.minor_domains.append( subsequence_list )
    
    return EChanges.COMPONENTS


@command(folder = constants.F_DROP)
def drop_minor() -> EChanges:
    """
    Drops minor component information from model.
    """
    model = global_view.current_model()
    model.get_status( STAGES.MINOR_3 ).assert_drop()
    
    for comp in model.components:
        comp.minor_domains = None
    
    return EChanges.COMPONENTS


@command(folder = constants.F_SET)
def set_minor( component: Component, subsequences: List[Domain] ) -> EChanges:
    """
    Sets the minor subsequences of the component.
    
    :param component:           Component 
    :param subsequences:        Minor subsequences
    """
    model = global_view.current_model()
    model.get_status( STAGES.MINOR_3 ).assert_set()
    
    if component.minor_domains:
        raise ValueError( "minor_domains for this component «{}» already exist.".format( component ) )
    
    component.minor_domains = tuple( subsequences )
    
    return EChanges.COMPONENTS


@command( names = ["print_minor", "print_interlinks", "interlinks"], folder=constants.F_PRINT )
def print_minor( component: Optional[Component] = None, verbose: bool = False ) -> EChanges:
    """
    Prints the edges between the component subsequences.
    
    Each line is of the form:
    
        `FROM <minor> TO <major> [ <start> : <end> ] <length>`
        
    Where:
    
        `minor`  is the source component
        `major`  is the destination component
        `start`  is the average of the start of the destination entry point
        `end`    is the average of the end of the destination entry point
        `length` is the average length of the sequences in the destination 

    :param component: Component to print.
                      If not specified prints a summary of all components.
    :param verbose:   Print all the things!
    """
    model = global_view.current_model()
    
    if not model.components:
        raise ValueError( "Cannot print components because components have not been calculated." )
    
    if verbose:
        message = Table()
        
        if component:
            message.add_title( component )
        else:
            message.add_title( "all components" )
        
        message.add_row( "component", "origins", "destinations" )
        message.add_hline()
        
        for comp in model.components:
            assert isinstance( comp, Component )
            
            if component is not None and component is not comp:
                continue
            
            major_genes = string_helper.format_array( comp.major_genes, join = "\n" )
            minor_domains = string_helper.format_array( comp.minor_domains, join = "\n" )
            
            message.add_row( comp, major_genes, minor_domains )
        
        MCMD.print( message.to_string() )
    
    message = Table()
    
    if component:
        message.add_title( component )
    else:
        message.add_title( "all components" )
    
    average_lengths = __get_average_component_lengths( model )
    
    message.add_row( "source", "destination", "sequence", "seq-length", "start", "end", "edge-length" )
    message.add_hline()
    
    for comp in model.components:
        if component is not None and component is not comp:
            continue
        
        major_genes = list( comp.major_genes )
        
        for minor in model.components:
            if comp is minor:
                continue
            
            start = 0
            end = 0
            failed = False
            
            for sequence in major_genes:
                # subsequences that are in major sequence is a major sequence of major and are a minor subsequence of minor
                subsequences = [x for x in minor.minor_domains if x.sequence is sequence]
                
                if subsequences:
                    start += subsequences[0].start
                    end += subsequences[-1].end
                    
                    if component is not None:
                        message.add_row( minor, comp, sequence.accession, sequence.length, subsequences[0].start, subsequences[-1].end, subsequences[-1].end - subsequences[0].start )
                else:
                    failed = True
            
            if failed:
                continue
            
            start /= len( major_genes )
            end /= len( major_genes )
            
            message.add_row( minor, comp, "AVG*{}".format( len( major_genes ) ), round( average_lengths[comp] ), round( start ), round( end ), round( end - start ) )
    
    MCMD.print( message.to_string() )
    return EChanges.INFORMATION


def __get_average_component_lengths( model: Model ):
    """
    Obtains a dictionary detailing the average lengths of the sequences in each component.
    :return: Dictionary:
                key:    component
                value:  average length 
    """
    average_lengths = { }
    
    for component in model.components:
        average_lengths[component] = array_helper.average( [x.length for x in component.major_genes] )
    
    return average_lengths


def __find_largest_relationship( model: Model, done: Set[Gene], to_do: Set[Gene] ) -> Tuple[Edge, Domain, Domain]:
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
        for edge in model.edges.find_gene( sequence ):
            ori, op = edge.sides( sequence )
            
            if op.gene in to_do:
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
