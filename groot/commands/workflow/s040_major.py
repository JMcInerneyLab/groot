"""
Components algorithms.

The only one publicly exposed is `detect`, so start there.
"""
from typing import List, Optional
from intermake import pr
from mhelper import ComponentFinder, Logger, string_helper

import warnings

from groot.application import app
from groot import constants
from groot.constants import EChanges, STAGES
from groot.data import Component, Edge, Gene, global_view

LOG_MAJOR = Logger( "comp.major", False )
LOG_MAJOR_V = Logger( "comp.major.v", False )
LOG_GRAPH = Logger( "comp.graph", False )


@app.command( folder = constants.F_CREATE )
def create_major( tol: int = 0, debug: bool = False ) -> EChanges:
    """
    Detects model components.
    
    First step of finding the components.
    
    We classify each component as a set of "major" genes.
    
    Components are defined as sets of genes that share a similarity path between them, where each edge between element 𝓧 and 𝓨 in that path:
        * Is sourced from no less than 𝓧's length, less the tolerance
        * Is targeted to no less than 𝓨's length, less the tolerance
        * The difference between 𝓧 and 𝓨's length is less than the tolerance
        
    We'll grab the minor domains that this component extends into in the next step.
    
    Requisites: Sequence similarity (BLAST data) must have been loaded 
    
    :param debug:       Assert the creation.
    :param tol:         Tolerance value
    :returns:           Nothing, the components are written to :ivar:`model.components`.
    """
    model = global_view.current_model()
    model.get_status( STAGES.MAJOR_4 ).assert_create()
    
    model.components.clear()
    
    # Find connected components
    components = ComponentFinder()
    
    # Basic assertions
    LOG_MAJOR( "There are {} sequences.", len( model.genes ) )
    missing_edges = []
    
    for sequence in model.genes:
        edges = model.edges.find_gene( sequence )
        
        if not edges:
            missing_edges.append( sequence )
    
    if missing_edges:
        raise ValueError( "Refusing to detect components because some sequences have no edges: «{}»".format( string_helper.format_array( missing_edges ) ) )
    
    # Iterate sequences
    for sequence_alpha in model.genes:
        assert isinstance( sequence_alpha, Gene )
        
        alpha_edges = model.edges.find_gene( sequence_alpha )
        any_accept = False
        
        LOG_MAJOR( "Sequence {} contains {} edges.", sequence_alpha, len( alpha_edges ) )
        
        for edge in alpha_edges:
            assert isinstance( edge, Edge )
            source_difference = abs( edge.left.length - edge.left.gene.length )
            destination_difference = abs( edge.right.length - edge.right.gene.length )
            total_difference = abs( edge.left.gene.length - edge.right.gene.length )
            
            LOG_MAJOR_V( "{}", edge )
            LOG_MAJOR_V( "-- Source difference ({})", source_difference )
            LOG_MAJOR_V( "-- Destination difference ({})", destination_difference )
            LOG_MAJOR_V( "-- Total difference ({})", total_difference )
            
            if source_difference > tol:
                LOG_MAJOR_V( "-- ==> REJECTED (SOURCE)" )
                continue
            elif destination_difference > tol:
                LOG_MAJOR_V( "-- ==> REJECTED (DEST)" )
                continue
            elif total_difference > tol:
                LOG_MAJOR_V( "-- ==> REJECTED (TOTAL)" )
                continue
            else:
                LOG_MAJOR_V( "-- ==> ACCEPTED" )
            
            if debug and edge.left.gene.accession[0] != edge.right.gene.accession[0]:
                raise ValueError( "Debug assertion failed. This edge not rejected: {}".format( edge ) )
            
            any_accept = True
            beta = edge.opposite( sequence_alpha ).gene
            LOG_MAJOR( "-- {:<40} LINKS {:<5} AND {:<5}", edge, sequence_alpha, beta )
            components.join( sequence_alpha, beta )
        
        if debug and not any_accept:
            raise ValueError( "Debug assertion failed. This sequence has no good edges: {}".format( sequence_alpha ) )
    
    # Create the components!
    sequences_in_components = set()
    
    for index, sequence_list in enumerate( components.tabulate() ):
        model.components.add( Component( model, index, sequence_list ) )
        LOG_MAJOR( "COMPONENT MAJOR: {}", sequence_list )
        sequences_in_components.update( sequence_list )
    
    # Create components for orphans
    for sequence in model.genes:
        if sequence not in sequences_in_components:
            LOG_MAJOR( "ORPHAN: {}", sequence )
            model.components.add( Component( model, len( model.components ), (sequence,) ) )
    
    # An assertion
    for component in model.components:
        assert isinstance( component, Component )
        if len( component.major_genes ) == 1:
            warnings.warn( "There are components with just one sequence in them. Maybe you meant to use a tolerance higher than {}?".format( tol ), UserWarning )
            break
    
    pr.printx( "<verbose>{} components detected.</verbose>".format( len( model.components ) ) )
    
    return EChanges.COMPONENTS


@app.command( folder = constants.F_DROP )
def drop_major( components: Optional[List[Component]] = None ) -> EChanges:
    """
    Drops all components from the model.
    The components are removed from :ivar:`model.components`.
    
    :param components: Components to drop. If `None` then all components are dropped. 
    """
    model = global_view.current_model()
    model.get_status( STAGES.MAJOR_4 ).assert_drop()
    
    previous_count = len( model.components )
    
    if not components:
        model.components.clear()
    else:
        for component in components:
            model.components.remove( component )
    
    pr.printx( "<verbose>{} components dropped</verbose>".format( previous_count - len( model.components ) ) )
    
    return EChanges.COMPONENTS


@app.command( folder = constants.F_SET )
def set_major( genes: List[Gene] ):
    """
    Creates a major component (manually). 
    
    :param genes:   Components 
    :return:            Nothing is returned, the component is added to the model. 
    """
    
    model = global_view.current_model()
    model.get_status( STAGES.MAJOR_4 ).assert_set()
    
    for gene in genes:
        if model.components.find_component_for_major_gene( gene, default = None ) is not None:
            raise ValueError( "Refusing to create a component containing the gene «{}» because that gene is already assigned to a component.".format( gene ) )
    
    model.components.add( Component( model,
                                     len( model.components ),
                                     tuple( genes ) ) )
    
    return EChanges.COMPONENTS


@app.command( names = ["print_major", "major", "print_components", "components"], folder = constants.F_PRINT )
def print_major( verbose: bool = False ) -> EChanges:
    """
    Prints the major components.
    
    Each line takes the form:
    
        `COMPONENT <major> = <sequences>`
        
    Where:
    
        `major` is the component name
        `sequences` is the list of components in that sequence
        
    :param verbose: Print verbose information (only with `legacy` parameter)
    
    """
    model = global_view.current_model()
    
    if not model.components:
        raise ValueError( "Cannot print major components because components have not been calculated." )
    
    if verbose:
        for component in model.components:
            with pr.pr_section( component ):
                print( component.to_details() )
        
        return EChanges.INFORMATION
    
    rows = []
    rows.append( ["component", "major elements"] )
    
    for component in model.components:
        rows.append( [component, ", ".join( x.accession for x in component.major_genes )] )
    
    with pr.pr_section( "major elements of components" ):
        pr.pr_table( rows )
    
    return EChanges.INFORMATION
