from intermake import subprocess_helper
from mhelper import bio_helper, file_helper
from groot.data.lego_model import LegoModel, ESiteType
from groot.algorithms.tree import register_algorithm


@register_algorithm
def tree_raxml( model: LegoModel, alignment: str ) -> str:
    """
    Uses Raxml to generate the tree.
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
