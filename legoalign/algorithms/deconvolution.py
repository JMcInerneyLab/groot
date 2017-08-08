from legoalign.LegoModels import LOG, LegoModel
from legoalign.algorithms import editor
from mhelper import ArrayHelper


def remove_redundant_subsequences( model : LegoModel ):
    """
    API
    Merges adjacent subsequences with identical edges
    """
    
    
    def it():
        for sequence in model.sequences:
            for previous, next in ArrayHelper.lagged_iterate( sequence.subsequences ):
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


def remove_redundant_edges( model : LegoModel ):
    """
    API
    Removes edges that have copies elsewhere (either forward or back)
    """
    the_list = list( model.all_edges )
    
    with LOG( "REMOVE REDUNDANT EDGES" ):
        removed = 0
        
        for x in the_list:
            for y in the_list:
                if not x.is_destroyed and not y.is_destroyed and x is not y:
                    x_source = set( x.source )
                    x_dest = set( x.destination )
                    y_source = set( y.source )
                    y_dest = set( y.destination )
                    
                    if (x_source == y_source and x_dest == y_dest) or (x_source == y_dest and x_dest == y_source):
                        with LOG( "EQUIVALENT:" ):
                            LOG( "X = {}".format( x ) )
                            LOG( "Y = {}".format( y ) )
                            y.unlink_all()
                            removed += 1
        
        return removed