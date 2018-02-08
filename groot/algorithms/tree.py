from typing import Optional

import groot.algorithms.external_runner
from groot.algorithms import importation
from groot.data.lego_model import LegoComponent


def generate_tree( algorithm: Optional[str], component: LegoComponent ) -> None:
    """
    Creates a tree from the component.
    
    The tree is set as the component's `tree` field. 
    """
    if component.alignment is None:
        raise ValueError( "Cannot generate the tree because the alignment has not yet been specified." )
    
    fn = groot.algorithms.external_runner.get_tool( "tree", algorithm )
    
    # Read the result
    newick = groot.algorithms.external_runner.run_in_temporary( fn, component.model, component.alignment )
    component.tree = importation.import_newick( newick, component.model )


def drop( component: LegoComponent ) -> bool:
    if component.model.fusion_events:
        raise ValueError( "Refusing to drop the tree because there are fusion events which may be using it. Did you mean to drop the fusion events first?" )
    
    if component.model.nrfg:
        raise ValueError( "Refusing to drop the tree because there is an NRFG which may be using it. Did you mean to drop the NRFG first?" )
    
    if component.tree is not None:
        component.tree = None
        return True
    
    return False
