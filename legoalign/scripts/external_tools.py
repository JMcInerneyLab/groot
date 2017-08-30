from mhelper import FileHelper, ExceptionHelper, BioHelper


def consensus( trees ):
    SCRIPT = """GetTrees file=in_file.nwk;
                ConTree /treeFile=temp_file.nex;
                GetTrees file=temp_file.nex;
                SaveTrees file=out_file.nwk format=Newick replace=yes;
                quit;"""
    
    FileHelper.write_all_text( "in_file.nwk", trees )
    FileHelper.write_all_text( "in_file.paup", SCRIPT )
    
    ExceptionHelper.run_subprocess( "paup in_file.paup" )
    
    return FileHelper.read_all_text( "out_file.nwk" )


def tree( alignment ):
    FileHelper.write_all_text( "in_file.fasta", alignment )
    BioHelper.convert_file( "in_file.fasta", "in_file.phy", "fasta", "phylip" )
    
    ExceptionHelper.run_subprocess( "raxml -m PROTGAMMAWAG -p 1 -s in_file.phy -# 20 -n t" )
    
    return FileHelper.read_all_text( "RAxML_bestTree.t" )


def align( fasta ):
    FileHelper.write_all_text( "in_file.fasta", fasta )
    
    alignment_command = "muscle -in in_file.fasta -out out_file.fasta"
    ExceptionHelper.run_subprocess( alignment_command )
    
    return FileHelper.read_all_text( "out_file.fasta" )
