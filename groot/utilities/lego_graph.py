from typing import Iterable, List, Set, Optional, cast
from mgraph import MNode, MGraph, analysing, importing, exporting
from groot.data.model_interfaces import EPosition, INode
from groot.data.model_core import Formation, Gene, Point
from groot.data.model import Model
from mhelper import NotFoundError, ByRef


def get_sequence_data( nodes: Iterable[MNode] ) -> Set[Gene]:
    return set( node.data for node in nodes if isinstance( node.data, Gene ) )


def get_fusion_data( nodes: Iterable[MNode] ) -> Set[Point]:
    return set( node.data for node in nodes if isinstance( node.data, Point ) )


def get_fusion_point_nodes( nodes: Iterable[MNode] ) -> List[MNode]:
    return [node for node in nodes if is_fusion_point( node )]


def get_fusion_formation_nodes( nodes: Iterable[MNode] ) -> List[MNode]:
    return [node for node in nodes if is_formation( node )]


def is_clade( node: MNode ) -> bool:
    return node.data is None or isinstance( node.data, str )


def is_fusion_like( node: MNode ) -> bool:
    return is_fusion_point( node ) or is_formation( node )


def is_formation( node: MNode ) -> bool:
    return isinstance( node.data, Formation )


def is_fusion_point( node: MNode ) -> bool:
    return isinstance( node.data, Point )


def is_sequence_node( node: MNode ) -> bool:
    return isinstance( node.data, Gene )


def is_lego_node( node: MNode ) -> bool:
    return isinstance( node.data, INode )


def get_ileaf_data( params: Iterable[MNode] ) -> Set[INode]:
    return set( x.data for x in params if isinstance( x.data, INode ) )


def rectify_nodes( graph: MGraph, model: Model ):
    for node in graph:
        if isinstance( node.data, str ):
            node.data = import_leaf_reference( node.data, model, skip_missing = True )


def import_leaf_reference( name: str, model: Model, *, allow_empty: bool = False, skip_missing: bool = False ) -> Optional[INode]:
    """
    Converts a sequence name to a sequence reference.
    
    :param name:            Name, either:
                                * A gene accession, denoting that gene
                                * A gene legacy accession, denoting that gene
                                * A fusion identifier
                                * If `allow_empty` then: `None`, `"root"`, or `"clade*"`, denoting a clade of no particular significance
    :param model:           The model to find the sequence in 
    :param allow_empty:     Allow `None` or `""` to denote a missing sequence, `None`.
    :param skip_missing:    Allow missing accessions to be skipped. 
    :return:                The gene, fusion, or `None` if permitted.
    """
    if skip_missing:
        allow_empty = True
    
    if allow_empty and name is None:
        return None
    
    assert isinstance( name, str )
    
    if allow_empty and name == "" or name == "root" or name.startswith( "clade" ):
        return None
    
    r = model.by_legacy_accession( name, None )
    
    if r is not None:
        return r
    
    r = model.genes.get( name )
    
    if r is not None:
        return r
    
    if skip_missing:
        return None
    else:
        raise NotFoundError( "Failed to import the leaf reference string «{}». This is not a recognised accession or legacy accession.".format( name ) )


def is_root( node: MNode ):
    if any( is_sequence_node( x ) and x.data.position == EPosition.OUTGROUP for x in node.relations ):
        return True
    
    return False


def export_newick( graph: MGraph ):
    """
    Exports Newick into a format suitable for use with other programs.
    
    * We use legacy accessions to cope with programs still relying on the old PHYLIP format, which limits gene names
    * We pull fusion clades into leaves to cope with programs that don't account for named clades
    * We don't label the other clades
    """
    # Declade fusion nodes
    nodes = analysing.realise_node_predicate_as_set( graph, is_fusion_like )
    
    for node in nodes:
        node.add_child( node.data )
        node.data = None
    
    # Ensure the root of the graph is not something weird
    if not is_clade( graph.root ):
        child = graph.root.child
        assert is_clade( child )
        child.make_root()
    
    # Write newick
    return exporting.export_newick( graph,
                                    fnode = lambda x: x.data.legacy_accession if x.data else "",
                                    internal = False )


def import_newick( newick: str, model: Model, root_ref: ByRef[MNode] = None, reclade: bool = True ) -> MGraph:
    """
    Imports a newick string as an MGraph object.
    
    The format is expected to be the same as that produced by `export_newick`, but we make accommodations
    for additional information programs might have added, such as clade names and branch lengths.
    """
    # Read newick
    graph: MGraph = importing.import_newick( newick,
                                             root_ref = root_ref )
    
    # Convert node names back to references
    for node in graph.nodes:
        node.data = import_leaf_reference( cast( str, node.data ),
                                           model,
                                           allow_empty = True )
    
    # Reclade fusion nodes
    if reclade:
        fusion_nodes = analysing.realise_node_predicate_as_set( graph, lambda x: isinstance( x.data, Point ) )
        
        for node in fusion_nodes:
            node.parent.data = node.data
            node.remove_node()
    
    return graph
