import os
import shutil
from itertools import chain
from typing import List, Optional, Callable
from uuid import uuid4

from Bio.Phylo import BaseTree
from Bio.Phylo.BaseTree import Clade

import networkx
from Bio import Phylo
from matplotlib import pyplot

from MHelper.ArrayHelper import Single
from MHelper import ExceptionHelper, FileHelper
from legoalign.LegoModels import LegoComponent, LegoModel, LegoSequence, LOG


def process_create_tree( model, component: LegoComponent ):
    """
    Creates a tree from the component.
    """
    try:
        # noinspection PyUnresolvedReferences
        from MHelper import BioHelper
        # noinspection PyUnresolvedReferences
        from Bio import Phylo
    except ImportError:
        raise ImportError( "Install BioPython if you want to generate NRFGs." )
    
    fasta = component.to_fasta( simplify = True )
    
    temp_folder_name = "legoalign-temporary-folder"
    
    if os.path.exists( temp_folder_name ):
        shutil.rmtree( temp_folder_name )
    
    FileHelper.create_directory( temp_folder_name )
    
    os.chdir( temp_folder_name )
    
    uid = component.index
    in_file_name = "temp_{}_in.fasta".format( uid )
    out_file_name = "temp_{}_out.fasta".format( uid )
    phy_file_name = "temp_{}_out.phy".format( uid )
    raxml_file_extension = "t{}".format( uid )
    RAXML_BEST_FILE_NAME = "RAxML_bestTree." + raxml_file_extension  # NOT MODIFYABLE
    
    alignment_command = "muscle -in " + in_file_name + " -out " + out_file_name
    
    FileHelper.write_all_text( in_file_name, fasta )
    ExceptionHelper.run_subprocess( alignment_command )
    
    BioHelper.convert_file( out_file_name, phy_file_name, "fasta", "phylip" )
    
    tree_command = "raxml -m PROTGAMMAWAG -p 1 -s {} -# 20 -n {}".format( phy_file_name, raxml_file_extension)
    ExceptionHelper.run_subprocess( tree_command )
    
    component.tree = FileHelper.read_all_text( RAXML_BEST_FILE_NAME )
    
    for sequence in component.all_sequences():
        if "?" not in sequence.array:
            component.tree = component.tree.replace( "S{}:".format( sequence.id ), sequence.accession + ":" )
    
    # clean up
    os.chdir( ".." )
    shutil.rmtree( temp_folder_name )


class MyNode:
    COMPOSITE_COLOURS = "#FFC080", "#FFC080", "#FFC080"
    CLADE_COLOURS = "#FF0000", "#00FF00", "#0000FF"
    SEQUENCE_COLOURS = "#FFC0C0", "#C0FFC0", "#C0C0FF"
    
    def __init__( self, component : LegoComponent, name, is_clade, sequence : Optional[LegoSequence] ):
        self.component = component
        self.name = name
        self.is_clade = is_clade
        self.is_composite = False
        self.sequence = sequence
    
    
    def __str__( self ):
        return "{}/{}".format(self.component, self.name)
    
    
    def colour( self ):
        index = self.component.index % len( self.COMPOSITE_COLOURS )
        
        if self.is_composite:
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

def __phylo_to_networkx( model: LegoModel, graph : networkx.DiGraph, phylo_node, nodes, candidates : Optional[List[MyNode]], candidate : Optional[MyNode ], component : LegoComponent ):
    """
    Converts a phylogeny to networkx.
    :param model:           The model we are working with 
    :param graph:           The graph to write into
    :param phylo_node:      The root of the phylogeny (arbitrary)
    :param nodes:           The set of visited nodes (starts out empty)
    :param candidates:      Set of potential candidates to merge the tree on (starts out empty). `None` if the candidate has already been chosen. 
    :param candidate:       The candidate to merge the tree on (if `candidates` is `None`, otherwise unused). 
    :return:                Nothing 
    """
    # Note: Phylo.to_networkx seems broken (it treats all clades as one), hence use our own.
    
    if phylo_node.name is None:
        # 
        # This is a clade
        # It is always unique
        # 
        LOG("CLADE {}".format(phylo_node.name))
        the_node = MyNode( component, uuid4(), True, None )
        nodes[object()] = the_node
    else:
        #
        # This is a sequence
        # It is always unique when `candidates` and `candidate` is `None`
        # When `candidates` is a list we add potential overlaps to `candidates`
        # When `candidate` is not `None` we accept `candidate` as an overlap and reject other overlaps
        #
        if candidates is not None or candidate is not None:
            the_node = nodes.get( phylo_node.name )
            
            if the_node is None:
                # New node
                LOG("UNSEEN {}".format(phylo_node.name))
                the_node = MyNode( component, phylo_node.name, False, model.find_sequence(phylo_node.name) )
                nodes[ phylo_node.name ] = the_node
            elif candidates is not None:
                # Collecting candidates
                LOG("POTENTIAL CANDIDATE {}".format(phylo_node.name))
                candidates.append(the_node)
            elif candidate is not None and the_node.name == candidate.name:
                    LOG("ACCEPTED CANDIDATE {}".format(phylo_node.name))
                    the_node.is_composite = True
            else:
                # Is not the only permissible composite
                LOG("REJECTED CANDIDATE {}".format(phylo_node.name))
                the_node = None
        else:
            the_node = MyNode( component, phylo_node.name, False, model.find_sequence(phylo_node.name) )
            nodes[object()] = the_node
        
    if the_node is not None:
        graph.add_node( the_node )
    
    for x in phylo_node.clades:  # type: Clade
        edge_node = __phylo_to_networkx( model, graph, x, nodes, candidates, candidate, component )
        
        if the_node is not None and edge_node is not None:
            graph.add_edge( the_node, edge_node, length = x.branch_length )
    
    return the_node


def __distance_to( graph : networkx.DiGraph, candidate : MyNode ) -> int:
    """
    Given the `candidate`, what is the shortest path to a node represents a sequence that is *not* a composite.
    :param graph:               The graph 
    :param candidate:           The candidate to check
    """
    shortest_path = __breadth_first_search( candidate, graph, match = lambda x: not x.is_clade and not x.sequence.is_composite )
    
    if shortest_path is None:
        return -1
    
    LOG("SHORTEST PATH IS: {}".format(", ".join(str(x) for x in shortest_path)))
    
    return len(shortest_path)


def __breadth_first_search( start : MyNode, graph : networkx.DiGraph, match : Callable[[MyNode],bool] ) -> Optional[List[MyNode]]:
    """
    Performs a breadth-first-search of `graph` starting from `start` for something that returns `true` given `match(node)`
    :return: Path from `start` to target, as a list. `None` if no match was found.
    """
    queue = [ [ start ] ]  #type: List[List[MyNode]]
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


def process_trees( model: LegoModel, roots : List[LegoSequence], fuse: bool ):
    """
    Creates the tree diagram
    :param model:   Model 
    :param roots:   Roots to use 
    :param fuse:    Whether to fuse the trees 
    :return: 
    """
    #
    # Create individual phylogenies
    #
    trees = []
    counter = Single()
    
    for component in sorted(model.components, key = lambda x: not x.is_composite):
        tree = __component_to_phylo( component )
        trees.append((component, tree))
        print( "***********" + str( component ) )
        Phylo.draw_ascii( tree )
    
    if fuse:
        #
        # Collect candidates
        #
        individual_graphs = [] #type: List[networkx.DiGraph()]
        candidates = [] #type: List[MyNode]
        visited_dict = {}
        
        for component, tree in trees:
            with LOG("COMPONENT {}".format(component)):
                graph = networkx.DiGraph()
                __phylo_to_networkx( model, graph, tree.root, visited_dict, candidates, None, component )
                
                if not component.is_composite:
                    individual_graphs.append(graph)
        
        #
        # Find best candidate
        #
        best_candidate = None
        best_dist = 0
        
        LOG("{} CANDIDATES.".format(len(candidates)))
        
        for candidate in candidates:
            with LOG("CANDIDATE {}".format(candidate)):
                num_components = sum(candidate.sequence in component.all_sequences() for component in model.components)
                
                if num_components == len(model.components):
                    dist_to = sum(__distance_to(graph, candidate) for graph in individual_graphs)
                    LOG("DISTANCE IS {}".format(dist_to))
                    
                    if candidate.sequence in roots:
                        dist_to += 1000
                    
                    if dist_to != -1 and dist_to > best_dist:
                        best_candidate = candidate
                        best_dist = dist_to
                else:
                    LOG("DOES NOT SPAN ALL COMPONENTS")
        
        if best_candidate is None:
            raise ValueError("Cannot find a suitable candidate.")
    else:
        best_candidate = None
    
    #
    # Create final graph with candidate as merge-point
    #
    graph = networkx.DiGraph()
    visited_dict = {}
        
    for component, tree in trees:
        with LOG("COMPONENT {}".format(component)):
            __phylo_to_networkx( model, graph, tree.root, visited_dict, None, best_candidate, component )

    #
    # Set the graph roots
    #
    __set_roots( graph, roots, best_candidate.name if best_candidate else None )
                
    #
    # Draw the graph
    #
    from networkx.drawing.nx_pydot import pydot_layout
    positions = pydot_layout( graph, prog = 'dot' if roots else 'neato' )
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
    smallest = min(edge_labels.values())
    edge_labels = dict( (k, "{0}".format(int( v/smallest ))) for k, v in edge_labels.items() )
    
    networkx.draw_networkx_edge_labels( G = graph,
                                        pos = positions,
                                        edge_labels = edge_labels,
                                        font_family = "Courier",
                                        font_size = 8,
                                        font_color = "#008000")
    
    #pyplot.show()


def __set_roots( graph, roots, candidate_name ):
    visited = set()
    
    def follow( child : MyNode, parent : Optional[MyNode ], is_composite ):
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
            
    for root_node in [ __find_node( graph, root.accession ) for root in roots]:
        with LOG("FOLLOW {}".format(root_node.name)):
            follow( root_node, None, False )
            
    if candidate_name is not None:
        follow(__find_node(graph, candidate_name), None, True)


def __find_node( graph, name ):
    root_node = None
    for node in graph.nodes_iter():
        assert isinstance( node, MyNode )
        if not node.is_clade and node.name == name:
            root_node = node
            break
    if root_node is None:
        raise ValueError( "The sequence '{}' is specified as a root, but a node representing that sequence does not exist in the graph.".format( name ) )
    return root_node


def __component_to_phylo( component ):
    temp_file_name = "temporary.new"
    FileHelper.write_all_text( temp_file_name, component.tree )
    tree = Phylo.read( temp_file_name, "newick" )  # type: BaseTree.Tree
    os.remove( temp_file_name )
    return tree
