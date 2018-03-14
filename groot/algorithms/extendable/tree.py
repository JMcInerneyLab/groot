from intermake import subprocess_helper
from mhelper import bio_helper, file_helper
from groot.data.lego_model import LegoModel, ESiteType
from groot.algorithms.tree import register_algorithm


@register_algorithm
def tree_neighbor_joining( model: LegoModel, alignment: str ) -> str:
    """
    Uses PAUP to generate the tree using neighbour-joining.
    """
    file_helper.write_all_text( "in_file.fasta", alignment )
    
    script = """
    toNEXUS format=FASTA fromFile=in_file.fasta toFile=in_file.nexus dataType=protein replace=yes;
    execute in_file.nexus;
    NJ;
    SaveTrees file=out_file.nwk format=Newick root=Yes brLens=Yes replace=yes;
    quit;"""
    
    if model.site_type in (ESiteType.DNA, ESiteType.RNA):
        site_type = "nucleotide"
    else:
        site_type = "protein"
    
    script = script.format( site_type )
    file_helper.write_all_text( "in_file.paup", script )
    
    subprocess_helper.run_subprocess( ["paup", "-n", "in_file.paup"] )
    
    return file_helper.read_all_text( "out_file.nwk" )


@register_algorithm
def tree_maximum_likelihood( model: LegoModel, alignment: str ) -> str:
    """
    Uses Raxml to generate the tree using maximum likelihood.
    The model used is GTRCAT for RNA sequences, and PROTGAMMAWAG for protein sequences.
    """
    file_helper.write_all_text( "in_file.fasta", alignment )
    bio_helper.convert_file( "in_file.fasta", "in_file.phy", "fasta", "phylip" )
    
    if model.site_type in (ESiteType.DNA, ESiteType.RNA):
        method = "GTRCAT"
    else:
        method = "PROTGAMMAWAG"
    
    subprocess_helper.run_subprocess( "raxml -T 4 -m {} -p 1 -s in_file.phy -# 20 -n t".format( method ).split( " " ) )
    
    return file_helper.read_all_text( "RAxML_bestTree.t" )
