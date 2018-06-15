"""
The `.data` submodule contains the "Lego Model" (the dynamic data the user instantiates),
and its static dependencies (interfaces, enumerations, error classes, etc.).  
"""
from .model import \
    Model

from .model_core import \
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
    UserGraph

from .model_interfaces import \
    INode, \
    EPosition, \
    ESiteType, \
    IHasFasta, \
    INamed, \
    INamedGraph

from .exceptions import \
    FastaError, \
    InUseError, \
    AlreadyError, \
    NotReadyError

from . import global_view

from .global_view import current_model, GlobalOptions


