from typing import Optional, Sequence, Tuple, Union

import mgvis
from intermake import Theme
from mgraph import DNodeToText, MGraph, MNode, NodeStyle, exporting, UNodeToText
from mhelper import SwitchError, ansi

from groot.constants import EFormat
from groot.data import global_view
from groot.data.lego_model import ILeaf, LegoComponent, LegoModel, LegoSequence, FusionPoint
from groot.frontends import ete_providers
from groot.frontends.cli import cli_view_utils


NEXT_SPECIAL = "["
END_SPECIAL = "]"
END_SKIP = "|"


class __Formatter:
    """
    Contains the set of functions used to provide a descriptive label for graph nodes.
    """
    
    
    def pipe( self, _: MNode ) -> str:
        """
        Pipe symbol (`|`)
        """
        return END_SKIP
    
    
    def lbr( self, _: MNode ) -> str:
        """
        Left bracket (`[`)
        """
        return NEXT_SPECIAL
    
    
    def rbr( self, _: MNode ) -> str:
        """
        Right bracket (`]`)
        """
        return END_SPECIAL
    
    
    def name( self, node: MNode ) -> str:
        """
        Name of the sequence, fusion, or clade, prefixed with `seq:`, `fus:` or `cla:` respectively
        """
        if isinstance( node.data, LegoSequence ):
            return "seq:{}".format( node.data.accession )
        elif isinstance( node.data, FusionPoint ):
            return "fus:{}:{}".format( node.data.opposite_component, node.data.count )
        else:
            return "cla:{}".format( node.uid )
    
    
    def uid( self, node: MNode ) -> str:
        """
        Node internal ID.
        """
        return str( node.uid )
    
    
    def short( self, node: MNode ) -> str:
        """
        Name of the sequence or fusion, or clade, prefixed with `⊕ `, `⊛ ` respectively.
        Clades are denoted by `⊙` and the name is not shown.
        """
        if isinstance( node.data, LegoSequence ):
            return "⊕ {}".format( node.data.accession )
        elif isinstance( node.data, FusionPoint ):
            return "⊛ {}".format( str( node.data ) )
        else:
            return "⊙"
    
    
    def colour_graph( self, node: MNode ) -> str:
        """
        Nodes to text, including ANSI colours.
        """
        d = node.data
        
        if isinstance( d, LegoSequence ):
            return "⊕ " + ansi.FORE_BLACK + cli_view_utils.component_to_ansi_back( d.model.components.find_component_for_major_sequence( d ) ) + str( d ) + ansi.FORE_RESET + ansi.BACK_RESET
        elif isinstance( d, FusionPoint ):
            return "⊛ " + ansi.BOLD + ansi.BACK_BRIGHT_WHITE + ansi.FORE_BLACK + str( d ) + ansi.RESET
        else:
            return "⊙ " + ansi.ITALIC + ansi.FORE_YELLOW + str( node ) + ansi.RESET
    
    
    def fusion_name( self, node: MNode ) -> str:
        """
        Name of the fusion, or empty if not a fusion.
        """
        if isinstance( node.data, FusionPoint ):
            return Theme.BOLD + str( node.data ) + Theme.RESET
    
    
    def component_name( self, node: MNode ) -> str:
        """
        Name of the component of the sequence, or empty if not a sequence or the sequence has no component.
        """
        if isinstance( node.data, LegoSequence ) and node.data.component:
            return str( node.data.component )
    
    
    def minor_component_names( self, node: MNode ) -> str:
        """
        Name of the minor components of the sequence, or empty if not a sequence or the sequence has no component.
        """
        if isinstance( node.data, LegoSequence ):
            minor_components = node.data.minor_components()
            
            if minor_components:
                for minor_component in sorted( minor_components, key = str ):
                    return str( minor_component )
    
    
    def sequence_accession( self, node: MNode ) -> str:
        """
        Accession of the sequence, or empty if not a sequence.
        """
        if isinstance( node.data, LegoSequence ):
            return node.data.accession
    
    
    def sequence_length( self, node: MNode ) -> str:
        """
        Length of the sequence, or empty if not a sequence.
        """
        if isinstance( node.data, LegoSequence ):
            return str( node.data.length )
    
    
    def sequence_internal_id( self, node: MNode ) -> str:
        """
        Internal ID of the sequence, or empty if not a sequence.
        """
        if isinstance( node.data, LegoSequence ):
            return node.data.id
    
    
    def prefixed_sequence_internal_id( self, node: MNode ) -> str:
        """
        Internal ID of the sequence, prefixed with an "S", or empty if not a sequence.
        """
        if isinstance( node.data, LegoSequence ):
            return node.data.legacy_accession
    
    
    def is_sequence( self, node: MNode ) -> bool:
        """
        Skips the text until the next `|` if this node is a sequence.
        """
        return isinstance( node.data, LegoSequence )
    
    
    def is_not_sequence( self, node: MNode ) -> bool:
        """
        Skips the text until the next `|` if this node is not a sequence.
        """
        return not isinstance( node.data, LegoSequence )
    
    
    def is_fusion( self, node: MNode ) -> bool:
        """
        Skips the text until the next `|` if this node is a fusion.
        """
        return isinstance( node.data, FusionPoint )
    
    
    def is_not_fusion( self, node: MNode ) -> bool:
        """
        Skips the text until the next `|` if this node is not a fusion.
        """
        return not isinstance( node.data, FusionPoint )
    
    
    def is_clade( self, node: MNode ) -> bool:
        """
        Skips the text until the next `|` if this node is a clade.
        """
        return not isinstance( node.data, ILeaf )
    
    
    def is_not_clade( self, node: MNode ) -> bool:
        """
        Skips the text until the next `|` if this node is not a clade.
        """
        return isinstance( node.data, ILeaf )


FORMATTER = __Formatter()
"""The singleton instance of the __Formatter"""


def create_user_formatter( format_str: str = None, ansi: bool = True ) -> DNodeToText:
    """
    Creates a formatter function based on the specified format string.
    
    The format strings are specified as follows: 
    
    `[xxx]`         - use special entry xxx (taken from __Formatter's methods)
    `|`             - stop skipping a section (after __Formatter's methods that return a bool)
                      if not in a section this character is ignored
    anything else   - verbatim
    """
    if not format_str:
        if ansi:
            return FORMATTER.colour_graph
        else:
            return FORMATTER.short
    
    return (lambda x: lambda n: __format_node( n, x ))( format_str )


def __format_node( node: MNode, format_str: str ) -> str:
    """
    Describes the nodes. 
    See `create_user_formatter` for format details.
    
    :param node: Node to format
    :param format_str: Format to use. 
    """
    ss = []
    skip = False
    special = False
    special_ss = []
    
    for x in format_str:
        if x == END_SKIP:
            skip = False
        elif skip:
            pass
        elif not special:
            if x == NEXT_SPECIAL:
                special_ss.clear()
                special = True
            else:
                ss.append( x )
        else:
            if x == END_SPECIAL:
                special_str = "".join( special_ss )
                method = getattr( FORMATTER, special_str )
                result = method( node )
                
                if isinstance( result, str ):
                    ss.append( result )
                elif result is False:
                    skip = True
                elif result is True:
                    skip = False
                else:
                    raise SwitchError( "result", result )
            else:
                special_ss.append( x )
    
    return "".join( str( x ) for x in ss ).strip()


def create( format_str: Optional[str], graphs: Sequence[Tuple[str, MGraph]], model: LegoModel, mode: EFormat ) -> str:
    """
    Converts a graph or set of graphs to its string representation. 
    :param format_str:   String describing how the nodes are formatted. See `specify_graph_help` for details.
    :param graphs:       Sequence of:
                            Tuple of:
                                1. Graph title, or `None` to not label the graph (e.g. if there is only one graph).
                                2. Graph itself 
    :param model:        Source model
    :param mode:         Output format 
    :return:             The string representing the graph(s)
    """
    text = []
    
    if mode == EFormat.VISJS:
        text.append( create_vis_js( graph = graphs, fnode = format_str ) )
    else:
        formatter = create_user_formatter( format_str )
        
        for name, tree in graphs:
            if name and len( graphs ) > 1:
                text.append( print_header( name ) )
            
            if mode == EFormat.ASCII:
                text.append( exporting.export_ascii( tree, fnode = formatter ) )
            elif mode == EFormat.ETE_ASCII:
                text.append( ete_providers.tree_to_ascii( tree, model, formatter ) )
            elif mode == EFormat.NEWICK:
                text.append( exporting.export_newick( tree, fnode = formatter ) )
            elif mode == EFormat.ETE_GUI:
                ete_providers.show_tree( tree, model, formatter )
            elif mode == EFormat.CSV:
                text.append( exporting.export_edgelist( tree, fnode = formatter ) )
            elif mode == EFormat.TSV:
                text.append( exporting.export_edgelist( tree, fnode = formatter, delimiter = "\t" ) )
            else:
                raise SwitchError( "mode", mode )
    
    return "\n".join( text )


def create_vis_js( graph: Union[MGraph, Sequence[MGraph], Sequence[Tuple[str, MGraph]]],
                   *,
                   fnode: UNodeToText = None,
                   inline_title: bool = False,
                   title: str = None,
                   rooted = True ):
    if global_view.options().visjs_component_view:
        node_styler = style_by_component
    else:
        node_styler = None
    
    return exporting.export_vis_js( graph = graph,
                                    visjs_path = mgvis.get_path(),
                                    fnode = fnode,
                                    inline_title = inline_title,
                                    title = title,
                                    rooted = rooted,
                                    node_styler = node_styler )


def style_by_component( style: NodeStyle ):
    if isinstance( style.node.data, LegoSequence ):
        # ...gene
        component = style.node.data.model.components.find_component_for_major_sequence( style.node.data )
        colours = ["#C0392B",
                   "#9B59B6",
                   "#2980B9",
                   "#1ABC9C",
                   "#27AE60",
                   "#F1C40F",
                   "#E74C3C",
                   "#8E44AD",
                   "#3498DB",
                   "#239B56",
                   "#16A085",
                   "#2ECC71",
                   "#F39C12",
                   "#D35400"]
        style.background = colours[component.index % len( colours )]


def print_header( x ):
    if isinstance( x, LegoComponent ):
        x = "COMPONENT {}".format( x )
    
    return "\n" + Theme.TITLE + "---------- {} ----------".format( x ) + Theme.RESET


