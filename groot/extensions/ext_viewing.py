from typing import Callable, Iterable, List, Optional, TypeVar, Set

from intermake import command, MCMD, MENV, Plugin, Table, IVisualisable
from intermake.engine.theme import Theme

from mhelper import MEnum, SwitchError, string_helper, ByRef, ansi

from groot.algorithms import components, fastaiser, fuse
from groot.data import global_view
from groot.data.lego_model import LegoComponent, LegoSubsequence
from groot.frontends import ete_providers
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.gui_view_utils import Changes
from groot.extensions import ext_files, ext_generating


__mcmd_folder_name__ = "Viewing"

T = TypeVar( "T" )


@command( names = ["print_fasta", "fasta"] )
def print_fasta( target: IVisualisable ) -> Changes:
    """
    Presents the FASTA sequences for an object.
    :param target:   Object to present.
    """
    MCMD.information( cli_view_utils.colour_fasta_ansi( fastaiser.to_fasta( target ), global_view.current_model().site_type ) )
    return Changes( Changes.INFORMATION )


@command( names = ["print_status", "status"] )
def print_status() -> Changes:
    """
    Prints the status of the model. 
    :return: 
    """
    model = global_view.current_model()
    
    p = ByRef[bool]( False )
    r = []
    r.append( Theme.HEADING + "Model" + Theme.RESET )
    r.append( "Project name:  {}".format( __get_status_line_comment( bool( model.sequences ), p, ext_files.import_blast, model.name ) ) )
    r.append( "File name:     {}".format( __get_status_line_comment( model.file_name is not None, p, ext_files.file_save, model.file_name if model.file_name else "Unsaved" ) ) )
    r.append( "" )
    r.append( Theme.HEADING + "Sequences" + Theme.RESET )
    r.append( "Sequences:     {}".format( __get_status_line( p, model.sequences, lambda _: True, ext_files.import_blast ) ) )
    r.append( "FASTA:         {}".format( __get_status_line( p, model.sequences, lambda x: x.site_array, ext_files.import_fasta ) ) )
    r.append( "Components:    {}".format( __get_status_line( p, model.sequences, lambda x: x.component, ext_generating.make_components ) ) )
    r.append( "" )
    r.append( Theme.HEADING + "Components" + Theme.RESET )
    r.append( "Components:    {}".format( __get_status_line( p, model.components, lambda x: True, ext_generating.make_components ) ) )
    r.append( "Alignments:    {}".format( __get_status_line( p, model.components, lambda x: x.alignment, ext_generating.make_alignment ) ) )
    r.append( "Trees:         {}".format( __get_status_line( p, model.components, lambda x: x.tree, ext_generating.make_tree ) ) )
    r.append( "Consensus:     {}".format( __get_status_line( p, model.components, lambda x: x.consensus, ext_generating.make_consensus ) ) )
    r.append( "" )
    r.append( Theme.HEADING + "NRFG" + Theme.RESET )
    r.append( "Fusion points: {}".format( __get_status_line( p, [model], lambda x: x.fusion_events, ext_generating.make_fusions ) ) )
    MCMD.print( "\n".join( r ) )
    return Changes( Changes.INFORMATION )


@command( names = ["print_alignment", "alignment"] )
def print_alignment( component: Optional[List[LegoComponent]] = None ) -> Changes:
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
            MCMD.information( cli_view_utils.colour_fasta_ansi( component_.alignment, global_view.current_model().site_type ) )
    
    return Changes( Changes.INFORMATION )


class EPrintTree( MEnum ):
    """
    :data NEWICK:       Newick format
    :data ASCII:        ASCII diagram
    :data ETE_GUI:      Interactive diagram, provided by Ete. Is also available in CLI.
    :data ETE_ASCII:    ASCII, provided by Ete
    """
    NEWICK = 1
    ASCII = 2
    ETE_GUI = 3
    ETE_ASCII = 4


@command( names = ["print_consensus", "consensus"] )
def print_consensus( component: Optional[List[LegoComponent]] = None, view: EPrintTree = EPrintTree.ASCII ) -> Changes:
    """
    Prints the consensus tree for a component.
    
    :param view:        How to view the tree
    :param component:   Component to print. If not specified prints all trees.
    """
    print_tree( component = component, consensus = True, view = view )
    
    return Changes( Changes.INFORMATION )


@command( names = ["print_tree", "tree"] )
def print_tree( component: Optional[LegoComponent] = None, consensus: bool = False, view: EPrintTree = EPrintTree.ASCII, format: str = "a c m f" ) -> Changes:
    """
    Prints the tree for a component.
    
    :param format:      Format string when view = ASCII.
                        `u`: Node UID
                        `a`: Sequence accession
                        `l`: Sequence length
                        `c`: Component
                        `f`: Fusion
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
        
        model = global_view.current_model()
        
        if view == EPrintTree.ASCII:
            MCMD.information( target.to_ascii( format ) )
        elif view == EPrintTree.ETE_ASCII:
            MCMD.information( ete_providers.tree_to_ascii( target, model ) )
        elif view == EPrintTree.NEWICK:
            MCMD.information( target.to_newick() )
        elif view == EPrintTree.ETE_GUI:
            ete_providers.show_tree( target, model )
        else:
            raise SwitchError( "view", view )
    
    return Changes( Changes.INFORMATION )


def __print_header( x ):
    if isinstance( x, LegoComponent ):
        x = "COMPONENT {}".format( x )
    
    MCMD.information( "\n" + Theme.TITLE + "---------- {} ----------".format( x ) + Theme.RESET )


@command( names = ["print_interlinks", "interlinks"] )
def print_component_edges( component: Optional[LegoComponent] = None ) -> Changes:
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
    model = global_view.current_model()
    
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
                subsequences = [x for x in sequence.subsequences if minor in x.components]
                
                if subsequences:
                    start += subsequences[0].start
                    end += subsequences[-1].end
                    
                    if component is not None:
                        message.add_row( minor, major, sequence.accession, sequence.length, subsequences[0].start, subsequences[-1].end )
                else:
                    failed = True
            
            if failed:
                continue
            
            start /= len( major_sequences )
            end /= len( major_sequences )
            
            message.add_row( minor, major, "AVG*{}".format( len( major_sequences ) ), round( average_lengths[major] ), round( start ), round( end ) )
    
    MCMD.print( message.to_string() )
    return Changes( Changes.INFORMATION )


@command( names = ["print_sequences", "sequences"] )
def print_sequences() -> Changes:
    """
    Prints the sequences (as components)
    """
    
    model = global_view.current_model()
    longest = max( x.length for x in model.sequences )
    r = []
    
    
    def ___get_seq_msg( component_index: int, num: int, counter: int, component: LegoComponent, last_components: Set[LegoComponent] ):
        if counter == 0:
            return
        
        if component in last_components:
            x = component.str_ansi_back()
        else:
            x = ansi.BACK_LIGHT_BLACK
        
        size = max( 1, int( (counter / longest) * 80 ) )
        
        r.append( x + ansi.DIM + ansi.FORE_BLACK + ("▏" if num else " ") + ansi.NORMAL + string_helper.centre_align( str( counter ) if component_index == 0 else (" " * len( str( counter ) )), size ) + " " )
    
    
    for sequence in model.sequences:
        for component_index, component in enumerate( sequence.minor_components() ):
            if component_index == 0:
                r.append( sequence.accession.ljust( 20 ) )
            else:
                r.append( "".ljust( 20 ) )
            
            r.append( component.str_ansi + " " )
            
            last_components = None
            counter = 0
            num = 0
            
            for subsequence in sequence.subsequences:
                if last_components is None:
                    last_components = subsequence.components
                
                if subsequence.components != last_components:
                    ___get_seq_msg( component_index, num, counter, component, last_components )
                    num += 1
                    last_components = subsequence.components
                    counter = 0
                else:
                    counter += subsequence.length
            
            ___get_seq_msg( component_index, num, counter, component, last_components )
            
            r.append( Theme.RESET + "\n" )
        
        r.append( "\n" )
    
    MCMD.information( "".join( r ) )
    return Changes( Changes.INFORMATION )


@command( names = ["print_components", "components"] )
def print_components() -> Changes:
    """
    Prints the major components.
    
    Each line takes the form:
    
        `COMPONENT <major> = <sequences>`
        
    Where:
    
        `major` is the component name
        `sequences` is the list of components in that sequence
    
    """
    model = global_view.current_model()
    
    if not model.components:
        raise ValueError( "Cannot print major components because components have not been calculated." )
    
    message = Table()
    
    message.add_title( "major elements of components" )
    message.add_row( "component", "major elements" )
    message.add_hline()
    
    for component in model.components:
        message.add_row( component, ", ".join( x.accession for x in component.major_sequences() ) )
    
    MCMD.print( message.to_string() )
    
    print_component_edges()
    
    return Changes( Changes.INFORMATION )


def __get_status_line( warned: ByRef[bool], the_list: Iterable[T], test: Callable[[T], bool], plugin: Plugin ) -> str:
    assert isinstance( plugin, Plugin ), plugin
    total = 0
    filtered = 0
    
    for x in the_list:
        total += 1
        if test( x ):
            filtered += 1
    
    return __get_status_line_comment( filtered and filtered == total, warned, plugin, "{}/{}".format( filtered, total ) )


def __get_status_line_comment( is_done: bool, warned: ByRef[bool], plugin: Optional[Plugin], message ):
    if not is_done:
        if not warned.value and plugin is not None:
            warned.value = True
            return Theme.STATUS_NO + message + Theme.COMMENT + " - Consider running " + Theme.COMMAND_NAME + MENV.host.translate_name( plugin.name ) + Theme.RESET
        else:
            return Theme.STATUS_NO + message + Theme.RESET
    else:
        return Theme.STATUS_YES + message + Theme.RESET


@command( names = ["print_fusions", "fusions"] )
def print_fusions() -> Changes:
    """
    Estimates model fusions. Does not affect the model.
    """
    results: List[str] = []
    
    model = global_view.current_model()
    
    for fusion_event in model.fusion_events:
        results.append( "{}".format( fusion_event ) )
        results.append( "" )
        
        for fusion_point in fusion_event.points_a:
            results.append( "  •  {}".format( fusion_point ) )
        
        results.append( "" )
        
        for fusion_point in fusion_event.points_b:
            results.append( "  •  {}".format( fusion_point ) )
        
        results.append( "" )
        results.append( "" )
    
    MCMD.information( "\n".join( results ) )
    return Changes( Changes.INFORMATION )
