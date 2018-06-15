from typing import Optional
from intermake import Theme
from mgraph import MNode, exporting, MGraph, EShape, NodeStyle, UNodeToFormat
from mhelper import SwitchError
from colorama import Fore

from groot.constants import EFormat
from groot.data import Model, INamedGraph
from groot.utilities import lego_graph


NEXT_SPECIAL = "["
END_SPECIAL = "]"
END_SKIP = "|"


def create( format_str: Optional[str], graph: INamedGraph, model: Model, format: EFormat ) -> str:
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
        text.append( __ete_tree_to_ascii( graph.graph, model, fnode = __lego_style ) )
    elif format == EFormat.NEWICK:
        text.append( exporting.export_newick( graph.graph, fnode = __lego_style ) )
    elif format == EFormat.ETE_GUI:
        __ete_show_tree( graph.graph, model, fnode = __lego_style )
    elif format == EFormat.CSV:
        text.append( exporting.export_edgelist( graph.graph, fnode = __lego_style ) )
    elif format == EFormat.TSV:
        text.append( exporting.export_edgelist( graph.graph, fnode = __lego_style, delimiter = "\t" ) )
    elif format == EFormat.SVG:
        text.append( exporting.export_svg( graph.graph, fnode = __lego_style, title = graph.name, html = True ) )
    else:
        raise SwitchError( "format", format )
    
    return "\n".join( text )


def __ete_tree_to_ascii( target: MGraph, model: Model, fnode: UNodeToFormat ):
    ascii = __ete_tree_from_newick( exporting.export_newick( target, fnode = fnode ) ).get_ascii( show_internal = True )
    
    for sequence in model.genes:
        component = model.components.find_component_for_major_gene( sequence )
        colour = Theme.PROGRESSION_FORE[component.index % Theme.PROGRESSION_COUNT]
        ascii = ascii.replace( sequence.accession, colour + sequence.accession + Fore.RESET )
    
    return ascii


def __ete_show_tree( target: MGraph, model: Model, fnode: UNodeToFormat ):
    tree__ = __ete_tree_from_newick( exporting.export_newick( target, fnode = fnode ) )
    colours = ["#C00000", "#00C000", "#C0C000", "#0000C0", "#C000C0", "#00C0C0", "#FF0000", "#00FF00", "#FFFF00", "#0000FF", "#FF00FF", "#00FFC0"]
    
    for n in tree__.traverse():
        n.img_style["fgcolor"] = "#000000"
    
    for node in tree__:
        sequence = model.genes[node.name]
        component = model.components.find_component_for_major_gene( sequence )
        node.img_style["fgcolor"] = colours[component % len( colours )]
    
    tree__.show()


def __ete_tree_from_newick( newick: str ):
    try:
        # noinspection PyPackageRequirements
        from ete3 import Tree
    except ImportError as ex:
        raise ImportError( "You must `pip install ete3` in order to use Ete functionality." ) from ex
    
    try:
        return Tree( newick, format = 0 )
    except:
        try:
            return Tree( newick, format = 1 )
        except:
            raise ValueError( "Cannot understand this tree: {}".format( newick ) )
