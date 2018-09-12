"""
Sets up Intermake to run Groot.
This is called in `groot.__init__`.
"""
import intermake
from groot import constants
from intermake.hosts.base import ERunMode


def __create_lego_gui_host():
    import groot_gui
    return groot_gui.LegoGuiHost()


def __execute_command( result: intermake.AsyncResult ):
    from groot import global_view
    model = global_view.current_model()
    
    if model:
        model.command_history.append( "{}".format( result ) )


#
# Define our application
#
GROOT_APP = intermake.Environment( name = constants.APP_NAME,
                                   abv_name = "groot",
                                   version = "0.0.0.40" )
GROOT_APP.host_provider[ERunMode.GUI] = __create_lego_gui_host
GROOT_APP.after_command_hook.subscribe( __execute_command )

from groot.utilities import string_coercion


string_coercion.setup()

# Register model (_after_ setting up Intermake!)
# noinspection PyUnresolvedReferences
from groot.data import global_view
