from intermake import pr
from mgraph import MGraph
from mhelper import isFilename, isOptional, SwitchError, io_helper
from typing import Callable, List, Optional

from groot import constants
from groot.application import app
from groot.constants import EFormat, EChanges
from groot.data import EPosition, ESiteType, INamedGraph, Component, Model, Gene, global_view
from groot.utilities import AlgorithmCollection, cli_view_utils, external_runner, graph_viewing, lego_graph


DAlgorithm = Callable[[Model, str], str]
"""A delegate for a function that takes a model and aligned FASTA data, and produces a tree, in Newick format."""

tree_algorithms = AlgorithmCollection( DAlgorithm, "Tree" )


@app.command( folder = constants.F_CREATE )
def create_trees( algorithm: tree_algorithms.Algorithm, components: Optional[List[Component]] = None ) -> None:
    """
    Creates a tree from the component.
    Requisites: `create_alignments`
    
    :param algorithm:   Algorithm to use. See `algorithm_help`.
    :param components:   Component, or `None` for all.
    
    :returns: Nothing, the tree is set as the component's `tree` field. 
    """
    # Get the current model
    model = global_view.current_model()
    
    # Get the site type
    if model.site_type == ESiteType.DNA:
        site_type = "n"
    elif model.site_type == ESiteType.PROTEIN:
        site_type = "p"
    else:
        raise SwitchError( "site_type", model.site_type )
    
    # Get the components
    components = cli_view_utils.get_component_list( components )
    
    # Assert that we are in a position to create the trees
    model.get_status( constants.STAGES.TREES_8 ).assert_create()
    assert all( x.alignment is not None for x in components ), "Cannot generate the tree because the alignment has not yet been specified."
    assert all( x.tree is None for x in components ), "Cannot generate the tree because the tree has already been generated."
    
    # Iterate the components
    for component in pr.pr_iterate( components, "Generating trees" ):
        # Handle the edge cases for a tree of three or less
        num_genes = len( component.minor_genes )
        if num_genes <= 3:
            if num_genes == 1:
                newick = "({});"
            elif num_genes == 2:
                newick = "({},{});"
            elif num_genes == 3:
                newick = "(({},{}),{});"
            else:
                raise SwitchError( "num_genes", num_genes )
            
            newick = newick.format( *(x.legacy_accession for x in component.minor_genes) )
        else:
            # Run the algorithm normally
            newick = external_runner.run_in_temporary( algorithm, site_type, component.alignment )
        
        # Set the tree on the component
        set_tree( component, newick )
    
    # Show the completion message
    after = sum( x.tree is not None for x in model.components )
    pr.printx( "<verbose>{} trees generated. {} of {} components have a tree.</verbose>".format( len( components ), after, len( model.components ) ) )
    return EChanges.COMP_DATA


@app.command( folder = constants.F_SET )
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
    
    _force_set_tree( component, newick )
    
    return EChanges.COMP_DATA


def _force_set_tree( component, newick ):
    component.tree_newick = newick
    component.tree_unrooted = lego_graph.import_newick( newick, component.model )
    component.tree = component.tree_unrooted.copy()
    reposition_tree( component.tree )
    component.tree_unmodified = component.tree.copy()


@app.command( folder = constants.F_DROP )
def drop_trees( components: Optional[List[Component]] = None ) -> bool:
    """
    Removes component tree(s).
    
    :param components:   Component(s), or `None` for all. 
    """
    components = cli_view_utils.get_component_list( components )
    count = 0
    
    for component in components:
        if component.model.get_status( constants.STAGES.FUSIONS_9 ):
            raise ValueError( "Refusing to drop the tree because fusions have already been recorded. Did you mean to drop the fusions first?" )
        
        if component.tree is not None:
            component.tree = None
            component.tree_unrooted = None
            component.tree_newick = None
            count += 1
    
    pr.printx( "<verbose>{} trees removed across {} components.</verbose>".format( count, len( components ) ) )
    return EChanges.COMP_DATA


@app.command( folder = constants.F_PRINT )
def print_trees( graph: Optional[INamedGraph] = None,
                 format: EFormat = EFormat.ASCII,
                 file: isOptional[isFilename] = None,
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
        print( "Available graphs:" )
        is_any = False
        for named_graph in model.iter_graphs():
            is_any = True
            print( type( named_graph ).__name__.ljust( 20 ) + named_graph.name )
        if not is_any:
            print( "(None available)" )
        print( "(arbitrary)".ljust( 20 ) + "(see `format_help`)" )
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
