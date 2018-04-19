from intermake import MENV, MCMD, visibilities, Theme, command, help_command
from mgraph import NodeStyle

from groot.utilities import AlgorithmCollection


@command( names = ["groot"], visibility = visibilities.ADVANCED )
def cmd_groot():
    """
    Displays the application version.
    """
    MCMD.print( "I AM {}. VERSION {}.".format( MENV.name, MENV.version ) )


@help_command()
def print_help() -> str:
    """
    Help on tree-node formatting.
    """
    return str( NodeStyle.replace_placeholders.__doc__ )


@help_command( names = ["algorithm_help", "print_algorithms", "algorithms"] )
def algorithm_help():
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
