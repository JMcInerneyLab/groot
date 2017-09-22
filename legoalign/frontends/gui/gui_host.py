from mcommand.hosts.gui import GuiHost


class LegoGuiHost(GuiHost):
    def create_window( self, args ):
        from legoalign.frontends.gui.forms.frm_main import FrmMain
        return FrmMain()
