from typing import Callable, Iterator, Optional, Set, Tuple, cast, Iterable, Dict, List

from ete3 import TreeNode

from groot import constants

from groot.data.lego_model import LegoComponent, LegoModel, LegoSequence
from intermake.engine.theme import Theme

from mhelper import array_helper


DFindId = Callable[[str], object]


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


class MGraph:
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self._nodes: "Set[MNode]" = set()
        self.uid_counter: int = 1
    
    
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
            r.append( "{},{}".format( edge.a.describe( format_str ), edge.b.describe( format_str ) ) )
        
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
        
        
        first = array_helper.first_unsafe( self._nodes )
        
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
    
    
    def import_graph( self, graph: "MGraph" ):
        lookup_table = { }
        
        for edge in graph.get_edges():
            a = self.__import_node( lookup_table, edge.a )
            b = self.__import_node( lookup_table, edge.b )
            MEdge( self, a, b )
        
        return lookup_table
    
    
    def __import_node( self, lookup_table: "Dict[ MNode, MNode ]", node: "MNode" ) -> "MNode":
        result = lookup_table.get( node )
        
        if result is None:
            result = MNode( self )
            result.sequence = node.sequence
            lookup_table[node] = result
        
        return result


class MNode:
    """
    Nodes of the MGraph.
    """
    
    
    def __init__( self, graph: MGraph ):
        """
        CONSTRUCTOR 
        """
        from groot.algorithms.fuse import FusionPoint
        
        if not hasattr( graph, "uid_counter" ):
            graph.uid_counter = 1
        
        self.__uid: int = graph.uid_counter
        self._graph: MGraph = graph
        self.sequence: Optional[LegoSequence] = None
        self._edges: Dict[MNode, MEdge] = { }
        self.fusion_comment: Optional[FusionPoint] = None
        
        graph._nodes.add( self )
        graph.uid_counter += 1
    
    
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
                skip = self.fusion_comment is None
            elif x == "C":
                skip = self.fusion_comment is None
            elif x == "T":
                skip = self.sequence is not None
            elif x == "G":
                skip = self.fusion_comment is not None
            elif x == "D":
                skip = self.fusion_comment is not None
            elif x == "t":
                if self.sequence:
                    ss.append( "seq:{}".format( self.sequence.accession ) )
                elif self.fusion_comment:
                    ss.append( "fus:{}:{}".format( self.fusion_comment.opposite_component, self.fusion_comment.count ) )
                else:
                    ss.append( "cla:{}".format( self.__uid ) )
            elif x == "f":
                if self.fusion_comment:
                    ss.append( Theme.BOLD + str( self.fusion_comment ) + Theme.RESET )
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
        return sorted( self._edges.values(), key = lambda x: "{}-{}".format( id( x.a ), id( x.b ) ) )
    
    
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
    def __init__( self, graph: MGraph, a: MNode, b: MNode ):
        if a is b:
            raise ValueError( "Cannot create an edge to the same node." )
        
        if b in a._edges or a in b._edges:
            raise ValueError( "Cannot add an edge from node to node because these nodes already share an edge." )
        
        self._graph = graph
        self._a = a
        self._b = b
        
        a._edges[b] = self
        b._edges[a] = self
    
    
    def remove( self ) -> None:
        del self._a._edges[self._b]
        del self._b._edges[self._a]
    
    
    def __repr__( self ) -> str:
        return "{}-->{}".format( self._a, self._b )
    
    
    @property
    def a( self ) -> MNode:
        return self._a
    
    
    @property
    def b( self ) -> MNode:
        return self._b
    
    
    def opposite( self, node: MNode ) -> MNode:
        if self._a is node:
            return self._b
        elif self._b is node:
            return self._a
        else:
            raise KeyError( "Cannot find opposite side to '{}' because that isn't part of this edge '{}'.".format( node, self ) )
    
    
    def iter_a( self ) -> Set[MNode]:
        return self._graph.follow( FollowParams( root = self._a, exclude_nodes = [self._b] ) ).exclude_nodes
    
    
    def iter_b( self ) -> Set[MNode]:
        return self._graph.follow( FollowParams( root = self._b, exclude_nodes = [self._a] ) ).exclude_nodes
