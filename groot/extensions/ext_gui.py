from groot.frontends.gui.gui_view_utils import EChanges
from intermake import command, visibilities


@command( visibility = visibilities.GUI & visibilities.ADVANCED )
def refresh( change: EChanges ):
    """
    Refreshes the GUI
    :param change:  Level of refresh
    """
    return change
