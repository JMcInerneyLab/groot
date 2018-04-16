from typing import Iterable, List, Set, Optional
from mgraph import MNode, MGraph
from groot.data.model_interfaces import EPosition, ILegoNode
from groot.data.model_core import LegoFormation, LegoSequence, LegoPoint
from groot.data.model import LegoModel
from mhelper import NotFoundError


def get_sequence_data( nodes: Iterable[MNode] ) -> Set[LegoSequence]:
    return set( node.data for node in nodes if isinstance( node.data, LegoSequence ) )


def get_fusion_data( nodes: Iterable[MNode] ) -> Set[LegoPoint]:
    return set( node.data for node in nodes if isinstance( node.data, LegoPoint ) )


def get_fusion_point_nodes( nodes: Iterable[MNode] ) -> List[MNode]:
    return [node for node in nodes if is_fusion_point( node )]


def get_fusion_formation_nodes( nodes: Iterable[MNode] ) -> List[MNode]:
    return [node for node in nodes if is_formation( node )]


def is_clade( node: MNode ) -> bool:
    return node.data is None or isinstance( node.data, str )


def is_fusion_like( node: MNode ) -> bool:
    return is_fusion_point( node ) or is_formation( node )


def is_formation( node: MNode ) -> bool:
    return isinstance( node.data, LegoFormation )


def is_fusion_point( node: MNode ) -> bool:
    return isinstance( node.data, LegoPoint )


def is_sequence_node( node: MNode ) -> bool:
    return isinstance( node.data, LegoSequence )


def is_lego_node( node: MNode ) -> bool:
    return isinstance( node.data, ILegoNode )


def get_ileaf_data( params: Iterable[MNode] ) -> Set[ILegoNode]:
    return set( x.data for x in params if isinstance( x.data, ILegoNode ) )


def rectify_nodes( graph: MGraph, model: LegoModel ):
    for node in graph:
        if isinstance( node.data, str ):
            node.data = import_leaf_reference( node.data, model, skip_missing = True )


def import_leaf_reference( name: str, model: LegoModel, *, allow_empty: bool = False, skip_missing: bool = False ) -> Optional[ILegoNode]:
    """
    Converts a sequence name to a sequence reference.
    
    :param name:        Name, either:
                            i.  The accession
                            ii. The ID, of the form `"S[0-9]+"`
    :param model:       The model to find the sequence in 
    :param allow_empty: Allow `None` or `""` to denote a missing sequence, `None`.
    :param skip_missing: Allow missing accessions to be skipped. 
    :return:            The sequence, or `None` if `allow_empty` is set.
    """
    if skip_missing:
        allow_empty = True
    
    if allow_empty and name is None:
        return None
    
    assert isinstance( name, str )
    
    try:
        if allow_empty and name == "" or name == "root" or name.startswith( "clade" ):
            return None
        elif LegoSequence.is_legacy_accession( name ):
            return model.find_sequence_by_legacy_accession( name )
        elif LegoPoint.is_legacy_accession( name ):
            return model.find_fusion_point_by_legacy_accession( name )
        elif LegoFormation.is_legacy_accession( name ):
            return model.find_fusion_formation_by_legacy_accession( name )
        else:
            return model.find_sequence_by_accession( name )
    except NotFoundError as ex:
        if skip_missing:
            return None
        else:
            raise NotFoundError( "Failed to import the leaf reference string «{}». This is not a recognised accession or legacy accession.".format( name ) ) from ex


def is_root( node: MNode ):
    if is_sequence_node( node ) and node.data.position == EPosition.ROOT:
        return True
    elif any( is_sequence_node( x ) and x.data.position == EPosition.OUTGROUP for x in node.relations ):
        return True
    
    return False
