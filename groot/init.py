from intermake import MENV
from groot import constants
from groot.frontends.gui import gui_host
from intermake.hosts.base import ERunMode 

if MENV.configure( name = constants.APP_NAME,
                   abv_name = "groot",
                   version = "0.0.0.40" ):
    
    MENV.host_provider[ERunMode.GUI] = gui_host.create_lego_gui_host
    
    from groot.extensions import string_coercion
    string_coercion.setup()
    

# Register model (_after_ setting up Intermake!)
# noinspection PyUnresolvedReferences
from groot.data import global_view

