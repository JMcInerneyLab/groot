"""
Module for creating the NRFG.
"""

from typing import FrozenSet, Union, Iterable, Set, Dict, Tuple

from groot.algorithms.classes import FusionPoint
from groot.data.lego_model import LegoModel, LegoSequence, LegoComponent
from mgraph import FollowParams, MGraph, MNode
from mhelper import string_helper, array_helper, Logger, LogicError


_TDataByComponent = Dict[LegoComponent, Tuple[FrozenSet[LegoSequence], Set[FrozenSet[LegoSequence]]]]
_TGetSequences = Union[Iterable[MNode], FollowParams]
_TSetSet = Set[FrozenSet[LegoSequence]]

__LOG = Logger( "nrfg", True )


def __get_split_leaves( params: _TGetSequences ) -> Set[object]:
    if isinstance( params, FollowParams ):
        params = params.visited_nodes
    
    result: Set[object] = set()
    
    for node in params:
        if isinstance( node.data, LegoSequence ):
            result.add( node.data )
        elif isinstance( node.data, FusionPoint ):
            result.add( node.data )
    
    return result


def __print_split( x: Iterable[object] ):
    return string_helper.format_array( x, sort = True )


class NewickItem:
    def __init__( self, sequence ):
        if isinstance( sequence, LegoSequence ):
            self.sequence = sequence
            self.list = None
        else:
            self.sequence = None
            self.list = sequence
    
    
    def __repr__( self ):
        if self.sequence:
            return str( self.sequence )
        else:
            return "({})".format( ", ".join( str( x ) for x in self.list ) )
    
    
    def is_subset_of( self, it ):
        for x in self:
            if x not in it:
                return False
        
        return True
    
    
    def __iter__( self ):
        if self.sequence:
            yield self.sequence
        else:
            for x in self.list:
                yield from x
    
    
    def __contains__( self, item ):
        if self.sequence is not None:
            r = item is self.sequence
            print( "{} is {}.sequence = {}".format( item, self, r ) )
            return r
        else:
            r = any( item in x for x in self.list )
            print( "any( {} in x for x in {}.list ) = {}".format( item, self, r ) )
            return r


def __iter_splits( graph: MGraph ) -> Iterable[Tuple[FrozenSet[LegoSequence], FrozenSet[LegoSequence]]]:
    """
    Obtains the set of splits in a graph.
    """
    all_sequences = __get_split_leaves( graph.nodes )
    
    for edge in graph.edges:
        left_sequences = __get_split_leaves( graph.follow( FollowParams( start = edge.left, exclude_edges = [edge] ) ) )
        right_sequences = all_sequences - left_sequences
        yield frozenset( left_sequences ), frozenset( right_sequences )


def __get_splits( graph: MGraph ) -> _TSetSet:
    """
    Obtains the set of splits in a graph.
    """
    all_splits: _TSetSet = set()
    
    for left_sequences, right_sequences in __iter_splits( graph ):
        all_splits.add( left_sequences )
        all_splits.add( right_sequences )
    
    return all_splits


def __make_graph_from_splits( splits ):
    # Nb. treemodel.Tree.from_split_bitmasks just skips dud splits, not sure we should do that here
    
    g = MGraph()
    to_use = sorted( splits, key = lambda x: len( x ) )
    root: MNode = g.add_node( data = "root" )
    
    for i, split in enumerate( to_use ):
        split_str = __print_split( split )
        
        __LOG( "CURRENT STATUS" )
        __LOG( g.to_ascii() )
        __LOG( g.to_edgelist( delimiter = "    --->    ", pad = True ) )
        __LOG( "========================================" )
        __LOG( "SPLIT {} OF {}".format( i, len( to_use ) ) )
        __LOG( "= " + split_str )
        
        if len( split ) == 1:
            sequence = array_helper.single_or_error( split )
            
            if not any( x.data is sequence for x in g.nodes ):
                root.add_child( data = sequence )
            
            continue
        
        # Find the most recent common ancestor of all sequences in our split
        paths = g.find_common_ancestor_paths( filter = lambda x: x.data in split )
        mrca: MNode = paths[0][0]
        __LOG( "MRCA = {}".format( mrca ) )
        
        # Some nodes will be attached by the same clade, reduce this to the final set
        destinations = set( path[1] for path in paths )
        
        if len( destinations ) == len( mrca.edges.outgoing_dict ):
            # Already a self-contained clade, nothing to do
            continue
        
        new_node = mrca.add_child()
        new_node.data = "split: " + split_str
        __LOG( "NEW CHILD = {}".format( new_node ) )
        
        for destination in destinations:
            # MCMD.print( "MRCA DESTINATION #n = {}".format( destination ) )
            mrca.remove_edge_to( destination )
            new_node.add_edge_to( destination )
        
        __LOG( "========================================" )
    
    __LOG( "FINAL STATUS" )
    __LOG( g.to_ascii() )
    return g


def reduce_and_rebuild( graph: MGraph ):
    results = []
    
    # ORIGINAL
    graph.get_root()
    
    results.append( "============= ORIGINAL GRAPH =============" )
    results.append( graph.to_ascii() )
    
    # SPLIT
    all_sequences = __get_split_leaves( graph.nodes )
    l = len( __print_split( all_sequences ) )
    splits = __get_splits( graph )
    
    results.append( "============= SPLITS =============" )
    for i, split in enumerate( sorted( splits, key = str ) ):
        results.append( "SPLIT {} OF {}: {} | {}".format( i, len( splits ), __print_split( split ).ljust( l ), __print_split( all_sequences - split ) ) )
    
    # RECOMBINE
    g = __make_graph_from_splits( splits )
    
    results.append( "============= RECOMBINE =============" )
    results.append( g.to_ascii() )
    
    __LOG( "\n".join( results ) )


def create_nrfg( model: LegoModel, verbose: bool = False, cutoff: float = 0.5 ):
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ SPLITS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    __LOG( "========== SPLITS STAGE ==========" )
    splits: _TSetSet = set()
    data_by_component: _TDataByComponent = { }
    
    for component in model.components:
        __LOG( str( component ) )
        
        tree: MGraph = component.tree
        tree.get_root()
        
        component_sequences = __get_split_leaves( tree.get_nodes() )
        component_splits = __get_splits( tree )
        
        for split in component_splits:
            __LOG( "SPLIT    : {}".format( __print_split( split ) ) )
        
        splits.update( component_splits )
        data_by_component[component] = component_splits, component_sequences
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ EVIDENCE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    __LOG( "========== EVIDENCE STAGE ==========" )
    to_use: _TSetSet = set()
    
    for split in splits:
        if len( split ) == 0:
            continue
        
        evidence_for = set()
        evidence_against = set()
        evidence_unused = set()
        
        for component in model.components:
            component_splits, component_sequences = data_by_component[component]
            
            if split.issubset( component_sequences ):
                if split in component_splits:
                    evidence_for.add( component )
                else:
                    evidence_against.add( component )
            else:
                evidence_unused.add( component )
        
        if not evidence_for:
            raise LogicError( "There is no evidence for this split «{}», but the split must have come from somewhere.".format( split ) )
        
        total_evidence = len( evidence_for ) + len( evidence_against )
        frequency = len( evidence_for ) / total_evidence
        accept = frequency > cutoff
        
        __LOG( "SPLIT    : {}".format( __print_split( split ) ) )
        __LOG( "SPLITSIZE: {}".format( len( split ) ) )
        __LOG( "FOR      : {}".format( string_helper.format_array( evidence_for, sort = True ) ) )
        __LOG( "AGAINST  : {}".format( string_helper.format_array( evidence_against, sort = True ) ) )
        __LOG( "UNUSED   : {}".format( string_helper.format_array( evidence_unused, sort = True ) ) )
        __LOG( "FREQUENCY: {} / {} = {}%".format( len( evidence_for ), total_evidence, int( frequency * 100 ) ) )
        __LOG( "STATUS:    {}".format( "accepted" if accept else "rejected" ) )
        __LOG( "" )
        
        if accept:
            to_use.add( split )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ RECOMBINE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # Sort the to_use by size
    __LOG( "========== RECOMBINE STAGE ==========" )
    model.nrfg = __make_graph_from_splits( to_use )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ FIX CONNECTIONS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    suitable = [x for x in model.nrfg if isinstance( x.data, FusionPoint )]
    
    for a, b in array_helper.triangular_comparison( suitable ):
        assert isinstance( a, MNode )
        assert isinstance( b, MNode )
        af: FusionPoint = a.data
        bf: FusionPoint = b.data
        
        if af.genes == bf.genes:
            if a.edges.has_node( b ):
                continue
            
            a.add_edge_to( b )
