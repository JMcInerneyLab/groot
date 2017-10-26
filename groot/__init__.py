from groot.extensions import ext_viewing
from groot import extensions
from intermake import MENV, create_simple_host_provider_from_class, ConsoleHost

def __gui_host():
    from groot.frontends.gui.gui_host import LegoGuiHost
    return LegoGuiHost()

MENV.name = "GROOT"
MENV.abv_name = "groot"
MENV.plugins.load_namespace( extensions )
MENV.host_provider = create_simple_host_provider_from_class( ConsoleHost, __gui_host )
