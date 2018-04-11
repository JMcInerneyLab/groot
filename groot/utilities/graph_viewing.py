from typing import Optional

from groot.constants import EFormat
from groot.data import lego_graph
from groot.data.lego_model import INamedGraph, LegoComponent, LegoModel
from groot.frontends import ete_providers
from intermake import Theme
from mgraph import MNode, exporting
from mgraph.exporting import EShape, NodeStyle
from mhelper import SwitchError


NEXT_SPECIAL = "["
END_SPECIAL = "]"
END_SKIP = "|"


def create( format_str: Optional[str], graph: INamedGraph, model: LegoModel, format: EFormat ) -> str:
    """
    Converts a graph or set of graphs to its string representation. 
    :param format_str:   String describing how the nodes are formatted. See `specify_graph_help` for details.
    :param graph:        Graph to output 
    :param model:        Source model
    :param format:         Output format 
    :return:             The string representing the graph(s)
    """
    text = []
    
    
    def __lego_style( node: MNode ) -> NodeStyle:
        if lego_graph.is_fusion_like( node ):
            background = "#FF0000"
            shape = EShape.STAR
        elif lego_graph.is_sequence_node( node ):
            background = None
            shape = EShape.BOX
        else:
            background = "#FFFFFF"
            shape = EShape.ELLIPSE
        
        return NodeStyle.default( node = node,
                                  format_str = format_str,
                                  background = background,
                                  shape = shape )
    
    
    if format == EFormat.VISJS:
        text.append( exporting.export_vis_js( graph.graph, fnode = __lego_style, title = graph.name ) )
    elif format == EFormat.COMPACT:
        text.append( exporting.export_compact( graph.graph, fnode = __lego_style ) )
    elif format == EFormat.CYJS:
        text.append( exporting.export_cytoscape_js( graph.graph, fnode = __lego_style, title = graph.name ) )
    elif format == EFormat.ASCII:
        text.append( exporting.export_ascii( graph.graph, fnode = __lego_style ) )
    elif format == EFormat.ETE_ASCII:
        text.append( ete_providers.tree_to_ascii( graph.graph, model, fnode = __lego_style ) )
    elif format == EFormat.NEWICK:
        text.append( exporting.export_newick( graph.graph, fnode = __lego_style ) )
    elif format == EFormat.ETE_GUI:
        ete_providers.show_tree( graph.graph, model, fnode = __lego_style )
    elif format == EFormat.CSV:
        text.append( exporting.export_edgelist( graph.graph, fnode = __lego_style ) )
    elif format == EFormat.TSV:
        text.append( exporting.export_edgelist( graph.graph, fnode = __lego_style, delimiter = "\t" ) )
    elif format == EFormat.SVG:
        text.append( exporting.export_svg( graph.graph, fnode = __lego_style, title = graph.name, html = True ) )
    else:
        raise SwitchError( "format", format )
    
    return "\n".join( text )


def print_header( x ):
    if isinstance( x, LegoComponent ):
        x = "COMPONENT {}".format( x )
    
    return "\n" + Theme.TITLE + "---------- {} ----------".format( x ) + Theme.RESET
