from groot.algorithms import external_tools
from groot.data.graphing import MGraph
from groot.data.lego_model import LegoComponent


def generate_tree( component: LegoComponent ) -> None:
    """
    Creates a tree from the component.
    
    The tree is set as the component's `tree` field. 
    """
    if component.alignment is None:
        raise ValueError( "Cannot generate the tree because the alignment has not yet been specified." )
    
    # Read the result
    newick = external_tools.run_in_temporary( external_tools.tree, component.alignment )
    g = MGraph()
    g.import_newick( newick, component.model )
    component.tree = g


def drop( component: LegoComponent ) -> bool:
    if component.tree is not None:
        component.tree = None
        return True
    
    return False