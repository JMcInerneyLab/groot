import os
import shutil
from os import path
from typing import Iterable

from groot.algorithms.wizard import Wizard
from groot.constants import EFormat
from groot.data import global_view
from groot.data.lego_model import LegoModel, LegoSequence
from groot.extensions import ext_files, ext_gimmicks, ext_viewing
from intermake import MCMD, MENV, command, visibilities
from mgraph import MGraph, MNode, analysing, exporting, importing
from mhelper import ansi, file_helper, io_helper


@command( visibility = visibilities.TEST )
def run_test( name: str, refresh: bool = False, view: bool = False ):
    """
    Runs a test case and saves the results to the global results folder. 
    
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
                                exporting.export_edgelist( model.nrfg.fusion_graph_clean.graph,
                                                           fnode = lambda x: x.data.accession if isinstance( x.data, LegoSequence ) else "CL{}".format( x.get_session_id() ),
                                                           delimiter = "\t" ) )
    
    if view:
        ext_gimmicks.view_graph( text = test_tree_file, title = "ORIGINAL GRAPH. GUID = {}.".format( guid ) )
        # ext_gimmicks.view_graph( text = results_nrfg_file, title = "RECALCULATED GRAPH. GUID = {}.".format( guid ) )
        ext_viewing.print_trees( model.nrfg.fusion_graph_clean.graph, format = EFormat.VISJS, file = "open" )
    
    # Save extra data
    ext_viewing.print_alignments( file = results_saved_alignments )
    ext_viewing.print_trees( format = EFormat.TSV, file = results_edges_file )
    
    # Read original graph
    new_newicks = []
    differences = []
    differences.append( "[test_data]" )
    differences.append( "test_case_folder={}".format( test_case_folder ) )
    differences.append( "original_graph={}".format( test_tree_file ) )
    original_graph = importing.import_edgelist( file_helper.read_all_text( test_tree_file ), delimiter = "\t" )
    differences.append( compare_graphs( model.nrfg.fusion_graph_clean.graph, original_graph ) )
    
    # Write results
    file_helper.write_all_text( results_newick_file, new_newicks, newline = True )
    file_helper.write_all_text( results_compare_file, differences, newline = True )
    
    MCMD.progress( "The test has completed, see «{}».".format( results_compare_file ) )


def compare_graphs( calc_graph: MGraph, orig_graph: MGraph ):
    """
    Compares graphs using quartets.
    
    :param calc_graph: The model graph. Data is ILeaf or None. 
    :param orig_graph: The source graph. Data is str.
    :return: 
    """
    ccs = analysing.find_connected_components( calc_graph )
    if len( ccs ) != 1:
        raise ValueError( "The graph has more than 1 connected component ({}).".format( len( ccs ) ) )
    
    calc_quartets = analysing.get_quartets( calc_graph )
    orig_quartets = analysing.get_quartets( orig_graph )
    comparison = calc_quartets.compare( orig_quartets )
    
    res = []
    
    res.append( "total_quartets     = {}".format( len( comparison ) ) )
    res.append( "match_quartets     = {}".format( len( comparison.match ) ) )
    res.append( "mismatch_quartets  = {}".format( len( comparison.mismatch ) ) )
    res.append( "new_quartets       = {}".format( len( comparison.missing_in_left ) ) )
    res.append( "missing_quartets   = {}".format( len( comparison.missing_in_right ) ) )
    
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
