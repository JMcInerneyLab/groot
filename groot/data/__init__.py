"""
The `.data` submodule contains the "Lego Model" (the dynamic data the user instantiates),
and its static dependencies (interfaces, enumerations, error classes, etc.).  
"""

from .model import \
    LegoModel

from .model_core import \
    LegoComponent, \
    LegoReport, \
    LegoEdge, \
    LegoSequence, \
    LegoFusion, \
    LegoFormation, \
    LegoPoint, \
    LegoPregraph, \
    LegoSubset, \
    LegoSubsequence, \
    LegoUserDomain, \
    LegoSplit, \
    Subgraph, \
    FusionGraph, \
    FixedUserGraph, \
    UserGraph

from .model_interfaces import \
    ILegoNode, \
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