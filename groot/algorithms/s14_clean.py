from groot.constants import STAGES
from groot.data import lego_graph
from groot.data.lego_model import EPosition, FusionGraph, LegoModel, LegoPoint, LegoSequence, LegoFormation
from mgraph import MEdge, MGraph, MNode, analysing
from mhelper import Logger, LoopDetector, SwitchError


LOG = Logger( "clean", True )


def drop_cleaned( model: LegoModel ):
    model.get_status( STAGES.CLEANED_13 ).assert_drop()
    
    model.fusion_graph_clean = None


def create_cleaned( model: LegoModel ):
    """
    Cleans the NRFG.
    """
    model.get_status( STAGES.CLEANED_13 ).assert_create()
    nrfg = model.fusion_graph_unclean.graph.copy()
    
    __remove_redundant_fusions( nrfg )
    __remove_redundant_clades( nrfg )
    __make_fusions_rootlets( nrfg )
    __make_outgroup_parents_roots( nrfg )
    
    model.fusion_graph_clean = FusionGraph( nrfg, True )


def __make_outgroup_parents_roots( nrfg: MGraph ) -> None:
    """
    Finally, nodes explicitly flagged as roots or outgroups should be made so
    We don't "reclade" the nodes here (i.e. (A,B,C) becomes A->B and A->C and not A,(B,C)
    as earlier, because the intermediate clades should already be present
    """
    LOG( "Fixing outgroups..." )
    
    for node in nrfg:
        if isinstance( node.data, LegoSequence ) and node.data.position != EPosition.NONE:
            if node.data.position == EPosition.OUTGROUP:
                # We call "make root" and not "make outgroup" because the network should
                # already have the right topology, we just need to adjust the directions
                LOG( "Make outgroup: {}".format( node ) )
                LOG( "--i.e. make root: {}".format( node.relation ) )
                node.relation.make_root( node_filter = lambda x: not lego_graph.is_fusion_like( x ), ignore_cycles = True )
            elif node.data.position == EPosition.ROOT:
                LOG( "Make root: {}".format( node ) )
                node.make_root( node_filter = lambda x: not isinstance( x.data, LegoPoint ), ignore_cycles = True )
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
            fusion: LegoFormation = node.data
            major = set()
            
            for p in fusion.event.products:
                major.update( p.major_sequences )
            
            path = analysing.find_shortest_path( nrfg,
                                                 start = node,
                                                 end = lambda x: isinstance( x.data, LegoSequence ) and x.data in major )
            
            # "path" now points to one of our event's created sequences (i.e. the things that are formed)
            for edge in list( node.edges ):
                assert isinstance( edge, MEdge )
                oppo = edge.opposite( node )
                
                if oppo is path[1]:
                    # OUTGOING edge
                    oppo.make_root( node_filter = lambda x: not isinstance( x.data, LegoPoint ),
                                    edge_filter = lambda x: not isinstance( x.left.data, LegoPoint ) and not isinstance( x.right.data, LegoPoint ),
                                    ignore_cycles = True )
                    
                    edge.ensure( node, oppo )
                else:
                    # INCOMING edge
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
                else:
                    LOG( "Node has <> 2 relations: {}", node )
            else:
                LOG( "Node is not clade: {}", node )


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
