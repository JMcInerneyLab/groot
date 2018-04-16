"""
Components algorithms.

The only one publicly exposed is `detect`, so start there.
"""
from typing import List, cast

from groot.constants import STAGES
from groot.data import LegoModel, LegoSequence, LegoComponent
from mhelper import Logger, string_helper
from mhelper.component_helper import ComponentFinder


LOG_MAJOR = Logger( "comp.major", False )
LOG_MAJOR_V = Logger( "comp.major.v", False )
LOG_GRAPH = Logger( "comp.graph", False )


def drop_major( model: LegoModel ) -> int:
    """
    Drops all components from the model.
    The components are removed from :attr:`model.components`.
    
    :returns: Number of components removed.
    """
    model.get_status( STAGES.MAJOR_3 ).assert_drop()
    
    previous_count = len( model.components )
    model.components.clear()
    return previous_count


def create_major( model: LegoModel, tolerance: int, debug: bool ) -> None:
    """
    Detects model components.
    
    First step of finding the components.
    
    We classify each component as a set of "major" genes.
    
    Components are defined as sets of genes that share a similarity path between them, where each edge between element 𝓧 and 𝓨 in that path:
        * Is sourced from no less than 𝓧's length, less the tolerance
        * Is targeted to no less than 𝓨's length, less the tolerance
        * The difference between 𝓧 and 𝓨's length is less than the tolerance
        
    We'll grab the minor domains that this component extends into in the next step. 
    
    :param debug:       Assert the creation.
    :param model:       Model
    :param tolerance:   Tolerance value
    :returns:           Nothing, the components are written to :attr:`model.components`.
    """
    model.get_status( STAGES.MAJOR_3 ).assert_create()
    
    model.components.clear()
    
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


def __clear( model: LegoModel ) -> None:
    """
    Clears the components from the model.
    """
    model.components.clear()
