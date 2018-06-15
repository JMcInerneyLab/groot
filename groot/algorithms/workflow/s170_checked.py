from intermake import command
from mgraph import analysing

from groot import constants
from groot.data import Report, global_view
from groot.constants import EChanges
from groot.utilities import lego_graph


_TABLE = '<table border=1 style="border-collapse: collapse;">'
_END_TABLE = "</table>"

__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME

@command(folder = constants.F_CREATE)
def create_checked(  ):
    """
    Checks the NRFG.
    
    Requisites: `create_cleaned`
    """
    model=global_view.current_model()
    model.get_status( constants.STAGES.CHECKED_14 ).assert_create()
    
    nrfg = model.fusion_graph_clean.graph
    title = "{} - NRFG report".format( model )
    
    r = []
    r.append( "<html><head><title>{0}</title></head><body><h1>{0}</h1>".format( title ) )
    
    warnings = []
    
    #
    # WARNINGS AND ERRORS
    #
    
    # Basic checks
    if len( nrfg.nodes ) == 0:
        warnings.append( "The NRFG is bad. It doesn't contain any nodes." )
    
    if len( nrfg.edges ) == 0:
        warnings.append( "The NRFG is bad. It doesn't contain any edges." )
    
    # NRFG should be connected
    ccs = analysing.find_connected_components( nrfg )
    
    if len( ccs ) != 1:
        warnings.append( "The NRFG is bad. It contains more than one connected component. It contains {} components.".format( len( ccs ) ) )
    
    # Fusion node checks
    for node in nrfg:
        if lego_graph.is_fusion_like( node ):
            if node.num_parents != 2 and node.num_children != 1:
                warnings.append( "Possible badly formed fusion at node «{}». This fusion has {} input and {} outputs, instead of the expected 2 inputs and 1 output.".format( node, node.num_parents, node.num_children ) )
        elif lego_graph.is_root( node ):
            if node.num_parents > 0:
                warnings.append( "Possibly badly formed root at node «{}». This node has {} parents instead of the expected 0.".format( node, node.num_parents ) )
        elif node.num_parents > 1:
            warnings.append( "Possibly badly formed clade at node «{}». This node has {} parents instead of the expected 1.".format( node, node.num_parents ) )
        
        if lego_graph.is_sequence_node( node ):
            if node.num_children > 0:
                warnings.append( "Possibly badly formed sequence at node «{}». This node has {} children instead of the expected 0.".format( node, node.num_parents ) )
        elif lego_graph.is_clade( node ):
            if node.num_children <= 1:
                warnings.append( "Possible redundant clade at node «{}». This node has {} children instead of 2 or more.".format( node, node.num_parents ) )
    
    # Format warnings
    r.append( "<br/>" )
    r.append( "<h2>Warnings and errors</h2>" )
    if warnings:
        for warning in warnings:
            r.append( "<li>{}</li>".format( warning ) )
        r.append( "</ol>" )
    else:
        r.append( "None!" )
    
    # General information
    r.append( "<br/>" )
    r.append( "<h2>General information</h2>" )
    r.append( _TABLE )
    r.append( "<tr><td>{}<td><td>{}<td>".format( "Nodes", nrfg.nodes.__len__() ) )
    r.append( "<tr><td>{}<td><td>{}<td>".format( "Edges", nrfg.edges.__len__() ) )
    r.append( "<tr><td>{}<td><td>{}<td>".format( "Clades", sum( 1 for x in nrfg if lego_graph.is_clade( x ) ) ) )
    r.append( "<tr><td>{}<td><td>{}<td>".format( "Fusions", sum( 1 for x in nrfg if lego_graph.is_formation( x ) ) ) )
    r.append( "<tr><td>{}<td><td>{}<td>".format( "Sequences", sum( 1 for x in nrfg if lego_graph.is_sequence_node( x ) ) ) )
    r.append( _END_TABLE )
    
    r.append( "</body></html>" )
    
    model.report = Report( "NRFG report", "\n".join( r ) )
    return EChanges.MODEL_DATA

@command(folder = constants.F_DROP)
def drop_checked( ):
    """
    Removes the check-NRFG report from the model.
    """
    model=global_view.current_model()
    model.get_status( constants.STAGES.CHECKED_14 ).assert_drop()
    
    model.report = None
    return EChanges.MODEL_DATA
