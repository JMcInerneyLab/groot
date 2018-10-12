from groot.data import config
from intermake import Controller, visibilities, Theme, command, Application
from mgraph import NodeStyle

from groot import constants
from groot.utilities import AlgorithmCollection


@command( names = ["groot", "dirse"], visibility = visibilities.ADVANCED, folder = constants.F_EXTRA )
def cmd_groot():
    """
    Displays the application version.
    
    Also has the secondary affect of loading all the options from disk.
    """
    print( "I AM {}. VERSION {}.".format( Controller.ACTIVE.app.name, Controller.ACTIVE.app.version ) )
    _ = config.options()


def __print_help() -> str:
    """
    Help on tree-node formatting.
    """
    return str( NodeStyle.replace_placeholders.__doc__ )


Application.LAST.help.add( "node_formatting", "List of available node display formats", __print_help )


def __algorithm_help():
    """
    Prints available algorithms.
    """
    r = []
    for collection in AlgorithmCollection.ALL:
        r.append( "" )
        r.append( Theme.TITLE + "========== " + collection.name + " ==========" + Theme.RESET )
        
        for name, function in collection:
            if name != "default":
                r.append( "    " + Theme.COMMAND_NAME + name + Theme.RESET )
                r.append( "    " + (function.__doc__ or "").strip() )
                r.append( "" )
        
        r.append( "" )
    
    return "\n".join( r )


Application.LAST.help.add( "algorithms", "List of available algorithms", __algorithm_help )
