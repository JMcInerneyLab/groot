from legoalign.mcommand_extensions import viewing
from legoalign import mcommand_extensions
from legoalign.mcommand_extensions.old import _current_model
from mcommand import MENV, create_simple_host_provider_from_class, ConsoleHost

def __gui_host():
    from legoalign.frontends.gui.gui_host import LegoGuiHost
    return LegoGuiHost()

MENV.name = "GR⚆⚆T"
MENV.abv_name = "groot"
MENV.plugins.load_namespace( mcommand_extensions )
MENV.root = _current_model()
MENV.host_provider = create_simple_host_provider_from_class( ConsoleHost, __gui_host )
