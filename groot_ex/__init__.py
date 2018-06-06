"""
GrootEx provides the default set of algorithms for Groot.
It is automatically loaded when Groot starts.

To get Groot to register custom algorithms, use the `import` command.
You can register python packages with an `__init__.py` (like this one) or stand-alone python files (like `align.py`).  
"""
from groot_ex import align, domains, supertree, tree
