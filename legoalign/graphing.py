from typing import Set, Callable




DFindId = Callable[[str], object]

class MClade:
    pass

class MGraph:
    def __init__(self):
        self._nodes = {}
    
    
    def import_tree(self, tree : object, find : DFindId):
        """
        Imports an ETE3 tree
        :param tree:    ETE3 tree 
        :param find:    How to lookup the ID of nodes with names (nodes without names are always assigned a unique `MClade` as their ID). 
        :return:        Nothing 
        """
        from ete3 import TreeNode
        assert isinstance(tree, TreeNode)
        
        for a_list, b_list in tree.iter_edges():
            assert len(a_list) == 1, "Didn't expect a hyper-graph but this edge has more than one left: {}".format(a_list)
            assert len(b_list) == 1, "Didn't expect a hyper-graph but this edge has more than one right: {}".format(b_list)
            
            a_node = self.__make_node(a_list[0],find)
            b_node = self.__make_node(b_list[0],find)
            edge = MEdge( self, a_node, b_node )
            a_node._edges[b_node]=edge
            b_node._edges[a_node]=edge
            
            
    def __make_node(self, tree : ,find : DFindId):
        from ete3 import TreeNode
        assert isinstance(tree, TreeNode)
        
        if hasattr(tree, "tag_node"):
            if tree.name:
                id = find(tree.name)
            else:
                id = MClade()
            
            tree.tag_node = MNode( self, id )
            self._nodes[id] = tree.tag_node 
        
        return tree.tag_node
            


    def get_edges(self):
        result = set()
        
        for node in self._nodes:
            result.update(node.iter_edges())
            
        return result
    
    
    def iter_nodes(self):
        return iter( self._nodes.values() )
    
        
    def make_node(self, a : object):
        node = self._nodes.get( a )
        
        if node is None:
            node = MNode( self, a )
            self._nodes[a ] = node
            
        return node
    
    
    def make_edge(self, a : object, b : object):
        left = self.make_node(a) 
        right = self.make_node(b)
        
        edge = left._edges.get( right )
        
        if edge is None:
            edge = MEdge( self, left, right )
            left._edges[right]=edge
            right._edges[left]=edge
        
        return edge
    
    def into_set( self, source : MNode, visited : Set[MNode ] ):
        if source in visited:
            return
        
        visited.add(source)
        
        for edge in source.iter_edges():
            self.into_set(edge.opposite(source), visited)
        
        
class MNode:
    def __init__(self, graph : MGraph, id : object):
        self._graph = graph
        self._id = id
        self._edges = {}
        
    def iter_edges(self):
        return iter(self._edges)
    
class MEdge:
    def __init__( self, graph : MGraph, a : MNode, b : MNode ):
        self._graph = graph
        self._a = a
        self._b = b
        
    @property
    def a(self):
        return self._a 
    
    @property
    def b(self):
        return self._b
    
    def opposite( self, x : MNode ):
        if self._a is x:
            return self._b
        elif self._b is x:
            return self._a
        else:
            raise KeyError("Cannot find opposite side to '{}' because that isn't part of this edge '{}'.".format(x, self))
        
    def iter_a(self):
        visited = set()
        visited.add(self._b)
        self._graph.into_set(self._a, visited)
        visited.remove(self._b)
        return visited
    
    def iter_b(self):
        visited = set()
        visited.add(self._a)
        self._graph.into_set(self._b, visited)
        visited.remove(self._a)
        return visited
        