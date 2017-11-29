from typing import cast

from intermake.hosts.gui import GuiHost


class LegoGuiHost(GuiHost):
    def create_window( self, args ):
        from groot.frontends.gui.forms.frm_main import FrmMain
        from groot.frontends.gui.forms import resources_rc
        cast(None, resources_rc)
        return FrmMain()
