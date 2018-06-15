from intermake import MCMD, command
from mgraph import MGraph, MNode
from mhelper import Logger, SwitchError, string_helper, FunctionInspector
from typing import Callable, Iterable, Sequence, Union

import groot.utilities.external_runner
from groot import constants
from groot.constants import STAGES, EChanges
from groot.data import INamedGraph, Formation, Point, Pregraph, Subset, Subgraph, global_view, Gene
from groot.utilities import AlgorithmCollection, lego_graph


LOG = Logger( "possible_graphs", False )
__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME

DAlgorithm = Callable[[Union[str, Subset]], Union[str, MGraph]]
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

supertree_algorithms = AlgorithmCollection( DAlgorithm, "Supertree" )


@command( folder = constants.F_CREATE )
def create_supertrees( algorithm: supertree_algorithms.Algorithm ) -> None:
    """
    Creates the supertrees/subgraphs for the model.
    
    Requisites: `create_pregraphs`
    
    :param algorithm:   Algorithm to use, see `algorithm_help`.
    :return:            Nothing is returned, the state is saved into the model. 
    """
    
    # Check we're ready to go
    model = global_view.current_model()
    model.get_status( STAGES.SUBGRAPHS_11 ).assert_create()
    
    # Create the subgraphs 
    subgraphs = []
    
    for subset in model.subsets:
        subgraph = __create_supertree( algorithm, subset )
        
        subgraphs.append( (subset, subgraph) )
    
    # Collect the sources and destinations
    destinations = set()
    sources = set()
    
    for subset, subgraph in subgraphs:
        sequences = lego_graph.get_sequence_data( subgraph )
        ffn = lego_graph.get_fusion_formation_nodes( subgraph )
        
        if not ffn:
            raise ValueError( "The subgraph («{}») of the subset «{}» («{}») doesn't appear to have any fusion point nodes. Refusing to continue because this means the subgraph's position in the NRFG is unavailable.".format( string_helper.format_array( subgraph.nodes ), subset, string_helper.format_array( subset.contents ) ) )
        
        for node in ffn:  # type:MNode
            formation: Formation = node.data
            
            if any( x in sequences for x in formation.pertinent_inner ):
                destinations.add( node.uid )
            else:
                sources.add( node.uid )
    
    model.subgraphs_destinations = tuple( destinations )
    model.subgraphs_sources = tuple( sources )
    model.subgraphs = tuple( Subgraph( subgraph, subset, repr( algorithm ) ) for subset, subgraph in subgraphs )
    
    return EChanges.MODEL_DATA


@command( folder = constants.F_DROP )
def drop_supertrees() -> EChanges:
    """
    Removes data from the model.
    """
    model = global_view.current_model()
    model.get_status( STAGES.SUBGRAPHS_11 ).assert_drop()
    
    model.subgraphs = tuple()
    model.subgraphs_destinations = tuple()
    model.subgraphs_sources = tuple()
    
    return EChanges.MODEL_DATA


@command( names = ["print_supertrees", "supertrees"], folder = constants.F_PRINT )
def print_supertrees() -> EChanges:
    """
    Prints the names of the NRFG subgraphs (you'll need to use `print_trees` to print the actual trees).
    """
    model = global_view.current_model()
    
    for subgraph in model.subgraphs:
        MCMD.information( "{} = {}".format( subgraph.name, lego_graph.export_newick( subgraph.graph ) ) )
    else:
        MCMD.information( "The current model has no subgraphs." )
    
    return EChanges.INFORMATION


def __create_supertree( algorithm: supertree_algorithms.Algorithm, subset: Subset ) -> MGraph:
    """
    Generates a supertree from a set of trees.
    
    :param algorithm:   Algorithm to use. See `algorithm_help`.
    :param subset:      Subset of genes from which we generate the consensus from 
    :return:            The consensus graph (this may be a reference to one of the input `graphs`)
    """
    # Get our algorithm
    ins = FunctionInspector( algorithm.function )
    
    # We allow two kinds of algorithm
    # - Python algorithms, which takes a `LegoSubset` instance
    # - External algorithms, which takes a newick-formatted string
    if ins.args[0].annotation == Subset:
        # Python algorithms get the subset instance
        input = subset
    else:
        # External algorithms get newick strings for each possible tree in the subset
        input_lines = __graphs_to_newick( subset.pregraphs )
        
        if __is_redundant( subset.pregraphs, input_lines ):
            return subset.pregraphs[0].graph
        
        input = "\n".join( input_lines ) + "\n"
    
    # Run the algorithm!
    output = groot.utilities.external_runner.run_in_temporary( algorithm, input )
    
    # We allow two types of result
    # - `MGraph` objects
    # - `str` objects, which denote a newick-formatted string
    if isinstance( output, MGraph ):
        result = output
    elif isinstance( output, str ):
        # We don't reclade the newick, it's pointless at this stage and we remove redundancies during the NRFG_CLEAN stage anyway 
        result = lego_graph.import_newick( output, subset.model, reclade = False )
    else:
        raise SwitchError( "create_supertree::output", output, instance = True )
    
    # Assert the result
    # - All elements of the subset are in the supertree
    for element in subset.contents:
        if isinstance( element, Gene ):
            if element in result.nodes.data:
                continue
        elif isinstance( element, Point ):
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
            if any( x.formation is node.data for x in subset.contents if isinstance( x, Point ) ):
                continue
        
        if lego_graph.is_sequence_node( node ):
            if node.data in subset.contents:
                continue
        
        raise ValueError( _MSG2.format( node.data,
                                        string_helper.format_array( subset.contents, format = lambda x: "{}:{}".format( type( x ).__name__, x ), sort = True ),
                                        type( node.data ).__name__ ) )
    
    return result


def __graphs_to_newick( graphs: Iterable[Pregraph] ):
    """
    Converts a set of pregraphs to Newick.
    """
    newick = []
    for graph in graphs:
        newick.append( lego_graph.export_newick( graph.graph ) )
    
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
