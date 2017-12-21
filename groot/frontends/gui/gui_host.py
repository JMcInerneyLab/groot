from typing import cast

from intermake.hosts.gui import GuiHost


class LegoGuiHost(GuiHost):
    def create_window( self, args ):
        from groot.frontends.gui.forms.resources import resources_rc as groot_resources_rc
        from intermake.hosts.frontends.gui_qt.designer.resource_files import resources_rc as intermake_resources_rc
        cast(None, groot_resources_rc)
        cast(None, intermake_resources_rc)
        from groot.frontends.gui.forms.frm_main import FrmMain
        return FrmMain()
