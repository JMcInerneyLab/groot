from typing import Callable, Iterable, Optional, Union, Sequence

import groot.utilities.external_runner
from groot import algorithms
from groot.data import LegoModel, LegoSequence, LegoSubset, LegoPoint, INamedGraph, Subgraph, LegoFormation, LegoPregraph
from groot.constants import STAGES
from groot.utilities import lego_graph, AlgorithmCollection
from mgraph import MGraph, MNode
from mhelper import Logger, SwitchError, string_helper
from mhelper.reflection_helper import FnInspect


LOG = Logger( "possible_graphs", False )

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
    
    model.subgraphs = tuple()
    model.subgraphs_destinations = tuple()
    model.subgraphs_sources = tuple()


def create_supertrees( algorithm: str, model: LegoModel ) -> None:
    """
    Creates the supertrees/subgraphs for the model.
    
    :param algorithm:   Algorithm to use. 
    :param model:       Model to generate for.
    :return:            Nothing is returned, the state is saved into the model. 
    """
    
    # Check we're ready to go
    model.get_status( STAGES.SUBGRAPHS_11 ).assert_create()
    
    # Create the subgraphs 
    subgraphs = []
    
    for subset in model.subsets:
        subgraph = algorithms.s140_supertrees.create_supertree( algorithm, subset )
        
        subgraphs.append( (subset, subgraph) )
    
    # Collect the sources and destinations
    destinations = set()
    sources = set()
    
    for subset, subgraph in subgraphs:
        sequences = lego_graph.get_sequence_data( subgraph )
        ffn = lego_graph.get_fusion_formation_nodes( subgraph )
        
        if not ffn:
            raise ValueError( "The subgraph («{}») of the subset «{}» («{}») doesn't appear to have any fusion point nodes. Refusing to continue because this means the subgraph's position in the NRFG is unavailable.".format( string_helper.format_array(subgraph.nodes), subset, string_helper.format_array(subset.contents) ) )
        
        for node in ffn:  # type:MNode
            formation: LegoFormation = node.data
            
            if any( x in sequences for x in formation.pertinent_inner ):
                destinations.add( node.uid )
            else:
                sources.add( node.uid )
    
    model.subgraphs_destinations = tuple( destinations )
    model.subgraphs_sources = tuple( sources )
    model.subgraphs = tuple( Subgraph( subgraph, subset, algorithm ) for subset, subgraph in subgraphs )


def create_supertree( algorithm: Optional[str], subset: LegoSubset ) -> MGraph:
    """
    Generates a supertree from a set of trees.
    
    :param algorithm:   Algorithm to use. See `algorithm_help`.
    :param subset:      Subset to generate consensus from 
    :return:            Consensus graph (this may be a reference to one of the input `graphs`)
    """
    # Get our algorithm
    algo = supertree_algorithms[algorithm]
    ins = FnInspect( algo )
    
    # We allow two kinds of algorithm
    # - Python - take a `LegoSubset` instance
    # - External - take a newick-formatted string
    if ins.args[0].annotation == LegoSubset:
        # Python algorithms get the subset instance
        input = subset
    else:
        # External algorithms get newick strings for each possible tree in the subset
        input_lines = __graphs_to_newick( subset.pregraphs )
        
        if __is_redundant( subset.pregraphs, input_lines ):
            return subset.pregraphs[0].graph
        
        input = "\n".join( input_lines ) + "\n"
    
    output = groot.utilities.external_runner.run_in_temporary( algo, input )
    
    if isinstance( output, MGraph ):
        result = output
    elif isinstance( output, str ):
        # We don't reclade the newick, it's pointless at this stage and we remove redundancies during the NRFG_CLEAN stage anyway 
        result = algorithms.s020_importation.import_newick( output, subset.model, reclade = False )
    else:
        raise SwitchError( "create_supertree::output", output, instance = True )
    
    # Assert the result
    # - All elements of the subset are in the supertree
    for element in subset.contents:
        if isinstance( element, LegoSequence ):
            if element in result.nodes.data:
                continue
        elif isinstance( element, LegoPoint ):
            if element.formation in result.nodes.data:
                continue
        
        raise ValueError( _MSG1.format( element,
                                        string_helper.format_array( result.nodes.data, format = lambda x: "{}:{}".format( type( x ).__name__, x ), sort = True ),
                                        type( element ).__name__ ) )
    
    # - All (non-clade) elements of the supertree are in the subset
    for node in result.nodes:
        if lego_graph.is_clade( node ):
            continue
        
        if lego_graph.is_formation( node ):
            if any( x.formation is node.data for x in subset.contents if isinstance( x, FusionPoint ) ):
                continue
        
        if lego_graph.is_sequence_node( node ):
            if node.data in subset.contents:
                continue
        
        raise ValueError( _MSG2.format( node.data,
                                        string_helper.format_array( subset.contents, format = lambda x: "{}:{}".format( type( x ).__name__, x ), sort = True ),
                                        type( node.data ).__name__ ) )
    
    return result


def __graphs_to_newick( graphs: Iterable[LegoPregraph] ):
    """
    Converts a set of pregraphs to Newick.
    """
    newick = []
    for graph in graphs:
        newick.append( algorithms.s020_importation.export_newick( graph.graph ) )
    
    return newick


def __is_redundant( graphs: Sequence[INamedGraph], input_lines: Sequence[str] ) -> bool:
    # The following two cases shouldn't be a problem in theory,
    # but CLANN crashes when it receives them, so we account for them now
    if len( graphs ) == 1:
        # * Only one input, return that
        return True
    elif all( x.graph.nodes.__len__() == 1 for x in graphs ) and set( x.graph.nodes == set( graphs[0].graph.nodes ) for x in graphs ):
        # * All graphs contain only one node and that is the same node for all graphs, return that
        return True
    
    if all( line == input_lines[0] for line in input_lines ):
        # * All graphs are the same (not a problem but we can speed things up)
        return True
    
    return False


_MSG1 = "The subset element «{}» is not to be found in the supertree data «{}» (or its type «{}» is not recognised)."
_MSG2 = "The supertree node «{}» is not to be found in the subset «{}» (or its type «{}» is not recognised)."
