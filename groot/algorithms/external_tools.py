import os
import shutil

from mcommand import MENV, constants
from mhelper import bio_helper, exception_helper, file_helper


def run_in_temporary(command, *args, **kwargs):
    temp_folder_name = os.path.join( MENV.local_data.local_folder( constants.FOLDER_TEMPORARY ), "generate-tree" )
    
    if os.path.exists( temp_folder_name ):
        shutil.rmtree( temp_folder_name )
        
    file_helper.create_directory( temp_folder_name )
    os.chdir( temp_folder_name )
    
    try:
        return command(*args, **kwargs)
    finally:
        os.chdir( ".." )
        shutil.rmtree(temp_folder_name)


def consensus( trees ):
    SCRIPT = """GetTrees file=in_file.nwk;
                ConTree /treeFile=temp_file.nex;
                GetTrees file=temp_file.nex;
                SaveTrees file=out_file.nwk format=Newick replace=yes;
                quit;"""
    
    file_helper.write_all_text( "in_file.nwk", trees )
    file_helper.write_all_text( "in_file.paup", SCRIPT )
    
    exception_helper.run_subprocess( "paup in_file.paup" )
    
    return file_helper.read_all_text( "out_file.nwk" )


def tree( alignment ):
    file_helper.write_all_text( "in_file.fasta", alignment )
    bio_helper.convert_file( "in_file.fasta", "in_file.phy", "fasta", "phylip" )
    
    exception_helper.run_subprocess( "raxml -m PROTGAMMAWAG -p 1 -s in_file.phy -# 20 -n t" )
    
    return file_helper.read_all_text( "RAxML_bestTree.t" )


def align( fasta ):
    file_helper.write_all_text( "in_file.fasta", fasta )
    
    alignment_command = "muscle -in in_file.fasta -out out_file.fasta"
    exception_helper.run_subprocess( alignment_command )
    
    return file_helper.read_all_text( "out_file.fasta" )
