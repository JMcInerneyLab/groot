from groot.algorithms import fastaiser, external_tools
from groot.data.lego_model import LegoComponent


def clear( component: LegoComponent ):
    component.alignment = None


def align( component: LegoComponent ):
    fasta = fastaiser.component_to_fasta( component, simplify_ids = True )
    
    component.alignment = external_tools.run_in_temporary( external_tools.align, fasta )


def drop( component: LegoComponent ):
    if component.tree:
        raise ValueError("Refusing to drop the alignment because there is already a tree for this component. Did you mean to drop the tree first?")
    
    if component.alignment is not None:
        component.alignment = None
        return True
    
    return False
