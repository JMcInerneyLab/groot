from groot import constants
from groot.data import INamedGraph, global_view, FixedUserGraph
from intermake.commands.basic_command import command

__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME_EXTRA

@command( folder=constants.F_IMPORT )
def import_graph( graph: INamedGraph, name: str = "" ):
    """
    Imports a graph or tree as a user-graph.
    
    User graphs are graphs that can be viewed and explored but do not, by default, form part of the model.
    
    :param graph:   Graph to import. See `format_help`. If you specify an existing user-graph or a graph
                    that is already part of the model, a copy will be made. 
    :param name:    Name of the graph. If not provided your graph will be assigned a default name. 
    """
    model = global_view.current_model()
    
    graph = FixedUserGraph( graph.graph.copy(), name or "usergraph{}".format( len( model.user_graphs ) ) )
    
    model.user_graphs.append( graph )



@command( folder=constants.F_DROP )
def drop_graph( graph: INamedGraph ):
    """
    Removes a graph created with `import_graph`.
    :param graph:   Graph to remove. See `format_help`.
    """
    model = global_view.current_model()
    
    if not isinstance( graph, FixedUserGraph ):
        raise ValueError( "The specified graph is not a user-graph and cannot be removed. Please specify an _existing_ user-graph." )
    
    model.user_graphs.remove( graph )