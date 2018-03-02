from typing import List, Optional

from groot.algorithms import alignment, components, tree, nrfg, fuse, userdomains
from groot.data import global_view
from groot.data.lego_model import LegoComponent
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.gui_view_support import EDomainFunction
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import command
from intermake.engine.environment import MCMD
from mhelper import string_helper


__mcmd_folder_name__ = "Generating"


@command( names = ["make_domains", "create_domains", "find_domains"] )
def make_domains( mode: EDomainFunction, param: int = 0 ) -> EChanges:
    """
    Creates the domains.
    Existing domains are always replaced.
    Domains are only used for viewing and have no bearing on the actual calculations.
    
    :param mode:        Mode of domain generation 
    :param param:       Parameter for mode. 
    """
    model = global_view.current_model()
    
    userdomains.create_userdomains( model, mode, param )
    
    MCMD.progress( "Domains created, there are now {} domains.".format( len( model.user_domains ) ) )
    
    return EChanges.DOMAINS


@command( names = ["make_components", "create_components", "find_components"] )
def make_components( major_tol: int = 0, minor_tol: Optional[int] = None, debug: bool = False ) -> EChanges:
    """
    Detects composites in the model.
    :param major_tol:   Tolerance on overlap, in sites.
    :param minor_tol:   Tolerance on overlap, in sites. If `None` uses the `major_tol`.
    :param debug:       Internal parameter.
    """
    if minor_tol is None:
        minor_tol = major_tol
    
    model = global_view.current_model()
    
    if len( model.edges ) == 0:
        raise ValueError( "Refusing to make components because there is no edge data. Did you mean to load the edge data (BLAST) first?" )
    
    with MCMD.action( "Component detection" ):
        components.detect( model, major_tol, minor_tol, debug )
    
    for component in model.components:
        if len( component.major_sequences ) == 1:
            MCMD.warning( "There are components with just one sequence in them. Maybe you meant to use a tolerance higher than {}/{}?".format( major_tol, minor_tol ) )
            break
    
    MCMD.progress( "{} components detected.".format( len( model.components ) ) )
    
    return EChanges.COMPONENTS


@command( names = ["make_alignments", "create_alignments", "make_alignment", "create_alignment"] )
def make_alignments( algorithm: Optional[str] = None, component: Optional[List[LegoComponent]] = None ) -> EChanges:
    """
    Aligns the component. If no component is specified, aligns all components.
    
    Requisites: The FASTA sequences. You must have called `load_fasta` first.
    
    :param algorithm:   Algorithm to use. See `algorithm_help`.
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
    
    :param algorithm:   Algorithm to use. See `algorithm_help`.
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
    
    for x in model.components:
        if x.tree is None:
            raise ValueError( "Cannot find fusion events because there is no tree data for at least one component ({}). Did you mean to generate the trees first?".format( x ) )
    
    if overwrite:
        fuse.remove_fusions( model )
    
    fuse.find_all_fusion_points( model )
    
    n = len( model.fusion_events )
    MCMD.progress( "{} {} detected".format( n, "fusion" if n == 1 else "fusions" ) )
    
    return EChanges.MODEL_DATA


@command( names = ["make_nrfg", "create_nrfg"] )
def make_nrfg( cutoff: float = 0.5, dirty: bool = False, no_super: bool = True ) -> EChanges:
    """
    Creates the N-rooted fusion graph.
    :param cutoff:      Cutoff on consensus 
    :param dirty:       Leave graph dirty. You don't want this.
                        Turn it off to see how the NRFG is fused together. 
    :param no_super:    Drop supersets from trees. You want this.
                        Turn if off to see the supersets in the final graph (your NRFG will therefore be a disjoint union of multiple possibilities).
    """
    model = global_view.current_model()
    
    nrfg.create_nrfg( model, cutoff = cutoff, clean = not dirty, no_super = no_super )
    
    MCMD.progress( "NRFG created OK." )
    
    return EChanges.MODEL_DATA
