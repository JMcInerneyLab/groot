from typing import Callable, Iterator, Optional, Set, Tuple, cast, Iterable, Dict, List, Sequence
from uuid import uuid4

from ete3 import TreeNode

from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence
from intermake.engine.theme import Theme

from mhelper import array_helper, ComponentFinder


_MGraph = "MGraph"
_MNode = "MNode"
_MEdge = "MEdge"

DFindId = Callable[[str], object]
DNodePredicate = Callable[[_MNode], bool]


class MClade:
    """
    An empty object that designates a node as a clade (i.e. a point in the tree without sequence data).
    """
    pass


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
    
    
    def describe( self, format_str: str ) -> str:
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
        ss.append( self.node.describe( format_str ) )
        
        return "".join( ss )


class FollowParams:
    def __init__( self,
                  *,
                  root: "MNode",
                  include_repeats: bool = False,
                  exclude_edges: "Iterable[MEdge]" = None,
                  exclude_nodes: "Iterable[MNode]" = None ):
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
    def __init__( self, left_subgraph: MGraph, left_node: MNode, right_subgraph: MGraph, right_node: MNode ):
        self.left_subgraph: MGraph = left_subgraph
        self.left_node: MNode = left_node
        self.right_subgraph: MGraph = right_subgraph
        self.right_node: MNode = right_node


class _FusionPointCandidate:
    def __init__( self, edge: MEdge, internal_node: MNode, external_node: MNode, genes: List[LegoSequence] ) -> None:
        self.edge: MEdge = edge
        self.internal_node: MNode = internal_node
        self.external_node: MNode = external_node
        self.genes: List[LegoSequence] = genes
    
    
    @property
    def count( self ):
        return len( self.genes )


class MGraph:
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self._nodes: Dict[int, MNode] = { }
    
    
    def extract_isolation( self, inside: DNodePredicate, outside : DNodePredicate ) -> _MGraph:
        """
        A combination of `find_isolation_points` and `cut_one`.
        
        :except ValueError: More than one isolation point is found
        """
        points = self.find_isolation_points( inside, outside )
        
        if len( points ) != 1:
            raise ValueError( "Cannot extract the isolation from the graph because the specified points are not uniquely isolated." )
        
        point = points[0]
        
        return self.cut_one( point.internal_node, point.external_node )
    
    
    def find_isolation_points( self, inside: DNodePredicate, outside : DNodePredicate ) -> List[_FusionPointCandidate]:
        """
        Finds the points on the graph that separate the specified `inside` nodes from the `outside` nodes.
        
              --------I
          ----X1
          |   --------I
          |
         -X2
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
         -X2
          |           --------I
          |   --------X3
          ----X4      --------I
              |
              --------O
         
         
        :param outside:   A delegate expression yielding `True` for nodes outside the set to be separated, and `False` for all other nodes. 
        :param inside:    A delegate expression yielding `True` for nodes inside the set to be separated,  and `False` for all other nodes. 
        :return:          A list of `_FusionPointCandidate` detailing the isolation points. 
        """
        # Iterate over all the edges to make a list of `candidate` edges
        # - those separating βγδ from everything else
        candidates: List[_FusionPointCandidate] = []
        for edge in self.get_edges():
            for node in cast( Sequence[MNode], (edge.left, edge.right) ):
                params = FollowParams( root = node, exclude_edges = [edge] )
                self.follow( params )
                count = []
                
                # Count the number of fusion sequences in the subgraph
                for relative in params.visited_nodes:
                    if relative.sequence is not None:
                        count.append( relative.sequence )
                        
                        if not inside( relative ):
                            # Fusion sequence are not alone - disregard
                            count.clear()
                            break
                
                if count:
                    candidates.append( _FusionPointCandidate( edge, node, edge.opposite( node ), count ) )
        
        # Connected candidates (such as 1,2,3 in the diagram above) need to be reduced to just the one encompassing them all
        # - To do this, make a CC set of the candidates
        cc_finder = ComponentFinder()
        for candidate_1 in candidates:
            for candidate_2 in candidates:
                if candidate_1.internal_node is candidate_2.internal_node or candidate_1.external_node is candidate_2.internal_node:
                    cc_finder.join( candidate_1, candidate_2 )
        
        # - Now for each CC, just use the candidate encompassing the most composites
        fusions_refined: List[_FusionPointCandidate] = []
        tabulation: List[List[_FusionPointCandidate]] = cc_finder.tabulate()
        for component_ in tabulation:
            fusions_refined.append( max( component_, key = lambda x: x.count ) )
        
        return fusions_refined
    
    
    def cut( self, left_node: MNode, right_node: MNode ) -> Tuple[_MGraph, _MGraph]:
        """
        This is the same as `cut_one`, but returns both the left and the right halves of the cut.
        """
        left_graph = self.cut_one( left_node, right_node )
        right_graph = self.cut_one( right_node, left_node )
        return left_graph, right_graph
    
    
    def cut_one( self, internal_node: _MNode, external_node: _MNode ) -> _MGraph:
        """
        Cuts the graph along the edge between the specified nodes, yielding a new subset graph.
        
        The new subset contains `containing_node`, and all its relations, excluding those crossing `missing_node`. 
        
        Note this function accepts two nodes, rather than an edge, so that the assignment of
        `containing_node` and `missing_node` is always explicit, which wouldn't be obvious for undirected edges. 
        
        :param internal_node:     Node that will form the inside (accepted) half of the cut 
        :param external_node:     Node that will form the outside (rejected) half of the cut. 
        :return:                  The new graph
        """
        new = MGraph()
        
        fp = FollowParams( root = internal_node, exclude_nodes = [external_node] )
        self.follow( fp )
        
        for node in fp.visited_nodes:
            node.copy_into( new )
        
        for node in fp.visited_nodes:
            for edge in node.iter_edges():
                edge.copy_into( new )
        
        return new
    
    
    def find_connected_components( self ) -> List[List[_MNode]]:
        """
        Calculates and returns the list of connected components.
        """
        cf = ComponentFinder()
        
        for edge in self.get_edges():
            cf.join( edge.left, edge.right )
        
        return cast( List[List[_MNode]], cf.tabulate() )
    
    
    @classmethod
    def consensus( cls, graphs: Iterable[_MGraph] ) -> _MGraph:
        """
        Creates the consensus of two trees.
        NOTE: The graphs must be trees!
        
        :param graphs:  An iterable containing two or more graphs. 
        :return:        A new graph describing the consensus. 
        """
        raise NotImplementedError( "TODO" )
    
    
    def incorporate( self, graph: _MGraph ) -> None:
        """
        Clones an existing graph into this one.
        Note that node information and UIDs are copied, which prevents accidentally incorporating the same set of nodes twice.
        :param graph:   The graph to incorporate.
        """
        self.incorporate_nodes( graph._nodes.values() )
    
    
    def find_node( self, uid: int ) -> Optional[MNode]:
        """
        Finds the equivalent node in this graph, to one that exists in a different graph. 
        :param uid:    UID of node to find. 
        :return:        Node in this graph. 
        """
        return self._nodes.get( uid )
    
    
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
    
    
    def to_csv( self, format_str: str = "a c f" ):
        r = []
        
        for edge in self.get_edges():
            r.append( "{},{}".format( edge.left.describe( format_str ), edge.right.describe( format_str ) ) )
        
        return "\n".join( r )
    
    
    def to_ascii( self, format_str: str = "a c f" ):
        """
        Shows the graph as ASCII-art, which is actually in UTF8.
        """
        results: List[str] = []
        visited: Set[MNode] = set()
        
        while True:
            first = array_helper.first( x for x in self._nodes if x not in visited )
            
            if first is None:
                break
            
            params = FollowParams( root = first, include_repeats = True )
            self.follow( params )
            visited.update( params.exclude_nodes )
            results.extend( x.describe( format_str ) for x in params.visited )
        
        return "\n".join( results )
    
    
    def to_newick( self ) -> str:
        """
        Converts the graph to a Newick tree.
        """
        ete_tree = self.to_ete()
        return ete_tree.write( format = 1 )
    
    
    def to_ete( self ) -> TreeNode:
        """
        Converts the graph to an Ete tree.
        """
        
        
        def __recurse( m_node: MNode, ete_node: TreeNode, visited: Set ):
            visited.add( m_node )
            # noinspection PyTypeChecker
            new_ete_node = ete_node.add_child( name = m_node.describe( "a" ) )
            
            for child in m_node.iter_relations():
                if child not in visited:
                    __recurse( child, new_ete_node, visited )
            
            return ete_node
        
        
        first = array_helper.first_or_error( self._nodes )
        
        return __recurse( first, TreeNode(), set() )
    
    
    def _node_from_ete( self, tree: TreeNode, model: LegoModel ):
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
        
        for node in self._nodes:
            result.update( node.iter_edges() )
        
        return result
    
    
    def get_nodes( self ) -> "Iterator[ MNode ]":
        """
        Iterates over all the nodes.
        """
        return iter( self._nodes )
    
    
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
    """
    
    
    def __init__( self, graph: MGraph, uid: int = None ):
        """
        CONSTRUCTOR 
        """
        from groot.algorithms.fuse import FusionPoint
        
        if uid is None:
            uid = uuid4().int
        
        self.__uid: int = uid
        self._graph: MGraph = graph
        self.sequence: Optional[LegoSequence] = None
        self._edges: Dict[MNode, MEdge] = { }
        self.fusion: Optional[FusionPoint] = None
        
        graph._nodes.add( self )
    
    
    def copy_into( self, target_graph: MGraph ) -> _MNode:
        """
        Copies the node (but not the edges!)
        """
        new = MNode( target_graph, self.__uid )
        new.sequence = self.sequence
        new.fusion = self.fusion
        return new
    
    
    @property
    def uid( self ) -> int:
        return self.__uid
    
    
    def describe( self, format_str ) -> str:
        """
        Describes the nodes.
        The following format strings are accepted:
        
        `t` -   type-based description:
                    "seq:accession" for sequences
                    "fus:fusion"    for fusions
                    "cla:uid"       for nodes with neither sequences nor fusions ("clades")
        `f` -   fusion                      (or empty)
        `u` -   node     uid
        `c` -   sequence major component    (or empty)
        `m` -   sequence minor components   (or empty)
        `a` -   sequence accession          (or empty)
        `l` -   sequence length             (or empty)
        `<` -   following characters are verbatim
        `>` -   stop verbatim / skip
        `S` -   skip if not in sequence
        `F` -   skip if not in fusion
        `C` -   skip if not in clade
        `T` -   skip if in sequence
        `G` -   skip if in fusion
        `D` -   skip if in clade
        -   -   anything else is verbatim
        """
        ss = []
        verbatim = False
        skip = False
        
        for x in format_str:
            if skip:
                if x == ">":
                    skip = False
            elif verbatim:
                if x == ">":
                    verbatim = False
                else:
                    ss.append( x )
            elif x == "<":
                verbatim = True
            elif x == "S":
                skip = self.sequence is None
            elif x == "F":
                skip = self.fusion is None
            elif x == "C":
                skip = self.fusion is None
            elif x == "T":
                skip = self.sequence is not None
            elif x == "G":
                skip = self.fusion is not None
            elif x == "D":
                skip = self.fusion is not None
            elif x == "t":
                if self.sequence:
                    ss.append( "seq:{}".format( self.sequence.accession ) )
                elif self.fusion:
                    ss.append( "fus:{}:{}".format( self.fusion.opposite_component, self.fusion.count ) )
                else:
                    ss.append( "cla:{}".format( self.__uid ) )
            elif x == "f":
                if self.fusion:
                    ss.append( Theme.BOLD + str( self.fusion ) + Theme.RESET )
            elif x == "u":
                ss.append( self.__uid )
            elif x == "c":
                if self.sequence and self.sequence.component:
                    ss.append( str( self.sequence.component ) )
            elif x == "m":
                if self.sequence:
                    minor_components = self.sequence.minor_components()
                    
                    if minor_components:
                        for minor_component in sorted( minor_components, key = str ):
                            ss.append( str( minor_component ) )
            elif x == "a":
                if self.sequence:
                    ss.append( self.sequence.accession )
            elif x == "l":
                if self.sequence:
                    ss.append( self.sequence.length )
            else:
                ss.append( x )
        
        return "".join( str( x ) for x in ss ).strip()
    
    
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
        
        self._graph._nodes.remove( self )
    
    
    def iter_relations( self ) -> "Iterator[MNode]":
        """
        Iterates the node(s) connected to this node.
        """
        for edge in self.iter_edges():
            yield edge.opposite( self )


def import_name( model: LegoModel, name: str ) -> Tuple[Optional[LegoSequence], Optional[LegoComponent]]:
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
        if left is right:
            raise ValueError( "Cannot create an edge to the same node." )
        
        if right in left._edges or left in right._edges:
            raise ValueError( "Cannot add an edge from node to node because these nodes already share an edge." )
        
        self._graph = graph
        self._left = left
        self._right = right
        
        left._edges[right] = self
        right._edges[left] = self
    
    
    def copy_into( self, target_graph: MGraph ) -> Optional[_MEdge]:
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
