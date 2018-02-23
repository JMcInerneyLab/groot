import re
from os import path
from typing import Sequence, Tuple, Optional

import itertools

import groot.data.global_view
from groot.algorithms.classes import FusionPoint
from groot.constants import EFormat
from groot.data.lego_model import ILeaf, LegoComponent, LegoSequence, LegoModel
from groot.frontends import ete_providers
from groot.frontends.cli import cli_view_utils
from intermake import MENV, Theme
from mgraph import DNodeToText, MGraph, MNode
from mhelper import SwitchError, ansi, array_helper, file_helper


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
        text.append( create_vis_js( format_str, graphs, model ) )
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


def create_vis_js( format_str: Optional[str], names_and_graphs: Sequence[Tuple[str, MGraph]], model: LegoModel, inline_title: bool = True, title: str = None ) -> str:
    """
    Creates a vis.js html file, to view a graph.
     
    :param format_str:          String describing how the nodes are formatted. See `specify_graph_help` for details. 
    :param names_and_graphs:    Sequence of graphs. See `create`. 
    :param model:               Source model 
    :param inline_title:        When `True` a heading is added to the page. 
    :param title:               The title of the page. When `None` a default title is suggested.
                                Note that the title will always show in the title bar, even if `inline_title` is `False`. 
    :return:                    A string containing the HTML. 
    """
    # Page heading
    if inline_title:
        prefix = "<p><b>$(TITLE)</b></p><p>$(COMMENT)</p>"
    else:
        prefix = ""
    
    # Page title
    include_labels = len( names_and_graphs ) != 1
    
    if not title:
        title = MENV.name + " - " + model.name
        
        if not include_labels:
            title += " - " + names_and_graphs[0][0]
    
    # Get graph information
    graphs = [x[1] for x in names_and_graphs]
    all_nodes = [λnode for λgraph in graphs for λnode in λgraph.nodes]
    all_edges = [λedge for λgraph in graphs for λedge in λgraph.edges]
    nodes = array_helper.create_index_lookup( itertools.chain( all_nodes, names_and_graphs ) )
    node_to_string = create_user_formatter( format_str, ansi = False )
    
    # Add the nodes
    node_list = []
    
    for node, node_id in nodes.items():
        if isinstance( node, MNode ):
            # Nodes...
            if isinstance( node.data, LegoSequence ):
                # ...gene
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
                shape = 'box'
            elif isinstance( node.data, FusionPoint ):
                # ...fusion
                colour = "#FF0000"
                shape = 'star'
            elif node.data is None:
                # ...clade
                colour = "#FFFFFF"
                shape = 'circle'
            else:
                # ...something else :(
                raise SwitchError( "node.data", node.data, instance = True )
            
            node_list.append( "{{shape:'{}', id: {}, label: '{}', color: '{}'}},".format( shape,
                                                                                          node_id,
                                                                                          node_to_string( node ),
                                                                                          colour ) )
        elif isinstance( node, tuple ):
            # Labels...
            name, graph = node
            
            if include_labels:
                node_list.append( "{{shape:'text', id: {}, label: '{}', color: '#FFFFC0', font:{{size:32}}}},".format( node_id, name ) )
        else:
            # Something else...
            raise SwitchError( "node", node, instance = True )
    
    # Add the edges
    edge_list = []
    
    for edge in all_edges:
        edge_list.append( "{{from: {}, to: {}, color:{{color:'#000000'}}}},".format( nodes[edge.left],
                                                                                     nodes[edge.right] ) )
    
    # Fake edges to the labels
    for name_graph in names_and_graphs:
        if include_labels:
            node_id_1 = nodes[name_graph[1].first_node]
            node_id_2 = nodes[name_graph]
            edge_list.append( "{{from: {}, to: {}, dashes:'true', color:{{color:'#C0C0C0'}}, smooth:{{enabled:'false'}}}},".format( node_id_1, node_id_2 ) )
    
    # Output the page
    HTML_T = file_helper.read_all_text( path.join( file_helper.get_directory( __file__, ), "vis_js_template.html" ) )
    HTML_T = HTML_T.replace( "$(PREFIX)", prefix )
    HTML_T = HTML_T.replace( "$(TITLE)", title )
    HTML_T = HTML_T.replace( "$(PATH)", path.join( groot.data.global_view.options().visjs_path, "" ) if groot.data.global_view.options().visjs_path else "" )
    HTML_T = HTML_T.replace( "$(COMMENT)", "File automatically generated by Groot. Please replace this line with your own description." )
    HTML_T = HTML_T.replace( "$(NODES)", "\n".join( node_list ) )
    HTML_T = HTML_T.replace( "$(EDGES)", "\n".join( edge_list ) )
    return HTML_T


def print_header( x ):
    if isinstance( x, LegoComponent ):
        x = "COMPONENT {}".format( x )
    
    return "\n" + Theme.TITLE + "---------- {} ----------".format( x ) + Theme.RESET


def tree_to_debug( model: LegoModel, tree: MGraph ) -> str:
    """
    Debugging feature only.
    Gets a description of the `import_info` for a tree.
    """
    rx = []
    r = re.compile( ":[0-9.]+" )
    for line in tree.import_info:
        line = r.sub( "", line )
        for s in sorted( model.sequences, key = lambda x: -len( str( x.id ) ) ):
            assert isinstance( s, LegoSequence )
            line = line.replace( s.legacy_accession, s.accession )
        rx.append( line )
    rrx = "\n".join( rx )
    return rrx
