"""
GrootEx provides the default set of algorithms for Groot.
It is automatically loaded when Groot starts.

GrootEx could have been integrated into Groot itself, but by including it as a separate package,
it serves as an example on how to specify your own Groot algorithms.

To get Groot to register custom algorithms, use the `import` command.
You can register python packages with an `__init__.py` (like `groot_ex`!) or stand-alone python files (like `align.py`).  
"""
from groot_ex import align, domains, supertree, tree
