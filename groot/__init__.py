"""
Groot entry point.
"""


__author__ = "Martin Rusilowicz"
__version__ = "0.0.0.43"

import groot.init
from groot.extensions import ext_dropping, ext_files, ext_generating, ext_gimmicks, ext_gui, ext_modifications, ext_viewing, ext_unittests, ext_unittests_creator  # export; to register
from groot import extensions
from groot import algorithms
from groot.algorithms.s5_alignment import alignment_algorithms
from groot.algorithms.s12_supertrees import supertree_algorithms
from groot.algorithms.s6_tree import tree_algorithms
from groot.algorithms.s4_userdomains import domain_algorithms
from groot.data.lego_model import LegoModel, LegoPoint, LegoSubset, LegoSequence, LegoStage, LegoSplit, LegoComponent, LegoSubsequence, LegoEdge, LegoUserDomain, LegoComponentCollection, LegoEdgeCollection, LegoFusion, LegoFusionEventCollection, LegoSequenceCollection, LegoUserDomainCollection, LegoViewOptions, ILegoNode, ILegoSelectable

from intermake import run_jupyter
run_jupyter = run_jupyter

import groot_ex
