import warnings

from groot.constants import STAGES
from groot.data import lego_graph
from groot.data.lego_model import LegoModel, LegoPoint, LegoSequence, EPosition, NamedGraph
from mgraph import MNode, analysing
from mhelper import NotFoundError, SwitchError


def drop_cleaned( model: LegoModel ):
    model.get_status( STAGES.CLEANED_13 ).assert_drop()
    
    model.nrfg.fusion_graph_unclean = None
    model.nrfg.is_checked = False
    model.nrfg.is_clean = False


def create_cleaned( model: LegoModel ):
    """
    Cleans the NRFG.
    """
    model.get_status( STAGES.CLEANED_13 ).assert_create()
    
    nrfg = model.nrfg.fusion_graph_unclean.graph.copy()
    
    for node in list( nrfg ):
        assert isinstance( node, MNode )
        
        # Remove "fusion" nodes listed in `sources`, these are the sew points
        # and will be adjacent to other identical nodes
        if lego_graph.is_fusion( node ):
            if node.uid in model.nrfg.minigraphs_sources:
                node.remove_node_safely()
        
        # Remove clades that don't add anything to the model.
        # (i.e. those which span only 2 nodes)
        if lego_graph.is_clade( node ):
            in_ = len( node.edges.incoming )
            out_ = len( node.edges.outgoing )
            if in_ == 1 and out_ == 1:
                node.parent.add_edge_to( node.child )
                node.remove_node()
            if in_ == 0 and out_ == 2:
                c = list( node.children )
                c[0].add_edge_to( c[1] )
                node.remove_node()
    
    for node in nrfg:
        # Make sure our fusion nodes act as roots to their creations
        # and as ancestors to their creators
        if lego_graph.is_fusion( node ):
            fusion: LegoPoint = node.data
            
            for edge in list( node.edges ):
                oppo: MNode = edge.opposite( node )
                try:
                    path = analysing.find_shortest_path( nrfg,
                                                         start = oppo,
                                                         end = lambda x: isinstance( x.data, LegoSequence ),
                                                         filter = lambda x: x is not node )
                except NotFoundError:
                    warnings.warn( "Cannot re-root along fusion edge «{}» because there is no outer path.".format( edge ), UserWarning )
                    continue
                
                if path[-1].data in fusion.sequences:
                    edge.ensure( node, oppo )
                    oppo.make_root( node_filter = lambda x: not isinstance( x.data, LegoPoint ),
                                    edge_filter = lambda x: x is not edge )
                else:
                    edge.ensure( oppo, node )
    
    for node in nrfg:
        # Nodes explicitly flagged as roots or outgroups should be made so
        if isinstance( node.data, LegoSequence ) and node.data.position != EPosition.NONE:
            if node.data.position == EPosition.OUTGROUP:
                node.relation.make_root( node_filter = lambda x: not isinstance( x.data, LegoPoint ) )
            elif node.data.position == EPosition.ROOT:
                node.make_root( node_filter = lambda x: not isinstance( x.data, LegoPoint ) )
            else:
                raise SwitchError( "node.data.position", node.data.position )
    
    model.nrfg.fusion_graph_clean = NamedGraph( nrfg, "NRFG" )