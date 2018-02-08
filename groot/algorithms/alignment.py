import groot.algorithms.external_runner
from groot.algorithms import fastaiser, external_tools
from groot.data.lego_model import LegoComponent


def clear( component: LegoComponent ):
    component.alignment = None


def align( algorithm: str, component: LegoComponent ):
    fasta = fastaiser.component_to_fasta( component, simplify_ids = True )
    
    if algorithm is None:
        algorithm = "default"
    
    fn = groot.algorithms.external_runner.get_tool("align" , algorithm)
    
    component.alignment = groot.algorithms.external_runner.run_in_temporary( fn, component.model, fasta )


def drop( component: LegoComponent ):
    if component.tree:
        raise ValueError( "Refusing to drop the alignment because there is already a tree for this component. Did you mean to drop the tree first?" )
    
    if component.alignment is not None:
        component.alignment = None
        return True
    
    return False
