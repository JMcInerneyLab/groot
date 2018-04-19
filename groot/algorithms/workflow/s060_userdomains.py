"""
Algorithms for user-domains

Used for display, nothing to do with the model.
"""
from typing import Callable
from intermake import MCMD, Theme, command
from mhelper import ansi, string_helper

from groot.data import LegoSequence, global_view
from groot.constants import EChanges
from groot.utilities import cli_view_utils
from groot.utilities.extendable_algorithm import AlgorithmCollection


DAlgorithm = Callable[[LegoSequence, int], str]
"""A delegate for a function that takes a sequence and an arbitrary parameter, and produces an list of domains."""

domain_algorithms = AlgorithmCollection[DAlgorithm]( "Domain" )


@command()
def create_domains( algorithm: str, param: int = 0 ):
    """
    Creates the domains.
    Existing domains are always replaced.
    Domains are only used for viewing and have no bearing on the actual calculations.
    
    :param algorithm:   Mode of domain generation. See `algorithm_help`.
    :param param:       Parameter for mode. 
    """
    model = global_view.current_model()
    if not model.sequences:
        raise ValueError( "Cannot generate domains because there are no sequences." )
    
    model.user_domains.clear()
    
    fn = domain_algorithms[algorithm]
    
    for sequence in model.sequences:
        for domain in fn( sequence, param ):
            model.user_domains.add( domain )
    
    MCMD.progress( "Domains created, there are now {} domains.".format( len( model.user_domains ) ) )
    
    return EChanges.DOMAINS


@command()
def drop_domains():
    """
    Removes the user-domains from the model.
    """
    model = global_view.current_model()
    model.user_domains.clear()


@command( names = ["print_domains", "domains"] )
def print_domains( domain: str = "", parameter: int = 0 ) -> EChanges:
    """
    Prints the genes (highlighting components).
    Note: Use :func:`print_fasta` or :func:`print_alignments` to show the actual sites.
    
    :param domain:      How to break up the sequences. See `algorithm_help`.
    :param parameter:   Parameter on `domain`. 
    """
    
    model = global_view.current_model()
    longest = max( x.length for x in model.sequences )
    r = []
    
    for sequence in model.sequences:
        minor_components = model.components.find_components_for_minor_sequence( sequence )
        
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
            
            subsequences = __list_userdomains( sequence, domain, parameter )
            
            for subsequence in subsequences:
                components = model.components.find_components_for_minor_subsequence( subsequence )
                
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


def __list_userdomains( sequence: LegoSequence, algorithm: str, param: int ):
    fn = domain_algorithms[algorithm]
    return fn( sequence, param )
