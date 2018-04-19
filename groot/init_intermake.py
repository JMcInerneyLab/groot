"""
Sets up Intermake to run Groot.
This is called by `groot.__init__`.
"""
from intermake import MENV
from groot import constants
from intermake.hosts.base import ERunMode


def __create_lego_gui_host():
    import groot_gui
    return groot_gui.LegoGuiHost


if MENV.configure( name = constants.APP_NAME,
                   abv_name = "groot",
                   version = "0.0.0.40" ):
    MENV.host_provider[ERunMode.GUI] = __create_lego_gui_host()

    from groot.utilities import string_coercion


    string_coercion.setup()
    

# Register model (_after_ setting up Intermake!)
# noinspection PyUnresolvedReferences
from groot.data import global_view
