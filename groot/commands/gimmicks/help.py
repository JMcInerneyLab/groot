from groot.data import config
from intermake import Controller, visibilities, Application, pr
from mgraph import NodeStyle

from groot.application import app
from groot import constants
from groot.utilities import AlgorithmCollection


@app.command( visibility = visibilities.ADVANCED, folder = constants.F_EXTRA )
def groot():
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
        r.append( pr.fmt_section_start( collection.name ) )
        
        for name, function in collection:
            if name != "default":
                r.append( pr.fmt_code( name ) )
                r.append( pr.fmt_rst( function.__doc__ ) )
                r.append( "" )
        
        r.append( "" )
    
    return "\n".join( r )


Application.LAST.help.add( "algorithms", "List of available algorithms", __algorithm_help, format = "html" )
