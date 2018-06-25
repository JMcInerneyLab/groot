"""
Algorithms for user-domains

Used for display, nothing to do with the model.
"""
from typing import Callable

from groot import constants
from intermake import MCMD, Theme, command
from mhelper import ansi, string_helper

from groot.data import Gene, global_view
from groot.constants import EChanges
from groot.utilities import cli_view_utils
from groot.utilities.extendable_algorithm import AlgorithmCollection


__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME
DAlgorithm = Callable[[Gene], str]
"""A delegate for a function that takes a sequence and an arbitrary parameter, and produces an list of domains."""

domain_algorithms = AlgorithmCollection( DAlgorithm, "Domain" )


@command( folder = constants.F_CREATE )
def create_domains( algorithm: domain_algorithms.Algorithm ):
    """
    Creates the domains.
    Existing domains are always replaced.
    Domains are only used for viewing and have no bearing on the actual calculations.
    
    :param algorithm:   Mode of domain generation. See `algorithm_help`.
    """
    model = global_view.current_model()
    if not model.genes:
        raise ValueError( "Cannot generate domains because there are no sequences." )
    
    model.user_domains.clear()
    
    for sequence in model.genes:
        for domain in algorithm( sequence ):
            model.user_domains.add( domain )
    
    MCMD.progress( "Domains created, there are now {} domains.".format( len( model.user_domains ) ) )
    
    return EChanges.DOMAINS


@command( folder = constants.F_DROP )
def drop_domains():
    """
    Removes the user-domains from the model.
    """
    model = global_view.current_model()
    model.user_domains.clear()


@command( names = ["print_domains", "domains"], folder = constants.F_PRINT )
def print_domains( algorithm: domain_algorithms.Algorithm ) -> EChanges:
    """
    Prints the genes (highlighting components).
    Note: Use :func:`print_fasta` or :func:`print_alignments` to show the actual sites.
    
    :param algorithm:      How to break up the sequences. See `algorithm_help`.
    """
    assert isinstance(algorithm, domain_algorithms.Algorithm), algorithm
    
    model = global_view.current_model()
    longest = max( x.length for x in model.genes )
    r = []
    
    for sequence in model.genes:
        minor_components = model.components.find_components_for_minor_gene( sequence )
        
        if not minor_components:
            minor_components = [None]
        
        for component_index, component in enumerate( minor_components ):
            if component_index == 0:
                r.append( sequence.accession.ljust( 20 ) )
            else:
                r.append( "".ljust( 20 ) )
            
            if component:
                r.append( cli_view_utils.component_to_ansi( component ) + " " )
            else:
                r.append( "Ø " )
            
            subsequences = __list_userdomains( sequence, algorithm )
            
            for subsequence in subsequences:
                components = model.components.find_components_for_minor_domain( subsequence )
                
                if component in components:
                    colour = cli_view_utils.component_to_ansi_back( component )
                else:
                    colour = ansi.BACK_LIGHT_BLACK
                
                size = max( 1, int( (subsequence.length / longest) * 80 ) )
                name = "{}-{}".format( subsequence.start, subsequence.end )
                
                r.append( colour +
                          ansi.DIM +
                          ansi.FORE_BLACK +
                          "▏" +
                          ansi.NORMAL +
                          string_helper.centre_align( name, size ) )
            
            r.append( Theme.RESET + "\n" )
        
        r.append( "\n" )
    
    MCMD.information( "".join( r ) )
    return EChanges.INFORMATION


def __list_userdomains( sequence: Gene, algorithm: domain_algorithms.Algorithm ):
    assert isinstance(algorithm, domain_algorithms.Algorithm), algorithm
    return algorithm( sequence )
