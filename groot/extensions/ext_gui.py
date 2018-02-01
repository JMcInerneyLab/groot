from groot.algorithms import fastaiser
from groot.data.lego_model import ILegoVisualisable, LegoComponent
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import EThread, MENV, command, visibilities


_VIS = visibilities.GUI & visibilities.ADVANCED







@command( visibility = _VIS )
def refresh( change: EChanges ) -> EChanges:
    """
    Refreshes the GUI
    :param change:  Level of refresh
    """
    return change




@command( visibility = _VIS, threading = EThread.UNMANAGED )
def view_fasta_gui( entity: ILegoVisualisable ) -> None:
    """
    Views the FASTA in the GUI.
    :param entity:  Entity to view Fasta for
    """
    from groot.frontends.gui.forms.frm_alignment import FrmAlignment
    
    fasta = fastaiser.to_fasta( entity )
    FrmAlignment.request( MENV.host.form, "FASTA for {}".format( entity ), MENV.host.form.view.lookup_table, fasta )
