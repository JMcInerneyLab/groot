from intermake import subprocess_helper
from mhelper import bio_helper, file_helper, SwitchError
from groot import tree_algorithms


@tree_algorithms.register( "neighbor_joining" )
def tree_neighbor_joining( model: str, alignment: str ) -> str:
    """
    Uses PAUP to generate the tree using neighbour-joining.
    
    There are some major issues with Paup. Please see the troubleshooting section of Groot's readme.
    
    :param model:       Format, a string `n` or `p` denoting the site type.
    :param alignment:   Alignment in FASTA format.
    :return:            The tree in Newick format.
    """
    # TODO: Use an alternative that doesn't have the PAUP time-out problem.
    file_helper.write_all_text( "in_file.fasta", alignment )
    
    script = """
    toNEXUS format=FASTA fromFile=in_file.fasta toFile=in_file.nexus dataType=protein replace=yes;
    execute in_file.nexus;
    NJ;
    SaveTrees file=out_file.nwk format=Newick root=Yes brLens=Yes replace=yes;
    quit;"""
    
    if model == "n":
        site_type = "nucleotide"
    elif model == "p":
        site_type = "protein"
    else:
        raise SwitchError( "model", model )
    
    script = script.format( site_type )
    file_helper.write_all_text( "in_file.paup", script )
    
    # Paup is shareware and periodically fails with an error.
    # Unfortunately it doesn't report it in its return code so we try to catch this error based on STD-OUT here.
    
    with open( "temp.io", "w" ) as tmp:
        def tmpc( x ):
            if "This version of PAUP has expired." in x:
                raise ValueError( "Shareware timeout: 'This version of PAUP has expired'. Please update your software or use a different method and try again." )
            
            tmp.write( x )
            tmp.write( "\n" )
        
        # The return code seems to have no bearing on Paup's actual output, so ignore it.
        subprocess_helper.run_subprocess( ["paup", "-n", "in_file.paup"], collect = tmpc, no_err = True )
    
    return file_helper.read_all_text( "out_file.nwk", details = "the expected output from paup" )


@tree_algorithms.register( "maximum_likelihood" )
def tree_maximum_likelihood( model: str, alignment: str ) -> str:
    """
    Uses Raxml to generate the tree using maximum likelihood.
    The model used is GTRCAT for RNA sequences, and PROTGAMMAWAG for protein sequences.
    """
    file_helper.write_all_text( "in_file.fasta", alignment )
    bio_helper.convert_file( "in_file.fasta", "in_file.phy", "fasta", "phylip" )
    
    if model == "n":
        method = "GTRCAT"
    elif model == "p":
        method = "PROTGAMMAWAG"
    else:
        raise SwitchError( "model", model )
    
    subprocess_helper.run_subprocess( "raxml -T 4 -m {} -p 1 -s in_file.phy -# 20 -n t".format( method ).split( " " ) )
    
    return file_helper.read_all_text( "RAxML_bestTree.t", "the expected output from raxml" )
