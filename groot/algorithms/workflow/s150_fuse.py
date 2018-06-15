from groot import constants
from intermake import command
from mgraph import MGraph
from mhelper import Logger, array_helper, string_helper

from groot.constants import STAGES, EChanges
from groot.data import FusionGraph, Formation, global_view
from groot.utilities import lego_graph


__LOG = Logger( "nrfg.sew", False )
__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME

@command(folder = constants.F_CREATE)
def create_fused():
    """
    Creates the NRFG (uncleaned).
    
    Sews the subgraphs back together at the fusion points.
    
    Requisites: `create_subgraphs`
    """
    __LOG.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ SEW ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    
    model = global_view.current_model()
    model.get_status( STAGES.FUSED_12 ).assert_create()
    
    # First, we pull all of our subgraphs ("supertrees") into the nrfg
    nrfg: MGraph = MGraph()
    
    for minigraph in model.subgraphs:
        minigraph.graph.copy( target = nrfg, merge = True )
    
    # Second, we find the fusion points ("formation nodes") and stitch these together
    fusion_nodes = lego_graph.get_fusion_formation_nodes( nrfg )
    
    for an, bn in array_helper.square_comparison( fusion_nodes ):
        a: Formation = an.data
        b: Formation = bn.data
        
        assert an.uid in model.subgraphs_sources or an.uid in model.subgraphs_destinations
        assert bn.uid in model.subgraphs_sources or bn.uid in model.subgraphs_destinations
        
        a_is_source = an.uid in model.subgraphs_sources
        b_is_source = bn.uid in model.subgraphs_sources
        
        assert isinstance( a, Formation )
        assert isinstance( b, Formation )
        
        __LOG( "-----------------------------------" )
        __LOG( "COMPARING THE NEXT TWO FUSION NODES" )
        __LOG( "-----------------------------------" )
        __LOG( "    A: {}", __str_long( a ) )
        __LOG( "    B: {}", __str_long( b ) )
        
        if a.event is not b.event:
            __LOG( "SKIP (THEY REFERENCE DIFFERENT EVENTS)" )
            continue
        
        if b_is_source or not a_is_source:
            __LOG( "SKIP (DEALING WITH THE A->B TRANSITIONS AND THIS IS B->A)" )
            continue
        
        if not a.pertinent_inner.intersection( b.pertinent_inner ):
            __LOG( "SKIP (THE INNER GROUPS DON'T MATCH)" )
            continue
        
        __LOG( "MATCH! (I'M READY TO MAKE THAT EDGE)" )
        an.add_edge_to( bn )
    
    __LOG.pause( "NRFG AFTER SEWING ALL:" )
    __LOG( nrfg.to_ascii() )
    __LOG.pause( "END OF SEW" )
    
    model.fusion_graph_unclean = FusionGraph( nrfg, False )
    return EChanges.MODEL_DATA


@command(folder = constants.F_DROP)
def drop_fused( ):
    """
    Removes data from the model.
    """
    model = global_view.current_model()
    model.get_status( STAGES.FUSED_12 ).assert_drop()
    
    model.fusion_graph_unclean = None
    return EChanges.MODEL_DATA


def __str_long( formation: Formation ):
    return "¨EVENT {} FORMING {}¨".format( formation.event,
                                           __format_elements( formation.pertinent_inner ) )


def __format_elements( y ):
    return string_helper.format_array( y, join = ",", sort = True, autorange = True )
