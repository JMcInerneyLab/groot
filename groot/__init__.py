from intermake import MENV, create_simple_host_provider_from_class, ConsoleHost
from groot.extensions import ext_viewing, ext_files, ext_generating, ext_gimmicks, ext_modifications

def __gui_host():
    from groot.frontends.gui.gui_host import LegoGuiHost
    return LegoGuiHost()

MENV.name = "GROOT"
MENV.abv_name = "groot"
MENV.host_provider = create_simple_host_provider_from_class( ConsoleHost, __gui_host )
