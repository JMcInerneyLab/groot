from intermake import subprocess_helper
from mhelper import bio_helper, file_helper, SwitchError
from groot import tree_algorithms


@tree_algorithms.register( "neighbor_joining" )
def tree_neighbor_joining( model: str, alignment: str ) -> str:
    """
    Uses PAUP to generate the tree using neighbour-joining.
    
    :remarks:
    PAUP is trial-ware, displaying a "This version of PAUP has expired"
    after a timeout period. If this function doesn't work, check your
    PAUP version.
    
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
    
    subprocess_helper.run_subprocess( ["paup", "-n", "in_file.paup"] )
    
    return file_helper.read_all_text( "out_file.nwk" )


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
    
    return file_helper.read_all_text( "RAxML_bestTree.t" )
