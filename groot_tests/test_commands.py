import os
import shutil
import uuid
from os import path
from typing import Optional

import groot.data.sample_data
from groot.algorithms.gimmicks import wizard, compare
from groot.algorithms.workflow import s010_file, s080_tree, s070_alignment
from groot_tests.test_directory import TestDirectory
from intermake import MCMD, Theme, command, subprocess_helper, visibilities
from mgraph import importing
from mhelper import SwitchError, file_helper, io_helper, OpeningWriter

from groot import constants
from groot.constants import EFormat, EChanges
from groot.data import global_view, UserGraph, FixedUserGraph
from groot.utilities import lego_graph


__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME_TESTS


@command( visibility = visibilities.TEST )
def list_tests() -> EChanges:
    """
    Lists the available test cases.
    """
    MCMD.print( "TESTS:" )
    for file in file_helper.list_dir( TestDirectory.get_test_folder() ):
        MCMD.print( file_helper.highlight_file_name_without_extension( file, Theme.BOLD, Theme.RESET ) )
    
    return EChanges.INFORMATION


@command( visibility = visibilities.TEST )
def run_test( name: str ) -> EChanges:
    """
    Runs a test case and saves the results to the global results folder. 
    
    :param name:       A name or path to the test case.
                       If no full path is provided the "samples" folder will be assumed.
                       The test case folder must contain:
                        
                            * The data (BLAST, FASTA)
                            * A `tree.csv` file describing the expected results (in edge-list format)
                            * A `groot.ini` file describing the parameters to use.
                             
    :return:           Nothing is returned, the results are saved to the global results folder. 
    """
    
    # Load sample file
    tdir = TestDirectory( name )
    
    # Define outputs
    file_helper.create_directory( tdir.r_folder, overwrite = True )
    
    # Check the requisite files exist
    if not path.isdir( tdir.t_folder ):
        raise ValueError( "This is not a test case (it is not even a folder, «{}»).".format( tdir.t_folder ) )
    
    if not path.isfile( tdir.t_tree ):
        raise ValueError( "This is not a test case (it is missing the edge list file, «{}»).".format( tdir.t_tree ) )
    
    if not path.isfile( tdir.t_ini ):
        raise ValueError( "This is not a test case (it is missing the INI file, «{}»).".format( tdir.t_ini ) )
    
    # Read the test specs
    specs = io_helper.load_ini( tdir.t_ini )
    
    if "groot_test" not in specs:
        raise ValueError( "This is not a test case (it is missing the `groot_test` section from the INI file, «{}»).".format( tdir.t_ini ) )
    
    if not "groot_wizard" in specs:
        raise ValueError( "This is not a test case (it is missing the «wizard» section from the INI «{}»).".format( tdir.t_ini ) )
    
    wizard_params = specs["groot_wizard"]
    
    try:
        wiz_tol = int( wizard_params["tolerance"] )
        wiz_og = wizard_params["outgroups"].split( "," )
    except KeyError as ex:
        raise ValueError( "This is not a test case (it is missing the «{}» setting from the «wizard» section of the INI «{}»).".format( ex, tdir.t_ini ) )
    
    # Copy the test files to the output folder
    for file in file_helper.list_dir( tdir.t_folder ):
        shutil.copy( file, file_helper.format_path( file, tdir.r_folder + "/input_{N}{E}" ) )
    
    # Create settings
    walkthrough = wizard.Wizard( new = False,
                                 name = tdir.r_model,
                                 imports = groot.data.sample_data.get_sample_contents( tdir.t_folder ),
                                 pauses = set(),
                                 tolerance = wiz_tol,
                                 outgroups = wiz_og,
                                 alignment = "",
                                 tree = "maximum_likelihood",  # "neighbor_joining",
                                 view = False,
                                 save = False,
                                 supertree = "clann" )
    
    try:
        # Execute the wizard (no pauses are set so this only requires 1 `step`)
        walkthrough.make_active()
        walkthrough.step()
        
        if not walkthrough.is_completed:
            raise ValueError( "Expected wizard to complete but it did not." )
        
        # Add the original graph to the Groot `Model` in case we debug
        test_tree_file_data = UserGraph( importing.import_edgelist( file_helper.read_all_text( tdir.t_tree ), delimiter = "\t" ), name = "original_graph" )
        lego_graph.rectify_nodes( test_tree_file_data.graph, global_view.current_model() )
        global_view.current_model().user_graphs.append( FixedUserGraph( test_tree_file_data.graph, "original_graph" ) )
    finally:
        # Save the final model regardless of whether the test succeeded
        s010_file.file_save( tdir.r_model )
    
    # Perform the comparison
    model = global_view.current_model()
    differences = compare.compare_graphs( model.fusion_graph_clean, test_tree_file_data )
    
    # Write the results---
    
    # ---Summary
    io_helper.save_ini( tdir.r_summary, differences.raw_data )
    
    # ---Alignments
    s070_alignment.print_alignments( file = tdir.r_alignments )
    
    # ---Differences
    file_helper.write_all_text( tdir.r_comparison, differences.html, newline = True )
    differences.name = "test_differences"
    global_view.current_model().user_reports.append( differences )
    
    # ---Model
    s010_file.file_save( tdir.r_model )
    
    # Done
    MCMD.progress( "The test has completed, see «{}».".format( tdir.r_comparison ) )
    return EChanges.MODEL_OBJECT


@command()
def load_test( name: str ) -> EChanges:
    """
    Loads the model created via `run_test`.
    :param name:    Test name
    """
    tdir = TestDirectory( name )
    
    if not path.isfile( tdir.r_model ):
        raise ValueError( "Cannot load test because it has not yet been run." )
    
    return s010_file.file_load( tdir.r_model )


@command()
def view_test_results( name: Optional[str] = None ):
    """
    View the results of a particular test.
    
    :param name:    Name, or `None` to use the currently loaded model.
    """
    if name:
        tdir = TestDirectory( name )
        groot.file_load( tdir.r_model )
    
    model = groot.current_model()
    
    s080_tree.print_trees( model.user_graphs["original_graph"], format = EFormat._HTML, file = "open" )
    s080_tree.print_trees( model.fusion_graph_unclean, format = EFormat._HTML, file = "open" )
    s080_tree.print_trees( model.fusion_graph_clean, format = EFormat._HTML, file = "open" )
    
    for component in model.components:
        s080_tree.print_trees( component.named_tree_unrooted, format = EFormat._HTML, file = "open" )
        s080_tree.print_trees( component.named_tree, format = EFormat._HTML, file = "open" )
    
    report = model.user_reports["test_differences"].html
    
    with OpeningWriter() as view_report:
        view_report.write( report )


@command( visibility = visibilities.ADVANCED )
def drop_tests():
    """
    Deletes *all* test cases and their results.
    """
    for folder in TestDirectory.get_test_folder(), TestDirectory.get_results_folder():
        shutil.rmtree( folder )
        MCMD.progress( "Removed: {}".format( folder ) )


@command( visibility = visibilities.ADVANCED )
def create_test( types: str = "1", no_blast: bool = False, size: int = 2, run: bool = True ) -> EChanges:
    """
    Creates a GROOT unit test in the sample data folder.
    
    * GROOT should be installed in developer mode, otherwise there may be no write access to the sample data folder.
    * Requires the `faketree` library. 
    
    :param run:         Run test after creating it.
    :param no_blast:    Perform no BLAST 
    :param size:        Clade size
    :param types:       Type(s) of test(s) to create.
    :return: List of created test directories 
    """
    # noinspection PyPackageRequirements
    import faketree as Ж
    MCMD.print( "START" )
    r = []
    args_random_tree = { "suffix": "1", "delimiter": "_", "size": size, "outgroup": True }
    # args_fn = "-d 0.2"
    mutate_args = ""
    
    if not types:
        raise ValueError( "Missing :param:`types`." )
    
    tdir = TestDirectory( None )
    
    for name in types:
        try:
            Ж.new()
            # The SeqGen mutator has a weird problem where, given a root `(X,O)R` in which `R`
            # is set as a result of an earlier tree, `O` will be more similar to the leaves of
            # that earlier tree than to the leaves in X. For this reason we use a simple random
            # model and not SeqGen.
            mutate_fn = Ж.random
            
            if name == "1":
                # 1 fusion point; 3 genes; 2 origins
                #
                # # Should be an acyclic 2-rooted tree:
                #
                # A
                #  \
                #   -->C
                #  /
                # B
                #
                
                # Trees
                outgroups = Ж.random_tree( ["A", "B", "C"], **args_random_tree )
                a, b, c = (x.parent for x in outgroups)
                __remove_outgroups( outgroups, 2 )
                
                mutate_fn( [a, b, c], *mutate_args )
                
                # Fusion point
                fa = Ж.random_node( a, avoid = outgroups )
                fb = Ж.random_node( b, avoid = outgroups )
                Ж.branch( [fa, fb], c )
                Ж.mk_composite( [c] )
            elif name == "4":
                # 2 fusion points; 4 genes; 2 origins
                # (Possibly the most difficult scenario because the result is cyclic)
                #
                # Should be a cyclic 2-rooted graph:
                #
                #
                # A--------
                #  \       \
                #   -->C    -->D
                #  /       /
                # B--------
                #         
                
                
                # Trees
                outgroups = Ж.random_tree( ["A", "B", "C", "D"], **args_random_tree )
                a, b, c, d = (x.parent for x in outgroups)
                mutate_fn( [a, b, c, d], *mutate_args )
                __remove_outgroups( outgroups, 2, 3 )
                
                # Fusion points
                fa1 = Ж.random_node( a, avoid = outgroups )
                fb1 = Ж.random_node( b, avoid = outgroups )
                fa2 = Ж.random_node( a, avoid = outgroups )
                fb2 = Ж.random_node( b, avoid = outgroups )
                Ж.branch( [fa1, fb1], c )
                Ж.branch( [fa2, fb2], d )
                Ж.mk_composite( [c, d] )
            
            elif name == "5":
                # 2 fusion points; 5 genes; 3 origins
                #
                # # Should be an acyclic 3-rooted tree:
                #
                # A
                #  \
                #   -->C
                #  /    \
                # B      -->E
                #       /
                #      D
                
                # Trees
                outgroups = Ж.random_tree( ["A", "B", "C", "D", "E"], **args_random_tree )
                a, b, c, d, e = (x.parent for x in outgroups)
                mutate_fn( [a, b, c, d, e], *mutate_args )
                __remove_outgroups( outgroups, 2, 4 )
                
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
                #
                # Should be an acyclic 4-rooted tree:
                #
                # A
                #  \
                #   -->C
                #  /    \
                # B      \
                #         -->G
                # D      /
                #  \    /
                #   -->F
                #  /
                # E
                #
                
                
                # Trees
                outgroups = Ж.random_tree( ["A", "B", "C", "D", "E", "F", "G"], **args_random_tree )
                a, b, c, d, e, f, g = (x.parent for x in outgroups)
                mutate_fn( [a, b, c, d, e, f, g], *mutate_args )
                __remove_outgroups( outgroups, 2, 5, 6 )
                
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
            
            file_helper.create_directory( tdir.t_folder )
            os.chdir( tdir.t_folder )
            
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
            return run_test( tdir.t_name )
    
    return EChanges.INFORMATION


def __remove_outgroups( outgroups, *args ):
    # noinspection PyPackageRequirements
    import faketree
    
    # Check is actually outgroup!
    for x in args:
        assert outgroups[x].num_children == 0
    
    faketree.remove( [outgroups[x] for x in args] )
    
    for x in sorted( args, reverse = True ):
        del outgroups[x]
