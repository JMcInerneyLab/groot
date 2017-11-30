from typing import Callable, Iterator, Optional, Set, Tuple, cast, Iterable, Dict, List, Sequence, Union
from uuid import uuid4
from ete3 import TreeNode

from mhelper import array_helper, ComponentFinder, exception_helper, SwitchError


_LegoComponent_ = "groot.data.lego_model.LegoComponent"
_LegoModel_ = "groot.data.lego_model.LegoModel"
_LegoSequence_ = "groot.data.lego_model.LegoSequence"
_MGraph_ = "groot.data.graphing.MGraph"
_MNode_ = "groot.data.graphing.MNode"
_MEdge_ = "groot.data.graphing.MEdge"
TUid = int
TNodeOrUid = Union[TUid, _MNode_]  # A node in the graph, or a UID allowing the node to be found, or a node in another graph that can also be found in this graph
DFindId = Callable[[str], object]
DNodePredicate = Callable[[_MNode_], bool]
DNodeToText = Callable[[_MNode_], str]


class DepthInfo:
    def __init__( self,
                  *,
                  node: "MNode",
                  is_last: bool,
                  is_repeat: bool,
                  parent_info: "Optional[DepthInfo]",
                  has_children: bool ):
        self.node = node
        self.is_last = is_last
        self.is_repeat = is_repeat
        self.parent_info = parent_info
        self.depth = (parent_info.depth + 1) if parent_info is not None else 0
        self.has_children = has_children
    
    
    def full_path( self ) -> "List[DepthInfo]":
        r = []
        parent = self.parent_info
        
        while parent:
            r.append( parent )
            parent = parent.parent_info
        
        return list( reversed( r ) )
    
    
    def describe( self, get_text: DNodeToText ) -> str:
        # return "{}:{}{}".format( "{}".format(self.parent.node.uid) if self.parent else "R", "*" if self.is_repeat else "", self.node.detail )
        # return "{}{}->{}".format( "{}".format( self.parent.node.uid ) if self.parent else "(NO_PARENT)", "(POINTER)" if self.is_repeat else "", self.node.detail )
        ss = []
        
        for parent in self.full_path():
            ss.append( "    " if parent.is_last else "│   " )
            # ss.append( str(parent.node.uid).ljust(4, ".") )
        
        ss.append( "└───" if self.is_last else "├───" )
        
        if self.is_repeat:
            ss.append( "(REPEAT)" )
        
        ss.append( "┮" if self.has_children else "╼" )
        ss.append( get_text( self.node ) )
        
        return "".join( ss )


class FollowParams:
    def __init__( self,
                  *,
                  root: "MNode",
                  include_repeats: bool = False,
                  exclude_edges: "Iterable[MEdge]" = None,
                  exclude_nodes: "Iterable[MNode]" = None ) -> None:
        if exclude_edges is None:
            exclude_edges = []
        
        if exclude_nodes is None:
            exclude_nodes = []
        
        for x in cast( list, exclude_edges ):
            assert isinstance( x, MEdge )
        
        for x in cast( list, exclude_nodes ):
            assert isinstance( x, MNode )
        
        self.include_repeats: bool = include_repeats
        self.exclude_nodes: Set[MNode] = set( exclude_nodes )
        self.visited: List[DepthInfo] = []
        self.exclude_edges: Set[MEdge] = set( exclude_edges )
        self.root_info: DepthInfo = DepthInfo( node = root,
                                               is_last = True,
                                               is_repeat = False,
                                               parent_info = None,
                                               has_children = False )
        
        self.visited.append( self.root_info )
        self.exclude_nodes.add( self.root_info.node )
    
    
    @property
    def visited_nodes( self ) -> "Iterator[MNode]":
        return (x.node for x in self.visited)


class CutPoint:
    def __init__( self, left_subgraph: _MGraph_, left_node: _MNode_, right_subgraph: _MGraph_, right_node: _MNode_ ) -> None:
        self.left_subgraph: MGraph = left_subgraph
        self.left_node: MNode = left_node
        self.right_subgraph: MGraph = right_subgraph
        self.right_node: MNode = right_node


class IsolationPoint:
    def __init__( self, edge: _MEdge_, internal_node: _MNode_, external_node: _MNode_, inside_nodes: Set[_MNode_], cladistic_nodes: Set[_MNode_] ) -> None:
        self.edge: MEdge = edge
        self.internal_node: MNode = internal_node
        self.external_node: MNode = external_node
        self.inside_nodes: Set[_MNode_] = inside_nodes
        self.cladistic_nodes: Set[_MNode_] = cladistic_nodes
    
    
    @property
    def count( self ):
        return len( self.inside_nodes )
    
    
    def __str__( self ):
        return "<ISOLATES {} GIVEN {}>".format( self.inside_nodes, self.cladistic_nodes )


class IsolationError( Exception ):
    pass


class MGraph:
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self._nodes: Dict[int, MNode] = { }
    
    
    @property
    def nodes( self ):
        return self._nodes.values()
    
    
    def cut_one_at_isolation( self, is_inside: DNodePredicate, is_outside: DNodePredicate ) -> _MGraph_:
        """
        A combination of `find_isolation_point` and `cut_one`.
        
        :except IsolationError: More than one isolation point is found
        """
        point = self.find_isolation_point( is_inside, is_outside )
        return self.cut_one( point.internal_node, point.external_node )
    
    
    def cut_at_isolation( self, is_inside: DNodePredicate, is_outside: DNodePredicate ) -> Tuple[_MGraph_, _MGraph_]:
        """
        A combination of `find_isolation_point` and `cut`.
        
        :except IsolationError: More than one isolation point is found
        """
        point = self.find_isolation_point( is_inside, is_outside )
        return self.cut( point.internal_node, point.external_node )
    
    
    def find_isolation_point( self, is_inside: DNodePredicate, is_outside: DNodePredicate ) -> IsolationPoint:
        """
        Convenience function that calls `find_isolation_points`, returning the resultant point or raising an error.
        
        :except IsolationError: Points are not isolated.
        """
        points = self.find_isolation_points( is_inside, is_outside )
        
        if len( points ) != 1:
            raise IsolationError( "Cannot extract the isolation from the graph because the specified points are not uniquely isolated." )
        
        return points[0]
    
    
    def find_isolation_points( self, is_inside: DNodePredicate, is_outside: DNodePredicate ) -> List[IsolationPoint]:
        """
        Finds the points on the graph that separate the specified `inside` nodes from the `outside` nodes.
        
              --------I
          ----X1
          |   --------I
          |
        --X2
          |
          |   --------O
          ----X3
              --------O
             
        
        Nodes (X) not in the `inside` (I) and `outside` (O) sets are can be either inside or outside the isolated subgraph, however this
        algorithm will attempt to keep as many as possible outside, so in the diagram about, the point that isolates I from O is X1. 
        
        Ideally, there will just be one point in the results list, but if the inside points are scattered, more than one point will be
        returned, e.g. X1 and X3 separate I from O:
        
              --------I
          ----X1
          |   --------I
          |
        --X2
          |           --------I
          |   --------X3
          ----X4      --------I
              |
              --------O
         
         
        :param is_outside:   A delegate expression yielding `True` for nodes outside the set to be separated, and `False` for all other nodes. 
        :param is_inside:    A delegate expression yielding `True` for nodes inside the set to be separated,  and `False` for all other nodes. 
        :return:          A list of `IsolationPoint` detailing the isolation points. 
        """
        # Iterate over all the edges to make a list of `candidate` edges
        # - those separating INSIDE from OUTSIDE
        candidates: List[IsolationPoint] = []
        
        for edge in self.get_edges():
            for node in cast( Sequence[MNode], (edge.left, edge.right) ):
                params = FollowParams( root = node, exclude_edges = [edge] )
                self.follow( params )
                outside_nodes = False
                inside_nodes = set()
                cladistic_nodes = set()
                
                # Count the number of fusion sequences in the subgraph
                for visited_node in params.visited_nodes:
                    if is_inside( visited_node ):
                        inside_nodes.add( visited_node )
                    elif is_outside( visited_node ):
                        outside_nodes = True
                        break  # we can stop
                    else:
                        cladistic_nodes.add( visited_node )
                
                if not outside_nodes:
                    candidates.append( IsolationPoint( edge, node, edge.opposite( node ), inside_nodes, cladistic_nodes ) )
        
        # Our candidates overlap, so remove the redundant ones
        drop_candidates = []
        
        for candidate_1 in candidates:
            for candidate_2 in candidates:
                if candidate_1 is candidate_2:
                    continue
                
                is_subset = candidate_1.inside_nodes.issubset( candidate_2.inside_nodes )
                
                # If the candidates encompass different sequences don't bother
                if not is_subset:
                    continue
                
                # Any candidates that are a _strict_ subset of another can be dropped
                if len( candidate_1.inside_nodes ) < len( candidate_2.inside_nodes ):
                    drop_candidates.append( candidate_1 )
                    break
                
                # Any candidates equal to another, but have a greater number of cladistic nodes, can be dropped
                if len( candidate_1.cladistic_nodes ) > len( candidate_2.cladistic_nodes ):
                    drop_candidates.append( candidate_1 )
                    break
        
        for candidate in drop_candidates:
            candidates.remove( candidate )
        
        return candidates
    
    
    def cut( self, left_node: TNodeOrUid, right_node: TNodeOrUid ) -> Tuple[_MGraph_, _MGraph_]:
        """
        This is the same as `cut_one`, but returns both the left and the right halves of the cut.
        """
        left_node = self.find_node( left_node )
        right_node = self.find_node( right_node )
        
        exception_helper.assert_type( "left_node", left_node, MNode )
        exception_helper.assert_type( "right_node", right_node, MNode )
        
        left_graph = self.cut_one( left_node, right_node )
        right_graph = self.cut_one( right_node, left_node )
        return left_graph, right_graph
    
    
    def cut_one( self, internal_node: _MNode_, external_node: _MNode_ ) -> _MGraph_:
        """
        Cuts the graph along the edge between the specified nodes, yielding a new subset graph.
        
        The new subset contains `containing_node`, and all its relations, excluding those crossing `missing_node`. 
        
        Note this function accepts two nodes, rather than an edge, so that the assignment of
        `containing_node` and `missing_node` is always explicit, which wouldn't be obvious for undirected edges. 
        
        :param internal_node:     Node that will form the inside (accepted) half of the cut 
        :param external_node:     Node that will form the outside (rejected) half of the cut. 
        :return:                  The new graph
        """
        new_graph = MGraph()
        
        params = FollowParams( root = internal_node, exclude_nodes = [external_node] )
        self.follow( params )
        
        visited_nodes = set( params.visited_nodes )
        visited_edges = set()  # use a set because every edge appears twice (TODO: fix using a directional query)
        
        for node in visited_nodes:
            node.copy_into( new_graph )
            
            for edge in node.iter_edges():
                if edge.left in visited_nodes and edge.right in visited_nodes:
                    visited_edges.add( edge )  # add the edges after when all the nodes exist
        
        for edge in visited_edges:
            edge.copy_into( new_graph )
        
        return new_graph
    
    
    def find_connected_components( self ) -> List[List[_MNode_]]:
        """
        Calculates and returns the list of connected components.
        """
        cf = ComponentFinder()
        
        for edge in self.get_edges():
            cf.join( edge.left, edge.right )
        
        return cast( List[List[_MNode_]], cf.tabulate() )
    
    
    @classmethod
    def consensus( cls, graphs: Iterable[_MGraph_] ) -> _MGraph_:
        """
        Creates the consensus of two trees.
        NOTE: The graphs must be trees!
        
        :param graphs:  An iterable containing two or more graphs. 
        :return:        A new graph describing the consensus. 
        """
        raise NotImplementedError( "TODO" )
    
    
    def add_node( self ) -> _MNode_:
        """
        Convenience function that creates a node with this graph as the owner.
        :return:     The added node 
        """
        return MNode( self )
    
    
    def add_edge( self, left: TNodeOrUid, right: TNodeOrUid ) -> _MEdge_:
        """
        Convenience function that creates an edge with this graph as the owner.
        :param left:    Left node of edge (or a TNodeOrUid allowing the left node to be found)     
        :param right:   Right node of edge (or a TNodeOrUid allowing the right node to be found) 
        :return:        Resulting edge 
        """
        return MEdge( self, self.find_node( left ), self.find_node( right ) )
    
    
    def copy( self ) -> _MGraph_:
        """
        Makes a deep copy of this graph.
        """
        result = MGraph()
        self.copy_into( result )
        return result
    
    
    def copy_into( self, target: _MGraph_ ) -> None:
        """
        Copies all nodes and edges from this graph into another.
        Note that node information and UIDs are copied, which prevents accidentally incorporating the same set of nodes twice.
        :param target:   The graph to incorporate this graph into.
        """
        for node in self._nodes.values():
            node.copy_into( target )
        
        for edge in self.get_edges():
            edge.copy_into( target )
    
    
    def find_node( self, node: TNodeOrUid ) -> _MNode_:
        """
        Finds a node in this graph, to one that exists in a different graph.
         
        :param node:    Node or UID of node to find. 
        :return:        Node in this graph. 
        """
        if isinstance( node, MNode ):
            if node._graph is self:
                return node
            else:
                node = node.uid
        
        if isinstance( node, TUid ):
            result = self._nodes.get( node )
            
            if result is not None:
                return result
            
            raise ValueError( "Cannot find the requested node («{}») in this graph.".format( node ) )
        
        raise SwitchError( "node", node, instance = True )
    
    
    @classmethod
    def from_newick( cls, newick_tree: str, model: _LegoModel_ ) -> _MGraph_:
        """
        Calls `import_newick` on a new graph.
        """
        result = cls()
        result.import_newick( newick_tree, model )
        return result
    
    
    def import_newick( self, newick_tree: str, model: _LegoModel_ ) -> None:
        """
        Imports a newick tree.
        :param model:           Model to find sequences in
        :param newick_tree:     Newick format tree (ETE format #1)
        """
        tree__ = TreeNode( newick_tree, format = 1 )
        self.import_ete( tree__, model )
    
    
    def import_ete( self, ete_tree: TreeNode, model: _LegoModel_ ) -> None:
        """
        Imports an Ete tree
        
        :param model:       Model to find sequences in
        :param ete_tree:    Ete tree 
        """
        root = MNode( self )
        
        
        def ___recurse( m_node_start, e_node_start, depth ) -> None:
            for e_node_next in e_node_start.get_children():
                m_node_next = self._node_from_ete( e_node_next, model )
                
                MEdge( self, m_node_start, m_node_next )
                
                ___recurse( m_node_next, e_node_next, depth + 1 )
        
        
        ___recurse( root, ete_tree, 0 )
    
    
    def to_csv( self, get_text: DNodeToText ):
        r = []
        
        for edge in self.get_edges():
            r.append( "{},{}".format( get_text( edge.left ), get_text( edge.right ) ) )
        
        return "\n".join( r )
    
    
    def to_ascii( self, get_text: DNodeToText ):
        """
        Shows the graph as ASCII-art, which is actually in UTF8.
        """
        results: List[str] = []
        visited: Set[MNode] = set()
        
        while True:
            # Choose an arbitrary root
            first = array_helper.first( x for x in self._nodes.values() if x not in visited )
            
            if first is None:
                break
            
            params = FollowParams( root = first, include_repeats = True )
            self.follow( params )
            visited.update( params.exclude_nodes )
            results.extend( x.describe( get_text ) for x in params.visited )
        
        return "\n".join( results )
    
    
    def to_newick( self, get_text: DNodeToText ) -> str:
        """
        Converts the graph to a Newick tree.
        """
        ete_tree = self.to_ete( get_text )
        return ete_tree.write( format = 1 )
    
    
    def to_ete( self, get_text: DNodeToText ) -> TreeNode:
        """
        Converts the graph to an Ete tree.
        """
        
        
        def __recurse( m_node: MNode, ete_node: TreeNode, visited: Set ):
            visited.add( m_node )
            # noinspection PyTypeChecker
            new_ete_node = ete_node.add_child( name = get_text( m_node ) )
            
            for child in m_node.iter_relations():
                if child not in visited:
                    __recurse( child, new_ete_node, visited )
            
            return ete_node
        
        
        # Choose an arbitrary starting point
        first = array_helper.first_or_error( self._nodes.values() )
        
        return __recurse( first, TreeNode(), set() )
    
    
    def _node_from_ete( self, tree: TreeNode, model: _LegoModel_ ):
        """
        Imports an Ete tree into the graph.
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
        Retrieves the set of all edges.
        """
        result = set()
        
        for node in self._nodes.values():
            result.update( node.iter_edges() )
        
        return result
    
    
    def get_nodes( self ) -> "Iterator[ MNode ]":
        """
        Iterates over all the nodes.
        """
        return iter( self._nodes.values() )
    
    
    def follow( self, params: FollowParams ) -> FollowParams:
        self.__follow( params = params, parent_info = params.root_info )
        return params
    
    
    def __follow( self,
                  *,
                  params: FollowParams,
                  parent_info: DepthInfo ) -> None:
        """
        Populates the `visited` set with all connected nodes, starting from the `source` node.
        Nodes already in the visited list will not be visited again.
        
        Unlike normal path-following, e.g. Dijkstra, this does not use the visited list as the `source`,
        this allows the caller to iterate from a node to the exclusion of a specified branch(es).
        """
        parent = parent_info.node
        targets = [edge.opposite( parent ) for edge in parent.iter_edges() if edge not in params.exclude_edges]
        
        if parent_info.parent_info is not None:
            targets = [node for node in targets if node is not parent_info.parent_info.node]
        
        depth_info = None
        
        for target in targets:
            if target in params.exclude_nodes:
                if not params.include_repeats:
                    continue
                
                depth_info = DepthInfo( node = target,
                                        is_repeat = True,
                                        parent_info = parent_info,
                                        is_last = False,
                                        has_children = False )
                
                params.visited.append( depth_info )
                
                continue
            
            params.exclude_nodes.add( target )
            
            depth_info = DepthInfo( node = target,
                                    parent_info = parent_info,
                                    is_last = False,
                                    is_repeat = False,
                                    has_children = False )
            
            params.visited.append( depth_info )
            
            self.__follow( params = params,
                           parent_info = depth_info )
        
        if depth_info is not None:
            parent_info.has_children = True
            depth_info.is_last = True


class MNode:
    """
    Nodes of the MGraph.
    
    :attr __uid:    UID of node
    :attr _graph:   Graph this node is contained within
    :attr _edges:   Edges on this node (in any direction)
    :attr data:     User (arbitrary) data associated with this node
    """
    
    
    def __init__( self, graph: MGraph, uid: int = None, data: object = None ):
        """
        CONSTRUCTOR 
        """
        if uid is None:
            uid = uuid4().int
        
        self.__uid: int = uid
        self._graph: MGraph = graph
        self._edges: Dict[MNode, MEdge] = { }
        self.data: object = data
        
        assert self.__uid not in graph._nodes
        
        graph._nodes[self.__uid] = self
    
    
    def copy_into( self, target_graph: MGraph ) -> _MNode_:
        """
        Copies the node (but not the edges!)
        """
        return MNode( target_graph, self.__uid, self.data )
    
    
    @property
    def uid( self ) -> int:
        return self.__uid
    
    
    def __repr__( self ):
        return "MNode( {} )".format( self.data )
    
    
    def iter_edges( self ) -> "Iterator[MEdge]":
        """
        Iterates over the edges on this node.
        """
        return sorted( self._edges.values(), key = lambda x: "{}-{}".format( id( x.left ), id( x.right ) ) )
    
    
    def num_edges( self ) -> int:
        """
        The number of edges on this node.
        """
        return len( self._edges )
    
    
    def remove( self ) -> None:
        """
        Removes this node from the graph.
        
        Associated edges are also removed.
        """
        while self._edges:
            for x in self._edges.values():
                x.remove()
                break
        
        del self._graph._nodes[self.__uid]
    
    
    def iter_relations( self ) -> "Iterator[MNode]":
        """
        Iterates the node(s) connected to this node.
        """
        for edge in self.iter_edges():
            yield edge.opposite( self )


def import_name( model: _LegoModel_, name: str ) -> Tuple[Optional[_LegoSequence_], Optional[_LegoComponent_]]:
    if not name:
        return None, None
    
    sequence = None
    component = None
    
    for value in name.split( "_" ):
        if value.startswith( "S" ):
            sequence = model.find_sequence_by_id( int( value[1:] ) )
        elif value.startswith( "F" ):
            component = model.components[int( value[1:] )]
        elif value.startswith( "X" ):
            pass
        else:
            # LEGACY-ONLY (TODO)
            sequence = model.find_sequence( value )
    
    return sequence, component


def export_name( *args ) -> Optional[str]:
    from groot.data.lego_model import LegoSequence, LegoComponent
    
    r = []
    
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
    def __init__( self, graph: MGraph, left: MNode, right: MNode ):
        assert isinstance( graph, MGraph )
        assert isinstance( left, MNode )
        assert isinstance( right, MNode )
        
        if left is right:
            raise ValueError( "Cannot create an edge to the same node." )
        
        if right in left._edges or left in right._edges:
            raise ValueError( "Cannot add an edge from node to node because these nodes already share an edge." )
        
        self._graph = graph
        self._left = left
        self._right = right
        
        left._edges[right] = self
        right._edges[left] = self
    
    
    def copy_into( self, target_graph: MGraph ) -> Optional[_MEdge_]:
        """
        Copies this edge into the target graph.
        
        If the same nodes do not exist in the target graph, no edge is created and the function returns `None`.
        """
        left = target_graph.find_node( self._left.uid )
        
        if left is None:
            return None
        
        right = target_graph.find_node( self._right.uid )
        
        if right is None:
            return None
        
        new_edge = MEdge( target_graph, left, right )
        return new_edge
    
    
    def remove( self ) -> None:
        del self._left._edges[self._right]
        del self._right._edges[self._left]
    
    
    def __repr__( self ) -> str:
        return "{}-->{}".format( self._left, self._right )
    
    
    @property
    def left( self ) -> MNode:
        return self._left
    
    
    @property
    def right( self ) -> MNode:
        return self._right
    
    
    def opposite( self, node: MNode ) -> MNode:
        if self._left is node:
            return self._right
        elif self._right is node:
            return self._left
        else:
            raise KeyError( "Cannot find opposite side to '{}' because that isn't part of this edge '{}'.".format( node, self ) )
    
    
    def iter_a( self ) -> Set[MNode]:
        return self._graph.follow( FollowParams( root = self._left, exclude_nodes = [self._right] ) ).exclude_nodes
    
    
    def iter_b( self ) -> Set[MNode]:
        return self._graph.follow( FollowParams( root = self._right, exclude_nodes = [self._left] ) ).exclude_nodes
