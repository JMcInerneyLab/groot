"""
This is Groot's main package.
"""

from groot.application import *
from groot.data import *
from groot.commands import *

from groot.utilities import run_subprocess, rectify_nodes  # groot.utilities is primarily internal, though we export a few things for convenience
from groot.constants import STAGES, Stage, EChanges, EDomainNames, EFormat, EStartupMode, EWindowMode  # groot.constants is a mix of internal and external stuff, we specify the external bits now

# noinspection PyUnresolvedReferences
import groot_ex as _  # Allow the default Groot algorithm collection to register itself




