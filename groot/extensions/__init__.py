"""
This module contains what essentially comprises the core API.

The Intermake CLI/GUI exposes these functions through the command line, and Groot's own GUI relies on these functions to
manage the workload.

In reality these functions serve primarily as well defined entry points, delegating the heavy work to the `.algorithms` submodule. 
"""

from groot.extensions import ext_dropping, ext_files, ext_generating, ext_gimmicks, ext_gui, ext_importation, ext_modifications, ext_viewing, ext_unittests_creator, ext_unittests