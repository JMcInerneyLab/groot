import warnings

from groot import constants
from groot.data.lego_model import LegoModel, NrfgReport
from mgraph import analysing


def drop_checked( model: LegoModel ):
    model.get_status( constants.STAGES.CHECKED_14 ).assert_drop()
    
    model.report = None


def create_checked( model: LegoModel ):
    model.get_status( constants.STAGES.CHECKED_14 ).assert_create()
    
    nrfg = model.fusion_graph_clean.graph
    
    if len( nrfg.nodes ) == 0:
        warnings.warn( "The NRFG is bad. It doesn't contain any edges.", UserWarning )
    
    if len( nrfg.edges ) == 0:
        warnings.warn( "The NRFG is bad. It doesn't contain any edges.", UserWarning )
    
    ccs = analysing.find_connected_components( nrfg )
    
    if len( ccs ) != 1:
        warnings.warn( "The NRFG is bad. It contains more than one connected component. It contains {}.".format( len( ccs ) ), UserWarning )
    
    model.report = NrfgReport()