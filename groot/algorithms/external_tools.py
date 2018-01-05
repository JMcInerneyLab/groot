import re

from groot.algorithms import extenal_runner
from mhelper import bio_helper, file_helper


_RX1 = re.compile( ":[0-9.]+" )


def consensus( trees ):
    """
    Generates a consensus tree.
    
    :param trees:       Input trees, in Newick format. One tree per line. 
    :return:            Output (consensus) tree, in Newick format.
    """
    
    SCRIPT = """GetTrees file=in_file.nwk;
                ConTree /treeFile=temp_file.nex;
                GetTrees file=temp_file.nex;
                SaveTrees file=out_file.nwk format=Newick replace=yes;
                quit;"""
    
    # Strip the branch lengths, Paup doesn't like them
    trees = _RX1.sub( "", trees )
    file_helper.write_all_text( "in_file.nwk", trees )
    file_helper.write_all_text( "in_file.paup", SCRIPT )
    
    extenal_runner.run_subprocess( ["paup", "in_file.paup"] )
    
    return file_helper.read_all_text( "out_file.nwk" )


# def consensus( trees ):
#     """
#     Generates a consensus tree.
#     
#     :param trees:       Input trees, in Newick format. One tree per line. 
#     :return:            Output (consensus) tree, in Newick format.
#     """
#     import sys
#     from Bio.Phylo import Consensus
#     
#     # Let's use BioPython and a majority consensus.
#     trees_ = [bio_helper.newick_to_biotree( x ) for x in trees.split( "\n" ) if x]
#     orig = sys.getrecursionlimit()
#     sys.setrecursionlimit( 100000 )
#     majority_tree = Consensus.adam_consensus( trees_ )
#     sys.setrecursionlimit( orig )
#     result = bio_helper.biotree_to_newick( majority_tree )
#     return result


def tree( alignment ):
    """
    Generates a tree.
    
    :param alignment:   Alignment data, in Fasta format. 
    :return:            Output tree, in Newick format.
    """
    file_helper.write_all_text( "in_file.fasta", alignment )
    bio_helper.convert_file( "in_file.fasta", "in_file.phy", "fasta", "phylip" )
    
    extenal_runner.run_subprocess( "raxml -T 4 -m PROTGAMMAWAG -p 1 -s in_file.phy -# 20 -n t".split( " " ) )
    
    return file_helper.read_all_text( "RAxML_bestTree.t" )


def align( fasta ):
    """
    Generates an alignment.
    
    :param fasta:       Input data, in Fasta format. 
    :return:            Output data, in Fasta format.
    """
    file_helper.write_all_text( "in_file.fasta", fasta )
    
    extenal_runner.run_subprocess( "muscle -in in_file.fasta -out out_file.fasta".split( " " ) )
    
    return file_helper.read_all_text( "out_file.fasta" )
