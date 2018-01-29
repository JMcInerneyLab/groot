"""
Module for creating the NRFG.
"""

from typing import Dict, FrozenSet, Iterable, Set, Tuple, Union, AbstractSet

import itertools

from groot.algorithms.classes import IFusion
from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence
from intermake.engine.environment import MCMD
from mgraph import FollowParams, MEdge, MGraph, MNode
from mhelper import Logger, LogicError, TTristate, ansi, array_helper, string_helper, ansi_helper


_TLeaf = Union[LegoSequence, IFusion]
_TDataByComponent = Dict[LegoComponent, Tuple[FrozenSet[LegoSequence], Set[FrozenSet[LegoSequence]]]]
_TGetSequences = Union[Iterable[MNode], FollowParams]

__LOG = Logger( "nrfg", True )


class Split:
    def __init__( self, inside: FrozenSet[_TLeaf], outside: FrozenSet[_TLeaf] ):
        self.inside: FrozenSet[_TLeaf] = inside
        self.outside: FrozenSet[_TLeaf] = outside
        self.all = frozenset( itertools.chain( self.inside, self.outside ) )
    
    
    def __str__( self ):
        r = []
        
        for x in sorted( self.all, key = str ):
            if x in self.inside:
                r.append( ansi.FORE_GREEN + str( x ) + ansi.FORE_RESET )
            else:
                r.append( ansi.FORE_RED + str( x ) + ansi.FORE_RESET )
        
        return ", ".join( r )
        
        # return string_helper.format_array( self.all, sort = True )+" = "+ ansi.FORE_GREEN + string_helper.format_array( self.inside, sort = True ) + ansi.RESET + " ¦ " + ansi.FORE_RED + string_helper.format_array( self.outside, sort = True ) + ansi.RESET
    
    
    @property
    def is_empty( self ):
        return len( self.inside ) == 0
    
    
    def is_evidenced_by( self, other: "Split" ) -> TTristate:
        """
        A split is evidenced by another if it is a subset of it
        No evidence can be provided if the other set of leaves is not a subset 
        """
        if not self.all.issubset( other.all ):
            return None
        
        return self.inside.issubset( other.inside ) and self.outside.issubset( other.outside )
    
    
    def __len__( self ):
        return len( self.inside )
    
    
    def __hash__( self ):
        return hash( (self.inside, self.outside) )
    
    
    def __eq__( self, other ):
        return isinstance( other, Split ) and self.inside == other.inside and self.outside == other.outside


def __is_clade( node: MNode ) -> bool:
    return node.data is None or isinstance( node.data, str )


def __is_fusion( node: MNode ) -> bool:
    return isinstance( node.data, IFusion )


def __get_split_leaves( params: _TGetSequences ) -> Set[_TLeaf]:
    if isinstance( params, FollowParams ):
        params = params.visited_nodes
    
    result: Set[_TLeaf] = set()
    
    for node in params:
        if isinstance( node.data, LegoSequence ):
            result.add( node.data )
        elif isinstance( node.data, IFusion ):
            result.add( node.data )
    
    return result


def __iter_splits( graph: MGraph ) -> Iterable[Tuple[FrozenSet[LegoSequence], FrozenSet[LegoSequence]]]:
    """
    Obtains the set of splits in a graph.
    """
    all_sequences = __get_split_leaves( graph.nodes )
    
    for edge in graph.edges:
        left_leaves = __get_split_leaves( graph.follow( FollowParams( start = edge.left, exclude_edges = [edge] ) ) )
        right_leaves = all_sequences - left_leaves
        yield frozenset( left_leaves ), frozenset( right_leaves )


def __get_splits( graph: MGraph ) -> Set[Split]:
    """
    Obtains the set of splits in a graph.
    """
    all_splits: Set[Split] = set()
    
    for left_sequences, right_sequences in __iter_splits( graph ):
        all_splits.add( Split( left_sequences, right_sequences ) )
        all_splits.add( Split( right_sequences, left_sequences ) )
    
    return all_splits


def __make_graph_from_splits( splits: AbstractSet[Split] ):
    # Nb. treemodel.Tree.from_split_bitmasks just skips dud splits, not sure we should do that here
    
    g = MGraph()
    to_use = sorted( splits, key = lambda x: str( x ) )
    to_use = sorted( to_use, key = lambda x: len( x ) )
    root: MNode = g.add_node( data = "root" )
    
    for i, split in enumerate( to_use ):
        split_str = str( split )
        
        # __LOG( "CURRENT STATUS" )
        # __LOG( g.to_ascii() )
        # __LOG( g.to_edgelist( delimiter = "    --->    ", pad = True ) )
        # __LOG( "========================================" )
        # __LOG( "SPLIT {} OF {}".format( i, len( to_use ) ) )
        # __LOG( "= " + split_str )
        
        if len( split ) == 1:
            __LOG( "DEFINING SPLIT {} OF {} = {}", i, len( to_use ), split_str )
            sequence = array_helper.single_or_error( split.inside )
            
            if not any( x.data is sequence for x in g.nodes ):
                root.add_child( data = sequence )
            
            continue
        
        # Find the most recent common ancestor of all sequences in our split
        paths = g.find_common_ancestor_paths( filter = lambda x: x.data in split.inside )
        mrca: MNode = paths[0][0]
        # __LOG( "MRCA = {}".format( mrca ) )
        
        # Some nodes will be attached by the same clade, reduce this to the final set
        destinations = set( path[1] for path in paths )
        
        if len( destinations ) == len( mrca.edges.outgoing_dict ):
            # Already a self-contained clade, nothing to do
            __LOG( "EXISTING SPLIT {} OF {} = {} (@{})", i, len( to_use ), split_str, mrca )
            continue
        
        __LOG( "NEW      SPLIT {} OF {} = {} (@{})", i, len( to_use ), split_str, mrca )
        
        new_node = mrca.add_child()
        #new_node.data = "split: " + split_str
        # __LOG( "NEW CHILD = {}".format( new_node ) )
        
        for destination in destinations:
            # MCMD.print( "MRCA DESTINATION #n = {}".format( destination ) )
            mrca.remove_edge_to( destination )
            new_node.add_edge_to( destination )
        
        __LOG(g.to_ascii())

        __print_split_status( g, split )
            
        __LOG.pause()
        
        # __LOG( "========================================" )
    
    # __LOG( "FINAL STATUS" )
    # __LOG( g.to_ascii() )
    return g


def __print_split_status( g, split ):
    query = set( [split] )
    if __debug_splits( g, query ) == query:
        __LOG( "OK" )
    else:
        __LOG( "FAIL" )


def reduce_and_rebuild( graph: MGraph ):
    results = []
    
    # ORIGINAL
    graph.get_root()
    
    results.append( "============= ORIGINAL GRAPH =============" )
    results.append( graph.to_ascii() )
    
    # SPLIT
    splits = __get_splits( graph )
    
    results.append( "============= SPLITS =============" )
    for i, split in enumerate( sorted( splits, key = Split.__str__ ) ):
        results.append( "SPLIT {} OF {}: {}".format( i, len( splits ), str( split ) ) )
    
    # RECOMBINE
    g = __make_graph_from_splits( splits )
    
    results.append( "============= RECOMBINE =============" )
    results.append( g.to_ascii() )
    
    __LOG( "\n".join( results ) )


def create_nrfg( model: LegoModel, cutoff: float = 0.5, clean: bool = False, debug: bool = True ):
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ SPLITS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    __LOG( "========== SPLITS STAGE ==========" )
    if debug:
        MCMD.autoquestion( "begin splits" )
    all_splits: Set[Split] = set()
    data_by_component: Dict[LegoComponent, Tuple[FrozenSet[Split], FrozenSet[_TLeaf]]] = { }
    
    for component in model.components:
        __LOG( "FOR COMPONENT {}", component )
        
        tree: MGraph = component.tree
        tree.get_root()
        
        component_sequences = __get_split_leaves( tree.get_nodes() )
        component_splits = __get_splits( tree )
        
        for split in component_splits:
            __LOG( "---- FOUND SPLIT {}", str( split ) )
        
        all_splits.update( component_splits )
        data_by_component[component] = frozenset( component_splits ), frozenset( component_sequences )
        
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ EVIDENCE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    __LOG( "========== EVIDENCE STAGE ==========" )
    if debug:
        MCMD.autoquestion( "begin evidence ({} splits)".format( len( all_splits ) ) )
    to_use: Set[Split] = set()
    
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
            to_use.add( split )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ RECOMBINE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # Sort the to_use by size
    __LOG( "========== RECOMBINE STAGE ==========" )
    if debug:
        MCMD.autoquestion( "begin recombine" )
    model.nrfg = __make_graph_from_splits( to_use )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ DEBUG SPLITS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    if debug:
        MCMD.autoquestion( "begin debug" )
        

    supported = __debug_splits( model.nrfg, to_use )
    unsupported = to_use - supported 
    
    for split in unsupported:
        MCMD.print( ansi.FORE_RED + "unsupported: " + ansi.RESET + str( split ) )
    
    for split in supported:
        MCMD.print( ansi.FORE_GREEN + "supported: " + ansi.RESET + str( split ) )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ CLEAN GRAPH ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    if clean:
        if debug:
            MCMD.autoquestion( "begin clean" )
        __LOG( "========== CLEAN GRAPH ==========" )
        for node in list( model.nrfg ):
            assert isinstance( node, MNode )
            if __is_fusion( node ):
                node.remove_node()
        
        for node in list( model.nrfg ):
            assert isinstance( node, MNode )
            if __is_clade( node ):
                in_ = len( node.edges.incoming )
                out_ = len( node.edges.outgoing )
                if in_ == 1 and out_ == 1:
                    node.parent.add_edge_to( node.child )
                    node.remove_node()
                if in_ == 0 and out_ == 2:
                    c = list( node.children )
                    c[0].add_edge_to( c[1] )
                    node.remove_node()


def __debug_splits( graph, query ):
    supported: Set[Split] = set()
    new_splits: Set[Split] = set()
    
    for edge in graph.edges:
        assert isinstance( edge, MEdge )
        left: FrozenSet[_TLeaf] = frozenset( __get_split_leaves( edge.follow_left() ) )
        right: FrozenSet[_TLeaf] = frozenset( __get_split_leaves( edge.follow_right() ) )
        
        new_splits.add( Split( left, right ) )
        new_splits.add( Split( right, left ) )
        
    for split in query:
        for new_split in new_splits:
            if split.is_evidenced_by( new_split ) is True:
                supported.add( split )
                
    return supported
