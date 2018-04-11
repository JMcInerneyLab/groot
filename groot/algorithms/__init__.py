"""
Groot's core logic.

Groot's workflow is linear, so the stages are named after the order in which they appear.

As these processes are subject to change, the algorithms aren't part of the public API, use `groot.extensions` for that.
Note that several algorithms are outsourced to external tools and can be modified by providing a Groot extension.
"""

from groot.algorithms import s0_editor, s0_file, s1_importation, s3_components, s4_userdomains, s5_alignment, s7_fusion_events, s6_tree, s8_splits, s9_consensus, s10_subsets, s12_supertrees, s13_fuse, s14_clean, s15_checked, wizard, s2_similarity, s11_pregraphs


