"""
Groot entry point.
"""

#
# Meta-data
#
__author__ = "Martin Rusilowicz"
__version__ = "0.0.0.45"

#
# Initialise Groot
#
import groot.init

#
# Export API
#
from groot.extensions import ext_dropping, ext_files, ext_generating, ext_gimmicks, ext_gui, ext_modifications, ext_viewing, ext_unittests, ext_unittests_creator  # export; to register
from groot import extensions
from groot import algorithms
from groot.algorithms.s070_alignment import alignment_algorithms
from groot.algorithms.s140_supertrees import supertree_algorithms
from groot.algorithms.s080_tree import tree_algorithms
from groot.algorithms.s060_userdomains import domain_algorithms
from groot.constants import LegoStage
from groot.data.model_meta import LegoViewOptions
from groot.data.model_interfaces import ILegoNode
from groot.data.model_core import LegoEdge, LegoSubsequence, LegoUserDomain, LegoSequence, LegoComponent, LegoSplit, LegoSubset, LegoFusion, LegoPoint
from groot.data.model import LegoModel
from groot.data.model_collections import LegoEdgeCollection, LegoComponentCollection, LegoSequenceCollection, LegoUserDomainCollection, LegoFusionEventCollection

#
# Setup for use with Jupyter 
#
from intermake import run_jupyter
run_jupyter = run_jupyter

#
# Import default Groot algorithm collection
#
# noinspection PyUnresolvedReferences
import groot_ex
