"""
Groot initialisation logic and API exports.
"""

#
# Meta-data
#
from groot.data.model_meta import _ComponentAsFasta, _ComponentAsGraph


__author__ = "Martin Rusilowicz"
__version__ = "0.0.0.47"

#
# Initialise Groot
#
from groot.application import GROOT_APP

#
# Export API
#
from groot.data import Model, \
    Component, \
    Report, \
    Edge, \
    Gene, \
    Fusion, \
    Formation, \
    Point, \
    Pregraph, \
    Subset, \
    Domain, \
    UserDomain, \
    Split, \
    Subgraph, \
    FusionGraph, \
    FixedUserGraph, \
    UserGraph, \
    INode, \
    EPosition, \
    ESiteType, \
    IHasFasta, \
    INamed, \
    INamedGraph, \
    FastaError, \
    InUseError, \
    AlreadyError, \
    NotReadyError,\
    global_view, \
    GlobalOptions, \
    current_model

from groot.utilities import AlgorithmCollection, AbstractAlgorithm
from groot import constants
from groot.constants import STAGES, Stage, EChanges

from groot.algorithms.gimmicks.compare import create_comparison, compare_graphs
from groot.algorithms.gimmicks.miscellaneous import query_quartet, composite_search_fix, print_file
from groot.algorithms.gimmicks.status import print_status
from groot.algorithms.gimmicks.usergraphs import import_graph, drop_graph
from groot.algorithms.gimmicks.wizard import Wizard, create_wizard, drop_wizard, continue_wizard, create_components, drop_components, import_file, import_directory

from groot.algorithms.workflow.s010_file import file_load, file_load_last, file_new, file_save, file_sample, file_recent
from groot.algorithms.workflow.s020_sequences import drop_genes, set_genes, import_genes, set_gene_name, import_gene_names
from groot.algorithms.workflow.s030_similarity import create_similarity, drop_similarity, set_similarity, import_similarity, print_similarity
from groot.algorithms.workflow.s040_major import create_major, drop_major, set_major, print_major
from groot.algorithms.workflow.s050_minor import create_minor, drop_minor, print_minor
from groot.algorithms.workflow.s055_outgroups import set_outgroups, print_outgroups
from groot.algorithms.workflow.s060_userdomains import print_domains, create_domains, drop_domains, domain_algorithms
from groot.algorithms.workflow.s070_alignment import print_alignments, create_alignments, drop_alignment, set_alignment, alignment_algorithms
from groot.algorithms.workflow.s080_tree import print_trees, create_trees, set_tree, drop_tree, tree_algorithms
from groot.algorithms.workflow.s090_fusion_events import print_fusions, drop_fusions, create_fusions
from groot.algorithms.workflow.s100_splits import print_splits, drop_splits, create_splits
from groot.algorithms.workflow.s110_consensus import print_consensus, create_consensus, drop_consensus
from groot.algorithms.workflow.s120_subsets import print_subsets, create_subsets, drop_subsets
from groot.algorithms.workflow.s130_pregraphs import create_pregraphs, drop_pregraphs, print_pregraphs
from groot.algorithms.workflow.s140_supertrees import create_supertrees, drop_supertrees, print_supertrees, supertree_algorithms
from groot.algorithms.workflow.s150_fuse import create_fused, drop_fused
from groot.algorithms.workflow.s160_clean import create_cleaned, drop_cleaned
from groot.algorithms.workflow.s170_checked import create_checked, drop_checked


#
# Setup for use with Jupyter 
#
# noinspection PyUnresolvedReferences
from intermake import run_jupyter

#
# Allow the default Groot algorithm collection to register itself
#
# noinspection PyUnresolvedReferences
import groot_ex as _
