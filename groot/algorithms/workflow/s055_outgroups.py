from typing import List, Optional
from intermake import MCMD, command

from groot import Gene, constants
from groot.data import EPosition, global_view
from groot.constants import EChanges

__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME

@command(folder = constants.F_SET)
def set_outgroups( genes: List[Gene], position: Optional[bool] = None ) -> EChanges:
    """
    Defines or displays the position of a gene in the graph.
    If trees have been generated already they will be re-rooted.
     
    :param genes:       Gene(s) to affect, or `None` to display all genes.
    :param position:    New status.
                        `True` = "outgroup"
                        `False` = "ingroup"
                        `None` = "sole outgroup"
                        If not specified then the specified genes will be made outgroups and all others will be not.  
    """
    model = global_view.current_model()
    if position is None:
        for gene in model.genes:
            if gene in genes:
                gene.position = EPosition.OUTGROUP
            else:
                gene.position = EPosition.NONE
    else:
        for gene in genes:
            gene.position = EPosition.OUTGROUP if position else EPosition.NONE
    return EChanges.INFORMATION


@command(folder = constants.F_PRINT)
def print_outgroups():
    """
    Prints the outgroups.
    """
    model = global_view.current_model()
    
    for gene in model.genes:
        if gene.position != EPosition.NONE:
            MCMD.print( str( gene ) )
