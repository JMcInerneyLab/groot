from intermake import MCMD, command
from mgraph import MGraph
from mhelper import Filename, MOptional, SwitchError, io_helper, string_helper
from typing import Callable, List, Optional

from groot import constants
from groot.constants import EFormat, EChanges
from groot.data import EPosition, ESiteType, INamedGraph, Component, Model, Gene, global_view
from groot.utilities import AlgorithmCollection, cli_view_utils, external_runner, graph_viewing, lego_graph

__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME

DAlgorithm = Callable[[Model, str], str]
"""A delegate for a function that takes a model and aligned FASTA data, and produces a tree, in Newick format."""

tree_algorithms = AlgorithmCollection( DAlgorithm, "Tree" )

@command(folder = constants.F_CREATE)
def create_trees( algorithm: tree_algorithms.Algorithm, components: Optional[List[Component]] = None ) -> None:
    """
    Creates a tree from the component.
    Requisites: `create_alignments`
    
    :param algorithm:   Algorithm to use. See `algorithm_help`.
    :param components:   Component, or `None` for all.
    
    :returns: Nothing, the tree is set as the component's `tree` field. 
    """
    model = global_view.current_model()
    model.get_status(constants.STAGES.TREES_6).assert_create()
    
    components=  cli_view_utils.get_component_list( components )
    assert all( x.alignment is not None for x in components )
    before = sum( x.tree is not None for x in model.components )
    
    for component in MCMD.iterate( components, "Generating trees", text = True ):
        if component.alignment is None:
            raise ValueError( "Cannot generate the tree because the alignment has not yet been specified." )
        
        if component.model.site_type == ESiteType.DNA:
            site_type = "n"
        elif component.model.site_type == ESiteType.PROTEIN:
            site_type = "p"
        else:
            raise SwitchError( "component.model.site_type", component.model.site_type )
        
        # Read the result
        newick = external_runner.run_in_temporary( algorithm, site_type, component.alignment )
        component.tree_unrooted = lego_graph.import_newick( newick, component.model )
        component.tree = component.tree_unrooted.copy()
        component.tree_newick = newick
        reposition_tree( component.tree )
    
    after = sum( x.tree is not None for x in model.components )
    MCMD.progress( "{} trees generated. {} of {} components have a tree ({}).".format( len( components ), after, len( model.components ), string_helper.as_delta( after - before ) ) )
    
    return EChanges.COMP_DATA

@command(folder = constants.F_SET)
def set_tree( component: Component, newick: str ) -> EChanges:
    """
    Sets a component tree manually.
    Note that if you have roots/outgroups set your tree may be automatically re-rooted to remain consistent with these settings.
    
    :param component:   Component 
    :param newick:      Tree to set. In Newick format. 
                        _Gene accessions_ and/or _gene internal IDs_ may be provided.
    """
    if component.tree:
        raise ValueError( "This component already has an tree. Did you mean to drop the existing tree first?" )
    
    component.tree_unrooted = lego_graph.import_newick( newick, component.model )
    component.tree = component.tree_unrooted.copy()
    component.tree_newick = newick
    reposition_all( global_view.current_model(), component )
    
    return EChanges.COMP_DATA
    
@command( names = ["drop_tree", "drop_trees"], folder = constants.F_DROP )
def drop_tree( components: Optional[List[Component]] = None ) -> bool:
    """
    Removes component tree(s).
    
    :param components:   Component(s), or `None` for all. 
    """
    components = cli_view_utils.get_component_list( components )
    count = 0
    
    for component in components:
        if component.model.get_status( constants.STAGES.FUSIONS_7 ):
            raise ValueError( "Refusing to drop the tree because fusions have already been recorded. Did you mean to drop the fusions first?" )
        
        if component.tree is not None:
            component.tree = None
            component.tree_unrooted = None
            component.tree_newick = None
            count += 1
    
    MCMD.progress( "{} trees removed across {} components.".format( count, len( components ) ) )
    return EChanges.COMP_DATA


@command( names = ["print_trees", "print_graphs", "trees", "graphs", "print"], folder=constants.F_PRINT )
def print_trees( graph: Optional[INamedGraph] = None,
                 format: EFormat = EFormat.ASCII,
                 file: MOptional[Filename] = None,
                 fnode: str = None
                 ) -> EChanges:
    """
    Prints trees or graphs.
    
    :param file:       File to write the output to. See `file_write_help`.
                       The default prints to the current display.
    :param graph:      What to print. See `format_help` for details.
    :param fnode:      How to format the nodes. See `print_help`.
    :param format:     How to view the tree.
    """
    model = global_view.current_model()
    
    if graph is None and file is None and format == EFormat.ASCII and fnode is None:
        MCMD.print( "Available graphs:" )
        is_any = False
        for named_graph in model.iter_graphs():
            is_any = True
            MCMD.print( type( named_graph ).__name__.ljust( 20 ) + named_graph.name )
        if not is_any:
            MCMD.print( "(None available)" )
        MCMD.print( "(arbitrary)".ljust( 20 ) + "(see `format_help`)" )
        return EChanges.INFORMATION
    
    if graph is None:
        raise ValueError( "Graph cannot be `None` when other parameters are set." )
    
    text = graph_viewing.create( fnode, graph, model, format )
    
    with io_helper.open_write( file, format.to_extension() ) as file_out:
        file_out.write( text + "\n" )
    
    return EChanges.INFORMATION



def reposition_all( model: Model, component: Optional[Component] = None ) -> List[Component]:
    """
    Repositions a component tree based on node.position data.
    """
    if model.fusions:
        raise ValueError( "Cannot reposition trees because they already have assigned fusion events. Maybe you meant to drop the fusion events first?" )
    
    components = [component] if component is not None else model.components
    changes = []
    
    for component_ in components:
        if component_.tree is None:
            continue
        
        if component_.tree is not None and reposition_tree( component_.tree ):
            changes.append( component_ )
    
    return changes


def reposition_tree( tree: MGraph ) -> bool:
    """
    Re-lays out a tree using `LegoSequence.position`.
    """
    for node in tree:
        d = node.data
        if isinstance( d, Gene ):
            if d.position == EPosition.OUTGROUP:
                node.make_outgroup()
                return True
            elif d.position == EPosition.NONE:
                pass
            else:
                raise SwitchError( "node.data.position", d.position )
    
    return False
