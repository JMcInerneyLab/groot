import os
import shutil
from enum import Enum
from itertools import chain
from typing import List, Optional, Callable
from uuid import uuid4

from Bio.Phylo import BaseTree
from Bio.Phylo.BaseTree import Clade
from Bio import Phylo
from Bio.Phylo.Consensus import strict_consensus

import networkx
from networkx import DiGraph

from mhelper.LogHelper import Logger
from mhelper.ExceptionHelper import SwitchError
from mhelper import ExceptionHelper, FileHelper

from legoalign.LegoModels import LegoSsComponent, LegoModel, LegoSequence

LOG = Logger(True)

class ERoot(Enum):
    """
    Root methods.
    
    `NONE`
        Don't root.
        
    `ROOTED`
        Root on provided roots.
    """
    NONE = 0
    ROOTED = 1


class EFuse(Enum):
    """
    Fuse methods.
    
    :attr NONE:
        Don't fuse.
        See `__fuse_none`.
        
    :attr XYZ:
        Fuse X, Y and Z trees (my original method)
        See `__fuse_xyz`
        
    :attr XY:
        Fuse X and Y trees, and create a consensus Z tree (James's suggested improvement)
        See `__fuse_xy`
    """
    NONE = 0
    XYZ = 1
    XY = 2



    
def fuse_trees( model: LegoModel, root_mode : ERoot, fuse_mode: EFuse ):
    """
    Creates the tree diagram by fusing existing trees.
    
    :param model:       Model 
    :param root_mode:   See `ERoot` 
    :param fuse_mode:   See `EFuse` 
    :return:            Nothing - the result is plotted to the current `pyplot` figure. 
    """
    #
    # Create individual phylogenies
    #
    trees = []
    
    for component in sorted( model.subsequence_components, key = lambda x: not x.is_composite ):
        tree = __component_to_phylo( component )
        trees.append(tree)
    
    if fuse_mode == EFuse.NONE:
        graph = __fuse_none( model, trees, root_mode )
    elif fuse_mode == EFuse.XYZ:
        graph = __fuse_xyz( model, trees, root_mode )
    elif fuse_mode == EFuse.XY:
        graph = __fuse_xy( model, trees, root_mode )
    else:
        raise SwitchError("fuse_mode", fuse_mode)
    
    #
    # Draw the graph
    #
    from networkx.drawing.nx_pydot import pydot_layout
    positions = pydot_layout( graph, prog = 'dot' if (root_mode == ERoot.ROOTED) else 'neato' )
    networkx.draw_networkx( G = graph,
                            pos = positions,
                            with_labels = True,
                            node_color = [ x.colour() for x in graph ],
                            labels = dict( (x, x.label()) for x in graph ),
                            font_size = 8,
                            font_family = "Courier",
                            font_color = (0, 0, 1),
                            node_shape = "s",
                            edge_color = "#00FF00" )
    
    edge_labels = networkx.get_edge_attributes( graph, "length" )
    smallest = min(x if isinstance(x, float) else 1 for x in edge_labels.values())
    edge_labels = dict( (k, "{0}".format(int( v/smallest ) if isinstance(v, float) else "?")) for k, v in edge_labels.items() )
    
    networkx.draw_networkx_edge_labels( G = graph,
                                        pos = positions,
                                        edge_labels = edge_labels,
                                        font_family = "Courier",
                                        font_size = 8,
                                        font_color = "#008000")
    
    #pyplot.show()



class _MyNode:
    # Colours, comp. index: 1    ,  2       ,  3
    COMPOSITE_COLOURS = "#FFC080", "#FFC080", "#FFC080"
    CLADE_COLOURS     = "#FF0000", "#00FF00", "#0000FF"
    SEQUENCE_COLOURS  = "#FFC0C0", "#C0FFC0", "#C0C0FF"
    
    def __init__( self, component : LegoSsComponent, name, is_clade, sequence : Optional[LegoSequence ] ):
        self.component = component
        self.name = name
        self.is_clade = is_clade
        self.is_composite = False
        self.sequence = sequence
        self.is_destroyed = False
        
    def destroy(self):
        self.is_destroyed = True
    
    
    def __str__( self ):
        return "{}/{}".format(self.component, self.name)
    
    
    def colour( self ):
        if self.component is not None:
            index = self.component.index % len( self.COMPOSITE_COLOURS )
        else:
            index = len(self.COMPOSITE_COLOURS)-1
        
        if self.is_destroyed:
            return "#D0D0D0"
        elif self.is_composite:
            return self.COMPOSITE_COLOURS[index ]
        elif self.is_clade:
            return self.CLADE_COLOURS[index]
        else:
            return self.SEQUENCE_COLOURS[index ]
    
    
    def label( self ):
        if self.is_clade:
            return ""
        else:
            return self.name

def __find_by_name(graph : DiGraph, name : str):
    for x in graph.nodes(): #type: _MyNode
        if x.name == name:
            return x
        
    raise KeyError(name)


def __distance_to( graph : DiGraph, node_name : str ) -> int:
    """
    Given the `candidate`, what is the shortest path to a node represents a sequence that is *not* a composite.
    :param graph:               The graph 
    :param node_name:           The candidate to check
    """
    candidate_node = __find_by_name( graph, node_name )
    shortest_path = __breadth_first_search( candidate_node, graph, match = lambda x: not x.is_clade and not x.sequence.is_composite )
    
    if shortest_path is None:
        return -1
    
    LOG("SHORTEST PATH IS: {}".format(", ".join(str(x) for x in shortest_path)))
    
    return len(shortest_path)


def __breadth_first_search( start : _MyNode, graph : DiGraph, match : Callable[ [ _MyNode ], bool ] ) -> Optional[List[_MyNode ] ]:
    """
    Performs a breadth-first-search of `graph` starting from `start` for something that returns `true` given `match(node)`
    :return: Path from `start` to target, as a list. `None` if no match was found.
    """
    queue = [ [ start ] ]  #type: List[List[_MyNode]]
    visited = set()
    while queue:
        path = queue.pop( 0 )
        final = path[ -1 ]
        connected = chain.from_iterable( graph.in_edges( final ) + graph.out_edges( final ) )
        
        for node in connected:
            if node in visited:
                continue
            
            visited.add( node )
            
            if match( node ):
                return path + [node]
            
            queue.append( path + [ node ] )
            
    return None




def __fuse_none( model: LegoModel, trees: List[ _FITree ], root_mode: ERoot ) -> DiGraph:
    """
    See `EFuse`.
    """
    maker = TreeMaker( model )
    
    for tree in trees:
        with LOG( "COMPONENT {}".format( tree.ex_component ) ):
            maker.commit( tree )
    
    if root_mode == ERoot.ROOTED:
        __set_roots( maker.graph, model, None )
    
    return maker.graph


def __fuse_xyz( model: LegoModel, trees: List[ _FITree ], root_mode: ERoot ):
    """
    See `EFuse`.
    """
    merge_point, _ = __find_best_merge_point( model, trees )
    
    maker = TreeMaker( model )
    maker.merge.only( [ merge_point ])
    
    for tree in trees:
        with LOG( "COMPONENT {}".format( tree.ex_component ) ):
            maker.commit( tree )
    
    if root_mode == ERoot.ROOTED:
        __set_roots( maker.graph, model, [merge_point] )
    
    return maker.graph


def __fuse_xy( model: LegoModel, trees: List[ _FITree ], root_mode: ERoot ) -> DiGraph:
    """
    See `EFuse`.
    """
    # Consensus tree
    new_trees = [ ]
    
    for tree in trees:
        if not tree.ex_component.is_composite:
            new_trees.append( tree )
    
    consensus_tree = strict_consensus( new_trees )
    consensus_tree.ex_component = None
    new_trees.append(consensus_tree)
    
    # Merge point
    merge_point, duplicates = __find_best_merge_point( model, new_trees )
    
    # Final tree
    maker = TreeMaker( model )
    
    # Generate the composite part first
    permitted = [x.accession for x in model.sequences if x.is_composite]
    
    if merge_point not in permitted:
        permitted.append(merge_point)
    
    maker.allow.only( permitted )
    maker.merge.only([merge_point])
    LOG("ALLOW = {}".format(maker.allow))
    LOG("MERGE = {}".format(maker.merge))
    
    
    for tree in new_trees:
        if tree.ex_component is None:
            with LOG( "COMPONENT {}".format( tree.ex_component ) ):
                maker.commit( tree )
                
    # Then generate the non-composite part
    permitted = [x.accession for x in model.sequences if not x.is_composite]
    
    if merge_point not in permitted:
        permitted.append(merge_point)
    
    maker.allow.only( permitted )
    LOG("ALLOW = {}".format(maker.allow))
    LOG("MERGE = {}".format(maker.merge))
                
    for tree in new_trees:
        if tree.ex_component is not None:
            with LOG( "COMPONENT {}".format( tree.ex_component ) ):
                maker.commit( tree )
    
    if root_mode == ERoot.ROOTED:
        __set_roots( maker.graph, model, [merge_point] )
    
    return maker.graph


class TreeFilter:
    def __init__(self):
        self.match = True
        self.values = None
        
    def invert(self):
        self.match = not self.match
        
    def test(self, value):
        if self.values is None:
            return self.match
        elif self.match:
            return value in self.values
        else:
            return value not in self.values
        
    def all(self):
        self.values = None
        self.match = None
    
    def only(self, values = None):
        if values is not None:
            self.set_values (values)
            
        self.match = True
        
    def except_( self, values = None ):
        if values is not None:
            self.set_values (values)
            
        self.match = False
        
    def __str__(self):
        if self.values is None:
            return "all" if self.match else "none"
        elif self.match:
            return "only: {}".format(self.values)
        else:
            return "except: {}".format(self.values)


    def set_values( self, values ):
        self.values = list(values)
        
        if self.values:
            for x in self.values:
                assert isinstance(x, str) 


class TreeMaker:
    
    def __init__(self, model: LegoModel):
        """
        
        :param model:                    The model we are working with
        """
        self.__model = model
        self.graph = DiGraph()
        self.__visited_nodes = {}
        self.merge = TreeFilter()
        self.merge.invert()
        self.__current_component = None
        self.duplicates = set()
        self.allow = TreeFilter()
            
        
    def commit( self, tree : _FITree ):
        """
        Adds a phylogeny tree into an existing Network-x diagram.
        """
        with LOG("COMMITTING TREE ''".format(tree.ex_component or "consensus")):
            self.__current_component = tree.ex_component
            self.__commit(tree.root)
        
    def __commit( self, phylo_node : Clade ) -> Optional[_MyNode]:
        """
        Implementation of `commit`. 
        """
        # Note: Phylo.to_networkx seems broken (it treats all clades as one), hence use our own.
        
        if not phylo_node.name:
            # 
            # This is a numbered clade
            #
            # Clades are _always_ unique
            # 
            LOG("CLADE {}".format(phylo_node.name))
            the_node = _MyNode( self.__current_component, uuid4(), True, None )
        else:
            #
            # This is a sequence
            #
            # It is always unique when `duplicate_output` and `merge_on` is `None`
            # When `duplicate_output` is a list we add potential overlaps to `duplicate_output`
            # When `merge_on` is not `None` we accept `merge_on` as an overlap and reject other overlaps
            #
            if not self.allow.test(phylo_node.name):
                LOG("REJECTING '{}'".format(phylo_node.name))
                return None
            
            existing_node = self.__visited_nodes.get( phylo_node.name )  # type: _MyNode
            the_node = None
            
            if existing_node is not None:
                self.duplicates.add(phylo_node.name)
                
                if self.merge.test(phylo_node.name):
                    LOG("MERGING '{}'".format(phylo_node.name))
                    the_node = existing_node
                    
            if the_node is None: 
                LOG("ADDING '{}'".format(phylo_node.name))
                the_node = _MyNode( self.__current_component, phylo_node.name, False, self.__model.find_sequence( phylo_node.name ) )
                self.__visited_nodes[phylo_node.name ]= the_node
                self.graph.add_node( the_node )
        
        for relation in phylo_node.clades:  # type: Clade
            relation_node = self.__commit( relation )
            
            if the_node is not None and relation_node is not None:
                self.graph.add_edge( the_node, relation_node, length = relation.branch_length )
        
        return the_node


def __set_roots( graph, model : LegoModel, candidate_names : Optional[List[str]]):
    visited = set()
    
    def follow( child : _MyNode, parent : Optional[_MyNode ], is_composite ):
        LOG( "FOLLOWING {} TO {}".format( parent.name if parent is not None else "ROOT", child.name ) )
        
        
        
        if parent is not None:
            if child.is_composite and not is_composite:
                return
            
            if child.sequence is not None and child.sequence.is_composite != is_composite:
                return
            
        if child in visited:
            return
        
        visited.add(child)
        
        for src, dst in graph.in_edges( child ):
            assert dst is child
            if src is not parent:
                graph.remove_edge( src, dst )
                graph.add_edge( dst, src )
        
        for src, dst in graph.out_edges( child ):
            assert src is child
            assert dst is not child
            follow( dst, child, is_composite )
            
    roots = [x for x in model.sequences if x.is_root]
            
    for root_node in [ __find_node( graph, root.accession ) for root in roots]:
        with LOG("FOLLOW {}".format(root_node.name)):
            follow( root_node, None, False )
            
    if candidate_names:
        for candidate_name in candidate_names:
            follow(__find_node(graph, candidate_name), None, True)


def __find_node( graph, name ):
    root_node = None
    for node in graph.nodes_iter():
        assert isinstance( node, _MyNode )
        if not node.is_clade and node.name == name:
            root_node = node
            break
    if root_node is None:
        raise ValueError( "The sequence '{}' is specified as a root, but a node representing that sequence does not exist in the graph.".format( name ) )
    return root_node


def __component_to_phylo( component ) -> _FITree:
    temp_file_name = "temporary.new"
    FileHelper.write_all_text( temp_file_name, component.tree )
    tree = Phylo.read( temp_file_name, "newick" )  # type: BaseTree.Tree
    os.remove( temp_file_name )
    fi_tree = tree #type: _FITree
    fi_tree.ex_component = component
    return fi_tree

def __find_best_merge_point( model, trees ):
    #
    # Collect candidates
    #
    individual_graphs = [ ]  # type: List[DiGraph()]
    maker = TreeMaker( model )
    for tree in trees:
        with LOG( "COMPONENT {}".format( tree.ex_component ) ):
            maker.graph = DiGraph()
            maker.commit( tree )
            
            if tree.ex_component is not None and not tree.ex_component.is_composite:
                individual_graphs.append( maker.graph )
    
    #
    # Find best candidate
    #
    best_candidate = None
    best_dist = 0
    if not maker.duplicates:
        raise ValueError( "No suitable nodes are available to act as the merge-point. Make sure your components contain at least one overlapping node. This error may indicate that you do not have any composite sequences, if this is the case then use a standard tree generator, rather than a composite one." )
    LOG( "{} CANDIDATES.".format( len( maker.duplicates ) ) )
    for duplicate_name in maker.duplicates:
        with LOG( "CANDIDATE {}".format( duplicate_name ) ):
            sequence = model.find_sequence( duplicate_name )
            num_components = sum( sequence in component.all_sequences() for component in model.components )
            
            if num_components == len( model.components ):
                dist_to = sum( __distance_to( graph, duplicate_name ) for graph in individual_graphs )
                LOG( "DISTANCE IS {}".format( dist_to ) )
                
                if sequence.is_root:
                    dist_to += 1000
                
                if dist_to != -1 and dist_to > best_dist:
                    best_candidate = duplicate_name
                    best_dist = dist_to
            else:
                LOG( "DOES NOT SPAN ALL COMPONENTS" )
    if best_candidate is None:
        raise ValueError( "Cannot find a suitable node to act as the merge-point. The nodes considered for the merger were: {}.".format( maker.duplicates ) )
    
    LOG("THE PROPOSED MERGE POINT IS '{}'".format(best_candidate))
    
    return best_candidate, maker.duplicates