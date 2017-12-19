from groot.algorithms import editor
from groot.data.lego_model import LegoModel, LOG
from mhelper import array_helper


def remove_redundant_subsequences( model: LegoModel ):
    """
    API
    Merges adjacent subsequences with identical edges
    """
    editor.assert_model_freshness( model )
    
    
    def it():
        for sequence in model.sequences:
            for previous, next in array_helper.lagged_iterate( sequence.subsequences ):
                if set( previous.edges ) == set( next.edges ) \
                        and previous.components == next.components:
                    with LOG( "EQUIVALENT:" ):
                        LOG( "X = {}".format( previous ) )
                        LOG( "Y = {}".format( next ) )
                        editor.merge_subsequences( (previous, next) )
                        return True
        
        return False
    
    
    with LOG( "REMOVE REDUNDANT SUBSEQUENCES" ):
        removed = 0
        
        while it():
            removed += 1
        
        return removed


def remove_redundant_edges( model: LegoModel ):
    """
    API
    Removes edges that have copies elsewhere (either forward or back)
    """
    editor.assert_model_freshness( model, False )
    
    the_list = list( model.all_edges )
    
    with LOG( "REMOVE REDUNDANT EDGES" ):
        removed = 0
        
        for edge_1 in the_list:
            for edge_2 in the_list:
                if not edge_1.is_destroyed and not edge_2.is_destroyed and edge_1 is not edge_2:
                    x_source = set( edge_1.left )
                    x_dest = set( edge_1.right )
                    y_source = set( edge_2.left )
                    y_dest = set( edge_2.right )
                    
                    if (x_source == y_source and x_dest == y_dest) or (x_source == y_dest and x_dest == y_source):
                        with LOG( "EQUIVALENT:" ):
                            LOG( "X = {}".format( edge_1 ) )
                            LOG( "Y = {}".format( edge_2 ) )
                            editor.unlink_all_edges( edge_2 )
                            removed += 1
        
        return removed
