"""
Module for creating the NRFG.
"""
from collections import defaultdict
from typing import Dict, FrozenSet, Iterable, Set, Tuple, List
from intermake import MCMD
from mgraph import MEdge, MGraph, MNode
from mhelper import Logger, LogicError, ansi, ansi_helper, array_helper, string_helper

from groot.algorithms import lego_graph
from groot.algorithms.classes import FusionPoint
from groot.algorithms.lego_graph import Split
from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence, ILeaf, LegoNrfg


_TDataByComponent = Dict[LegoComponent, Tuple[FrozenSet[LegoSequence], Set[FrozenSet[LegoSequence]]]]

__LOG_SPLITS = Logger( "nrfg.splits", False, { "join": "·" } )
__LOG_EVIDENCE = Logger( "nrfg.evidence", False, { "join": "·" } )
__LOG_FIND = Logger( "nrfg.find", False, { "join": "·" } )
__LOG_CREATE = Logger( "nrfg.create", True, { "join": "·" } )
__LOG_SEW = Logger( "nrfg.sew", True, { "join": "·" } )
__LOG_DEBUG = Logger( "nrfg.debug", True, { "join": "·" } )
__LOG_CLEAN = Logger( "nrfg.clean", True, { "join": "·" } )
__LOG_MAKE = Logger( "nrfg.make", False )


def __make_graph_from_splits( splits: Iterable[Split] ) -> MGraph:
    """
    Creates a graph from a set of splits.
    :param splits:  Iterable over splits 
    :return:        Constructed graph. 
    """
    
    # Nb. treemodel.Tree.from_split_bitmasks just skips dud splits, not sure we should do that here
    
    g = MGraph()
    to_use = sorted( splits, key = lambda x: str( x ) )
    to_use = sorted( to_use, key = lambda x: len( x ) )
    root: MNode = g.add_node( data = "root" )
    
    for i, split in enumerate( to_use ):
        split_str = str( split )
        
        if len( split ) == 1:
            __LOG_MAKE( "DEFINING SPLIT {} OF {} = {}", i, len( to_use ), split_str )
            sequence = array_helper.single_or_error( split.inside )
            
            if not any( x.data is sequence for x in g.nodes ):
                root.add_child( data = sequence )
            
            continue
        
        # Find the most recent common ancestor of all sequences in our split
        paths = g.find_common_ancestor_paths( filter = lambda x: x.data in split.inside )
        mrca: MNode = paths[0][0]
        # __LOGUS( "MRCA = {}".format( mrca ) )
        
        # Some nodes will be attached by the same clade, reduce this to the final set
        destinations = set( path[1] for path in paths )
        
        if len( destinations ) == len( mrca.edges.outgoing_dict ):
            # Already a self-contained clade, nothing to do
            __LOG_MAKE( "EXISTING SPLIT {} OF {} = {} (@{})", i, len( to_use ), split_str, mrca )
            continue
        
        __LOG_MAKE( "NEW      SPLIT {} OF {} = {} (@{})", i, len( to_use ), split_str, mrca )
        
        new_node = mrca.add_child()
        # new_node.data = "split: " + split_str
        # __LOGUS( "NEW CHILD = {}".format( new_node ) )
        
        for destination in destinations:
            # __LOGUS( "MRCA DESTINATION #n = {}", destination )
            mrca.remove_edge_to( destination )
            new_node.add_edge_to( destination )
        
        __LOG_MAKE( g.to_ascii() )
        
        __print_split_status( g, split )
        
        __LOG_MAKE.pause()
        
        # __LOGUS( "========================================" )
    
    # __LOGUS( "FINAL STATUS" )
    # __LOGUS( g.to_ascii() )
    return g


def __print_split_status( g, split: Split ) -> None:
    query = { split }
    if __debug_splits( g, query ) == query:
        __LOG_MAKE( "OK" )
    else:
        __LOG_MAKE( "FAIL" )


def reduce_and_rebuild( graph: MGraph ) -> None:
    """
    Breaks a graph into a set of splits and rebuilds it, printing out information as it goes.
    This serves no purpose and is only used for debugging.
    :param graph:   Graph to operate upon 
    :return:        Nothing is returned, the output is sent to the console. 
    """
    results = []
    
    # ORIGINAL
    graph.get_root()
    
    results.append( "============= ORIGINAL GRAPH =============" )
    results.append( graph.to_ascii() )
    
    # SPLIT
    splits = lego_graph.get_splits( graph )
    
    results.append( "============= SPLITS =============" )
    for i, split in enumerate( sorted( splits, key = Split.__str__ ) ):
        results.append( "SPLIT {} OF {}: {}".format( i, len( splits ), str( split ) ) )
    
    # RECOMBINE
    g = __make_graph_from_splits( splits )
    
    results.append( "============= RECOMBINE =============" )
    results.append( g.to_ascii() )
    
    __LOG_MAKE( "\n".join( results ) )


def expand_leaves( X: FrozenSet[ILeaf] ) -> FrozenSet[LegoSequence]:
    """
    Expands a set X to include fusion content.
    """
    r = []
    
    for x in X:
        if isinstance( x, LegoSequence ):
            r.append( x )
        elif isinstance( x, FusionPoint ):
            r.append(x) # TODO
    
    return frozenset( r )


def create_nrfg( model: LegoModel, cutoff: float = 0.5, clean: bool = True ) -> None:
    """
    Creates the NRFG.
    
    :param model:       Model 
    :param cutoff:      Consensus cutoff 
    :param clean:       Whether you want it clean. You do. 
    :return:            Nothing is returned, the NRFG is set on the model. 
    """
    all_splits, data_by_component = __nrfg_1_collect_splits( model )
    viable_splits = __nrfg_2_collect_evidence( all_splits, cutoff, data_by_component, model )
    all_gene_sets, gene_set_to_fusion = __nrfg_3_find_points( model )
    destinations, minigraphs, sources = __nrfg_4_graphs_from_points( all_gene_sets, gene_set_to_fusion, viable_splits )
    nrfg = __nrfg_5_sew_points( destinations, minigraphs, sources )
    __nrfg_debug_splits( nrfg, viable_splits )
    if clean:
        __nrfg_6_clean_graph( nrfg, sources )
    model.nrfg = LegoNrfg( nrfg )


def __nrfg_1_collect_splits( model ) -> Tuple[Set[Split],
                                              Dict[LegoComponent, Tuple[FrozenSet[Split], FrozenSet[ILeaf]]]]:
    """
    NRFG Stage I.
    
    Collects the splits present in the component trees.

    :remarks:
    --------------------------------------------------------------------------------------------------------------    
    | Some of our graphs may have contradictory information.                                                     |
    | To resolve this we perform a consensus.                                                                    |
    | We define all the graphs by their splits, then see whether the splits are supported by the majority.       |
    |                                                                                                            |
    | A couple of implementation notes:                                                                          |
    | 1. I've not used the most efficient algorithm, however this is fast enough for the purpose and it is much  |
    |    easier to explain what we're doing. For a fast algorithm see Jansson 2013, which runs in O(nk) time.    |
    | 2. We're calculating much more data than we need to, since we only reconstruct the subsets of the graphs   |
    |    pertinent to the domains of the composite gene. However, again, this allows us to get the consensus     |
    |    stuff out of the way early so we can perform the more relevant composite stage independent from the     |
    |    consensus.                                                                                              |
    --------------------------------------------------------------------------------------------------------------
    
    :param model:   Model to find the components in
    :return:        Tuple of:
                        1. Set of splits
                        2. Dictionary of:
                            K. Component
                            V. Tuple of:
                                1. Splits for this component
                                2. Leaves for this component
    """
    __LOG_SPLITS.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ SPLITS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    all_splits: Set[Split] = set()
    data_by_component: Dict[LegoComponent, Tuple[FrozenSet[Split], FrozenSet[ILeaf]]] = { }
    
    for component in model.components:
        __LOG_SPLITS( "FOR COMPONENT {}", component )
        
        tree: MGraph = component.tree
        tree.get_root()
        
        component_sequences = lego_graph.get_split_leaves( tree.get_nodes() )
        component_splits = lego_graph.get_splits( tree )
        
        for split in component_splits:
            __LOG_SPLITS( "---- FOUND SPLIT {}", str( split ) )
        
        all_splits.update( component_splits )
        data_by_component[component] = frozenset( component_splits ), frozenset( component_sequences )
    
    return all_splits, data_by_component


def __nrfg_2_collect_evidence( all_splits: Set[Split],
                               cutoff: float,
                               data_by_component: Dict[LegoComponent, Tuple[FrozenSet[Split], FrozenSet[ILeaf]]],
                               model: LegoModel
                               ) -> Set[Split]:
    """
    NRFG PHASE II.
    
    Collect consensus evidence.
    
    :remarks:
    ----------------------------------------------------------------------------------------------------
    | The second stage of the consensus.                                                               |
    | We collect evidence from the graphs to support or reject our splits.                             |
    | Unlike a normal majority rule consensus, there's no guarantee that our splits are in the graphs, |
    | so, in addition to support/reject evidence, we have a third category, whereby the graph neither  |
    | supports nor rejects a split.                                                                    |
    ----------------------------------------------------------------------------------------------------
                                                                                                       
    :param all_splits:          Set of all splits 
    :param cutoff:              Cutoff to be used in the consensus 
    :param data_by_component:   Mapping of components to their splits and leaves 
    :param model:               The model 
    :return:                    The set of splits not rejected by the consensus.
    """
    __LOG_EVIDENCE.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ EVIDENCE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    __LOG_EVIDENCE( "BEGIN EVIDENCE ({} splits)".format( len( all_splits ) ) )
    viable_splits: Set[Split] = set()
    
    for split in all_splits:
        if split.is_empty:
            __LOG_EVIDENCE( "SPLIT IS EMPTY: {}".format( split ) )
            continue
        
        evidence_for = set()
        evidence_against = set()
        evidence_unused = set()
        
        for component in model.components:
            component_splits, component_sequences = data_by_component[component]
            has_evidence = None
            
            for component_split in component_splits:
                evidence = split.is_evidenced_by( component_split )
                
                if evidence is True:
                    has_evidence = True
                    break
                elif evidence is False:
                    has_evidence = False
            
            if has_evidence is True:
                evidence_for.add( component )
            elif has_evidence is False:
                evidence_against.add( component )
            else:
                evidence_unused.add( component )
        
        if not evidence_for:
            raise LogicError( "There is no evidence for (F{} A{} U{}) this split «{}», but the split must have come from somewhere.".format( len( evidence_for ), len( evidence_against ), len( evidence_unused ), split ) )
        
        total_evidence: int = len( evidence_for ) + len( evidence_against )
        frequency: float = len( evidence_for ) / total_evidence
        accept: bool = frequency > cutoff
        
        __LOG_EVIDENCE( "{} {} = {}% -- FOR: ({}) {}, AGAINST: ({}) {}, UNUSED: ({}) {}",
                        "✔" if accept else "✘",
                        ansi_helper.ljust( str( split ), 80 ),
                        int( frequency * 100 ),
                        len( evidence_for ),
                        string_helper.format_array( evidence_for, sort = True ),
                        len( evidence_against ),
                        string_helper.format_array( evidence_against, sort = True ),
                        len( evidence_unused ),
                        string_helper.format_array( evidence_unused, sort = True ) )
        
        if accept:
            viable_splits.add( split )
    
    return viable_splits


def __nrfg_3_find_points( model: LegoModel
                          ) -> Tuple[Set[FrozenSet[LegoSequence]],
                                     Dict[FrozenSet[ILeaf], List[FusionPoint]]]:
    """
    NRFG PHASE III.
    
    # Now for the composite stuff. We need to separate all our graphs into mini-graphs.
    # Each minigraph must contain its sequences (`LegoSequence`), and the fusion points
    # (`FusionPoint`) showing where that graph fits into the big picture.
    
    :param model:   Model to operate upon 
    :return:        Tuple of:
                        0. The set of gene sets
                        1. A dictionary of:
                            K. A gene set
                            V. A list of fusion points
    """
    
    __LOG_FIND.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ FIND POINTS WITH SAME GENES ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    all_gene_sets: Set[FrozenSet[LegoSequence]] = set()
    gene_set_to_fusion: Dict[FrozenSet[ILeaf], List[FusionPoint]] = defaultdict( list )
    
    for fusion_event in model.fusion_events:
        for fusion_point in fusion_event.points:
            pertinent_inner = frozenset( fusion_point.pertinent_inner )
            pertinent_outer = frozenset( fusion_point.pertinent_outer )
            all_gene_sets.add( pertinent_inner )
            all_gene_sets.add( pertinent_outer )
            gene_set_to_fusion[pertinent_inner].append( fusion_point )
            gene_set_to_fusion[pertinent_outer].append( fusion_point )
    
    to_remove = set()
    
    for gene_set in all_gene_sets:
        if not any( isinstance( x, LegoSequence ) for x in gene_set ):
            to_remove.add( gene_set )
        else:
            __LOG_FIND( "GENE SET: {}", gene_set )
            for fusion_point in gene_set_to_fusion[gene_set]:
                __LOG_FIND( "    POINT: {}", fusion_point )
    
    for gene_set in to_remove:
        all_gene_sets.remove( gene_set )
    
    return all_gene_sets, gene_set_to_fusion


def __nrfg_4_graphs_from_points( all_gene_sets: Set[FrozenSet[LegoSequence]],
                                 gene_set_to_fusion: Dict[FrozenSet[ILeaf], List[FusionPoint]],
                                 viable_splits: Set[Split]
                                 ) -> Tuple[Set[int],
                                            List[MGraph],
                                            Set[int]]:
    """
    NRFG PHASE IV.
    
    Creates graphs from the gene sets.
    
    :param all_gene_sets:           Set of all gene sets
    :param gene_set_to_fusion:      Mapping of gene sets to the fusions contained within 
    :param viable_splits:           Set of splits permitted by the consensus 
    :return:                        Tuple of:
                                        1. Destinations (node UIDs)
                                        2. Minigraph
                                        3. Sources (node UIDs)
    """
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒ CREATE GRAPHS FOR POINTS ▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    __LOG_CREATE.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ CREATE GRAPHS FOR POINTS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    minigraphs = []
    destinations = set()
    sources = set()
    for gene_set_ in all_gene_sets:
        fused_gene_set: Set[ILeaf] = set( gene_set_ )
        
        for fusion_point in gene_set_to_fusion[gene_set_]:
            assert isinstance( fusion_point, FusionPoint )
            fused_gene_set.add( fusion_point )
        
        relevant_splits = set()
        
        __LOG_CREATE.pause( "***** GENE SET {} *****", fused_gene_set )
        
        for split in viable_splits:
            if split.all.issuperset( fused_gene_set ):  # S c G
                intersection = split.intersection( fused_gene_set )
                if intersection.is_bad():
                    __LOG_CREATE( "  BAD: {} “{}”", split, intersection )
                elif intersection not in relevant_splits:
                    __LOG_CREATE( "  OK : {} “{}”", split, intersection )
                    relevant_splits.add( intersection )
                else:
                    __LOG_CREATE( "  REP: {} “{}”", split, intersection )
            else:
                missing = fused_gene_set - split.all
                if not missing:
                    __LOG_CREATE( "ERROR" )
                __LOG_CREATE( "  NSU: {}", split )
                __LOG_CREATE( "    -: {}", missing )
        
        if not relevant_splits:
            raise LogicError( "I cannot reconstruct this graph because all splits for the gene set «{}» were rejected. The reasons for rejections have not been retained in memory. Please turn on logging and investigate history to see details.".format( fused_gene_set ) )
        
        minigraph = __make_graph_from_splits( relevant_splits )
        minigraphs.append( minigraph )
        
        sequences = lego_graph.get_sequences( minigraph )
        
        for node in lego_graph.get_fusion_nodes( minigraph ):
            assert isinstance( node, MNode )
            
            fusion_event = node.data
            if any( x in sequences for x in fusion_event.pertinent_inner ):
                destinations.add( node.uid )
            else:
                sources.add( node.uid )
        
        __LOG_CREATE( minigraph.to_ascii() )
        __LOG_CREATE( "END OF GENE SET {}", fused_gene_set, key = "nrfg.289" )
    
    return destinations, minigraphs, sources


def __nrfg_6_clean_graph( nrfg: MGraph, sources ):
    """
    Cleans the NRFG.
    """
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ CLEAN GRAPH ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    __LOG_CLEAN.pause( "CLEAN" )
    # for node in list( nrfg ):
    #     assert isinstance( node, MNode )
    #     if lego_graph.is_fusion( node ):
    #         node.remove_node()
    
    for node in list( nrfg ):
        assert isinstance( node, MNode )
        
        if lego_graph.is_fusion( node ):
            if node.uid in sources:
                node.remove_node_safely()
        if lego_graph.is_clade( node ):
            in_ = len( node.edges.incoming )
            out_ = len( node.edges.outgoing )
            if in_ == 1 and out_ == 1:
                node.parent.add_edge_to( node.child )
                node.remove_node()
            if in_ == 0 and out_ == 2:
                c = list( node.children )
                c[0].add_edge_to( c[1] )
                node.remove_node()


def __nrfg_debug_splits( nrfg, viable_splits ):
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ DEBUG SPLITS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    __LOG_DEBUG.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ DEBUG ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    supported = __debug_splits( nrfg, viable_splits )
    unsupported = viable_splits - supported
    for split in unsupported:
        MCMD.print( ansi.FORE_RED + "unsupported: " + ansi.RESET + str( split ) )
    for split in supported:
        MCMD.print( ansi.FORE_GREEN + "supported: " + ansi.RESET + str( split ) )


def __nrfg_5_sew_points( destinations, minigraphs, sources ):
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒ SEW POINTS BACK TOGETHER ▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # Sort the to_use by size
    __LOG_SEW.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ RECOMBINE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    nrfg: MGraph = MGraph()
    for minigraph in minigraphs:
        minigraph.copy_into( nrfg )
    __LOG_SEW( nrfg.to_ascii() )
    __LOG_SEW( "{} FUSION NODES", len( lego_graph.get_fusion_nodes( nrfg ) ) )
    __LOG_SEW.pause( "END OF COPY" )
    for an, bn in array_helper.square_comparison( lego_graph.get_fusion_nodes( nrfg ) ):
        a = an.data
        b = bn.data
        
        assert an.uid in sources or an.uid in destinations
        assert bn.uid in sources or bn.uid in destinations
        
        a_is_source = an.uid in sources
        b_is_source = bn.uid in sources
        
        assert isinstance( a, FusionPoint )
        assert isinstance( b, FusionPoint )
        
        __LOG_SEW( "{} VS {}", a, b )
        
        if a.event is not b.event:
            __LOG_SEW( "EVENT MISMATCH" )
            continue
        
        if b_is_source or not a_is_source:
            __LOG_SEW( "DIRECTION MISMATCH" )
            continue
        
        if a.pertinent_inner != b.pertinent_inner:
            __LOG_SEW( "SET MISMATCH ({} VS {})", a.pertinent_inner, b.pertinent_outer )
            continue
        
        __LOG_SEW( "MATCH - MAKING AN EDGE" )
        an.add_edge_to( bn )
    __LOG_SEW( nrfg.to_ascii() )
    __LOG_SEW.pause( "END OF RECOMBINE" )
    return nrfg


def __debug_splits( graph: MGraph, query: Iterable[Split] ) -> Set[Split]:
    """
    Given a set of splits to query, returns those which are supported by the graph.
    :param graph:   Graph 
    :param query:   Set of query splits 
    :return:        Set of supported splits 
    """
    supported: Set[Split] = set()
    new_splits: Set[Split] = set()
    
    for edge in graph.edges:
        assert isinstance( edge, MEdge )
        left: FrozenSet[ILeaf] = frozenset( lego_graph.get_split_leaves( edge.follow_left() ) )
        right: FrozenSet[ILeaf] = frozenset( lego_graph.get_split_leaves( edge.follow_right() ) )
        
        new_splits.add( Split( left, right ) )
        new_splits.add( Split( right, left ) )
    
    for split in query:
        for new_split in new_splits:
            if split.is_evidenced_by( new_split ) is True:
                supported.add( split )
    
    return supported
