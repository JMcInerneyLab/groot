from groot.data.lego_model import ILegoVisualisable, IHasFasta
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import EThread, MENV, command, visibilities
from intermake.engine.environment import MCMD


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
    
    if isinstance( entity, IHasFasta ):
        fasta = entity.to_fasta(  )
        FrmAlignment.request( MENV.host.form, "FASTA for {}".format( entity ), MENV.host.form.view.lookup_table, fasta )
    else:
        MCMD.warning( "Target «{}» does not have FASTA data.".format( entity ) )
