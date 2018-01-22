"""
This module contains the user-defined algorithms.

Which algorithm is used can be specified in GROOT by the `algorithm` parameter.
If no algorithm is specified, the `_default` function is used.

Please see the pre-defined `_default` functions for details.
"""
import re

from groot.algorithms import extenal_runner
from groot.data.lego_model import LegoModel, ESiteType
from mhelper import bio_helper, file_helper


_RX1 = re.compile( ":[0-9.]+" )


def consensus_default( model: LegoModel, trees ):
    """
    Generates a consensus tree.
    
    :param trees:       Input trees, in Newick format. One tree per line. 
    :return:            Output (consensus) tree, in Newick format.
    """
    return consensus_paup( model, trees )


def consensus_paup( model: LegoModel, trees ):
    SCRIPT = """GetTrees file=in_file.nwk;
                ConTree /treeFile=temp_file.nex;
                GetTrees file=temp_file.nex;
                SaveTrees file=out_file.nwk format=Newick replace=yes;
                quit;"""
    
    GARBAGE = ("P A U P \\*",
               "Version .*",
               "Mon .*",
               "Running on .*",
               "SSE vectorization enabled",
               "SSSE3 instructions supported",
               "Multithreading enabled for likelihood using Pthreads",
               "Compiled using .*",
               ".*----.*",
               "This is an alpha-test version that is still changing rapidly\\.",
               "It will expire on .*",
               "Time used",
               "Strict consensus of",
               "Please report bugs to dave@phylosolutions\\.com",
               "Keeping: trees from file \\(replacing any trees already in memory\\)",
               ".*\\|.*")
    
    # Strip the branch lengths, Paup doesn't like them
    trees = _RX1.sub( "", trees )
    file_helper.write_all_text( "in_file.nwk", trees )
    file_helper.write_all_text( "in_file.paup", SCRIPT )
    
    extenal_runner.run_subprocess( ["paup", "in_file.paup", "-n"], garbage = GARBAGE )
    
    return file_helper.read_all_text( "out_file.nwk" )


def consensus_biopython( model: LegoModel, trees ):
    """
    Generates a consensus tree.

    :param trees:       Input trees, in Newick format. One tree per line. 
    :return:            Output (consensus) tree, in Newick format.
    """
    import sys
    from Bio.Phylo import Consensus
    
    # Let's use BioPython and a majority consensus.
    trees_ = [bio_helper.newick_to_biotree( x ) for x in trees.split( "\n" ) if x]
    orig = sys.getrecursionlimit()
    sys.setrecursionlimit( 100000 )
    majority_tree = Consensus.adam_consensus( trees_ )
    sys.setrecursionlimit( orig )
    result = bio_helper.biotree_to_newick( majority_tree )
    return result


def tree_default( model: LegoModel, alignment ):
    """
    Generates a tree.
    
    :param alignment:   Alignment data, in Fasta format. 
    :return:            Output tree, in Newick format.
    """
    return tree_paup( model, alignment )


def tree_paup( model: LegoModel, alignment ):
    """
    Variation of `tree_default` that uses Paup.
    """
    file_helper.write_all_text( "in_file.fasta", alignment )
    bio_helper.convert_file( "in_file.fasta", "in_file.phy", "fasta", "phylip" )
    
    if model.site_type == ESiteType.DNA:
        method = "GTRCAT"
    else:
        method = "PROTGAMMAWAG"
    
    extenal_runner.run_subprocess( "raxml -T 4 -m {} -p 1 -s in_file.phy -# 20 -n t".format( method ).split( " " ) )
    
    return file_helper.read_all_text( "RAxML_bestTree.t" )


def align_default( model: LegoModel, fasta ):
    """
    Generates an alignment.
    
    :param fasta:       Input data, in Fasta format. 
    :return:            Output data, in Fasta format.
    """
    return align_muscle( model, fasta )


def align_muscle( model: LegoModel, fasta ):
    """
    Variation of `align_default` which uses MUSCLE to align.
    """
    file_helper.write_all_text( "in_file.fasta", fasta )
    
    extenal_runner.run_subprocess( "muscle -in in_file.fasta -out out_file.fasta".split( " " ) )
    
    return file_helper.read_all_text( "out_file.fasta" )


def align_as_is( model: LegoModel, fasta ):
    """
    Variation of `align_default` which uses the FASTA as is.
    """
    return fasta
