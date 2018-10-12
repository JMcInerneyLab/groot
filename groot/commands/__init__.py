"""
Groot's core logic.

* This subpackage should be considered internal: Groot's API is exposed through `groot.__init__.py`.
* Groot's workflow is linear, so the stages are named after the order in which they appear.
* Note that despite this submodule's name, several algorithms are outsourced to user provided
  functions or external tools, which can be supplemented by providing a Groot extension:- see the `groot_ex` package.
* These algorithms are able to report their progress through Intermake.
* The `gimmicks` subpackage contains features not required for groot's core logic, but which may be useful to the user.
"""


from . import gimmicks
from . import workflow

from .gimmicks.compare import create_comparison, compare_graphs
from .gimmicks.miscellaneous import query_quartet, composite_search_fix, print_file
from .gimmicks.status import print_status
from .gimmicks.usergraphs import import_graph, drop_graph
from .gimmicks.wizard import Wizard, create_wizard, drop_wizard, continue_wizard, create_components, drop_components, import_file, import_directory

from .workflow.s010_file import file_load, file_load_last, file_new, file_save, file_sample, file_recent
from .workflow.s020_sequences import drop_genes, set_genes, import_genes, set_gene_name, import_gene_names
from .workflow.s030_similarity import create_similarities, drop_similarities, set_similarity, import_similarities, print_similarities, similarity_algorithms
from .workflow.s040_major import create_major, drop_major, set_major, print_major
from .workflow.s050_minor import create_minor, drop_minor, print_minor
from .workflow.s055_outgroups import set_outgroups, print_outgroups
from .workflow.s060_userdomains import print_domains, create_domains, drop_domains, domain_algorithms
from .workflow.s070_alignment import print_alignments, create_alignments, drop_alignment, set_alignment, alignment_algorithms
from .workflow.s080_tree import print_trees, create_trees, set_tree, drop_trees, tree_algorithms
from .workflow.s090_fusion_events import print_fusions, drop_fusions, create_fusions
from .workflow.s100_splits import print_splits, drop_splits, create_splits
from .workflow.s110_consensus import print_consensus, create_consensus, drop_consensus
from .workflow.s120_subsets import print_subsets, create_subsets, drop_subsets
from .workflow.s130_pregraphs import create_pregraphs, drop_pregraphs, print_pregraphs
from .workflow.s140_supertrees import create_supertrees, drop_supertrees, print_supertrees, supertree_algorithms
from .workflow.s150_fuse import create_fused, drop_fused
from .workflow.s160_clean import create_cleaned, drop_cleaned
from .workflow.s170_checked import create_checked, drop_checked