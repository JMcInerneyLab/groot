import os
from os import path
import shutil
from typing import Iterable, List, Set
import uuid
import itertools

from groot.frontends.gui.gui_view_utils import EChanges
from intermake import MCMD, MENV, command, visibilities, subprocess_helper, Theme
from mgraph import AbstractQuartet, MGraph, MNode, QuartetCollection, QuartetComparison, analysing, exporting, importing
from mhelper import SwitchError, ansi, file_helper, io_helper, string_helper

from groot.algorithms.wizard import Wizard
from groot.constants import EFormat
from groot.data import global_view, lego_graph
from groot.data.lego_model import LegoModel, LegoSequence, UserGraph, FixedUserGraph
from groot.extensions import ext_files, ext_viewing


@command( visibility = visibilities.TEST )
def list_tests() -> EChanges:
    """
    Lists the available test cases.
    """
    MCMD.print( "TESTS:" )
    for file in file_helper.list_dir( global_view.get_test_data_folder() ):
        MCMD.print( file_helper.highlight_file_name_without_extension( file, Theme.BOLD, Theme.RESET ) )
    
    return EChanges.INFORMATION


@command( visibility = visibilities.TEST )
def reload_test( name: str ) -> EChanges:
    """
    Loads the model created via `run_test`.
    :param name:    Test name
    """
    test_case_folder = global_view.get_test_data_folder( name )
    results_folder = MENV.local_data.local_folder( "test_cases_results" )
    test_name = file_helper.get_filename( test_case_folder )
    results_saved_file = path.join( results_folder, test_name + "_results_session.groot" )
    
    if not path.isfile( results_saved_file ):
        raise ValueError( "Cannot load test because it has not yet been run." )
    
    return ext_files.file_load( results_saved_file )


@command( visibility = visibilities.TEST )
def run_test( name: str,
              view: bool = False ) -> EChanges:
    """
    Runs a test case and saves the results to the global results folder. 
    
    :param view:       Pause to view NRFG.
    :param name:       A name or path to the test case.
                       If no full path is provided the "samples" folder will be assumed.
                       The test case folder must contain:
                        
                            * The data (BLAST, FASTA)
                            * A `tree.csv` file describing the expected results (in edge-list format)
                            * A `groot.ini` file describing the parameters to use.
                             
    :return:           Nothing is returned, the results are saved to the global results folder. 
    """
    
    # Load sample file
    test_case_folder = global_view.get_test_data_folder( name )
    results_folder = MENV.local_data.local_folder( "test_cases_results" )
    test_name = file_helper.get_filename( test_case_folder )
    
    # Check the requisite files exist
    test_tree_file = path.join( test_case_folder, "tree.tsv" )
    test_ini_file = path.join( test_case_folder, "groot.ini" )
    results_original_file = path.join( results_folder, test_name + "_original.tsv" )
    results_compare_file = path.join( results_folder, test_name + "_results_summary.html" )
    results_edges_file = path.join( results_folder, test_name + "_results_trees.tsv" )
    results_nrfg_file = path.join( results_folder, test_name + "_results_nrfg.tsv" )
    results_saved_file = path.join( results_folder, test_name + "_results_session.groot" )
    results_saved_alignments = path.join( results_folder, test_name + "_results_alignments.fasta" )
    results_newick_file = path.join( results_folder, test_name + "_results_nrfg_divided.nwk" )
    results_sentinel = path.join( results_folder, test_name + "_results_sentinel.ini" )
    
    all_files = [results_original_file,
                 results_compare_file,
                 results_edges_file,
                 results_saved_file,
                 results_saved_alignments,
                 results_newick_file,
                 results_sentinel]
    
    # Read the test specs
    if not path.isdir( test_case_folder ):
        raise ValueError( "This is not a test case (it is not even a folder, «{}»).".format( test_case_folder ) )
    
    if not path.isfile( test_tree_file ):
        raise ValueError( "This is not a test case (it is missing the edge list file, «{}»).".format( test_tree_file ) )
    
    if not path.isfile( test_ini_file ):
        raise ValueError( "This is not a test case (it is missing the INI file, «{}»).".format( test_ini_file ) )
    
    keys = io_helper.load_ini( test_ini_file )
    
    if "groot_test" not in keys:
        raise ValueError( "This is not a test case (it is missing the `groot_test` section from the INI file, «{}»).".format( test_ini_file ) )
    
    guid = keys["groot_test"]["guid"]
    
    wizard_params = keys["groot_wizard"]
    
    try:
        wiz_tol = int( wizard_params["tolerance"] )
        wiz_og = wizard_params["outgroups"].split( "," )
    except KeyError as ex:
        raise ValueError( "This is not a test case (it is missing the «{}» setting from the «wizard» section of the INI «{}»).".format( ex, test_ini_file ) )
    
    test_tree_file_data = UserGraph( importing.import_edgelist( file_helper.read_all_text( test_tree_file ), delimiter = "\t" ), name = "ORIGINAL GRAPH. GUID = {}.".format( guid ) )
    
    # Remove obsolete results
    if any( path.isfile( file ) for file in all_files ):
        if path.isfile( results_sentinel ):
            sentinel = io_helper.load_ini( results_sentinel )
            old_guid = sentinel["groot_test"]["guid"]
        else:
            old_guid = None
        
        if old_guid is not guid:
            # Delete old files
            MCMD.progress( "Removing obsolete test results (the old test is no longer present under the same name)" )
            for file in all_files:
                if path.isfile( file ):
                    MCMD.progress( "..." + file )
                    os.remove( file )
    
    file_helper.write_all_text( results_sentinel, "[groot_test]\nguid={}\n".format( guid ) )
    
    if not "groot_wizard" in keys:
        raise ValueError( "This is not a test case (it is missing the «wizard» section from the INI «{}»).".format( test_ini_file ) )
    
    # Copy the 
    shutil.copy( test_tree_file, results_original_file )
    
    # Create settings
    walkthrough = Wizard( new = False,
                          name = path.join( results_folder, test_name + ".groot" ),
                          imports = global_view.get_sample_contents( test_case_folder ),
                          pause_import = False,
                          pause_components = False,
                          pause_align = False,
                          pause_tree = False,
                          pause_fusion = False,
                          pause_splits = False,
                          pause_consensus = False,
                          pause_subset = False,
                          pause_pregraphs = False,
                          pause_minigraph = False,
                          pause_sew = False,
                          pause_clean = False,
                          pause_check = False,
                          tolerance = wiz_tol,
                          outgroups = wiz_og,
                          alignment = "",
                          tree = "neighbor_joining",
                          view = False,
                          save = False,
                          supertree = "clann" )
    
    try:
        # Execute
        walkthrough.make_active()
        walkthrough.step()
        
        if not walkthrough.is_completed:
            raise ValueError( "Expected wizard to complete but it did not." )
        
        # Save the original graph as part of the model 
        global_view.current_model().user_graphs.append( FixedUserGraph( test_tree_file_data.graph, "original_graph" ) )
    finally:
        # Save the final model
        ext_files.file_save( results_saved_file )
    
    # Write the results
    model = global_view.current_model()
    file_helper.write_all_text( results_nrfg_file,
                                exporting.export_edgelist( model.fusion_graph_clean.graph,
                                                           fnode = lambda x: x.data.accession if isinstance( x.data, LegoSequence ) else "CL{}".format( x.get_session_id() ),
                                                           delimiter = "\t" ) )
    
    if view:
        ext_viewing.print_trees( test_tree_file_data, format = EFormat._HTML, file = "open" )
        ext_viewing.print_trees( model.fusion_graph_unclean, format = EFormat._HTML, file = "open" )
        ext_viewing.print_trees( model.fusion_graph_clean, format = EFormat._HTML, file = "open" )
        
        for component in model.components:
            ext_viewing.print_trees( component.named_tree_unrooted, format = EFormat._HTML, file = "open" )
            ext_viewing.print_trees( component.named_tree, format = EFormat._HTML, file = "open" )
    
    # Save extra data
    ext_viewing.print_alignments( file = results_saved_alignments )
    ext_viewing.print_trees( format = EFormat.TSV, file = results_edges_file )
    
    # Read original graph
    new_newicks = []
    differences = []
    differences.append( "<html><body>" )
    differences.append( '<table border=1 style="border-collapse: collapse;">' )
    differences.append( "<tr><td colspan=2><b>SUMMARY</b></td></tr>".format( test_case_folder ) )
    differences.append( "<tr><td>test_case_folder      </td><td>{}</td></tr>".format( test_case_folder ) )
    differences.append( "<tr><td>original_graph        </td><td>{}</td></tr>".format( test_tree_file ) )
    differences.append( "<tr><td>recalculated_graph    </td><td>{}</td></tr>".format( results_edges_file ) )
    differences.append( "<tr><td>original_graph_cmd    </td><td>groot print.graph {} visjs open</td></tr>".format( test_tree_file ) )
    differences.append( "<tr><td>recalculated_graph_cmd</td><td>groot print.graph {} visjs open</td></tr>".format( results_edges_file ) )
    differences.append( "</table><br/>" )
    
    original_graph = importing.import_edgelist( file_helper.read_all_text( test_tree_file ), delimiter = "\t" )
    lego_graph.rectify_nodes( original_graph, model )
    differences.append( compare_graphs( model.fusion_graph_clean.graph, original_graph ) )
    differences.append( "</body></html>" )
    
    # Write results
    file_helper.write_all_text( results_newick_file, new_newicks, newline = True )
    file_helper.write_all_text( results_compare_file, differences, newline = True )
    
    if view:
        os.system( "open \"" + results_compare_file + "\"" )
    
    MCMD.progress( "The test has completed, see «{}».".format( results_compare_file ) )
    return EChanges.MODEL_OBJECT


def compare_graphs( calc_graph: MGraph,
                    orig_graph: MGraph ):
    """
    Compares graphs using quartets.
    
    :param calc_graph: The model graph. Data is ILeaf or None. 
    :param orig_graph: The source graph. Data is str.
    :return: 
    """
    ccs = analysing.find_connected_components( calc_graph )
    if len( ccs ) != 1:
        raise ValueError( "The graph has more than 1 connected component ({}).".format( len( ccs ) ) )
    
    calc_seq: Set[object] = set( x.data for x in analysing.realise_node_predicate_as_set( calc_graph, lego_graph.is_sequence_node ) )
    orig_seq: Set[object] = set( x.data for x in analysing.realise_node_predicate_as_set( orig_graph, lego_graph.is_sequence_node ) )
    
    if not calc_seq:
        raise ValueError( "The calculated graph contains no sequences." )
    
    if not orig_seq:
        raise ValueError( "The original graph contains no sequences." )
    
    if calc_seq != orig_seq:
        raise ValueError( "The calculated graph has a different sequence set to the original. Missing: {}; additional: {}.".format(
                string_helper.format_array( orig_seq - calc_seq, sort = True, format = lambda x: "{}:{}".format( type( x ).__name__, x ) ),
                string_helper.format_array( calc_seq - orig_seq, sort = True, format = lambda x: "{}:{}".format( type( x ).__name__, x ) ) ) )
    
    calc_quartets = __get_quartets_with_progress( calc_graph, "calculated" )
    orig_quartets = __get_quartets_with_progress( orig_graph, "original" )
    comparison: QuartetComparison = calc_quartets.compare( orig_quartets )
    
    res = []
    
    res.append( '<table border=1 style="border-collapse: collapse;">' )
    res.append( "<tr><td colspan=2><b>QUARTETS</b></td></tr>" )
    res.append( "<tr><td>total_quartets</td><td>{}</td></tr>".format( len( comparison ) ) )
    res.append( "<tr><td>match_quartets</td><td>{}</td></tr>".format( string_helper.percent( len( comparison.match ), len( comparison.all ) ) ) )
    res.append( "<tr><td>mismatch_quartets</td><td>{}</td></tr>".format( string_helper.percent( len( comparison.mismatch ), len( comparison.all ) ) ) )
    if comparison.missing_in_left:
        res.append( "<tr><td>new_quartets</td><td>{}</td></tr>".format( string_helper.percent( len( comparison.missing_in_left ), len( comparison.all ) ) ) )
    if comparison.missing_in_right:
        res.append( "<tr><td>missing_quartets</td><td>{}</td></tr>".format( string_helper.percent( len( comparison.missing_in_right ), len( comparison.all ) ) ) )
    res.append( "</table><br/>" )
    
    __enumerate_2sequences( calc_seq, comparison, res, 1 )
    __enumerate_2sequences( calc_seq, comparison, res, 2 )
    __enumerate_2sequences( calc_seq, comparison, res, 3 )
    
    c = calc_quartets.get_unsorted_lookup()
    o = orig_quartets.get_unsorted_lookup()
    __list_comp( comparison.match, "MATCHING", res, c, o )
    __list_comp( comparison.mismatch, "MISMATCH", res, c, o )
    if comparison.missing_in_left:
        __list_comp( comparison.missing_in_left, "MISSING IN LEFT", res, c, o )
    if comparison.missing_in_right:
        __list_comp( comparison.missing_in_right, "MISSING IN RIGHT", res, c, o )
    
    return "\n".join( res )


def __list_comp( comparison, t, res, c, o ):
    res.append( '<table border=1 style="border-collapse: collapse;">' )
    res.append( "<tr><td colspan=6><b>{} QUARTETS</b></td></tr>".format( t ) )
    for quartet in comparison:
        calc = c[quartet.get_unsorted_key()]
        orig = o[quartet.get_unsorted_key()]
        res.append( "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format( *quartet.get_unsorted_key(), calc, orig ) )
    res.append( "</table><br/>" )


def __enumerate_2sequences( calc_seq: Set[object],
                            comparison: QuartetComparison,
                            res: List[str],
                            r: int
                            ) -> None:
    res.append( '<table border=1 style="border-collapse: collapse;">' )
    res.append( "<tr><td colspan=5><b>BREAKDOWN FOR COMBINATIONS OF {}</b></td></tr>".format( r ) )
    res.append( "<tr><td>total</td><td>hit</td><td>miss</td><td>missing in left</td><td>missing in right</td></tr>" )
    
    for comb in sorted( itertools.combinations( calc_seq, r ), key = str ):  # type: Iterable[object]
        n_tot = []
        n_hit = []
        n_mis = []
        n_mil = []
        n_mir = []
        
        for quartet in comparison.all:
            assert isinstance( quartet, AbstractQuartet )
            
            if all( x in quartet.get_unsorted_key() for x in comb ):
                n_tot.append( quartet )
                
                if quartet in comparison.match:
                    n_hit.append( quartet )
                elif quartet in comparison.mismatch:
                    n_mis.append( quartet )
                elif quartet in comparison.missing_in_left:
                    n_mil.append( quartet )
                elif quartet in comparison.missing_in_right:
                    n_mir.append( quartet )
                else:
                    raise SwitchError( "quartet(in)", quartet )
        
        if not n_mis and not n_mil and not n_mir:
            continue
        
        res.append( "<tr>" )
        res.append( "<td>{}</td>".format( format( string_helper.format_array( comb ) ) ) )
        res.append( "<td>{}</td>".format( string_helper.percent( len( n_hit ), len( n_tot ) ) if n_hit else "" ) )
        res.append( "<td>{}</td>".format( string_helper.percent( len( n_mis ), len( n_tot ) ) if n_mis else "" ) )
        res.append( "<td>{}</td>".format( string_helper.percent( len( n_mil ), len( n_tot ) ) if n_mil else "" ) )
        res.append( "<td>{}</td>".format( string_helper.percent( len( n_mir ), len( n_tot ) ) if n_mil else "" ) )
        res.append( "</tr>" )
        
        if len( n_hit ) < len( n_mis ) < 10:
            for quartet in n_mis:
                res.append( "<tr>" )
                res.append( "<td></td>" )
                res.append( "<td colspan=4>{}</td>".format( quartet ) )
                res.append( "</tr>" )
    
    res.append( "</table><br/>" )


def __get_quartets_with_progress( graph, title ) -> QuartetCollection:
    r = []
    
    for q in MCMD.iterate( analysing.iter_quartets( graph, lego_graph.is_sequence_node ), "Reducing '{}' to quartets".format( title ), count = analysing.get_num_quartets( graph, lego_graph.is_sequence_node ) ):
        r.append( q )
    
    return QuartetCollection( r )


def __append_ev( out_list: List[str],
                 the_set,
                 title: str
                 ) -> None:
    for index, b_split in enumerate( the_set ):
        out_list.append( title + "_({}/{}) = {}".format( index + 1, len( the_set ), b_split.to_string() ) )


class __NodeFilter:
    def __init__( self, model: LegoModel, accessions: Iterable[str] ):
        self.sequences = [model.find_sequence_by_accession( accession ) for accession in accessions]
    
    
    def format( self, node: MNode ):
        d = node.data
        
        if d is None:
            t = "x"
        else:
            t = str( d )
        
        if d in self.sequences:
            assert isinstance( d, LegoSequence )
            return ansi.FORE_GREEN + t + ansi.RESET
        
        for rel in node.relations:
            if rel.data in self.sequences:
                return ansi.FORE_YELLOW + t + ansi.RESET
        
        return ansi.FORE_RED + t + ansi.RESET
    
    
    def query( self, node: MNode ):
        if isinstance( node.data, LegoSequence ):
            return node.data in self.sequences
        
        for rel in node.relations:
            if rel.data in self.sequences:
                return True
        
        for rel in node.relations:
            if isinstance( rel.data, LegoSequence ) and rel.data not in self.sequences:
                return False
        
        return True


@command( visibility = visibilities.ADVANCED )
def drop_tests():
    """
    Deletes all test cases from the sample data folder.
    """
    dirs = file_helper.list_dir( global_view.get_test_data_folder() )
    
    for dir in dirs:
        ini_file = path.join( dir, "groot.ini" )
        if path.isfile( ini_file ):
            if "groot_test" in io_helper.load_ini( ini_file ):
                shutil.rmtree( dir )
                MCMD.progress( "Removed: {}".format( dir ) )


@command( visibility = visibilities.ADVANCED )
def create_test( types: str = "1", no_blast: bool = False, size: int = 2, view: bool = False, run: bool = True ) -> EChanges:
    """
    Creates a GROOT unit test in the sample data folder.
    
    * GROOT should be installed in developer mode, otherwise there may be no write access to the sample data folder.
    * Requires the `faketree` library. 
    
    :param run:         Run test after creating it.
    :param no_blast:    Perform no BLAST 
    :param size:        Clade size
    :param types:       Type(s) of test(s) to create.
    :param view:        View the final tree
    :return: List of created test directories 
    """
    # noinspection PyPackageRequirements
    import faketree as Ж
    MCMD.print( "START" )
    r = []
    args_random_tree = { "suffix": "1", "delimiter": "_", "size": size, "outgroup": True }
    # args_fn = "-d 0.2"
    args_fn = ""
    
    if not types:
        raise ValueError( "Missing :param:`types`." )
    
    folder: str = global_view.get_test_data_folder()
    
    for name in types:
        try:
            Ж.new()
            # The SeqGen mutator has a weird problem where, given a root `(X,O)R` in which `R`
            # is set as a result of an earlier tree, `O` will be more similar to the leaves of
            # that earlier tree than to the leaves in X. For this reason we use a simple random
            # model and not SeqGen.
            fn = Ж.random
            
            if name == "1":
                # 1 fusion point; 3 genes; 2 origins
                
                # Trees
                outgroups = Ж.random_tree( ["A", "B", "C"], **args_random_tree )
                a, b, c = (x.parent for x in outgroups)
                __remove( outgroups, 2 )
                
                fn( [a, b, c], *args_fn )
                
                # Fusion point
                fa = Ж.random_node( a, avoid = outgroups )
                fb = Ж.random_node( b, avoid = outgroups )
                Ж.branch( [fa, fb], c )
                Ж.mk_composite( [c] )
            elif name == "4":
                # 2 fusion points; 4 genes; 2 origins
                
                # Trees
                outgroups = Ж.random_tree( ["A", "B", "C", "D"], **args_random_tree )
                a, b, c, d = (x.parent for x in outgroups)
                fn( [a, b, c, d], *args_fn )
                __remove( outgroups, 2, 3 )
                
                # Fusion points
                fa1 = Ж.random_node( a, avoid = outgroups )
                fb1 = Ж.random_node( b, avoid = outgroups )
                fa2 = Ж.random_node( fa1, avoid = outgroups )
                fb2 = Ж.random_node( fb1, avoid = outgroups )
                Ж.branch( [fa1, fb1], c )
                Ж.branch( [fa2, fb2], d )
                Ж.mk_composite( [c, d] )
            
            elif name == "5":
                # 2 fusion points; 5 genes; 3 origins
                
                # Trees
                outgroups = Ж.random_tree( ["A", "B", "C", "D", "E"], **args_random_tree )
                a, b, c, d, e = (x.parent for x in outgroups)
                fn( [a, b, c, d, e], *args_fn )
                __remove( outgroups, 2, 4 )
                
                # Fusion points
                fa = Ж.random_node( a, avoid = outgroups )
                fb = Ж.random_node( b, avoid = outgroups )
                fc = Ж.random_node( c, avoid = outgroups )
                fd = Ж.random_node( d, avoid = outgroups )
                Ж.branch( [fa, fb], c )
                Ж.branch( [fc, fd], e )
                Ж.mk_composite( [c, e] )
            elif name == "7":
                # 3 fusion points; 7 genes; 4 origins
                
                # Trees
                outgroups = Ж.random_tree( ["A", "B", "C", "D", "E", "F", "G"], **args_random_tree )
                a, b, c, d, e, f, g = (x.parent for x in outgroups)
                fn( [a, b, c, d, e, f, g], *args_fn )
                __remove( outgroups, 2, 5, 6 )
                
                # Fusion points
                fa = Ж.random_node( a, avoid = outgroups )
                fb = Ж.random_node( b, avoid = outgroups )
                fc = Ж.random_node( c, avoid = outgroups )
                fd = Ж.random_node( d, avoid = outgroups )
                fe = Ж.random_node( e, avoid = outgroups )
                ff = Ж.random_node( f, avoid = outgroups )
                Ж.branch( [fa, fb], c )
                Ж.branch( [fd, fe], f )
                Ж.branch( [fc, ff], g )
                Ж.mk_composite( [c, f, g] )
            else:
                raise SwitchError( "name", name )
            
            Ж.apply()
            
            out_folder = file_helper.sequential_file_name( file_helper.join( folder, name + "_*" ) )
            file_helper.create_directory( out_folder )
            os.chdir( out_folder )
            
            Ж.show( format = Ж.EGraphFormat.ASCII, file = "tree.txt" )
            Ж.show( format = Ж.EGraphFormat.TSV, file = "tree.tsv", name = True, mutator = False, sequence = False, length = False )
            Ж.fasta( which = Ж.ESubset.ALL, file = "all.fasta.hidden" )
            Ж.fasta( which = Ж.ESubset.LEAVES, file = "leaves.fasta" )
            
            if not no_blast:
                blast = []
                # noinspection SpellCheckingInspection
                subprocess_helper.run_subprocess( ["blastp",
                                                   "-subject", "leaves.fasta",
                                                   "-query", "leaves.fasta",
                                                   "-outfmt", "6"],
                                                  collect_stdout = blast.append )
                
                file_helper.write_all_text( "leaves.blast", blast )
            
            guid = uuid.uuid4()
            outgroups_str = ",".join( x.data.name for x in outgroups if x.parent.is_root )
            file_helper.write_all_text( "groot.ini", "[groot_wizard]\ntolerance=50\noutgroups={}\n\n[groot_test]\nguid={}\n".format( outgroups_str, guid ) )
            
            path_ = path.abspath( "." )
            MCMD.print( "FINAL PATH: " + path_ )
            r.append( path_ )
        
        except Ж.RandomChoiceError as ex:
            MCMD.print( "FAILURE {}".format( ex ) )
            return EChanges.INFORMATION
        
        if run:
            return run_test( path_, refresh = True, view = view )
    
    return EChanges.INFORMATION


def __remove( outgroups, *args ):
    import faketree
    faketree.remove( [outgroups[x] for x in args] )
    
    for x in sorted( args, reverse = True ):
        del outgroups[x]
