from typing import List, Optional, TypeVar

from groot import constants
from groot.algorithms import alignment, components, graph_viewing, tree, userdomains
from groot.constants import EFormat, LegoStage
from groot.data import global_view
from groot.data.lego_model import ILegoVisualisable, LegoComponent, IHasFasta
from groot.extensions import ext_files, ext_generating
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.gui_view_support import EDomainFunction
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import MCMD, MENV, Table, Theme, cli_helper, command, help_command, visibilities
from mgraph import MGraph
from mhelper import ByRef, Filename, MOptional, ansi, io_helper, string_helper


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
    if isinstance( target, IHasFasta ):
        MCMD.information( cli_view_utils.colour_fasta_ansi( target.to_fasta(), global_view.current_model().site_type ) )
    else:
        MCMD.warning( "Target «{}» does not have FASTA data.".format( target ) )
    
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
    r.append( "Project name:  {}".format( model.name ) )
    r.append( "File name:     {}".format( __get_status( p, constants.STAGES.FILE_0, ext_files.file_save ) ) )
    p.value = False
    r.append( "" )
    r.append( Theme.HEADING + "Sequences" + Theme.RESET )
    r.append( "BLAST:         {}".format( __get_status( p, constants.STAGES.BLAST_1, ext_files.import_blast ) ) )
    r.append( "FASTA:         {}".format( __get_status( p, constants.STAGES.FASTA_2, ext_files.import_fasta ) ) )
    r.append( "" )
    r.append( Theme.HEADING + "Components" + Theme.RESET )
    r.append( "Components:    {}".format( __get_status( p, constants.STAGES.COMPONENTS_3, ext_generating.create_components ) ) )
    r.append( "Alignments:    {}".format( __get_status( p, constants.STAGES.ALIGNMENTS_5, ext_generating.create_alignments ) ) )
    r.append( "Trees:         {}".format( __get_status( p, constants.STAGES.TREES_6, ext_generating.create_trees ) ) )
    r.append( "" )
    r.append( Theme.HEADING + "NRFG" + Theme.RESET )
    r.append( "Fusion points: {}".format( __get_status( p, constants.STAGES.FUSIONS_7, ext_generating.create_fusions ) ) )
    r.append( "Candidates:    {}".format( __get_status( p, constants.STAGES.SPLITS_8, ext_generating.create_splits ) ) )
    r.append( "Viable:        {}".format( __get_status( p, constants.STAGES.CONSENSUS_9, ext_generating.create_consensus ) ) )
    r.append( "Leaf subsets:  {}".format( __get_status( p, constants.STAGES.SUBSETS_10, ext_generating.create_subsets ) ) )
    r.append( "Minigraphs:    {}".format( __get_status( p, constants.STAGES.SUBGRAPHS_11, ext_generating.create_subgraphs ) ) )
    r.append( "Sewed graph:   {}".format( __get_status( p, constants.STAGES.FUSED_12, ext_generating.create_fused ) ) )
    r.append( "Cleaned graph: {}".format( __get_status( p, constants.STAGES.CLEANED_13, ext_generating.create_cleaned ) ) )
    r.append( "Checked graph: {}".format( __get_status( p, constants.STAGES.CHECKED_14, ext_generating.create_checked ) ) )
    MCMD.print( "\n".join( r ) )
    return EChanges.INFORMATION


@command( names = ["print_alignments", "alignments"] )
def print_alignments( component: Optional[List[LegoComponent]] = None, x = 1, n = 0, file: str = "" ) -> EChanges:
    """
    Prints the alignment for a component.
    :param file:        File to write to. See `file_write_help`. If this is empty then colours and headings are also printed. 
    :param component:   Component to print alignment for. If not specified prints all alignments.
    :param x:           Starting index (where 1 is the first site).
    :param n:           Number of sites to display. If zero a number of sites appropriate to the current UI will be determined.
    """
    to_do = cli_view_utils.get_component_list( component )
    m = global_view.current_model()
    
    if not n:
        n = MENV.host.console_width - 5
    
    r = []
    
    colour = not file
    
    for component_ in to_do:
        if colour or len( to_do ) > 1:
            r.append( graph_viewing.print_header( component_ ) )
        
        if component_.alignment is None:
            raise ValueError( "No alignment is available for this component. Did you remember to run `align` first?" )
        else:
            if colour:
                r.append( cli_view_utils.colour_fasta_ansi( component_.alignment, m.site_type, m, x, n ) )
            else:
                r.append( component_.alignment )
    
    with io_helper.open_write( file ) as file_out:
        file_out.write( "\n".join( r ) + "\n" )
    
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


@command( names = ["print_trees", "trees"] )
def print_trees( graph: Optional[MGraph] = None,
                 format: EFormat = EFormat.ASCII,
                 file: MOptional[Filename] = None,
                 fnode: str = None
                 ) -> EChanges:
    """
    Prints trees or graphs
    
    :param file:       File to write the output to. See `file_write_help`.
    :param graph:      What to print. See `specify_graph_help` for details.
                       All graphs are printed if nothing is specified.
    :param fnode:      How to format the nodes. See `print_help`.
    :param format:     How to view the tree.
    """
    model = global_view.current_model()
    trees = []
    
    if graph is None:
        for component_ in model.components:
            if component_.tree:
                trees.append( (str( component_ ), component_.tree) )
            else:
                MCMD.print( "I cannot draw the tree for component «{}» because it has not yet been generated.".format( component_ ) )
                continue
        
        if model.nrfg.fusion_graph_clean:
            trees.append( (str( "NRFG" ), model.nrfg.fusion_graph_clean) )
    else:
        name = "unknown"
        
        for component in model.components:
            if graph is component.tree:
                name = str( component )
        
        if model.nrfg.fusion_graph_clean is not None and graph is model.nrfg.fusion_graph_clean:
            name = "NRFG"
        
        if model.nrfg.fusion_graph_unclean is not None and graph is model.nrfg.fusion_graph_unclean:
            name = "NRFG (unclean)"
        
        trees.append( (name, graph) )
    
    text = graph_viewing.create( fnode, trees, model, format )
    
    with io_helper.open_write( file, format.to_extension() ) as file_out:
        file_out.write( text + "\n" )
    
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
    Prints model edges.
    """
    
    model = global_view.current_model()
    
    for edge in model.edges:
        MCMD.print( str( edge ) )
    
    return EChanges.NONE


@command( names = ["print_genes", "genes"] )
def print_genes( domain: EDomainFunction = EDomainFunction.COMPONENT, parameter: int = 0 ) -> EChanges:
    """
    Prints the genes (highlighting components).
    Note: Use :func:`print_fasta` or :func:`print_alignments` to show the actual sites.
    
    :param domain:      How to break up the sequences.
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
        
    :param verbose: Print verbose information (only with `legacy` parameter)
    
    """
    model = global_view.current_model()
    
    if not model.components:
        raise ValueError( "Cannot print major components because components have not been calculated." )
    
    if verbose:
        for component in model.components:
            MCMD.print( cli_helper.format_title( component ) )
            MCMD.print( component.to_details() )
        
        return EChanges.INFORMATION
    
    message = Table()
    
    message.add_title( "major elements of components" )
    message.add_row( "component", "major elements" )
    message.add_hline()
    
    for component in model.components:
        message.add_row( component, ", ".join( x.accession for x in component.major_sequences ) )
    
    MCMD.print( message.to_string() )
    
    return EChanges.INFORMATION | print_component_edges()


def __get_status( warned: ByRef[bool], stage: LegoStage, incomplete, *, yes = None ):
    status = global_view.current_model().get_status( stage )
    
    if status.is_complete:
        r = Theme.STATUS_YES + (yes or str( status )) + Theme.RESET
    else:
        if status.is_partial:
            r = Theme.STATUS_INTERMEDIATE + str( status ) + Theme.RESET
        else:
            r = Theme.STATUS_NO + str( status ) + Theme.RESET
        
        if not warned.value:
            warned.value = True
            r += " - Consider running " + Theme.COMMAND_NAME + incomplete.__name__ + Theme.RESET
    
    return r


@command( names = ["print_fusions", "fusions"] )
def print_fusions() -> EChanges:
    """
    Estimates model fusions. Does not affect the model.
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


@command()
def print_candidates( component: Optional[LegoComponent] = None ) -> EChanges:
    """
    Prints NRFG candidate splits.
    :param component:   Component, or `None` for the global split set.
    """
    model = global_view.current_model()
    
    if component:
        for x in component.splits:
            MCMD.information( str( x ) )
    else:
        for x in model.nrfg.splits:
            MCMD.information( str( x ) )
    
    return EChanges.INFORMATION


@command()
def print_viable() -> EChanges:
    """
    Prints NRFG viable splits.
    """
    
    model = global_view.current_model()
    
    for x in model.nrfg.consensus:
        MCMD.information( str( x ) )
    
    return EChanges.INFORMATION


@command()
def print_subsets() -> EChanges:
    """
    Prints NRFG subsets.
    """
    model = global_view.current_model()
    
    for x in model.nrfg.subsets:
        MCMD.information( string_helper.format_array( x, sort = True, autorange = True ) )
    
    return EChanges.INFORMATION


@command()
def print_minigraphs() -> EChanges:
    """
    Prints the names of the NRFG minigraphs (you'll need to use `print_trees` to print the actual trees).
    """
    model = global_view.current_model()
    
    for i in range( len( model.nrfg.minigraphs ) ):
        MCMD.information( "{}{} - {}".format( constants.MINIGRAPH_PREFIX, i, model.nrfg.minigraphs[i] ) )
    
    return EChanges.INFORMATION


@command( visibility = visibilities.ADVANCED )
def groot():
    """
    Displays the application version.
    """
    MCMD.print( "I AM {}. VERSION {}.".format( MENV.name, MENV.version ) )
