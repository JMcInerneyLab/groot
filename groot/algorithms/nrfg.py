"""
Module for creating the NRFG.
"""
import warnings
from collections import defaultdict
from typing import Dict, FrozenSet, List, Set, Tuple

from groot import constants
from groot.algorithms import lego_graph
from groot.data.exceptions import AlreadyError, InUseError, NotReadyError
from groot.data.lego_model import EPosition, FusionPoint, ILeaf, LegoComponent, LegoModel, LegoSequence, LegoSplit, NamedGraph, LegoSubset, NrfgReport
from mgraph import MGraph, MNode, Split, analysing, exporting, importing
from mhelper import Logger, LogicError, NotFoundError, SwitchError, ansi_helper, array_helper, string_helper


_TDataByComponent = Dict[LegoComponent, Tuple[FrozenSet[LegoSequence], Set[FrozenSet[LegoSequence]]]]

__log_settings = { "join": "·", "sort": False }
__LOG_SPLITS = Logger( "nrfg.splits", False, __log_settings )
__LOG_EVIDENCE = Logger( "nrfg.evidence", False, __log_settings )
__LOG_FIND = Logger( "nrfg.find", False, __log_settings )
__LOG_CREATE = Logger( "nrfg.create", False, __log_settings )
__LOG_SEW = Logger( "nrfg.sew", False, __log_settings )
__LOG_DEBUG = Logger( "nrfg.debug", False, __log_settings )
__LOG_CLEAN = Logger( "nrfg.clean", False, __log_settings )
__LOG_MAKE = Logger( "nrfg.make", False )
del __log_settings


def s1_drop_candidates( model: LegoModel ):
    if model.get_status( constants.STAGES.SPLITS_8 ).is_not_complete:
        raise NotReadyError( s1_drop_candidates.__name__, s1_create_splits.__name__ )
    
    if model.get_status( constants.STAGES.CONSENSUS_9 ).is_partial:
        raise InUseError( s1_drop_candidates.__name__, s2_create_consensus.__name__ )
    
    model.nrfg.splits = frozenset()
    
    for component in model.components:
        component.splits = None
        component.leaves = None


def s1_create_splits( model: LegoModel ):
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
    
    # Status check
    if model.get_status( constants.STAGES.FUSIONS_7 ).is_not_complete:
        raise NotReadyError( s1_create_splits.__name__, "find_fusions" )
    
    if model.get_status( constants.STAGES.SPLITS_8 ).is_partial:
        raise AlreadyError( s1_create_splits.__name__ )
    
    all_splits: Dict[Split, LegoSplit] = { }
    
    for component in model.components:
        __LOG_SPLITS( "FOR COMPONENT {}", component )
        
        tree: MGraph = component.tree
        tree.any_root.make_root()  # ensure root is root-like
        
        component_sequences = lego_graph.get_ileaf_data( tree.get_nodes() )
        
        # Split the tree, `ILeaf` is a strange definition of a "leaf", since we'll pull out clades too (`FusionPoint`s).
        # We fix this when we reconstruct the NRFG.
        component_splits = exporting.export_splits( tree, filter = lambda x: isinstance( x.data, ILeaf ) )
        component_splits_r = []
        
        for split in component_splits:
            __LOG_SPLITS( "---- FOUND SPLIT {}", str( split ) )
            
            exi = all_splits.get( split )
            
            if exi is None:
                exi = LegoSplit( split, len( all_splits ) )
                all_splits[split] = exi
            
            exi.components.add( component )
            component_splits_r.append( exi )
        
        component.splits = frozenset( component_splits_r )
        component.leaves = frozenset( component_sequences )
    
    model.nrfg.splits = frozenset( all_splits.values() )


def s2_drop_viable( model: LegoModel ):
    if model.get_status( constants.STAGES.CONSENSUS_9 ).is_not_complete:
        raise NotReadyError( s2_drop_viable.__name__, s2_create_consensus.__name__ )
    
    if model.get_status( constants.STAGES.SUBSETS_10 ).is_partial:
        raise InUseError( s2_drop_viable.__name__, s3_create_subsets.__name__ )
    
    model.nrfg.consensus = frozenset()


def s2_create_consensus( model: LegoModel, cutoff: float ) -> None:
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
                                                                                                       
    :param cutoff:              Cutoff to be used in the consensus 
    :param model:               The model 
    :return:                    The set of splits not rejected by the consensus.
    """
    __LOG_EVIDENCE.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ EVIDENCE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    
    if model.get_status( constants.STAGES.CONSENSUS_9 ).is_partial:
        raise AlreadyError( s2_create_consensus.__name__ )
    
    if model.get_status( constants.STAGES.SPLITS_8 ).is_not_complete:
        raise NotReadyError( s2_create_consensus.__name__, s1_create_splits.__name__ )
    
    __LOG_EVIDENCE( "BEGIN EVIDENCE ({} splits)".format( len( model.nrfg.splits ) ) )
    viable_splits: Set[LegoSplit] = set()
    
    for split in model.nrfg.splits:
        assert isinstance( split, LegoSplit ), split
        
        if split.split.is_empty:
            __LOG_EVIDENCE( "SPLIT IS EMPTY: {}".format( split ) )
            continue
        
        evidence_for = set()
        evidence_against = set()
        evidence_unused = set()
        
        for component in model.components:
            component_splits = component.splits
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
        split.evidence_for = frozenset( evidence_for )
        split.evidence_against = frozenset( evidence_against )
        split.evidence_unused = frozenset( evidence_unused )
        
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
    
    model.nrfg.consensus = frozenset( viable_splits )


def s3_drop_subsets( model: LegoModel ):
    if model.get_status( constants.STAGES.SUBSETS_10 ).is_not_complete:
        raise NotReadyError( s3_drop_subsets.__name__, s3_create_subsets.__name__ )
    
    if model.get_status( constants.STAGES.SUBGRAPHS_11 ).is_partial:
        raise InUseError( s3_drop_subsets.__name__, s4_create_minigraphs.__name__ )
    
    model.nrfg.subsets = frozenset()


def s3_create_subsets( model: LegoModel, no_super: bool ):
    """
    NRFG PHASE III.
    
    Find the gene sets
    
    :remarks:
    
    Now for the composite stuff. We need to separate all our graphs into mini-graphs.
    Each minigraph must contain...
          ...its genes (`LegoSequence`)
          ...the fusion points (`FusionPoint`)
              - showing where that graph fits into the big picture.
              
    In this stage we collect "gene_sets", representing the set of sequences in each minigraph.
    We also make a dictionary of "gene_set_to_fusion", representing which fusion points are matched to each "gene set".
    
    :param model:       Model to operate upon
    :param no_super:    Drop supersets from the trees. You want this.
                        Turn if off to see the supersets in the final graph (your NRFG will therefore be a disjoint union of multiple possibilities!).
    :return:            The set of gene sets
    """
    
    if model.get_status( constants.STAGES.CONSENSUS_9 ).is_not_complete:
        raise NotReadyError( s3_create_subsets.__name__, s2_create_consensus.__name__ )
    
    if model.get_status( constants.STAGES.SUBSETS_10 ).is_partial:
        raise AlreadyError( s3_create_subsets.__name__ )
    
    __LOG_FIND.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ FIND POINTS WITH SAME GENES ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    
    # Define our output variables
    all_gene_sets: Set[FrozenSet[ILeaf]] = set()
    gene_set_to_fusion: Dict[FrozenSet[ILeaf], List[FusionPoint]] = defaultdict( list )
    
    # Iterate over the fusion points 
    for fusion_event in model.fusion_events:
        for fusion_point in fusion_event.points:
            # Each fusion point splits the graph into two halves ("inside" and "outside" that point)
            # Each half defines one of our minigraphs.
            pertinent_inner = frozenset( fusion_point.pertinent_inner )
            pertinent_outer = frozenset( fusion_point.pertinent_outer )
            all_gene_sets.add( pertinent_inner )
            all_gene_sets.add( pertinent_outer )
            
            # Note that multiple points may define the same graphs, hence here we specify which points define which graphs. 
            gene_set_to_fusion[pertinent_inner].append( fusion_point )
            gene_set_to_fusion[pertinent_outer].append( fusion_point )
    
    to_remove = set()
    
    # Some of our gene sets will ̶d̶e̶v̶o̶i̶d̶ ̶o̶f̶ ̶g̶e̶n̶e̶s shit
    
    # Drop these now 
    for gene_set in all_gene_sets:
        if not any( isinstance( x, LegoSequence ) for x in gene_set ):
            # No genes in this set
            __LOG_FIND( "DROP GENE SET (EMPTY): {}", gene_set )
            to_remove.add( gene_set )
            continue
        
        if no_super:
            remaining = set( gene_set )
            
            for gene_set_2 in all_gene_sets:
                if gene_set_2 is not gene_set:
                    if gene_set_2.issubset( gene_set ):
                        remaining -= gene_set_2
            
            if not remaining:
                # Gene set is a superset of other sets
                __LOG_FIND( "DROP GENE SET (SUPERSET): {}", gene_set )
                to_remove.add( gene_set )
                continue
        
        # Good gene set (keep)
        __LOG_FIND( "KEEP GENE SET: {}", gene_set )
        for fusion_point in gene_set_to_fusion[gene_set]:
            __LOG_FIND( "    POINT: {}", fusion_point )
    
    for gene_set in to_remove:
        all_gene_sets.remove( gene_set )
    
    # Finally, complement our gene sets with the fusion points they are adjacent to
    # We'll need these to know where our graph fits into the big picture
    results: Set[FrozenSet[ILeaf]] = set()
    
    for gene_set in all_gene_sets:
        new_set = set( gene_set )
        new_set.update( gene_set_to_fusion[gene_set] )
        results.add( frozenset( new_set ) )
    
    model.nrfg.subsets = frozenset( LegoSubset( i, x ) for i, x in enumerate( results ) )


def s4_drop_minigraphs( model: LegoModel ):
    if model.get_status( constants.STAGES.SUBGRAPHS_11 ).is_not_complete:
        raise NotReadyError( s4_drop_minigraphs.__name__, s4_create_minigraphs.__name__ )
    
    if model.get_status( constants.STAGES.FUSED_12 ).is_partial:
        raise InUseError( s4_drop_minigraphs.__name__, s5_create_sewed.__name__ )
    
    model.nrfg.minigraphs = tuple()
    model.nrfg.minigraphs_destinations = tuple()
    model.nrfg.minigraphs_sources = tuple()


def s4_create_minigraphs( model: LegoModel ) -> None:
    """
    NRFG PHASE IV.
    
    Creates graphs from the gene sets.
    
    :return:                        Tuple of:
                                        1. Destinations (node UIDs)
                                        2. Minigraph
                                        3. Sources (node UIDs)
    """
    if model.get_status( constants.STAGES.SUBGRAPHS_11 ).is_partial:
        raise AlreadyError( s4_create_minigraphs.__name__ )
    
    if model.get_status( constants.STAGES.SUBSETS_10 ).is_not_complete:
        raise NotReadyError( s4_create_minigraphs.__name__, s3_create_subsets.__name__ )
    
    __LOG_CREATE.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ CREATE GRAPHS FOR POINTS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    minigraphs = []
    destinations = set()
    sources = set()
    for leaf_set_ in model.nrfg.subsets:
        assert isinstance( leaf_set_, LegoSubset )
        leaf_set = leaf_set_.contents
        __LOG_CREATE.pause( "***** LEAF SET {} *****", leaf_set )
        
        relevant_splits = set()
        
        __LOG_CREATE.pause( "LEAF SET {}", leaf_set )
        
        for split in model.nrfg.consensus:
            leaf_set_sequences = frozenset( x for x in leaf_set if isinstance( x, LegoSequence ) )
            
            if split.split.all.issuperset( leaf_set_sequences ):  # S c G
                intersection = split.split.intersection( leaf_set )
                if intersection.is_redundant():
                    __LOG_CREATE( "  BAD: {} “{}”", split, intersection )
                elif intersection not in relevant_splits:
                    __LOG_CREATE( "  OK : {} “{}”", split, intersection )
                    relevant_splits.add( intersection )
                else:
                    __LOG_CREATE( "  REP: {} “{}”", split, intersection )
            else:
                missing = leaf_set - split.split.all
                if not missing:
                    __LOG_CREATE( "ERROR" )
                
                __LOG_CREATE( "  NSU: {}", split )
                __LOG_CREATE( "    -: {}", missing )
        
        if not relevant_splits:
            msg = "I cannot reconstruct this graph because all splits for the gene set «{}» were rejected. " \
                  "The reasons for rejections have not been retained in memory. " \
                  "Please turn on logging and investigate history to see details."
            raise LogicError( msg.format( leaf_set ) )
        
        minigraph = importing.import_splits( relevant_splits )
        minigraphs.append( NamedGraph( minigraph, constants.MINIGRAPH_PREFIX + str( len( minigraphs ) ) ) )
        
        sequences = lego_graph.get_sequence_data( minigraph )
        
        for node in lego_graph.get_fusion_nodes( minigraph ):
            assert isinstance( node, MNode )
            
            fusion_event = node.data
            if any( x in sequences for x in fusion_event.pertinent_inner ):
                destinations.add( node.uid )
            else:
                sources.add( node.uid )
        
        __LOG_CREATE( minigraph.to_ascii() )
        __LOG_CREATE( "END OF GENE SET {}", leaf_set, key = "nrfg.289" )
    
    model.nrfg.minigraphs = tuple( minigraphs )
    model.nrfg.minigraphs_destinations = tuple( destinations )
    model.nrfg.minigraphs_sources = tuple( sources )


def s5_drop_sewed( model: LegoModel ):
    if model.get_status( constants.STAGES.FUSED_12 ).is_not_complete:
        raise NotReadyError( s5_drop_sewed.__name__, s5_create_sewed.__name__ )
    
    if model.get_status( constants.STAGES.CLEANED_13 ).is_partial:
        raise InUseError( s5_drop_sewed.__name__, s6_create_cleaned.__name__ )
    
    model.nrfg.fusion_graph_unclean = None


def s5_create_sewed( model: LegoModel ):
    """
    Sews the minigraphs back together at the fusion points.
    """
    __LOG_SEW.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ SEW ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    
    if model.get_status( constants.STAGES.SUBGRAPHS_11 ).is_not_complete:
        raise NotReadyError( s5_create_sewed.__name__, s4_create_minigraphs.__name__ )
    
    if model.get_status( constants.STAGES.FUSED_12 ).is_partial:
        raise AlreadyError( s5_create_sewed.__name__ )
    
    # Create our final composite graph
    nrfg: MGraph = MGraph()
    
    for minigraph in model.nrfg.minigraphs:
        minigraph.graph.copy( target = nrfg )
    
    # Debug
    __LOG_SEW( "FINAL UN-SEWED NRFG:" )
    __LOG_SEW( nrfg.to_ascii() )
    __LOG_SEW( "IN THIS GRAPH THERE ARE {} FUSION NODES", len( lego_graph.get_fusion_nodes( nrfg ) ) )
    
    for an, bn in array_helper.square_comparison( lego_graph.get_fusion_nodes( nrfg ) ):
        a = an.data
        b = bn.data
        
        assert an.uid in model.nrfg.minigraphs_sources or an.uid in model.nrfg.minigraphs_destinations
        assert bn.uid in model.nrfg.minigraphs_sources or bn.uid in model.nrfg.minigraphs_destinations
        
        a_is_source = an.uid in model.nrfg.minigraphs_sources
        b_is_source = bn.uid in model.nrfg.minigraphs_sources
        
        assert isinstance( a, FusionPoint )
        assert isinstance( b, FusionPoint )
        
        __LOG_SEW( "-----------------------------------" )
        __LOG_SEW( "COMPARING THE NEXT TWO FUSION NODES" )
        __LOG_SEW( "-----------------------------------" )
        __LOG_SEW( "    A: {}", a.str_long() )
        __LOG_SEW( "    B: {}", b.str_long() )
        
        if a.event is not b.event:
            __LOG_SEW( "SKIP (THEY REFERENCE DIFFERENT EVENTS)" )
            continue
        
        if b_is_source or not a_is_source:
            __LOG_SEW( "SKIP (DEALING WITH THE A->B TRANSITIONS AND THIS IS B->A)" )
            continue
        
        if not a.pertinent_inner.intersection( b.pertinent_inner ):
            __LOG_SEW( "SKIP (THE INNER GROUPS DON'T MATCH)" )
            continue
        
        __LOG_SEW( "MATCH! (I'M READY TO MAKE THAT EDGE)" )
        an.add_edge_to( bn )
    
    __LOG_SEW.pause( "NRFG AFTER SEWING ALL:" )
    __LOG_SEW( nrfg.to_ascii() )
    __LOG_SEW.pause( "END OF SEW" )
    
    model.nrfg.fusion_graph_unclean = NamedGraph( nrfg, "Intermediate" )


def s6_drop_cleaned( model: LegoModel ):
    if model.get_status( constants.STAGES.CLEANED_13 ).is_not_complete:
        raise NotReadyError( s6_drop_cleaned.__name__, s6_create_cleaned.__name__ )
    
    if model.get_status( constants.STAGES.CHECKED_14 ).is_partial:
        raise InUseError( s6_drop_cleaned.__name__, s7_create_checks.__name__ )
    
    model.nrfg.fusion_graph_unclean = None
    model.nrfg.is_checked = False
    model.nrfg.is_clean = False


def s6_create_cleaned( model: LegoModel ):
    """
    Cleans the NRFG.
    """
    if model.get_status( constants.STAGES.FUSED_12 ).is_not_complete:
        raise NotReadyError( s6_create_cleaned.__name__, s5_create_sewed.__name__ )
    
    if model.get_status( constants.STAGES.CLEANED_13 ).is_partial:
        raise AlreadyError( s6_create_cleaned.__name__ )
    
    nrfg = model.nrfg.fusion_graph_unclean.graph.copy()
    
    for node in list( nrfg ):
        assert isinstance( node, MNode )
        
        # Remove "fusion" nodes listed in `sources`, these are the sew points
        # and will be adjacent to other identical nodes
        if lego_graph.is_fusion( node ):
            if node.uid in model.nrfg.minigraphs_sources:
                node.remove_node_safely()
        
        # Remove clades that don't add anything to the model.
        # (i.e. those which span only 2 nodes)
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
    
    for node in nrfg:
        # Make sure our fusion nodes act as roots to their creations
        # and as ancestors to their creators
        if lego_graph.is_fusion( node ):
            fusion: FusionPoint = node.data
            
            for edge in list( node.edges ):
                oppo: MNode = edge.opposite( node )
                try:
                    path = analysing.find_shortest_path( nrfg,
                                                         start = oppo,
                                                         end = lambda x: isinstance( x.data, LegoSequence ),
                                                         filter = lambda x: x is not node )
                except NotFoundError:
                    warnings.warn( "Cannot re-root along fusion edge «{}» because there is no outer path.".format( edge ), UserWarning )
                    continue
                
                if path[-1].data in fusion.sequences:
                    edge.ensure( node, oppo )
                    oppo.make_root( node_filter = lambda x: not isinstance( x.data, FusionPoint ),
                                    edge_filter = lambda x: x is not edge )
                else:
                    edge.ensure( oppo, node )
    
    for node in nrfg:
        # Nodes explicitly flagged as roots or outgroups should be made so
        if isinstance( node.data, LegoSequence ) and node.data.position != EPosition.NONE:
            if node.data.position == EPosition.OUTGROUP:
                node.relation.make_root( node_filter = lambda x: not isinstance( x.data, FusionPoint ) )
            elif node.data.position == EPosition.ROOT:
                node.make_root( node_filter = lambda x: not isinstance( x.data, FusionPoint ) )
            else:
                raise SwitchError( "node.data.position", node.data.position )
    
    model.nrfg.fusion_graph_clean = NamedGraph( nrfg, "NRFG" )


def s7_drop_checked( model: LegoModel ):
    if model.get_status( constants.STAGES.CHECKED_14 ).is_not_complete:
        raise NotReadyError( s7_drop_checked.__name__, s7_create_checks.__name__ )
    
    model.nrfg.report = None


def s7_create_checks( model: LegoModel ):
    if model.get_status( constants.STAGES.CLEANED_13 ).is_not_complete:
        raise NotReadyError( s7_create_checks.__name__, s6_create_cleaned.__name__ )
    
    if model.get_status( constants.STAGES.CHECKED_14 ).is_partial:
        raise AlreadyError( s7_create_checks.__name__ )
    
    nrfg = model.nrfg.fusion_graph_clean.graph
    
    if len( nrfg.nodes ) == 0:
        warnings.warn( "The NRFG is bad. It doesn't contain any edges.", UserWarning )
    
    if len( nrfg.edges ) == 0:
        warnings.warn( "The NRFG is bad. It doesn't contain any edges.", UserWarning )
    
    ccs = analysing.find_connected_components( nrfg )
    
    if len( ccs ) != 1:
        warnings.warn( "The NRFG is bad. It contains more than one connected component. It contains {}.".format( len( ccs ) ), UserWarning )
    
    model.nrfg.report = NrfgReport()
