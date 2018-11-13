import os
import os.path
import shutil
import uuid
from itertools import count

import intermake
import mgraph

from typing import Optional
from mhelper import SwitchError, file_helper, io_helper, OpeningWriter

import groot
from groot.application import app
from groot_tests.test_directory import TestDirectory


@app.command()
def primary_test( repeats = 1 ):
    """
    This is Groot's primary test suite!
    
    :param repeats: Number of repeats.
                    The default `1` permits a quick test, though larger numbers will giver better edge-case coverage.
                    `-1` repeats forever (until Groot is forcibly closed). 
    :return:    Nothing is returned, the program shouldn't die and the output is printed to the screen when the test
                completes. If presumptively closed use the `print_test` command to review. 
    """
    if repeats < 0:
        r = count()
    elif repeats == 0:
        raise ValueError( "0 repeats is invalid." )
    else:
        r = range( repeats )
    
    for n in r:
        intermake.pr.printx( "groot - primary_test - repeat {} of {})".format( n, repeats ) )
        create_test( types = "01457", size = 10, run = True )


@app.command()
def print_test( name: str = "" ) -> groot.EChanges:
    """
    Lists the available test cases.
    
    :param name: Name of test to print. If `None` or empty all tests are printed. 
    """
    
    r = []
    
    if name:
        names = [name]
    else:
        names = [file_helper.get_filename( x ) for x in file_helper.list_sub_dirs( TestDirectory.get_test_folder() )]
    
    for name in intermake.pr.pr_iterate( names, "Parsing tests" ):
        tdir = TestDirectory( name )
        fp = name
        
        if not os.path.isfile( tdir.r_summary ):
            r.append( (fp, None, None, None) )
        else:
            ini = io_helper.load_ini( tdir.rc_ini )
            name = ini["groot_test"]["name"]
            size = ini["groot_test"]["size"]
            
            ini = io_helper.load_ini( tdir.r_summary, stop = ("quartets", "match_quartets") )
            match = ini["quartets"]["match_quartets"].split( " " )[1].strip( "()" )
            r.append( (fp, name, size, match) )
    
    with intermake.pr.pr_section( "Tests" ):
        print( "{} {} {} {}".format( "File".ljust( 20 ), "Name".ljust( 10 ), "Size".ljust( 10 ), "Match".ljust( 10 ) ) )
        
        for fp, name, size, match in sorted( r, key = lambda x: str( x[1] ) ):
            if name is None:
                print( fp.ljust( 20 ) + " - Not run" )
            else:
                print( "{} {} {} {}".format( fp.ljust( 20 ), name.ljust( 10 ), size.ljust( 10 ), match.ljust( 10 ) ) )
    
    return groot.EChanges.INFORMATION


@app.command()
def print_test_dir() -> groot.EChanges:
    """
    Prints the test directory.
    """
    print( TestDirectory.get_test_folder() )
    
    return groot.EChanges.INFORMATION


@app.command()
def run_test( name: str ) -> groot.EChanges:
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
    if not os.path.isdir( tdir.t_folder ):
        raise ValueError( "This is not a test case (it is not even a folder, «{}»).".format( tdir.t_folder ) )
    
    if not os.path.isfile( tdir.t_tree ):
        raise ValueError( "This is not a test case (it is missing the edge list file, «{}»).".format( tdir.t_tree ) )
    
    if not os.path.isfile( tdir.t_ini ):
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
    walkthrough = groot.Wizard( new = True,
                                 name = tdir.r_model,
                                 imports = groot.sample_data.get_sample_contents( tdir.t_folder ),
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
        test_tree_file_data = groot.UserGraph( mgraph.importing.import_edgelist( file_helper.read_all_text( tdir.t_tree ), delimiter = "\t" ), name = "original_graph" )
        groot.rectify_nodes( test_tree_file_data.graph, groot.current_model() )
        groot.current_model().user_graphs.append( groot.FixedUserGraph( test_tree_file_data.graph, "original_graph" ) )
    finally:
        # Save the final model regardless of whether the test succeeded
        groot.file_save( tdir.r_model )
    
    # Perform the comparison
    model = groot.current_model()
    differences = groot.compare_graphs( model.fusion_graph_clean, test_tree_file_data )
    q = differences.raw_data["quartets"]["match_quartets"]
    print( "match_quartets: " + q )
    
    # Write the results---
    
    # ---Summary
    io_helper.save_ini( tdir.r_summary, differences.raw_data )
    
    # ---Alignments
    groot.print_alignments( file = tdir.r_alignments )
    
    # ---Differences
    file_helper.write_all_text( tdir.r_comparison, differences.html, newline = True )
    differences.name = "test_differences"
    groot.current_model().user_reports.append( differences )
    
    # ---Model
    groot.file_save( tdir.r_model )
    
    # Done
    intermake.pr.printx( "<verbose>The test has completed, see «{}».</verbose>".format( tdir.r_comparison ) )
    return groot.EChanges.MODEL_OBJECT


@app.command()
def load_test( name: str ) -> groot.EChanges:
    """
    Loads the model created via `run_test`.
    :param name:    Test name
    """
    tdir = TestDirectory( name )
    
    if not os.path.isfile( tdir.r_model ):
        raise ValueError( "Cannot load test because it has not yet been run." )
    
    return groot.file_load( tdir.r_model )


@app.command()
def view_test_results( name: Optional[str] = None ):
    """
    View the results of a particular test.
    
    :param name:    Name, or `None` to use the currently loaded model.
    """
    if name:
        tdir = TestDirectory( name )
        groot.file_load( tdir.r_model )
    
    model = groot.current_model()
    
    groot.print_trees( model.user_graphs["original_graph"], format = groot.EFormat._HTML, file = "open" )
    groot.print_trees( model.fusion_graph_unclean, format = groot.EFormat._HTML, file = "open" )
    groot.print_trees( model.fusion_graph_clean, format = groot.EFormat._HTML, file = "open" )
    
    for component in model.components:
        groot.print_trees( component.named_tree_unrooted, format = groot.EFormat._HTML, file = "open" )
        groot.print_trees( component.named_tree, format = groot.EFormat._HTML, file = "open" )
    
    report = model.user_reports["test_differences"].html
    
    with OpeningWriter() as view_report:
        view_report.write( report )


@app.command()
def drop_tests():
    """
    Deletes *all* test cases and their results.
    """
    for folder in TestDirectory.get_test_folder(), TestDirectory.get_results_folder():
        shutil.rmtree( folder )
        intermake.pr.printx( "<verbose>Removed: {}</verbose>".format( folder ) )


@app.command()
def create_test( types: str = "1", no_blast: bool = False, size: int = 2, run: bool = True ) -> groot.EChanges:
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
    import faketree as FAKE
    print( "START" )
    r = []
    args_random_tree = { "suffix": "1", "delimiter": "_", "size": size, "outgroup": True }
    # args_fn = "-d 0.2"
    mutate_args = ""
    
    if not types:
        raise ValueError( "Missing :param:`types`." )
    
    for index, name in enumerate( types ):
        tdir = TestDirectory( None )
        
        print( "Test {} of {}".format( index + 1, len( types ) ) )
        
        try:
            FAKE.new_tree()
            # The SeqGen mutator has a weird problem where, given a root `(X,O)R` in which `R`
            # is set as a result of an earlier tree, `O` will be more similar to the leaves of
            # that earlier tree than to the leaves in X. For this reason we use a simple random
            # model and not SeqGen.
            mutate_fn = FAKE.make_random
            
            if name == "0":
                # 0 no fusions
                outgroups = FAKE.create_random_tree( ["A"], **args_random_tree )
                a, = (x.parent for x in outgroups)
                mutate_fn( [a], *mutate_args )
            elif name == "1":
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
                outgroups = FAKE.create_random_tree( ["A", "B", "C"], **args_random_tree )
                a, b, c = (x.parent for x in outgroups)
                __remove_outgroups( outgroups, 2 )
                
                mutate_fn( [a, b, c], *mutate_args )
                
                # Fusion point
                fa = FAKE.get_random_node( a, avoid = outgroups )
                fb = FAKE.get_random_node( b, avoid = outgroups )
                FAKE.create_branch( [fa, fb], c )
                FAKE.make_composite_node( [c] )
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
                outgroups = FAKE.create_random_tree( ["A", "B", "C", "D"], **args_random_tree )
                a, b, c, d = (x.parent for x in outgroups)
                mutate_fn( [a, b, c, d], *mutate_args )
                __remove_outgroups( outgroups, 2, 3 )
                
                # Fusion points
                fa1 = FAKE.get_random_node( a, avoid = outgroups )
                fb1 = FAKE.get_random_node( b, avoid = outgroups )
                fa2 = FAKE.get_random_node( a, avoid = outgroups )
                fb2 = FAKE.get_random_node( b, avoid = outgroups )
                FAKE.create_branch( [fa1, fb1], c )
                FAKE.create_branch( [fa2, fb2], d )
                FAKE.make_composite_node( [c, d] )
            
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
                outgroups = FAKE.create_random_tree( ["A", "B", "C", "D", "E"], **args_random_tree )
                a, b, c, d, e = (x.parent for x in outgroups)
                mutate_fn( [a, b, c, d, e], *mutate_args )
                __remove_outgroups( outgroups, 2, 4 )
                
                # Fusion points
                fa = FAKE.get_random_node( a, avoid = outgroups )
                fb = FAKE.get_random_node( b, avoid = outgroups )
                fc = FAKE.get_random_node( c, avoid = outgroups )
                fd = FAKE.get_random_node( d, avoid = outgroups )
                FAKE.create_branch( [fa, fb], c )
                FAKE.create_branch( [fc, fd], e )
                FAKE.make_composite_node( [c, e] )
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
                outgroups = FAKE.create_random_tree( ["A", "B", "C", "D", "E", "F", "G"], **args_random_tree )
                a, b, c, d, e, f, g = (x.parent for x in outgroups)
                mutate_fn( [a, b, c, d, e, f, g], *mutate_args )
                __remove_outgroups( outgroups, 2, 5, 6 )
                
                # Fusion points
                fa = FAKE.get_random_node( a, avoid = outgroups )
                fb = FAKE.get_random_node( b, avoid = outgroups )
                fc = FAKE.get_random_node( c, avoid = outgroups )
                fd = FAKE.get_random_node( d, avoid = outgroups )
                fe = FAKE.get_random_node( e, avoid = outgroups )
                ff = FAKE.get_random_node( f, avoid = outgroups )
                FAKE.create_branch( [fa, fb], c )
                FAKE.create_branch( [fd, fe], f )
                FAKE.create_branch( [fc, ff], g )
                FAKE.make_composite_node( [c, f, g] )
            else:
                raise SwitchError( "name", name )
            
            FAKE.generate()
            
            file_helper.create_directory( tdir.t_folder )
            os.chdir( tdir.t_folder )
            
            FAKE.print_trees( format = mgraph.EGraphFormat.ASCII, file = "tree.txt" )
            FAKE.print_trees( format = mgraph.EGraphFormat.TSV, file = "tree.tsv", name = True, mutator = False, sequence = False, length = False )
            FAKE.print_fasta( which = FAKE.ESubset.ALL, file = "all.fasta.hidden" )
            FAKE.print_fasta( which = FAKE.ESubset.LEAVES, file = "leaves.fasta" )
            
            if not no_blast:
                blast = []
                # noinspection SpellCheckingInspection
                intermake.subprocess_helper.run_subprocess( ["blastp",
                                                             "-subject", "leaves.fasta",
                                                             "-query", "leaves.fasta",
                                                             "-outfmt", "6"],
                                                            collect_stdout = blast.append )
                
                file_helper.write_all_text( "leaves.blast", blast )
            
            guid = uuid.uuid4()
            outgroups_str = ",".join( x.data.name for x in outgroups if x.parent.is_root )
            
            file_helper.write_all_text( "groot.ini", ["[groot_wizard]",
                                                      "tolerance=50",
                                                      "outgroups={}".format( outgroups_str ),
                                                      "",
                                                      "[groot_test]",
                                                      "name={}".format( name ),
                                                      "size={}".format( size ),
                                                      "guid={}".format( guid )] )
            
            path_ = os.path.abspath( "." )
            print( "FINAL PATH: " + path_ )
            r.append( path_ )
        
        except FAKE.RandomChoiceError as ex:
            print( "FAILURE {}".format( ex ) )
            return groot.EChanges.INFORMATION
        
        if run:
            run_test( tdir.t_name )
    
    return groot.EChanges.INFORMATION


def __remove_outgroups( outgroups, *args ):
    # noinspection PyPackageRequirements
    import faketree
    
    # Check is actually outgroup!
    for x in args:
        assert outgroups[x].num_children == 0
    
    faketree.remove_node( [outgroups[x] for x in args] )
    
    for x in sorted( args, reverse = True ):
        del outgroups[x]
