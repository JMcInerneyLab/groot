"""
Module for creating the NRFG.
"""
from collections import defaultdict
from typing import Dict, FrozenSet, Iterable, Set, Tuple

from groot.algorithms import lego_graph
from groot.algorithms.classes import FusionPoint
from groot.algorithms.lego_graph import Split
from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence, ILeaf
from intermake.engine.environment import MCMD
from mgraph import MEdge, MGraph, MNode
from mhelper import Logger, LogicError, ansi, ansi_helper, array_helper, string_helper


_TDataByComponent = Dict[LegoComponent, Tuple[FrozenSet[LegoSequence], Set[FrozenSet[LegoSequence]]]]

__LOG = Logger( "nrfg", False )
__LOGUS = Logger( "unsplit", False )


def __make_graph_from_splits( splits: Iterable[Split] ):
    # Nb. treemodel.Tree.from_split_bitmasks just skips dud splits, not sure we should do that here
    
    g = MGraph()
    to_use = sorted( splits, key = lambda x: str( x ) )
    to_use = sorted( to_use, key = lambda x: len( x ) )
    root: MNode = g.add_node( data = "root" )
    
    for i, split in enumerate( to_use ):
        split_str = str( split )
        
        # __LOGUS( "CURRENT STATUS" )
        # __LOGUS( g.to_ascii() )
        # __LOGUS( g.to_edgelist( delimiter = "    --->    ", pad = True ) )
        # __LOGUS( "========================================" )
        # __LOGUS( "SPLIT {} OF {}".format( i, len( to_use ) ) )
        # __LOGUS( "= " + split_str )
        
        if len( split ) == 1:
            __LOGUS( "DEFINING SPLIT {} OF {} = {}", i, len( to_use ), split_str )
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
            __LOGUS( "EXISTING SPLIT {} OF {} = {} (@{})", i, len( to_use ), split_str, mrca )
            continue
        
        __LOGUS( "NEW      SPLIT {} OF {} = {} (@{})", i, len( to_use ), split_str, mrca )
        
        new_node = mrca.add_child()
        # new_node.data = "split: " + split_str
        # __LOGUS( "NEW CHILD = {}".format( new_node ) )
        
        for destination in destinations:
            # __LOGUS( "MRCA DESTINATION #n = {}", destination )
            mrca.remove_edge_to( destination )
            new_node.add_edge_to( destination )
        
        __LOGUS( g.to_ascii() )
        
        __print_split_status( g, split )
        
        __LOGUS.pause()
        
        # __LOGUS( "========================================" )
    
    # __LOGUS( "FINAL STATUS" )
    # __LOGUS( g.to_ascii() )
    return g


def __print_split_status( g, split ):
    query = { split }
    if __debug_splits( g, query ) == query:
        __LOGUS( "OK" )
    else:
        __LOGUS( "FAIL" )


def reduce_and_rebuild( graph: MGraph ):
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
    
    __LOGUS( "\n".join( results ) )


def create_nrfg( model: LegoModel, cutoff: float = 0.5, clean: bool = True ):
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ CONSENSUS.I: COLLECTION ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    #
    # Some of our graphs may have contradictory information.
    # To resolve this we perform a consensus. 
    # We define all the graphs by their splits, then see whether the splits are supported by the majority.
    #
    # A couple of implementation notes:
    # 1. I've not used the most efficient algorithm, however this is fast enough for the purpose and it is much
    #    easier to explain what we're doing. For a fast algorithm see Jansson 2013, which runs in O(nk) time.
    # 2. We're calculating much more data than we need to, since we only reconstruct the subsets of the graphs
    #    pertinent to the domains of the composite gene. However, again, this allows us to get the consensus
    #    stuff out of the way early so we can perform the more relevant composite stage independent from the
    #    consensus.
    __LOG.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ SPLITS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    all_splits: Set[Split] = set()
    data_by_component: Dict[LegoComponent, Tuple[FrozenSet[Split], FrozenSet[ILeaf]]] = { }
    
    for component in model.components:
        __LOG( "FOR COMPONENT {}", component )
        
        tree: MGraph = component.tree
        tree.get_root()
        
        component_sequences = lego_graph.get_split_leaves( tree.get_nodes() )
        component_splits = lego_graph.get_splits( tree )
        
        for split in component_splits:
            __LOG( "---- FOUND SPLIT {}", str( split ) )
        
        all_splits.update( component_splits )
        data_by_component[component] = frozenset( component_splits ), frozenset( component_sequences )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ CONSENSUS.II: EVIDENCE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    #
    # The second stage of the consensus.
    # We collect evidence from the graphs to support or reject our splits.
    # Unlike a normal majority rule consensus, there's no guarantee that our splits are in the graphs,
    # so we have a third category of evidence, whereby the graph can neither support nor reject the split.
    #
    __LOG.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ EVIDENCE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    __LOG( "BEGIN EVIDENCE ({} splits)".format( len( all_splits ) ) )
    viable_splits: Set[Split] = set()
    
    for split in all_splits:
        if split.is_empty:
            __LOG( "SPLIT IS EMPTY: {}".format( split ) )
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
        
        total_evidence = len( evidence_for ) + len( evidence_against )
        frequency = len( evidence_for ) / total_evidence
        accept = frequency > cutoff
        
        # __LOG( "SPLIT    : {}".format( __print_split( split ) ) )
        # __LOG( "SPLITSIZE: {}".format( len( split ) ) )
        # __LOG( "FOR      : {}".format( string_helper.format_array( evidence_for, sort = True ) ) )
        # __LOG( "AGAINST  : {}".format( string_helper.format_array( evidence_against, sort = True ) ) )
        # __LOG( "UNUSED   : {}".format( string_helper.format_array( evidence_unused, sort = True ) ) )
        # __LOG( "FREQUENCY: {} / {} = {}%".format( len( evidence_for ), total_evidence, int( frequency * 100 ) ) )
        # __LOG( "STATUS:    {}".format( "accepted" if accept else "rejected" ) )
        # __LOG( "" )
        
        
        __LOG( "{} {} = {}% -- FOR: ({}) {}, AGAINST: ({}) {}, UNUSED: ({}) {}",
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
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒ FIND POINTS WITH SAME GENES ▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    #
    # Now for the composite stuff. We need to separate all our graphs into mini-graphs.
    # Each minigraph must contain its sequences (`LegoSequence`), and the fusion points
    # (`FusionPoint`) showing where that graph fits into the big picture.
    #
    __LOG.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ FIND POINTS WITH SAME GENES ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    gene_sets: Set[FrozenSet[LegoSequence]] = set()
    with_ = defaultdict( list )
    
    for fusion in model.fusion_events:
        for point in fusion.points:
            fs1 = frozenset( point.pertinent_inner )
            fs2 = frozenset( point.pertinent_outer )
            gene_sets.add( fs1 )
            gene_sets.add( fs2 )
            with_[fs1].append( point )
            with_[fs2].append( point )
    
    to_remove = set()
    
    for gene_set in gene_sets:
        if not any( isinstance( x, LegoSequence ) for x in gene_set ):
            to_remove.add( gene_set )
        else:
            __LOG( "GENE SET: {}", gene_set )
            for x in with_[gene_set]:
                __LOG( "        +: {}", x )
    
    for gene_set in to_remove:
        gene_sets.remove( gene_set )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒ CREATE GRAPHS FOR POINTS ▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    __LOG.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ CREATE GRAPHS FOR POINTS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    minigraphs = []
    destinations = set()
    sources = set()
    
    for gene_set_ in gene_sets:
        gene_set = set( gene_set_ )
        
        for with__ in with_[gene_set_]:
            gene_set.add( with__ )
        
        relevant_splits = set()
        
        __LOG( "***** GENE SET {} *****", gene_set )
        
        for split in viable_splits:
            if split.all.issuperset( gene_set ):
                intersection = split.intersection( gene_set )
                if intersection.is_bad():
                    __LOG( "   DISCARDED: {} “{}”", split, intersection )
                elif intersection not in relevant_splits:
                    __LOG( "    RELEVANT: {} “{}”", split, intersection )
                    relevant_splits.add( intersection )
                else:
                    __LOG( "    REPEATED: {} “{}”", split, intersection )
            else:
                __LOG( "NOT RELEVANT: {}", split )
        
        if not relevant_splits:
            raise LogicError( "No relevant splits for gene set «{}»".format( gene_set ) )
        
        minigraph = __make_graph_from_splits( relevant_splits )
        minigraphs.append( minigraph )
        
        sequences = lego_graph.get_sequences( minigraph )
        
        for node in lego_graph.get_fusion_nodes( minigraph ):
            fusion = node.data
            if any( x in sequences for x in fusion.pertinent_inner ):
                destinations.add( node.uid )
            else:
                sources.add( node.uid )
        
        __LOG( minigraph.to_ascii() )
        __LOG.pause( "END OF GENE SET {}", gene_set, key = "nrfg.289" )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒ SEW POINTS BACK TOGETHER ▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # Sort the to_use by size
    __LOG.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ RECOMBINE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    nrfg: MGraph = MGraph()
    
    for minigraph in minigraphs:
        minigraph.copy_into( nrfg )
    
    __LOG( nrfg.to_ascii() )
    __LOG( "{} FUSION NODES", len( lego_graph.get_fusion_nodes( nrfg ) ) )
    __LOG.pause( "END OF COPY" )
    
    for an, bn in array_helper.square_comparison( lego_graph.get_fusion_nodes( nrfg ) ):
        a = an.data
        b = bn.data
        
        assert an.uid in sources or an.uid in destinations
        assert bn.uid in sources or bn.uid in destinations
        
        a_is_source = an.uid in sources
        b_is_source = bn.uid in sources
        
        assert isinstance( a, FusionPoint )
        assert isinstance( b, FusionPoint )
        
        __LOG( "{} VS {}", a, b )
        
        if a.event is not b.event:
            __LOG( "EVENT MISMATCH" )
            continue
        
        if b_is_source or not a_is_source:
            __LOG( "DIRECTION MISMATCH" )
            continue
        
        if a.pertinent_inner != b.pertinent_inner:
            __LOG( "SET MISMATCH ({} VS {})", a.pertinent_inner, b.pertinent_outer )
            continue
        
        __LOG( "MATCH - MAKING AN EDGE" )
        an.add_edge_to( bn )
    
    __LOG( nrfg.to_ascii() )
    __LOG.pause( "END OF RECOMBINE" )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ DEBUG SPLITS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    __LOG.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ DEBUG ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    
    supported = __debug_splits( nrfg, viable_splits )
    unsupported = viable_splits - supported
    
    for split in unsupported:
        MCMD.print( ansi.FORE_RED + "unsupported: " + ansi.RESET + str( split ) )
    
    for split in supported:
        MCMD.print( ansi.FORE_GREEN + "supported: " + ansi.RESET + str( split ) )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ CLEAN GRAPH ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    if clean:
        __LOG.pause( "CLEAN" )
        # for node in list( nrfg ):
        #     assert isinstance( node, MNode )
        #     if lego_graph.is_fusion( node ):
        #         node.remove_node()
        
        for node in list( nrfg ):
            assert isinstance( node, MNode )
            
            if lego_graph.is_fusion(node):
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
    
    model.nrfg = nrfg


def __debug_splits( graph, query ):
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
