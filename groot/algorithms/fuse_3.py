from typing import FrozenSet, Set, Union as TUnion, Iterable as TIterable, Counter as TCounter, Set, Dict, Tuple
from groot.data.lego_model import LegoModel, LegoSequence, LegoComponent
from groot.graphing import FollowParams, MGraph, MNode
from intermake.engine.environment import MCMD
from mhelper import array_helper, string_helper


class SplitCounter:
    def __init__( self ):
        self.evidence_for = 0
        self.evidence_against = 0


def __get_sequences( params: TUnion[TIterable[MNode], FollowParams] ) -> Set[LegoSequence]:
    if isinstance( params, FollowParams ):
        params = params.visited_nodes
    
    result: Set[LegoSequence] = set()
    
    for node in params:
        if isinstance( node.data, LegoSequence ):
            result.add( node.data )
    
    return result


def create_nrfg( model: LegoModel, verbose: bool = False, cutoff: float = 0.5 ):
    splits: Set[FrozenSet[LegoSequence]] = set()
    data_by_component: Dict[LegoComponent, Tuple[FrozenSet[LegoSequence], Set[FrozenSet[LegoSequence]] ]] = { }
    
    for component in model.components:
        MCMD.print( component )
        tree: MGraph = component.tree
        
        tree.get_root()
        
        # MCMD.print( tree.to_ascii( lambda x: str( x.uid )[:4] + ". " + str( x ) ) )
        
        component_sequences = __get_sequences( tree.get_nodes() )
        
        component_splits = set()
        
        for edge in tree.get_edges():
            left_sequences = __get_sequences( tree.follow( FollowParams( start = edge.left, exclude_edges = [edge] ) ) )
            right_sequences = component_sequences - left_sequences
            MCMD.print( left_sequences )
            MCMD.print( right_sequences )
            left_sequence_set = frozenset( left_sequences )
            right_sequence_set = frozenset( right_sequences )
            component_splits.add( left_sequence_set )
            component_splits.add( right_sequence_set )
        
        splits.update( component_splits )
        data_by_component[component] = component_splits, component_sequences
    
    to_use: Set[FrozenSet[LegoSequence]] = set()
    
    for sequences in splits:
        ev_for = set()
        ev_aga = set()
        ev_not = set()
        
        for component in model.components:
            component_splits, component_sequences = data_by_component[component]
            
            
            if sequences.issubset( component_sequences ) and sequences != component_sequences:
                if sequences in data_by_component[component]:
                    ev_for.add( component )
                else:
                    ev_aga.add( component )
            else:
                ev_not.add( component )
        
        total_ev = len( ev_for ) + len( ev_aga )
        freq = len( ev_for ) / total_ev
        accept = freq > cutoff
        
        if verbose:
            MCMD.print( "{}".format( string_helper.format_array( sequences, sort = True ) ) )
            MCMD.print( "FOR      : {}".format( string_helper.format_array( ev_for, sort = True ) ) )
            MCMD.print( "AGAINST  : {}".format( string_helper.format_array( ev_aga, sort = True ) ) )
            MCMD.print( "UNUSED   : {}".format( string_helper.format_array( ev_not, sort = True ) ) )
            MCMD.print( "FREQUENCY: {} / {} = {}%".format( len( ev_for ), total_ev, int( freq ) ) )
            MCMD.print( "STATUS:    {}".format( "accepted" if accept else "rejected" ) )
            MCMD.print( "" )
        
        if accept:
            to_use.add( sequences )

    for sequences in to_use:
        