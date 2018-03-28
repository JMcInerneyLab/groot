from groot.constants import STAGES
from groot.data import lego_graph
from groot.data.lego_model import LegoModel, LegoPoint, NamedGraph
from mgraph import MGraph
from mhelper import array_helper, Logger


__LOG = Logger( "nrfg.sew", False )

def drop_fused( model: LegoModel ):
    model.get_status( STAGES.FUSED_12 ).assert_drop()
    
    model.nrfg.fusion_graph_unclean = None


def create_fused( model: LegoModel ):
    """
    Sews the minigraphs back together at the fusion points.
    """
    __LOG.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ SEW ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    
    model.get_status( STAGES.FUSED_12 ).assert_create()
    
    # Create our final composite graph
    nrfg: MGraph = MGraph()
    
    for minigraph in model.nrfg.minigraphs:
        minigraph.graph.copy( target = nrfg, merge = True )
    
    # Debug
    __LOG( "FINAL UN-SEWED NRFG:" )
    __LOG( nrfg.to_ascii() )
    __LOG( "IN THIS GRAPH THERE ARE {} FUSION NODES", len( lego_graph.get_fusion_nodes( nrfg ) ) )
    
    for an, bn in array_helper.square_comparison( lego_graph.get_fusion_nodes( nrfg ) ):
        a = an.data
        b = bn.data
        
        assert an.uid in model.nrfg.minigraphs_sources or an.uid in model.nrfg.minigraphs_destinations
        assert bn.uid in model.nrfg.minigraphs_sources or bn.uid in model.nrfg.minigraphs_destinations
        
        a_is_source = an.uid in model.nrfg.minigraphs_sources
        b_is_source = bn.uid in model.nrfg.minigraphs_sources
        
        assert isinstance( a, LegoPoint )
        assert isinstance( b, LegoPoint )
        
        __LOG( "-----------------------------------" )
        __LOG( "COMPARING THE NEXT TWO FUSION NODES" )
        __LOG( "-----------------------------------" )
        __LOG( "    A: {}", a.str_long() )
        __LOG( "    B: {}", b.str_long() )
        
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
    
    model.nrfg.fusion_graph_unclean = NamedGraph( nrfg, "Intermediate" )