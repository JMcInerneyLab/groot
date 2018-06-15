"""
Sets up Intermake to run Groot.
This is called by `groot.__init__`.
"""
import intermake
from groot import constants
from intermake.hosts.base import ERunMode


def __create_lego_gui_host():
    import groot_gui
    return groot_gui.LegoGuiHost()


GROOT_APP = intermake.Environment( name = constants.APP_NAME,
                                   abv_name = "groot",
                                   version = "0.0.0.40" )
GROOT_APP.host_provider[ERunMode.GUI] = __create_lego_gui_host

from groot.utilities import string_coercion


string_coercion.setup()

# Register model (_after_ setting up Intermake!)
# noinspection PyUnresolvedReferences
from groot.data import global_view
