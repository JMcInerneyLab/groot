from typing import List, Optional

from groot.algorithms import alignment, components, tree, nrfg, fuse
from groot.data import global_view
from groot.data.lego_model import LegoComponent
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import command
from intermake.engine.environment import MCMD
from mgraph import MGraph
from mhelper import string_helper


__mcmd_folder_name__ = "Generating"


@command( names = ["make_components", "create_components", "find_components"] )
def make_components( tolerance: int = 0 ) -> EChanges:
    """
    Detects composites in the model.
    :param tolerance:   Tolerance on overlap, in sites.
    """
    model = global_view.current_model()
    
    if len( model.edges ) == 0:
        raise ValueError( "Refusing to make components because there is no edge data. Did you mean to load the edge data (BLAST) first?" )
    
    with MCMD.action( "Component detection" ):
        components.detect( model, tolerance )
    
    for component in model.components:
        if len( component.major_sequences ) == 1:
            MCMD.warning( "There are components with just one sequence in them. Maybe you meant to use a tolerance higher than {}?".format( tolerance ) )
            break
    
    MCMD.progress( "{} components detected.".format( len( model.components ) ) )
    
    return EChanges.COMPONENTS


@command( names = ["make_alignments", "create_alignments", "make_alignment", "create_alignment"] )
def make_alignments( algorithm: Optional[str] = None, component: Optional[List[LegoComponent]] = None ) -> EChanges:
    """
    Aligns the component. If no component is specified, aligns all components.
    
    Requisites: The FASTA sequences. You must have called `load_fasta` first.
    
    :param algorithm:   Algorithm to use.
    :param component:   Component to align, or `None` for all.
    """
    model = global_view.current_model()
    
    if not all( x.site_array for x in model.sequences ):
        raise ValueError( "Refusing to make alignments because there is no site data. Did you mean to load the site data (FASTA) first?" )
    
    to_do = cli_view_utils.get_component_list( component )
    before = sum( x.alignment is not None for x in model.components )
    
    for component_ in MCMD.iterate( to_do, "Aligning", text = True ):
        alignment.align( algorithm, component_ )
    
    after = sum( x.alignment is not None for x in model.components )
    MCMD.progress( "{} components aligned. {} of {} components have an alignment ({}).".format( len( to_do ), after, len( model.components ), string_helper.as_delta( after - before ) ) )
    
    return EChanges.COMP_DATA


@command( names = ["make_trees", "create_trees", "make_tree", "create_tree"] )
def make_trees( algorithm: Optional[str] = None, component: Optional[List[LegoComponent]] = None ):
    """
    Generates component trees.
    
    Requisites: The alignments. You must have called `make_alignments` first.
    
    :param algorithm:   Algorithm to use. See `help_algorithms`.
    :param component:   Component, or `None` for all.
    """
    model = global_view.current_model()
    
    if not all( x.alignment is not None for x in model.components ):
        raise ValueError( "Refusing to generate trees because there are no alignments. Did you mean to align the sequences first?" )
    
    to_do = cli_view_utils.get_component_list( component )
    before = sum( x.tree is not None for x in model.components )
    
    for component_ in MCMD.iterate( to_do, "Generating trees", text = True ):
        tree.generate_tree( algorithm, component_ )
    
    after = sum( x.tree is not None for x in model.components )
    MCMD.progress( "{} trees generated. {} of {} components have a tree ({}).".format( len( to_do ), after, len( model.components ), string_helper.as_delta( after - before ) ) )
    
    return EChanges.COMP_DATA


@command( names = ["make_fusions", "make_fusion", "create_fusions", "create_fusion", "find_fusions", "find_fusion"] )
def make_fusions( overwrite: bool = False ) -> EChanges:
    """
    Makes the fusion points.
    
    Requisites: The trees. You must have called `make_trees` first.
    
    :param overwrite: Drop existing fusions first?
    """
    model = global_view.current_model()
    
    if not all( x.tree is not None for x in model.components ):
        raise ValueError( "Cannot find fusion events because there is no tree data. Did you mean to generate the trees first?" )
    
    if overwrite:
        fuse.remove_fusions( model )
    
    fuse.find_all_fusion_points( model )
    
    n = len( model.fusion_events )
    MCMD.progress( "{} {} detected".format( n, "fusion" if n == 1 else "fusions" ) )
    
    return EChanges.MODEL_DATA


@command( names = ["make_nrfg", "create_nrfg"] )
def make_nrfg() -> EChanges:
    """
    Creates the N-rooted fusion graph.
    """
    model = global_view.current_model()
    
    nrfg.create_nrfg( model )
    
    MCMD.progress( "NRFG created OK." )
    
    return EChanges.MODEL_DATA


@command()
def split_graph( tree: MGraph ) -> EChanges:
    """
    Shows the splits for a tree.
    :param tree:   Tree to split.
    """
    nrfg.reduce_and_rebuild( tree )
    
    return EChanges.NONE
