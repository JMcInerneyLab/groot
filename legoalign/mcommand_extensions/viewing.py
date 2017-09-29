from typing import Callable, Iterable, List, Optional, TypeVar

from colorama import Fore, Style, Back

from legoalign.algorithms import components, fastaiser, tree, fuse
from legoalign.data.lego_model import LegoComponent
from legoalign.frontends.cli import cli_view, cli_view_utils
from legoalign.mcommand_extensions import generating, files
from mcommand import command
from mcommand.engine.environment import MCMD, MENV
from mcommand.engine.plugin import Plugin
from mcommand.helpers.table_draw import Table
from mcommand.visualisables.visualisable import IVisualisable
from mhelper import SwitchError, MEnum


T = TypeVar( "T" )



@command( names = [ "print_fasta", "fasta" ] )
def print_fasta( target: IVisualisable ):
    """
    Presents the FASTA sequences for an object.
    :param target:   Object to present.
    """
    MCMD.information( cli_view_utils.colour_fasta_ansi( fastaiser.to_fasta( target ), cli_view.current_model().site_type ) )


@command( names = [ "print_status", "status" ] )
def print_status():
    """
    Prints the status of the model. 
    :return: 
    """
    model = cli_view.current_model()
    
    p = [ ]
    r = [ ]
    r.append( Fore.MAGENTA + model.name + Fore.RESET )
    if model.file_name:
        r.append( model.file_name )
    else:
        r.append( "Model not saved." )
    r.append( "" )
    r.append( Fore.MAGENTA + "Sequences" + Fore.RESET )
    r.append( "Sequences:     {}".format( __get_status_line( p, model.sequences, lambda _: True, files.import_blast ) ) )
    r.append( "FASTA:         {}".format( __get_status_line( p, model.sequences, lambda x: x.site_array, files.import_fasta ) ) )
    r.append( "Components:    {}".format( __get_status_line( p, model.sequences, lambda x: x.component, generating.make_components ) ) )
    r.append( "" )
    r.append( Fore.MAGENTA + "Components" + Fore.RESET )
    r.append( "Components:    {}".format( __get_status_line( p, model.components, lambda x: True, generating.make_components ) ) )
    r.append( "Alignments:    {}".format( __get_status_line( p, model.components, lambda x: x.alignment, generating.make_alignment ) ) )
    r.append( "Trees:         {}".format( __get_status_line( p, model.components, lambda x: x.tree, generating.make_tree ) ) )
    r.append( "Consensus:     {}".format( __get_status_line( p, model.components, lambda x: x.consensus, generating.make_consensus ) ) )
    MCMD.print( "\n".join( r ) )


@command( names = [ "print_alignment", "alignment" ] )
def print_alignment( component: Optional[ LegoComponent ] = None ):
    """
    Prints the alignment for a component.
    :param component:   Component to print alignment for. If not specified prints all alignments.
    """
    to_do = cli_view_utils.get_component_list( component )
    
    for component_ in to_do:
        __print_header( component_ )
        if component_.alignment is None:
            raise ValueError( "No alignment is available for this component. Did you remember to run `align` first?" )
        else:
            MCMD.information( cli_view_utils.colour_fasta_ansi( component_.alignment, cli_view.current_model().site_type ) )


class EPrintTree( MEnum ):
    """
    :data NEWICK: Newick format
    :data ASCII:  ASCII diagram
    :data GUI:    Interactive diagram
    """
    NEWICK = 1
    ASCII = 2
    GUI = 3


@command( names = [ "print_consensus", "consensus" ] )
def print_consensus( component: Optional[ LegoComponent ] = None, view: EPrintTree = EPrintTree.ASCII ):
    """
    Prints the consensus tree for a component.
    
    :param view:        How to view the tree
    :param component:   Component to print. If not specified prints all trees.
    """
    print_tree( component = component, consensus = True, view = view )


@command( names = [ "print_tree", "tree" ] )
def print_tree( component: Optional[ LegoComponent ] = None, consensus: bool = False, view: EPrintTree = EPrintTree.ASCII ):
    """
    Prints the tree for a component.
    
    :param view:        How to view the tree
    :param consensus:   When set, prints the consensus tree.
    :param component:   Component to print. If not specified prints all trees.
    :return: 
    """
    to_do = cli_view_utils.get_component_list( component )
    
    for component_ in to_do:
        __print_header( component_ )
        target = component_.consensus if consensus else component_.tree
        
        if consensus:
            if not component_.consensus:
                MCMD.print( "No consensus tree for this component." )
                continue
            
            MCMD.information( "Consensus tree:\nSources     : '{}'\nIntersection: '{}'\n".format( ", ".join( str( x ) for x in component_.incoming_components() ), ", ".join( str( x ) for x in component_.consensus_intersection ) ) )
        
        if target is None:
            raise ValueError( "Cannot draw this tree because the tree has not yet been created. Please create the tree first." )
        
        model = cli_view.current_model()
        
        if view == EPrintTree.ASCII:
            tree_ = tree.tree_from_newick( target ).get_ascii( show_internal = True )
            colours = [ Fore.RED, Fore.GREEN, Fore.YELLOW, Fore.BLUE, Fore.MAGENTA, Fore.CYAN, Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX ]
            
            for sequence in model.sequences:
                colour = colours[ sequence.component.index % len( colours ) ]
                tree_ = tree_.replace( sequence.accession, colour + sequence.accession + Fore.RESET )
            
            MCMD.information( tree_ )
        elif view == EPrintTree.NEWICK:
            MCMD.information( target )
        elif view == EPrintTree.GUI:
            tree__ = tree.tree_from_newick( target )
            colours = [ "#C00000", "#00C000", "#C0C000", "#0000C0", "#C000C0", "#00C0C0", "#FF0000", "#00FF00", "#FFFF00", "#0000FF", "#FF00FF", "#00FFC0" ]
            
            for n in tree__.traverse():
                n.img_style[ "fgcolor" ] = "#000000"
            
            for node in tree__:
                sequence = model.find_sequence( node.name )
                node.img_style[ "fgcolor" ] = colours[ sequence.component.index % len( colours ) ]
            
            tree__.show()
        else:
            raise SwitchError( "view", view )


def __print_header( x ):
    if isinstance(x, LegoComponent):
        x = "COMPONENT {}".format(x)
    
    MCMD.information( "\n" + Back.BLUE + Fore.WHITE + "---------- {} ----------".format( x ) + Style.RESET_ALL )


@command( names = [ "print_interlinks", "interlinks" ] )
def component_edges( component: Optional[ LegoComponent ] = None ):
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

    :param component: Component to print. If not specified prints a summary of all components.    
    """
    model = cli_view.current_model()
    
    if not model.components:
        raise ValueError( "Cannot print minor components because components have not been calculated." )
    
    message = Table()
    
    average_lengths = components.average_component_lengths( model )
    
    if component:
        message.add_title( component )
    else:
        message.add_title( "all components" )
    
    message.add_row( "source", "destination", "sequence", "seq-length", "start", "end" )
    message.add_hline()
    
    for major in model.components:
        if component is not None and component is not major:
            continue
        
        major_sequences = list( major.major_sequences() )
        
        for minor in model.components:
            if major is minor:
                continue
            
            start = 0
            end = 0
            failed = False
            
            for sequence in major_sequences:
                subsequences = [ x for x in sequence.subsequences if minor in x.components ]
                
                if subsequences:
                    start += subsequences[ 0 ].start
                    end += subsequences[ -1 ].end
                    
                    if component is not None:
                        message.add_row( minor, major, sequence.accession, sequence.length, subsequences[ 0 ].start, subsequences[ -1 ].end )
                else:
                    failed = True
            
            if failed:
                continue
            
            start /= len( major_sequences )
            end /= len( major_sequences )
            
            message.add_row( minor, major, "AVG*{}".format( len( major_sequences ) ), round( average_lengths[ major ] ), round( start ), round( end ) )
    
    MCMD.print( message.to_string() )


@command( names = [ "print_components", "components" ] )
def print_components():
    """
    Prints the major components.
    
    Each line takes the form:
    
        `COMPONENT <major> = <sequences>`
        
    Where:
    
        `major` is the component name
        `sequences` is the list of components in that sequence
    
    """
    model = cli_view.current_model()
    
    if not model.components:
        raise ValueError( "Cannot print major components because components have not been calculated." )
    
    message = Table()
    
    message.add_title( "major elements of components" )
    message.add_row( "component", "major elements" )
    message.add_hline()
    
    for component in model.components:
        message.add_row( component, ", ".join( x.accession for x in component.major_sequences() ) )
    
    MCMD.print( message.to_string() )


def __get_status_line( target: List[ Plugin ], the_list: Iterable[ T ], test: Callable[ [ T ], bool ], plugin: Plugin ) -> str:
    assert isinstance( plugin, Plugin ), plugin
    total = 0
    filtered = 0
    
    for x in the_list:
        total += 1
        if test( x ):
            filtered += 1
    
    if filtered and filtered == total:
        style = Fore.GREEN
        suffix = ""
    else:
        if filtered == 0:
            style = Fore.RED
        else:
            style = Fore.YELLOW
        
        if not target:
            suffix = Fore.WHITE + Style.DIM + " - Consider running '{}'.".format( MENV.host.translate_name( plugin.name ) )
            target.append( plugin )
        else:
            suffix = ""
    
    return style + "{}/{}".format( filtered, total ) + suffix + Style.RESET_ALL


@command( names = [ "print_fusions", "fusions" ] )
def print_fusions():
    """
    Estimates model fusions. Does not affect the model.
    """
    results = [ ]
    
    __print_header("FUSIONS")
    model = cli_view.current_model()
    
    for fusion in fuse.find_fusion_events( model ):
        results.append( str( fusion ) )
    
    MCMD.information( "\n".join( results ) )
    