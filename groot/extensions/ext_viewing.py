import os
from os import path
from typing import Callable, Iterable, List, Optional, TypeVar

import pyperclip

import intermake
from groot.algorithms import alignment, components, fastaiser, graph_viewing, tree, userdomains
from groot.algorithms.classes import FusionPoint
from groot.constants import EFormat, EOut
from groot.data import global_view
from groot.data.lego_model import ILegoVisualisable, LegoComponent
from groot.extensions import ext_files, ext_generating
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.gui_view_support import EDomainFunction
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import MCMD, MENV, Plugin, Table, Theme, command, help_command, visibilities
from mgraph import MGraph
from mhelper import ByRef, Filename, MOptional, SwitchError, ansi, file_helper, string_helper


__mcmd_folder_name__ = "Viewing"

T = TypeVar( "T" )


@help_command( names = ["algorithm_help", "print_algorithms", "algorithms"] )
def algorithm_help():
    """
    Prints available algorithms.
    """
    r = []
    for module in (tree, alignment):
        r.append( "" )
        r.append( Theme.TITLE + "========== " + module.__name__ + " ==========" + Theme.RESET )
        
        for name, function in module.algorithms.items():
            if name != "default":
                r.append( "    " + Theme.COMMAND_NAME + name + Theme.RESET )
                r.append( "    " + (function.__doc__ or "").strip() )
                r.append( "" )
        
        r.append( "" )
    
    return "\n".join( r )


@command( names = ["print_fasta", "fasta"] )
def print_fasta( target: ILegoVisualisable ) -> EChanges:
    """
    Presents the FASTA sequences for an object.
    :param target:   Object to present.
    """
    MCMD.information( cli_view_utils.colour_fasta_ansi( fastaiser.to_fasta( target ), global_view.current_model().site_type ) )
    return EChanges.INFORMATION


@command( names = ["print_status", "status"], highlight = True )
def print_status() -> EChanges:
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
    r.append( "Components:    {}".format( __get_status_line( p, model.sequences, lambda x: model.components.has_sequence( x ), ext_generating.make_components ) ) )
    r.append( "" )
    r.append( Theme.HEADING + "Components" + Theme.RESET )
    r.append( "Components:    {}".format( __get_status_line( p, model.components, lambda x: True, ext_generating.make_components ) ) )
    r.append( "Alignments:    {}".format( __get_status_line( p, model.components, lambda x: x.alignment, ext_generating.make_alignments ) ) )
    r.append( "Trees:         {}".format( __get_status_line( p, model.components, lambda x: x.tree, ext_generating.make_trees ) ) )
    r.append( "" )
    r.append( Theme.HEADING + "NRFG" + Theme.RESET )
    r.append( "Fusion points: {}".format( __get_status_line( p, [model], lambda x: x.fusion_events, ext_generating.make_fusions ) ) )
    r.append( "Fusion graph : {}".format( __get_status_line( p, [model], lambda x: x.nrfg, ext_generating.make_nrfg ) ) )
    MCMD.print( "\n".join( r ) )
    return EChanges.INFORMATION


@command( names = ["print_alignments", "alignments"] )
def print_alignments( component: Optional[List[LegoComponent]] = None, x = 1, n = 0 ) -> EChanges:
    """
    Prints the alignment for a component.
    :param component:   Component to print alignment for. If not specified prints all alignments.
    :param x:           Starting index (where 1 is the first site).
    :param n:           Number of sites to display. If zero a number of sites appropriate to the current UI will be determined.
    """
    to_do = cli_view_utils.get_component_list( component )
    m = global_view.current_model()
    
    if not n:
        n = MENV.host.console_width - 5
    
    for component_ in to_do:
        MCMD.print( graph_viewing.print_header( component_ ) )
        if component_.alignment is None:
            raise ValueError( "No alignment is available for this component. Did you remember to run `align` first?" )
        else:
            MCMD.information( cli_view_utils.colour_fasta_ansi( component_.alignment, m.site_type, m, x, n ) )
    
    return EChanges.INFORMATION


@help_command()
def print_help() -> str:
    """
    Help on tree-node formatting.
    """
    r = ["The following substitutions are made in the node format string.", ""]
    
    for method_name in dir( graph_viewing.FORMATTER ):
        if not method_name.startswith( "_" ) and callable( getattr( graph_viewing.FORMATTER, method_name ) ):
            r.append( "`[{}]`".format( method_name ) )
            doc = (getattr( graph_viewing.FORMATTER, method_name ).__doc__ or "Not documented :(").strip()
            r.extend( doc.split( "\n" ) )
    
    for i in range( len( r ) ):
        r[i] = r[i].strip()
    
    return "\n".join( r )


@command( names = ["print", "print_trees", "trees", "print_tree", "tree"] )
def print_trees( graph: Optional[MGraph] = None,
                 view: EFormat = EFormat.ASCII,
                 format: str = None,
                 out: EOut = EOut.DEFAULT,
                 file: MOptional[Filename] = None ) -> EChanges:
    """
    Prints trees or graphs
    
    :param file:        File to write the output to.
    :param out:         Output.
    :param graph:       What to print. See `specify_graph_help` for details.
                        All graphs are printed if nothing is specified.
    :param format:      How to format the nodes. See `print_help`.
    :param view:        How to view the tree.
    """
    model = global_view.current_model()
    trees = []
    
    if file:
        if out not in (EOut.DEFAULT, EOut.FILE, EOut.FILEOPEN):
            raise ValueError( "Cannot specify both the `out` and `file` parameters." )
        
        if out == EOut.DEFAULT:
            out = EOut.FILE
    elif out == EOut.DEFAULT:
        if view in (EFormat.VISJS, EFormat.HTML, EFormat.SVG):
            out = EOut.OPEN
        else:
            out = EOut.NORMAL
    
    if graph is None:
        for component_ in model.components:
            if component_.tree:
                trees.append( (str( component_ ), component_.tree) )
            else:
                MCMD.print( "I cannot draw the tree for component «{}» because it has not yet been generated.".format( component_ ) )
                continue
        
        if model.nrfg:
            trees.append( (str( "NRFG" ), model.nrfg.graph) )
    else:
        name = "unknown"
        
        for component in model.components:
            if graph is component.tree:
                name = str( component )
        
        if model.nrfg is not None and graph is model.nrfg.graph:
            name = "NRFG"
        
        trees.append( (name, graph) )
    
    text = graph_viewing.create( format, trees, model, view )
    
    if out == EOut.NORMAL:
        MCMD.information( text )
    elif out == EOut.STDOUT:
        print( text )
    elif out == EOut.CLIP:
        pyperclip.copy( text )
        MCMD.information( "Output copied to clipboard." )
    elif out == EOut.FILE:
        file_helper.write_all_text( file, text )
    elif out == EOut.OPEN:
        extension = { EFormat.ASCII    : ".txt",
                      EFormat.DEBUG    : ".txt",
                      EFormat.NEWICK   : ".nwk",
                      EFormat.ETE_ASCII: ".txt",
                      EFormat.ETE_GUI  : ".txt",
                      EFormat.SVG      : ".svg",
                      EFormat.HTML     : ".html",
                      EFormat.CSV      : ".csv",
                      EFormat.VISJS    : ".html" }[view]
        file_name = path.join( MENV.local_data.local_folder( intermake.constants.FOLDER_TEMPORARY ), "groot_temporary{}".format( extension ) )
        file_helper.write_all_text( file_name, text )
        os.system( "open \"{}\"".format( file_name ) )
    elif out == EOut.FILEOPEN:
        file_helper.write_all_text( file, text )
        os.system( "open \"{}\"".format( file ) )
    else:
        raise SwitchError( "out", out )
    
    return EChanges.INFORMATION


@command( names = ["print_interlinks", "interlinks"] )
def print_component_edges( component: Optional[LegoComponent] = None, verbose: bool = False ) -> EChanges:
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
    :param verbose:   Print everything!
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
        
        for major in model.components:
            assert isinstance( major, LegoComponent )
            
            if component is not None and component is not major:
                continue
            
            major_seq = string_helper.format_array( major.major_sequences, join = "\n" )
            minor_seq = string_helper.format_array( major.minor_subsequences, join = "\n" )
            
            message.add_row( major, major_seq, minor_seq )
        
        MCMD.print( message.to_string() )
    
    message = Table()
    
    if component:
        message.add_title( component )
    else:
        message.add_title( "all components" )
    
    average_lengths = components.get_average_component_lengths( model )
    
    message.add_row( "source", "destination", "sequence", "seq-length", "start", "end", "edge-length" )
    message.add_hline()
    
    for major in model.components:
        if component is not None and component is not major:
            continue
        
        major_sequences = list( major.major_sequences )
        
        for minor in model.components:
            if major is minor:
                continue
            
            start = 0
            end = 0
            failed = False
            
            for sequence in major_sequences:
                # subsequences that are in major sequence is a major sequence of major and are a minor subsequence of minor
                subsequences = [x for x in minor.minor_subsequences if x.sequence is sequence]
                
                if subsequences:
                    start += subsequences[0].start
                    end += subsequences[-1].end
                    
                    if component is not None:
                        message.add_row( minor, major, sequence.accession, sequence.length, subsequences[0].start, subsequences[-1].end, subsequences[-1].end - subsequences[0].start )
                else:
                    failed = True
            
            if failed:
                continue
            
            start /= len( major_sequences )
            end /= len( major_sequences )
            
            message.add_row( minor, major, "AVG*{}".format( len( major_sequences ) ), round( average_lengths[major] ), round( start ), round( end ), round( end - start ) )
    
    MCMD.print( message.to_string() )
    return EChanges.INFORMATION


@command( names = ["print_edges", "edges"] )
def print_edges() -> EChanges:
    """
    Prints model edges
    """
    
    model = global_view.current_model()
    
    for edge in model.edges:
        MCMD.print( str( edge ) )
    
    return EChanges.NONE


@command( names = ["print_sequences", "sequences"] )
def print_sequences( domain: EDomainFunction = EDomainFunction.COMPONENT, parameter: int = 0 ) -> EChanges:
    """
    Prints the sequences (as components)
    
    :param domain:      How to break up the sequences 
    :param parameter:   Parameter on `domain` 
    :return: 
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
            
            subsequences = userdomains.sequence_by_enum( sequence, domain, parameter )
            
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


@command( names = ["print_components", "components"] )
def print_components( verbose: bool = False ) -> EChanges:
    """
    Prints the major components.
    
    Each line takes the form:
    
        `COMPONENT <major> = <sequences>`
        
    Where:
    
        `major` is the component name
        `sequences` is the list of components in that sequence
        
    :param verbose: Print verbose information
    
    """
    model = global_view.current_model()
    
    if not model.components:
        raise ValueError( "Cannot print major components because components have not been calculated." )
    
    message = Table()
    
    message.add_title( "major elements of components" )
    message.add_row( "component", "major elements" )
    message.add_hline()
    
    for component in model.components:
        message.add_row( component, ", ".join( x.accession for x in component.major_sequences ) )
    
    MCMD.print( message.to_string() )
    
    return EChanges.INFORMATION | print_component_edges( verbose = verbose )


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
def print_fusions() -> EChanges:
    """
    Estimates model fusions. Does not affect the model.
    
    :param verbose: Verbose output
    """
    results: List[str] = []
    
    model = global_view.current_model()
    
    for event in model.fusion_events:
        results.append( "- name               {}".format( event ) )
        results.append( "  component a        {}".format( event.component_a ) )
        results.append( "  component b        {}".format( event.component_b ) )
        results.append( "  component c        {}".format( event.component_c ) )
        results.append( "  index              {}".format( event.index ) )
        results.append( "  products           {}".format( string_helper.format_array( event.products ) ) )
        results.append( "  future products    {}".format( string_helper.format_array( event.future_products ) ) )
        results.append( "  points             {}".format( string_helper.format_array( event.points ) ) )
        
        for point in event.points:
            results.append( "     -   name               {}".format( point ) )
            results.append( "         component          {}".format( point.component ) )
            results.append( "         count              {}".format( point.count ) )
            results.append( "         outer sequences    {}".format( string_helper.format_array( point.outer_sequences ) ) )
            results.append( "         pertinent inner    {}".format( string_helper.format_array( point.pertinent_inner ) ) )
            results.append( "         pertinent outer    {}".format( string_helper.format_array( point.pertinent_outer ) ) )
            results.append( "         sequences          {}".format( string_helper.format_array( point.sequences ) ) )
            results.append( "" )
        
        results.append( "" )
    
    MCMD.information( "\n".join( results ) )
    
    return EChanges.INFORMATION


@command( visibility = visibilities.ADVANCED )
def groot():
    """
    Displays the application version.
    """
    MCMD.print( "I AM {}. VERSION {}.".format( MENV.name, MENV.version ) )
