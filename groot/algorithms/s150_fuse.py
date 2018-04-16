from groot.constants import STAGES
from groot.data import LegoModel, FusionGraph, LegoFormation
from groot.utilities import lego_graph
from mgraph import MGraph
from mhelper import array_helper, Logger, string_helper


__LOG = Logger( "nrfg.sew", False )


def drop_fused( model: LegoModel ):
    model.get_status( STAGES.FUSED_12 ).assert_drop()
    
    model.fusion_graph_unclean = None


def create_fused( model: LegoModel ):
    """
    Sews the subgraphs back together at the fusion points.
    """
    __LOG.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ SEW ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    
    model.get_status( STAGES.FUSED_12 ).assert_create()
    
    # First, we pull all of our subgraphs ("supertrees") into the nrfg
    nrfg: MGraph = MGraph()
    
    for minigraph in model.subgraphs:
        minigraph.graph.copy( target = nrfg, merge = True )
    
    # Second, we find the fusion points ("formation nodes") and stitch these together
    fusion_nodes = lego_graph.get_fusion_formation_nodes( nrfg )
    
    for an, bn in array_helper.square_comparison( fusion_nodes ):
        a: LegoFormation = an.data
        b: LegoFormation = bn.data
        
        assert an.uid in model.subgraphs_sources or an.uid in model.subgraphs_destinations
        assert bn.uid in model.subgraphs_sources or bn.uid in model.subgraphs_destinations
        
        a_is_source = an.uid in model.subgraphs_sources
        b_is_source = bn.uid in model.subgraphs_sources
        
        assert isinstance( a, LegoFormation )
        assert isinstance( b, LegoFormation )
        
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


def __str_long( formation: LegoFormation ):
    return "¨EVENT {} FORMING {}¨".format( formation.event,
                                           __format_elements( formation.pertinent_inner ) )


def __format_elements( y ):
    return string_helper.format_array( y, join = ",", sort = True, autorange = True )
