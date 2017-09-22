from collections import OrderedDict
from typing import Callable, Dict, Iterator, Optional, Set, Tuple

from ete3 import TreeNode

from legoalign.data.lego_model import LegoComponent, LegoModel, LegoSequence
from mhelper import array_helper as ArrayHelper


DFindId = Callable[ [ str ], object ]


class MClade:
    """
    An empty object that designates a node as a clade (i.e. a point in the tree without sequence data).
    """
    pass


class MGraph:
    def __init__( self ):
        self._nodes = set()
    
    
    def import_newick( self, newick_tree: str, model: LegoModel ) -> None:
        """
        Imports a newick tree.
        :param model:           Model to find sequences in
        :param newick_tree:     Newick format tree (ETE format #1)
        """
        tree__ = TreeNode( newick_tree, format = 1 )
        self.import_ete( tree__, model )
    
    
    def import_ete( self, ete_tree: TreeNode, model: LegoModel ) -> None:
        """
        Imports an ETE3 tree
        :param model:       Model to find sequences in
        :param ete_tree:    ETE3 tree  
        :return:        Nothing 
        """
        root = MNode( self )
        
        
        def ___recurse( m_node_start, e_node_start, depth ):
            for e_node_next in e_node_start.get_children():
                m_node_next = self._node_from_ete( e_node_next, model )
                
                MEdge( self, m_node_start, m_node_next )
                
                ___recurse( m_node_next, e_node_next, depth + 1 )
        
        
        ___recurse( root, ete_tree, 0 )
    
    
    def first( self ) -> "Optional[ MNode ]":
        return ArrayHelper.first( self._nodes )
    
    
    def to_string( self ):
        r = [ ]
        first = self.first()
        
        for node, depth in first.follow_with_depth().items():
            r.append( ("  " * depth) + node.name )
        
        return "\n".join( r )
    
    
    def to_newick( self ) -> str:
        ete_tree = self.to_ete()
        return ete_tree.write( format = 1 )
    
    
    def to_ete( self ) -> TreeNode:
        def __recurse( m_node, ete_node, visited ):
            visited.add( m_node )
            new_ete_node = ete_node.add_child( name = m_node.name )
            
            for child in m_node.iter_relations():
                if child not in visited:
                    __recurse( child, new_ete_node, visited )
            
            return ete_node
        
        
        return __recurse( self.first(), TreeNode(), set() )
    
    
    def _node_from_ete( self, tree: TreeNode, model: LegoModel ):
        """
        Imports an ETE3 node.
        """
        from ete3 import TreeNode
        assert isinstance( tree, TreeNode )
        
        if not hasattr( tree, "tag_node" ):
            sequence, fusion = import_name( model, tree.name )
            
            result = MNode( self )
            result.sequence = sequence
            result.fusion = fusion
            tree.tag_node = result
        
        return tree.tag_node
    
    
    def get_edges( self ) -> "Set[ MEdge ]":
        """
        Retrieves a set of all edges.
        """
        result = set()
        
        for node in self._nodes:
            result.update( node.iter_edges() )
        
        return result
    
    
    def traverse( self ) -> "Iterator[ MNode ]":
        """
        Iterates over the nodes.
        """
        return iter( self._nodes )
    
    
    def _follow( self, source: "MNode", visited: "Dict[ MNode, int ]", depth: int ) -> None:
        """
        Populates the `visited` set with all connected nodes, starting from the `source` node.
        Nodes already in the visited list will not be visited again.
        
        Unlike normal path-following, e.g. Dijkstra, this does not use the visited list as the `source`,
        this allows the caller to iterate from a node to the exclusion of a specified branch(es).
         
        :param source:  Starting point 
        :param visited: Visited list. 
        :return: Nothing, the result is stored in `visited`. 
        """
        if source in visited:
            return
        
        visited[ source ] = depth
        
        for edge in source.iter_edges():
            op = edge.opposite( source )
            #print( "*" * depth + " > {} --> {}".format( source, op ) )
            self._follow( op, visited, depth + 1 )


class MNode:
    __uid_counter = 0
    
    
    def __init__( self, graph: MGraph ):
        MNode.__uid_counter += 1
        self._graph = graph
        self.sequence = None
        self.fusion = None
        self.__uid = MNode.__uid_counter
        self._edges = { }
        graph._nodes.add( self )
    
    
    def __repr__( self ):
        return self.name
    
    
    @property
    def name( self ) -> Optional[ str ]:
        return export_name( self.sequence, self.fusion, self.__uid )
    
    
    def iter_edges( self ) -> "Iterator[MEdge]":
        return iter( self._edges.values() )
    
    
    def num_edges( self ) -> int:
        return len( self._edges )
    
    
    def remove( self ):
        self._graph._nodes.remove( self )
    
    
    def iter_relations( self ) -> "Iterator[MNode]":
        """
        Iterates the node(s) connected to this node.
        :return: 
        """
        for edge in self.iter_edges():
            yield edge.opposite( self )
    
    
    def follow( self, *args, **kwargs ) -> "Set[MNode]":
        d = self.follow_with_depth( *args, **kwargs )
        return set( d.keys() )
    
    
    def follow_with_depth( self, exclude = None ) -> "OrderedDict[MNode, int]":
        """
        Get all related nodes recursively
        
        :param exclude: Don't follow these edges
        """
        visited = OrderedDict()
        visited[ self ] = 0
        
        if exclude is None:
            exclude = [ ]
        
        for x in exclude:
            assert isinstance( x, MEdge )
        
        for edge in self.iter_edges():
            if edge not in exclude:
                self._graph._follow( edge.opposite( self ), visited, 1 )
        
        return visited


def import_name( model: LegoModel, name: str ) -> Tuple[ Optional[ LegoSequence ], Optional[ LegoComponent ] ]:
    if not name:
        return None, None
    
    sequence = None
    component = None
    
    for value in name.split( "_" ):
        if value.startswith( "S" ):
            sequence = model.find_sequence_by_id( int( value[ 1: ] ) )
        elif value.startswith( "F" ):
            component = model.components[ int( value[ 1: ] ) ]
        elif value.startswith( "X" ):
            pass
        else:
            # LEGACY-ONLY (TODO)
            sequence = model.find_sequence( value )
    
    return sequence, component


def export_name( *args ) -> Optional[ str ]:
    r = [ ]
    
    for arg in args:
        if isinstance( arg, LegoSequence ):
            r.append( "S" )
            r.append( str( arg.id ) )
        elif isinstance( arg, LegoComponent ):
            r.append( "F" )
            r.append( str( arg.index ) )
        elif isinstance( arg, int ):
            r.append( "X" )
            r.append( str( arg ) )
    
    return "_".join( r )


class MEdge:
    def __init__( self, graph: MGraph, a: MNode, b: MNode ):
        assert a is not b, "Cannot create an edge to the same node."
        
        self._graph = graph
        self._a = a
        self._b = b
        
        a._edges[ b ] = self
        b._edges[ a ] = self
        
        assert len(a._edges) <= 3
        assert len(b._edges) <= 3
    
    
    def remove( self ):
        del self._a._edges[ self._b ]
        del self._b._edges[ self._a ]
    
    
    def __repr__( self ):
        return "{}-->{}".format( self._a, self._b )
    
    
    @property
    def a( self ):
        return self._a
    
    
    @property
    def b( self ):
        return self._b
    
    
    def opposite( self, node: MNode ):
        if self._a is node:
            return self._b
        elif self._b is node:
            return self._a
        else:
            raise KeyError( "Cannot find opposite side to '{}' because that isn't part of this edge '{}'.".format( node, self ) )
    
    
    def iter_a( self ):
        visited = set()
        visited.add( self._b )
        self._graph._follow( self._a, visited )
        visited.remove( self._b )
        return visited
    
    
    def iter_b( self ):
        visited = set()
        visited.add( self._a )
        self._graph._follow( self._b, visited )
        visited.remove( self._a )
        return visited
