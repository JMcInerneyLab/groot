from typing import Callable, List, Optional, Union

import groot.utilities.external_runner
from groot import algorithms
from groot.constants import STAGES
from groot.data import lego_graph
from groot.data.extendable_algorithm import AlgorithmCollection
from groot.data.lego_model import LegoSubset, ILegoNode, LegoModel, NamedGraph
from mgraph import MGraph, analysing, MNode
from mhelper import LogicError, SwitchError, string_helper
from mhelper.reflection_helper import FnInspect


DAlgorithm = Callable[[Union[str, LegoSubset]], Union[str, MGraph]]
"""
Task:
    A supertree consensus is required whereby the set of taxa on the inputs may not be the same.

Input (ONE OF):
    str (default): newick trees
    LegoSubset: the gene subset in question
    
Output (ONE OF):
    str: A newick tree
    MGraph: The tree
    
Uses Pep-484 to indicate which input is required, otherwise the default will be assumed.
"""

supertree_algorithms = AlgorithmCollection[DAlgorithm]( "Supertree" )

def drop_supertrees( model: LegoModel ):
    model.get_status( STAGES.SUBGRAPHS_11 ).assert_drop()
    
    model.nrfg.minigraphs = tuple()
    model.nrfg.minigraphs_destinations = tuple()
    model.nrfg.minigraphs_sources = tuple()


def create_supertrees( algorithm: str, model: LegoModel ) -> None:
    model.get_status( STAGES.SUBGRAPHS_11 ).assert_create()
    
    subgraphs = []
    
    for subset in model.nrfg.subsets:
        subgraph = algorithms.s11_supertrees.create_supertree( algorithm, subset )
        
        subgraphs.append( subgraph )
    
    destinations = set()
    sources = set()
    for minigraph in subgraphs:
        sequences = lego_graph.get_sequence_data( minigraph )
        
        for node in lego_graph.get_fusion_nodes( minigraph ):
            assert isinstance( node, MNode )
            
            fusion_event = node.data
            if any( x in sequences for x in fusion_event.pertinent_inner ):
                destinations.add( node.uid )
            else:
                sources.add( node.uid )
                
    model.nrfg.minigraphs_destinations = tuple( destinations )
    model.nrfg.minigraphs_sources = tuple( sources )
    model.nrfg.minigraphs = tuple( NamedGraph( x, algorithm + "_{}".format( i ) ) for i, x in enumerate( subgraphs ) )
    
def create_supertree( algorithm: Optional[str], subset: LegoSubset ) -> MGraph:
    """
    Generates a supertree from a set of trees.
    
    :param algorithm:   Algorithm to use. See `algorithm_help`.
    :param subset:      Subset to generate consensus from 
    :return:            Consensus graph (this may be a reference to one of the input `graphs`)
    """
    assert isinstance( subset, LegoSubset )
    
    algo = supertree_algorithms[algorithm]
    ins = FnInspect( algo )
    
    if ins.args[0].type == LegoSubset:
        input = subset
    else:
        graphs = __subset_to_possible_graphs( subset )
        
        # The following two cases shouldn't be a problem, but CLANN crashes when it receives them, so we account for them now
        if len( graphs ) == 1:
            # Only one input, return that
            return graphs[0]
        elif all( x.nodes.__len__() == 1 for x in graphs ) and set( x.nodes == set( graphs[0].nodes ) for x in graphs ):
            # All graphs contain only one node and that is the same node for all graphs, return that
            return graphs[0]
        
        input = __graphs_to_newick( graphs )
    
    output = groot.utilities.external_runner.run_in_temporary( algo, input )
    
    if isinstance( output, MGraph ):
        result = output
    elif isinstance( output, str ):
        result = algorithms.s1_importation.import_newick( output, subset.model )
    else:
        raise SwitchError( "create_supertree::output", output, instance = True )
    
    # Assert the result
    for element in subset.contents:
        if element not in result.nodes.data:
            raise ValueError( "The subset element «{}» is not to be found in the supertree.".format( element ) )
    
    for node in result.nodes:
        if isinstance( node.data, ILegoNode ) and node.data not in subset.contents:
            raise ValueError( "The supertree node «{}» is not to be found in the requested subset «{}».".format( node.data, subset.contents ) )
        
    return result


def __graphs_to_newick( graphs ):
    newick = []
    for graph in graphs:
        newick.append( algorithms.s1_importation.export_newick( graph ) )
    input = "\n".join( newick ) + "\n"
    return input


def __subset_to_possible_graphs( subset: LegoSubset ):
    graphs: List[MGraph] = []
    for component in subset.model.components:
        intermediaries = analysing.get_intermediaries( component.tree, lambda x: x.data in subset.contents )
        
        graph = component.tree.copy( nodes = intermediaries )
        
        if sum( 1 for _ in graph.nodes.roots ) > 1:
            raise LogicError( "Graph of subset has multiple roots: {}".format( string_helper.format_array( graph.nodes.roots ) ) )
        
        if graph.nodes:
            graphs.append( graph )
    return graphs


