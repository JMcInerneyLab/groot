from typing import Iterable, List, Set
from mgraph import MNode
from groot.data.lego_model import ILeaf, LegoSequence, FusionPoint


def get_sequence_data( nodes: Iterable[MNode] ) -> Set[LegoSequence]:
    return set( node.data for node in nodes if isinstance( node.data, LegoSequence ) )


def get_fusion_data( nodes: Iterable[MNode] ) -> Set[FusionPoint]:
    return set( node.data for node in nodes if isinstance( node.data, FusionPoint ) )


def get_fusion_nodes( nodes: Iterable[MNode] ) -> List[MNode]:
    return [node for node in nodes if isinstance( node.data, FusionPoint )]


def is_clade( node: MNode ) -> bool:
    return node.data is None or isinstance( node.data, str )


def is_fusion( node: MNode ) -> bool:
    return isinstance( node.data, FusionPoint )


def get_ileaf_data( params: Iterable[MNode] ) -> Set[ILeaf]:
    return set( x.data for x in params if isinstance( x.data, ILeaf ) )



