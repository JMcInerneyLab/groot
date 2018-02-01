from typing import Sequence, Tuple
from os import path

import re

from groot.constants import EFormat
from intermake import MENV, Theme
from mgraph import DNodeToText, MNode, MGraph
from mhelper import SwitchError, ansi, file_helper, array_helper

from groot.algorithms.classes import FusionPoint, FusionEvent
from groot.data.lego_model import LegoSequence, LegoComponent, ILeaf
from groot.frontends.cli import cli_view_utils
from groot.frontends import ete_providers
from groot.data import user_options


NEXT_SPECIAL = "["
END_SPECIAL = "]"
END_SKIP = "|"


class __Formatter:
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
            return "S{}".format( node.data.id )
    
    
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


def create( format_str, graphs: Sequence[Tuple[str, MGraph]], model, mode ) -> str:
    text = []
    
    if mode == EFormat.VISJS:
        text.append( create_vis_js( format_str, [x[1] for x in graphs], model ) )
    else:
        formatter = create_user_formatter( format_str )
        
        for name, tree in graphs:
            if name:
                text.append( print_header( name ) )
            
            if mode == EFormat.ASCII:
                text.append( tree.to_ascii( formatter ) )
            elif mode == EFormat.ETE_ASCII:
                text.append( ete_providers.tree_to_ascii( tree, model, formatter ) )
            elif mode == EFormat.DEBUG:
                text.append( tree_to_debug( model, tree ) )
            elif mode == EFormat.NEWICK:
                text.append( tree.to_newick( formatter ) )
            elif mode == EFormat.ETE_GUI:
                ete_providers.show_tree( tree, model, formatter )
            elif mode == EFormat.SVG:
                text.append( tree.to_svg( formatter ) )
            elif mode == EFormat.HTML:
                text.append( tree.to_svg( formatter, html = True ) )
            elif mode == EFormat.CSV:
                text.append( tree.to_csv( formatter ) )
            else:
                raise SwitchError( "mode", mode )
    
    return "\n".join( text )


def create_vis_js( format_str, graphs: Sequence[MGraph], model, title = True ) -> str:
    if title:
        prefix = "<p><b>$(TITLE)</b></p><p>$(COMMENT)</p>"
    else:
        prefix = ""
    
    HTML_T = file_helper.read_all_text( path.join( file_helper.get_directory( __file__, ), "vis_js_template.html" ) )
    HTML_T = HTML_T.replace( "$(PREFIX)", prefix )
    HTML_T = HTML_T.replace( "$(TITLE)", MENV.name + " - " + model.name )
    HTML_T = HTML_T.replace( "$(PATH)", user_options.options().visjs_path )
    HTML_T = HTML_T.replace( "$(COMMENT)", "File automatically generated by Groot. Please replace this line with your own description." )
    
    r = []
    formatter = create_user_formatter( format_str, ansi = False )
    
    all_nodes = [λnode for λgraph in graphs for λnode in λgraph.nodes]
    all_edges = [λedge for λgraph in graphs for λedge in λgraph.edges]
    
    nodes = array_helper.create_index_lookup( all_nodes )
    
    for node, node_id in nodes.items():
        if isinstance( node.data, LegoSequence ):
            component = model.components.find_component_for_major_sequence( node.data )
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
            colour = colours[component.index % len( colours )]
        elif isinstance( node.data, FusionPoint ):
            colour = "#FF0000"
        else:
            colour = "#FFFFC0"
        
        r.append( "{{shape:'box', id: {}, label: '{}', color: '{}'}},".format( node_id,
                                                                               formatter( node ),
                                                                               colour ) )
    HTML_T = HTML_T.replace( "$(NODES)", "\n".join( r ) )
    r = []
    
    for edge in all_edges:
        r.append( "{{from: {}, to: {}, arrows:'to'}},".format( nodes[edge.left],
                                                               nodes[edge.right] ) )
    
    HTML_T = HTML_T.replace( "$(EDGES)", "\n".join( r ) )
    return HTML_T


def print_header( x ):
    if isinstance( x, LegoComponent ):
        x = "COMPONENT {}".format( x )
    
    return "\n" + Theme.TITLE + "---------- {} ----------".format( x ) + Theme.RESET


def tree_to_debug( model, tree ):
    rx = []
    r = re.compile( ":[0-9.]+" )
    for line in tree.import_info:
        line = r.sub( "", line )
        for s in sorted( model.sequences, key = lambda x: -len( str( x.id ) ) ):
            line = line.replace( "S{}".format( s.id ), s.accession )
        rx.append( line )
    rrx = "\n".join( rx )
    return rrx
