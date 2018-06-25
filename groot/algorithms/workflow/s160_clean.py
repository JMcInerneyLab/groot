from groot.constants import STAGES, EChanges
from groot.data import EPosition, FusionGraph, Formation, Point, Gene, global_view
from groot.utilities import lego_graph
from groot import constants
from intermake import command
from mgraph import MGraph, MNode, analysing
from mhelper import Logger, LoopDetector, SwitchError


LOG = Logger( "clean", False )
__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME


@command( folder = constants.F_CREATE )
def create_cleaned():
    """
    Cleans the NRFG.
    
    Requisites: `create_fused`
    """
    model = global_view.current_model()
    model.get_status( STAGES.CLEANED_13 ).assert_create()
    nrfg = model.fusion_graph_unclean.graph.copy()
    
    __remove_redundant_fusions( nrfg )
    __remove_redundant_clades( nrfg )
    __make_fusions_rootlets( nrfg )
    __make_outgroup_parents_roots( nrfg )
    
    model.fusion_graph_clean = FusionGraph( nrfg, True )
    return EChanges.MODEL_DATA


@command( folder = constants.F_DROP )
def drop_cleaned():
    """
    Removes data from the model.
    """
    model = global_view.current_model()
    model.get_status( STAGES.CLEANED_13 ).assert_drop()
    
    model.fusion_graph_clean = None
    return EChanges.MODEL_DATA


def __make_outgroup_parents_roots( nrfg: MGraph ) -> None:
    """
    Finally, nodes explicitly flagged as roots or outgroups should be made so
    We don't "reclade" the nodes here (i.e. (A,B,C) becomes A->B and A->C and not A,(B,C)
    as earlier, because the intermediate clades should already be present
    """
    LOG( "Fixing outgroups..." )
    
    for node in nrfg:
        if isinstance( node.data, Gene ) and node.data.position != EPosition.NONE:
            if node.data.position == EPosition.OUTGROUP:
                # We call "make root" and not "make outgroup" because the network should
                # already have the right topology, we just need to adjust the directions
                LOG( "Make outgroup: {}".format( node ) )
                LOG( "--i.e. make root: {}".format( node.relation ) )
                node.relation.make_root( node_filter = lambda x: not lego_graph.is_fusion_like( x ), ignore_cycles = True )
            else:
                raise SwitchError( "node.data.position", node.data.position )


def __make_fusions_rootlets( nrfg: MGraph ) -> None:
    """
    Make sure our fusion nodes act as roots to their creations and leaves to their creators
    """
    LOG( "Fixing fusion rootlets" )
    
    for node in nrfg:
        if lego_graph.is_formation( node ):
            LOG( "Fix fusion edges: {}".format( node ) )
            fusion: Formation = node.data
            major = set()
            
            major.update( fusion.event.component_out.major_genes )
            
            # Sometimes a fusion has more than the expected number of inputs/outputs (when we haven't been able to resolve it properly)
            # For this reason, we deal with each edge in turn
            
            for edge in list( node.edges ):
                oppo = edge.opposite( node )
                
                path = analysing.find_shortest_path( graph = nrfg,
                                                     start = oppo,
                                                     end = lego_graph.is_sequence_node,
                                                     filter = lambda x: x is not node )
                
                end = path[-1]
                assert lego_graph.is_sequence_node( end )
                
                if end.data in major:
                    # Is a product
                    LOG( "PRODUCT: {} --> {}".format( node, oppo ) )
                    oppo.make_root( node_filter = lambda x: not isinstance( x.data, Point ),
                                    edge_filter = lambda x: not isinstance( x.left.data, Point )
                                                            and not isinstance( x.right.data, Point ),
                                    ignore_cycles = True )
                    
                    edge.ensure( node, oppo )
                else:
                    # Is an ingredient
                    LOG( "INGREDIENT: {} <-- {}".format( node, oppo ) )
                    edge.ensure( oppo, node )


def __remove_redundant_clades( nrfg: MGraph ) -> None:
    """
    Remove redundant clades (clades which aren't the root and have only two edges)
    """
    LOG( "Fixing redundant clades" )
    safe = LoopDetector( nrfg.nodes.__len__() + 1, invert = True )
    
    # Repeat until nothing more changes
    while safe():
        for node in nrfg:  # type:MNode
            if lego_graph.is_clade( node ):
                if lego_graph.is_root( node ):
                    LOG( "Node is root: {}", node )
                    continue
                
                if node.num_relations == 2:
                    LOG( "Remove redundant clade: {}", node )
                    node.remove_node_safely( directed = False )
                    safe.persist()
                    break


def __remove_redundant_fusions( nrfg: MGraph ) -> None:
    """
    Remove redundant fusions (fusions next to fusions)
    
    We remove the fusion by reconnecting its relations to the adjacent fusion
    Note: This is NOT the same as :func:`MNode.remove_node_safely`
                                                                        
    X         X      X   X                                                
     \       /        \ /                                                 
      F-----F          F                                                  
     /       \        / \                                                 
    X         X      X   X                                                
                                                                        
    """
    LOG( "Fixing redundant fusions" )
    safe = LoopDetector( nrfg.nodes.__len__() + 1, invert = True )
    
    # Repeat until nothing more changes
    while safe():
        for node in nrfg:  # type: MNode
            if lego_graph.is_formation( node ):
                for relation in node.relations:  # type: MNode
                    if lego_graph.is_formation( relation ):
                        # So we have a fusion next to a fusion
                        for child in node.children:
                            relation.try_add_edge_to( child )
                        
                        for parent in node.parents:
                            parent.try_add_edge_to( relation )
                        
                        LOG( "Remove redundant fusion: {}", node )
                        node.remove_node()
                        safe.persist()
                        break  # relation
            
            if safe.check:  # list changed during iteration
                break
