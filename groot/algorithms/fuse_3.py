from typing import FrozenSet, Union, Iterable, Set, Dict, Tuple
from groot.data.lego_model import LegoModel, LegoSequence, LegoComponent
from groot.graphing import FollowParams, MGraph, MNode
from groot.graphing.graphing import IsolationPoint
from intermake.engine.environment import MCMD
from mhelper import string_helper, array_helper


_TDataByComponent = Dict[LegoComponent, Tuple[FrozenSet[LegoSequence], Set[FrozenSet[LegoSequence]]]]
_TGetSequences = Union[Iterable[MNode], FollowParams]
_TSetSet = Set[FrozenSet[LegoSequence]]


def __get_sequences( params: _TGetSequences ) -> Set[LegoSequence]:
    if isinstance( params, FollowParams ):
        params = params.visited_nodes
    
    result: Set[LegoSequence] = set()
    
    for node in params:
        if isinstance( node.data, LegoSequence ):
            result.add( node.data )
    
    return result


def __print_sequence( x: LegoSequence ):
    return x.accession


def __print_sequences( x: Iterable[LegoSequence] ):
    return string_helper.format_array( x, sort = True, format = __print_sequence )


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


def create_nrfg( model: LegoModel, verbose: bool = False, cutoff: float = 0.5 ):
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ SPLITS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    MCMD.print( "========== SPLITS STAGE ==========" )
    splits: _TSetSet = set()
    data_by_component: _TDataByComponent = { }
    all_sequences: Set[LegoSequence] = set()
    
    for component in model.components:
        MCMD.print( component )
        
        tree: MGraph = component.tree
        tree.get_root()
        
        component_sequences = __get_sequences( tree.get_nodes() )
        all_sequences.update( component_sequences )
        component_splits: _TSetSet = set()
        
        for edge in tree.get_edges():
            left_sequences = __get_sequences( tree.follow( FollowParams( start = edge.left, exclude_edges = [edge] ) ) )
            right_sequences = component_sequences - left_sequences
            left_sequence_set = frozenset( left_sequences )
            right_sequence_set = frozenset( right_sequences )
            component_splits.add( left_sequence_set )
            component_splits.add( right_sequence_set )
            
            MCMD.print( __print_sequences( left_sequences ) )
            MCMD.print( __print_sequences( right_sequences ) )
        
        splits.update( component_splits )
        data_by_component[component] = component_splits, component_sequences
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ EVIDENCE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    MCMD.print( "========== EVIDENCE STAGE ==========" )
    to_use: _TSetSet = set()
    
    for split in splits:
        evidence_for = set()
        evidence_against = set()
        evidence_unused = set()
        
        for component in model.components:
            component_splits, component_sequences = data_by_component[component]
            
            if split.issubset( component_sequences ) and split != component_sequences:
                if split in component_splits:
                    evidence_for.add( component )
                else:
                    evidence_against.add( component )
            else:
                evidence_unused.add( component )
        
        total_evidence = len( evidence_for ) + len( evidence_against )
        frequency = len( evidence_for ) / total_evidence
        accept = frequency > cutoff
        
        MCMD.print( "{}".format( __print_sequences( split ) ) )
        MCMD.print( "FOR      : {}".format( string_helper.format_array( evidence_for, sort = True ) ) )
        MCMD.print( "AGAINST  : {}".format( string_helper.format_array( evidence_against, sort = True ) ) )
        MCMD.print( "UNUSED   : {}".format( string_helper.format_array( evidence_unused, sort = True ) ) )
        MCMD.print( "FREQUENCY: {} / {} = {}%".format( len( evidence_for ), total_evidence, int( frequency ) ) )
        MCMD.print( "STATUS:    {}".format( "accepted" if accept else "rejected" ) )
        MCMD.print( "" )
        
        if accept:
            to_use.add( split )
    
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ RECOMBINE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
    # Sort the to_use by size
    MCMD.print( "========== RECOMBINE STAGE ==========" )
    to_use = sorted( to_use, key = lambda x: len( x ) )
    joins = []
    
    for i, split in enumerate(to_use):
        MCMD.print( "SPLIT {}/{}: ".format(i, len(to_use)) + __print_sequences( split ) )
        join = []
        
        for x in joins:
            if x.is_subset_of( split ):
                join.append( x )
        
        for x in join:
            joins.remove( x )
        
        if join:
            i = NewickItem( join )
        elif len( split ) == 1:
            i = NewickItem( array_helper.single_or_error( split ) )
        else:
            raise ValueError( "I don't understand the split «{}» given the current tree «{}».".format( __print_sequences( split ),
                                                                                                       string_helper.format_array( joins, sort = True ) ) )
        
        joins.append( i )
        MCMD.print( "STATUS: " + string_helper.format_array( joins, sort = True ) )
