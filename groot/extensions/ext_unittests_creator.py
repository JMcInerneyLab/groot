import shutil
from os import path

from typing import List
from uuid import uuid4

from intermake import MCMD, visibilities, command, subprocess_helper

from mhelper import file_helper, SwitchError, io_helper
import os
from groot.data import global_view
from groot.extensions import ext_gimmicks, ext_unittests


@command( visibility = visibilities.ADVANCED )
def drop_tests():
    """
    Deletes all test cases from the sample data folder.
    """
    dirs = file_helper.list_dir( global_view.get_sample_data_folder() )
    
    for dir in dirs:
        ini_file = path.join( dir, "groot.ini" )
        if path.isfile( ini_file ):
            if "groot_test" in io_helper.load_ini( ini_file ):
                shutil.rmtree( dir )
                MCMD.progress( "Removed: {}".format( dir ) )


@command( visibility = visibilities.ADVANCED )
def create_test( types: str = "1", no_blast: bool = False, size: int = 10, view: bool = False, run: bool = True ) -> List[str]:
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
    #args_fn = "-d 0.2"
    args_fn = ""
    
    if not types:
        raise ValueError( "Missing :param:`types`." )
    
    folder: str = global_view.get_sample_data_folder()
    
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
                                                  collect_stdout = blast.append,
                                                  hide = True )
                
                file_helper.write_all_text( "leaves.blast", blast )
            
            guid = uuid4()
            outgroups_str = ",".join( x.data.name for x in outgroups if x.parent.is_root )
            file_helper.write_all_text( "groot.ini", "[groot_wizard]\ntolerance=50\noutgroups={}\n\n[groot_test]\nguid={}\n".format( outgroups_str, guid ) )
            
            path_ = path.abspath( "." )
            MCMD.print( "FINAL PATH: " + path_ )
            r.append( path_ )
            
            if view:
                ext_gimmicks.view_graph( "tree.tsv", title = "ORIGINAL GRAPH. GUID = {}.".format( guid ) )
            
            if run:
                ext_unittests.run_test( path_, refresh = True )
        
        except Ж.RandomChoiceError as ex:
            MCMD.print( "FAILURE {}".format( ex ) )
    
    return r
