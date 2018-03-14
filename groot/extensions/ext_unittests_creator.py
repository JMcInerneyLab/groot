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
def remove_tests():
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
def make_test( types: str, no_blast: bool = False, size: int = 25, view: bool = False, run: bool = True ) -> List[str]:
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
    import faketree as ft
    MCMD.print( "START" )
    r = []
    kwargs = { "suffix": "1", "delimiter": "_", "size": size, "outgroup": True }
    sgargs = "-d 0.2"
    
    if not types:
        raise ValueError( "Missing :param:`types`." )
    
    folder: str = global_view.get_sample_data_folder()
    
    for name in types:
        try:
            ft.new()
            
            if name == "1":
                # 1 fusion point; 3 genes; 2 origins
                
                # Trees
                outgroups = ft.random_tree( ["A", "B", "C"], **kwargs )
                a, b, c = (x.parent for x in outgroups)
                
                ft.seqgen( [a, b, c], sgargs )
                
                # Fusion point
                fa = ft.random_node( a, avoid = outgroups )
                fb = ft.random_node( b, avoid = outgroups )
                ft.branch( [fa, fb], c )
                ft.mk_composite( [c] )
            elif name == "4":
                # 2 fusion points; 4 genes; 2 origins
                
                # Trees
                outgroups = ft.random_tree( ["A", "B", "C", "D"], **kwargs )
                a, b, c, d = (x.parent for x in outgroups)
                ft.seqgen( [a, b, c, d], sgargs )
                
                # Fusion points
                fa1 = ft.random_node( a, avoid = outgroups )
                fb1 = ft.random_node( b, avoid = outgroups )
                fa2 = ft.random_node( fa1, avoid = outgroups )
                fb2 = ft.random_node( fb1, avoid = outgroups )
                ft.branch( [fa1, fb1], c )
                ft.branch( [fa2, fb2], d )
                ft.mk_composite( [c, d] )
            
            elif name == "5":
                # 2 fusion points; 5 genes; 3 origins
                
                # Trees
                outgroups = ft.random_tree( ["A", "B", "C", "D", "E"], **kwargs )
                a, b, c, d, e = (x.parent for x in outgroups)
                ft.seqgen( [a, b, c, d, e], sgargs )
                
                # Fusion points
                fa = ft.random_node( a, avoid = outgroups )
                fb = ft.random_node( b, avoid = outgroups )
                fc = ft.random_node( c, avoid = outgroups )
                fd = ft.random_node( d, avoid = outgroups )
                ft.branch( [fa, fb], c )
                ft.branch( [fc, fd], e )
                ft.mk_composite( [c, e] )
            elif name == "7":
                # 3 fusion points; 7 genes; 4 origins
                
                # Trees
                outgroups = ft.random_tree( ["A", "B", "C", "D", "E", "F", "G"], **kwargs )
                a, b, c, d, e, f, g = (x.parent for x in outgroups)
                ft.seqgen( [a, b, c, d, e, f, g], sgargs )
                
                # Fusion points
                fa = ft.random_node( a, avoid = outgroups )
                fb = ft.random_node( b, avoid = outgroups )
                fc = ft.random_node( c, avoid = outgroups )
                fd = ft.random_node( d, avoid = outgroups )
                fe = ft.random_node( e, avoid = outgroups )
                ff = ft.random_node( f, avoid = outgroups )
                ft.branch( [fa, fb], c )
                ft.branch( [fd, fe], f )
                ft.branch( [fc, ff], g )
                ft.mk_composite( [c, f, g] )
            else:
                raise SwitchError( "name", name )
            
            ft.apply()
            dir = file_helper.sequential_file_name( file_helper.join( folder, name + "_*" ) )
            file_helper.create_directory( dir )
            os.chdir( dir )
            ft.show( format = ft.EGraphFormat.ASCII, file = "tree.txt" )
            ft.show( format = ft.EGraphFormat.TSV, file = "tree.tsv", name = True, mutator = False, sequence = False, length = False )
            ft.fasta( which = ft.ESubset.ALL, file = "all.fasta.hidden" )
            ft.fasta( which = ft.ESubset.LEAVES, file = "leaves.fasta" )
            
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
        
        except ft.RandomChoiceError as ex:
            MCMD.print( "FAILURE {}".format( ex ) )
    
    return r
