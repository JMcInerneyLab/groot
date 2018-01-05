from typing import List

from groot.algorithms import dbg, consensus
from groot.data.graphing import MGraph, MNode, MEdge
from groot.data.lego_model import LegoModel, LegoSequence, LegoComponent
from groot.graphing.graphing import FollowParams
from intermake.engine.environment import MCMD
from mhelper import string_helper, ansi, array_helper


VISITED = ansi.FORE_GREEN + "V" + ansi.RESET
UNVISITED = ansi.FORE_RED + "U" + ansi.RESET
LEFT = ansi.FORE_MAGENTA + "<<<" + ansi.RESET
RIGHT = ansi.FORE_MAGENTA + ">>>" + ansi.RESET


def ϵ( the_set ):
    the_set = set( the_set )
    return lambda x: isinstance( x.data, LegoSequence ) and x.data in the_set


def Nϵ( the_set ):
    the_set = set( the_set )
    return lambda x: isinstance( x.data, LegoSequence ) and x.data not in the_set

def sequences(g:MGraph):
    return set(x.data for x in g.nodes if isinstance(x.data, LegoSequence))


class StumpInfo:
    def __init__( self, graph: MGraph ):
        self.sequences = sequences(graph)
    
    
    def __str__( self ):
        return "[" + string_helper.format_array( self.sequences, sort = True ) + "]"


def best_iso( g: MGraph, is_inside, is_outside ):
    if not any( is_outside( x ) for x in g.nodes ):
        return None
    
    results = []
    
    for edge in g.get_edges():
        for left, right in ((edge.left, edge.right), (edge.right, edge.left)):
            p = FollowParams( root = left, exclude_edges = [edge] )
            g.follow( p )
            unvisited_nodes = set( g.nodes )
            
            for a in p.visited_nodes:
                unvisited_nodes.remove( a )
            
            if any( is_inside( x ) for x in unvisited_nodes ):
                score = -1
            else:
                score = sum( is_outside( x ) for x in p.visited_nodes )
            
            # if debug is not None and debug[0] == left and debug[1] == right:
            #     MCMD.print( g.to_ascii( lambda x: "{} {}".format( x, LEFT if x is left else RIGHT if x is right else VISITED if x in p.visited_nodes else UNVISITED if x in unvisited_nodes else "-" ) ) )
            #     MCMD.print( "SCORE {}".format( score ) )
            #     MCMD.question( "Continue", [True, False], True )
            
            if score >= 0:
                results.append( (score, left, right) )
    
    results = sorted( results, key = lambda x: x[0] )
    
    # if debug is None:
    #     return best_iso(g, is_inside, is_outside, (results[0][1], results[0][2]))
    
    return results[0]


def create_nrfg( model: LegoModel ):
    bag: List[MGraph] = []
    
    for component in model.components:
        MCMD.print( "********** COMPONENT {}".format( component ) )
        
        # Take a component tree
        t = component.tree
        dbg.graph( "initial tree", t )
        
        # Chop it
        for outgoing in sorted( component.outgoing_components(), key = lambda x: len( x.outgoing_components() ) ):  # todo: len isn't the correct way
            if outgoing is component:
                continue
            MCMD.print( "Chop on {}: {}".format( outgoing, string_helper.format_array( outgoing.major_sequences ) ) )
            t = _recut( component, outgoing, t, bag )
        
        # Add the final bit to our baggie
        dbg.graph( "final bagged bit", t )
        bag.append( t )
    
    MCMD.print( "********** FINAL BAG" )
    for tree in bag:
        dbg.graph( "tree_bag", tree )
    
    # The bits in our bag that overlap, we need to find a consensus for
    similar_tree_lists = []
    
    while bag:
        similar_trees = []
        use = bag.pop()
        similar_trees.append(use)
        
        use_seq = sequences(use)
        
        for other in bag:
            if sequences(other) == use_seq:
                similar_trees.append(other)
                
                
        similar_tree_lists.append(similar_trees)
        
    for i, similar_trees in enumerate(similar_tree_lists):
        MCMD.print("CONSENSUS")
        
        if len(similar_trees) != 1:
            for tree in similar_trees:
                MCMD.print("IN")
                MCMD.print(tree.to_ascii())
                
            consensus_tree = consensus.tree_consensus( model, similar_trees )[0]
            MCMD.print("FINAL")
            MCMD.print(consensus_tree.to_ascii())
            similar_tree_lists[i] = [consensus_tree]
        else:
            MCMD.print("NOT REQUIRED")
            
    
            
        


def _recut( component: LegoComponent, outgoing: LegoComponent, t, bag: List[MGraph] ) -> MGraph:
    iso = best_iso( t, Nϵ( outgoing.major_sequences ), ϵ( outgoing.major_sequences ) )
    
    if iso is None:
        # Already pure
        MCMD.print( "Tree is already pure." )
        return t
    else:
        MCMD.print( "Isolation point score {}".format( iso[0] ) )
        
        a, b = t.cut( iso[1], iso[2] )
        assert isinstance( a, MGraph )
        assert isinstance( b, MGraph )
        
        nn = MNode( a, data = StumpInfo( b ) )
        MEdge( a.find_node( iso[1] ), nn )
        
        nn = MNode( b, data = StumpInfo( a ) )
        MEdge( b.find_node( iso[2] ), nn )
        
        dbg.graph( "reduced to", a )
        dbg.graph( "bagged bit", b )
        
        # The second bit is pure, add it to our baggie
        bag.append( b )
        
        # The first bit is pure only if the iso score is zero
        if iso[0] == 0:
            MCMD.print( "Tree is now pure." )
            return a
        else:
            MCMD.print( "Tree needs more purification." )
            return _recut( component, outgoing, a, bag )
