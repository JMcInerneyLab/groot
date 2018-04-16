"""
Groot's core logic.

* As these processes are subject to change, these algorithms aren't part of the public API,
    * The `.extensions` subpackage providing the clean, managed, entry points.
* Groot's workflow is linear, so the stages are named after the order in which they appear.
* Note that despite this submodule's name, several algorithms are outsourced to user provided
  functions or external tools and can be modified by providing a Groot extension:- see the `groot_ex` package.
* These algorithms are able to report their progress through Intermake (`MCMD`).
"""

from groot.algorithms import s999_editor, s010_file, s020_importation, s040_major, s060_userdomains, s070_alignment, s090_fusion_events, s080_tree, s100_splits, s110_consensus, s120_subsets, s140_supertrees, s150_fuse, s160_clean, s170_checked, s999_wizard, s030_similarity, s130_pregraphs, s050_minor, s999_compare

