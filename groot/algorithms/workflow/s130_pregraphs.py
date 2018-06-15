from groot import constants
from intermake import MCMD, command
from mgraph import analysing
from mhelper import ComponentFinder, Logger, LogicError, string_helper
from typing import List

from groot.constants import STAGES, EChanges
from groot.data import INode, Pregraph, Subset, global_view
from groot.utilities import lego_graph


LOG = Logger( "pregraphs", False )
__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME

@command(folder = constants.F_CREATE)
def create_pregraphs():
    """
    Creates the pregraphs.
    
    Requisites: `create_subsets`
    """
    model = global_view.current_model()
    model.get_status( STAGES.PREGRAPHS_11 ).assert_create()
    
    for subset in model.subsets:
        __subset_to_possible_graphs( subset )
        __assert_recreatable( subset )
    
    return EChanges.MODEL_DATA


@command(folder = constants.F_DROP)
def drop_pregraphs():
    """
    Removes data from the model.
    """
    model = global_view.current_model()
    model.get_status( STAGES.PREGRAPHS_11 ).assert_drop()
    
    for subset in model.subsets:
        assert isinstance(subset, Subset)
        subset.pregraphs = None
        
    return EChanges.COMP_DATA


@command( names = ["print_pregraphs", "pregraphs"], folder = constants.F_PRINT )
def print_pregraphs() -> EChanges:
    """
    Prints the names of the NRFG subgraphs (you'll need to use `print_trees` to print the actual trees).
    """
    model = global_view.current_model()
    
    for subgraph in model.iter_pregraphs():
        MCMD.information( "{} = {}".format( subgraph.name, lego_graph.export_newick( subgraph.graph ) ) )
    else:
        MCMD.information( "The current model has no subgraphs." )
    
    return EChanges.INFORMATION


def __subset_to_possible_graphs( subset: Subset ):
    """
    Converts a subset of genes into the possible graphs representing these genes (1 graph per component).
    
    :remarks:
    This isn't as simple as just pulling out the genes from the component trees, we need to address the following issues:
    
    1.  Our resulting graphs might contain distinct fusions points which may, in fact, be the same.
        This causes problems in the supertree stage.
        We address this issue by coalescing identical fusions (`LegoPoint`s into `LegoFormation`s).
    2.  The "intermediaries" (the clades which hold our gene subset together to form a coherent graph)
        should generally just be boring clades, but occasionally we'll pull a fusion node into them.
        This also causes problems at the supertree stage.
        We address this issue by swapping them out these out for clades.
    """
    graphs: List[Pregraph] = []
    
    LOG( "{} :::: {}", subset, subset.contents )
    
    for component in subset.model.components:
        intermediaries = analysing.get_intermediaries( component.tree, lambda x: x.data in subset.contents )
        
        LOG( "{} :::: {}", subset, component )
        graph = component.tree.copy( nodes = intermediaries )
        
        # Hold up!
        for node in graph:
            LOG( "{} :::: {}", subset, node )
            
            if lego_graph.is_clade( node ):
                continue
            
            if lego_graph.is_fusion_point( node ):
                if node.data in subset.contents:
                    node.data = node.data.formation
                else:
                    # Substitute for clade
                    print( "SUB {}".format( node ) )
                    node.data = None
                continue
            
            if lego_graph.is_sequence_node( node ):
                if node.data in subset.contents:
                    continue
            
            raise ValueError( "Subset graph contains the node «{}», which does not appear in the actual subset «{}».".format( node, subset ) )
        
        if sum( 1 for _ in graph.nodes.roots ) > 1:
            raise LogicError( "Graph of subset has multiple roots: {}".format( string_helper.format_array( graph.nodes.roots ) ) )
        
        if graph.nodes:
            graphs.append( Pregraph( graph, subset, component ) )
    
    subset.pregraphs = tuple( graphs )


def __assert_recreatable( subset: Subset ):
    # This is a lengthy assertion, but a good one
    # - we check to make sure the trees we have created share at least
    #   1 node in common each, otherwise we can't recreate the NRFG.
    cf = ComponentFinder()
    for graph in subset.pregraphs:
        for node in graph.graph:
            if isinstance( node.data, INode ):
                cf.join( graph.graph, node.data )
    tab = cf.tabulate()
    if len( tab ) != 1:
        raise ValueError( "The subtrees do not share overlapping node sets. I would not expect any supertree algorithm to produce to a coherent tree so I am bailing out now. Operand: {}; Components: {}.".format( subset, tab ) )
