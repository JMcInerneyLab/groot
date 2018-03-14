import shutil
from os import path
import os
from typing import Iterable

from groot.algorithms.walkthrough import Walkthrough
from groot.constants import EFormat
from groot.data import global_view
from groot.data.lego_model import LegoModel, LegoSequence
from groot.extensions import ext_files, ext_viewing, ext_gimmicks
from intermake import command
from intermake.engine.environment import MENV, MCMD
from mgraph import MGraph, MNode, exporting, Split, importing, analysing
from mhelper import LogicError, ansi, array_helper, file_helper, io_helper


@command
def run_test( name: str, refresh: bool = False, interpret: bool = True, view: bool = True ):
    """
    Runs a test case and saves the results to the global results folder. 
    
    :param interpret:  When set interprets the results.
    :param refresh:    When set always generates the model, even if an existing one is present
                       in the results folder.
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
    test_case_folder = global_view.get_sample_data_folder( name )
    results_folder = MENV.local_data.local_folder( "test_cases" )
    test_name = file_helper.get_filename( test_case_folder )
    
    # Check the requisite files exist
    test_tree_file = path.join( test_case_folder, "tree.tsv" )
    test_ini_file = path.join( test_case_folder, "groot.ini" )
    results_original_file = path.join( results_folder, test_name + "_original.tsv" )
    results_compare_file = path.join( results_folder, test_name + "_results_summary.ini" )
    results_edges_file = path.join( results_folder, test_name + "_results_trees.tsv" )
    results_nrfg_file = path.join( results_folder, test_name + "_results_nrfg.tsv" )
    results_saved_trees = path.join( results_folder, test_name + "_results_trees.nwk" )
    results_saved_file = path.join( results_folder, test_name + "_results_session.groot" )
    results_saved_alignments = path.join( results_folder, test_name + "_results_alignments.fasta" )
    results_newick_file = path.join( results_folder, test_name + "_results_nrfg_divided.nwk" )
    results_sentinel = path.join( results_folder, test_name + "_results_sentinel.ini" )
    
    all_files = [results_original_file,
                 results_compare_file,
                 results_edges_file,
                 results_saved_trees,
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
    
    if not refresh and path.isfile( results_saved_file ):
        ext_files.file_load( results_saved_file )
    else:
        if not "groot_wizard" in keys:
            raise ValueError( "This is not a test case (it is missing the «wizard» section from the INI «{}»).".format( test_ini_file ) )
        
        # Copy the 
        shutil.copy( test_tree_file, results_original_file )
        
        # Create settings
        walkthrough = Walkthrough( new = False,
                                   name = path.join( results_folder, test_name + ".groot" ),
                                   imports = global_view.get_sample_contents( test_case_folder ),
                                   pause_import = False,
                                   pause_components = False,
                                   pause_align = False,
                                   pause_tree = False,
                                   pause_fusion = False,
                                   pause_nrfg = False,
                                   tolerance = wiz_tol,
                                   outgroups = wiz_og,
                                   alignment = "",
                                   tree = "neighbor_joining",
                                   view = not interpret )
        
        # Execute
        walkthrough.make_active()
        walkthrough.step()
        
        if not walkthrough.is_completed:
            raise ValueError( "Expected wizard to complete but it did not." )
        
        # Save the final model
        ext_files.file_save( results_saved_file )
    
    # Write the results
    model = global_view.current_model()
    file_helper.write_all_text( results_nrfg_file,
                                exporting.export_edgelist( model.nrfg.fusion_graph.graph,
                                                           fnode = lambda x: x.data.accession if isinstance( x.data, LegoSequence ) else "CL{}".format( x.get_session_id() ),
                                                           delimiter = "\t" ) )
    
    if view:
        ext_gimmicks.view_graph( text = test_tree_file, title = "ORIGINAL GRAPH. GUID = {}.".format( guid ) )
        # ext_gimmicks.view_graph( text = results_nrfg_file, title = "RECALCULATED GRAPH. GUID = {}.".format( guid ) )
        ext_viewing.print_trees( model.nrfg.fusion_graph.graph, format = EFormat.VISJS, file = "open" )
        
        if interpret:
            MCMD.autoquestion( "Continue to interpretation stage?" )
    
    if interpret:
        # Save extra data
        ext_viewing.print_alignments( file = results_saved_alignments )
        ext_viewing.print_trees( format = EFormat.NEWICK, file = results_saved_trees )
        ext_viewing.print_trees( format = EFormat.TSV, file = results_edges_file )
        
        # Read original tree(s)
        new_newicks = []
        differences = []
        differences.append( "[test_data]" )
        differences.append( "test_case_folder={}".format( test_case_folder ) )
        differences.append( "original_graph={}".format( test_tree_file ) )
        original_graph = importing.import_edgelist( file_helper.read_all_text( test_tree_file ), delimiter = "\t" )
        differences.append( compare_graphs( model.nrfg.fusion_graph.graph, original_graph ) )
        
        # Write results
        file_helper.write_all_text( results_newick_file, new_newicks, newline = True )
        file_helper.write_all_text( results_compare_file, differences, newline = True )
    
    MCMD.progress( "The test has completed, see «{}».".format( results_compare_file ) )


def compare_graphs( calc_graph: MGraph, orig_graph: MGraph ):
    """
    Compares graphs using something approximating RF distance and something approximating cophenetic distance.
    (I say something approximating because we have graphs and not trees!)
    
    :param calc_graph: The model graph. Data is ILeaf or None. 
    :param orig_graph: The source graph. Data is str.
    :return: 
    """
    # Root both graphs randomly
    calc_graph.any_root.make_root()
    orig_graph.any_root.make_root()
    
    res = []
    
    calc_splits = exporting.export_splits( calc_graph, 
                                           filter = lambda λnode: isinstance( λnode.data, LegoSequence ), 
                                           gdata = lambda λnode: λnode.data.accession )
    orig_splits = exporting.export_splits( orig_graph )
    
    res.append( "num_calc_splits = {}".format( len( calc_splits ) ) )
    res.append( "num_orig_splits = {}".format( len( orig_splits ) ) )
    res.append( "" )
    res.append( "[test_results]" )
    
    num_support = 0
    num_rejects = 0
    
    com = []
    
    calc_leaves = set( x.data.accession for x in calc_graph if isinstance( x.data, LegoSequence ) )
    orig_leaves = set( x.data for x in orig_graph if x.is_leaf )
    
    if calc_leaves != orig_leaves:
        MCMD.print( "In `calc` but not `orig`: {}".format( calc_leaves - orig_leaves ) )
        MCMD.print( "In `orig` but not `calc`: {}".format( orig_leaves - calc_leaves ) )
        raise ValueError( "Total failure. The two graphs have different leaf sets." )
    
    calc_splits_sorted = sorted( calc_splits, key = Split.to_string )
    orig_splits_sorted = sorted( orig_splits, key = Split.to_string )
    
    for orig_split in orig_splits_sorted:
        assert isinstance( orig_split, Split )
        supported_by = set()
        rejected_by = set()
        com.append( "[" + orig_split.to_string() + "]" )
        
        for calc_split in calc_splits_sorted:
            assert isinstance( calc_split, Split )
            evidence = orig_split.is_evidenced_by( calc_split )
            
            if evidence is None:
                raise ValueError( "Didn't expect no evidence since the leaf sets should match." )
            elif evidence is True:
                supported_by.add( calc_split )
            elif evidence is False:
                rejected_by.add( calc_split )
        
        com.append( "num_support= {}".format( len( supported_by ) ) )
        com.append( "num_rejects= {}".format( len( rejected_by ) ) )
        __append_ev( com, supported_by, "support" )
        
        # __append_ev( com, s_rej, "rejects" )
        
        if supported_by:
            num_support += 1
            com.append( "conclusion=support" )
        elif rejected_by:
            num_rejects += 1
            com.append( "conclusion=rejects" )
        else:
            raise LogicError( "Split evidence is the empty set." )
        
        com.append( "" )
    
    num_splits = num_support + num_rejects
    res.append( "total_splits  = {}".format( num_splits ) )
    res.append( "total_support = {} ({:.1%})".format( num_support, num_support / num_splits ) )
    res.append( "total_rejects = {} ({:.1%})".format( num_rejects, num_rejects / num_splits ) )
    
    num_pathlen_matches = 0
    num_pathlen_mismatches = 0
    
    for calc_alpha, calc_beta in array_helper.triangular_comparison( list( calc_graph.nodes ) ):
        if not isinstance( calc_alpha.data, LegoSequence ) or not isinstance( calc_beta.data, LegoSequence ):
            continue
        
        orig_alpha = orig_graph.nodes.by_data( calc_alpha.data.accession )
        orig_beta = orig_graph.nodes.by_data( calc_beta.data.accession )
        calc_path = analysing.find_shortest_path(calc_graph, calc_alpha, calc_beta )
        orig_path = analysing.find_shortest_path(orig_graph, orig_alpha, orig_beta )
        
        calc_pathlen = len( calc_path )
        orig_pathlen = len( orig_path )
        
        com.append( "[{}, {}]".format( calc_alpha, calc_beta ) )
        com.append( "calc_path    = {}".format( calc_path ) )
        com.append( "orig_path    = {}".format( orig_path ) )
        com.append( "calc_pathlen = {}".format( calc_pathlen ) )
        com.append( "orig_pathlen = {}".format( orig_pathlen ) )
        com.append( "difference   = {}".format( calc_pathlen - orig_pathlen ) )
        com.append( "are_equal    = {}".format( calc_pathlen == orig_pathlen ) )
        com.append( "" )
        
        if calc_pathlen == orig_pathlen:
            num_pathlen_matches += 1
        else:
            num_pathlen_mismatches += 1
    
    num_path_lens = num_pathlen_matches + num_pathlen_mismatches
    
    res.append( "total_paths        = {}".format( num_path_lens ) )
    res.append( "pathlen_matches    = {} ({:.1%})".format( num_pathlen_matches, num_pathlen_matches / num_path_lens ) )
    res.append( "pathlen_mismatches = {} ({:.1%})".format( num_pathlen_mismatches, num_pathlen_mismatches / num_path_lens ) )
    res.append( "" )
    res.extend( com )
    
    return "\n".join( res )


def __append_ev( out_list, the_set, title ):
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
