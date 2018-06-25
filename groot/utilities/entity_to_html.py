"""
Converts Lego entities to HTML.
"""
from typing import List
from intermake import VisualisablePath
from mhelper import array_helper, string_helper
from mhelper_qt import qt_gui_helper

from groot.data import Model, IHasFasta, INamedGraph, Report, global_view
from groot.utilities import cli_view_utils, graph_viewing


HTML = List[str]
_ANSI_SCHEME = qt_gui_helper.ansi_scheme_light( family = 'monospace' )


def render( item, model: Model ):
    # A report (with HTML)
    if isinstance( item, Report ):
        return item.html
    
    html = []
    
    html.append( "<html><head><title>{}</title></head><body>".format( str( item ) ) )
    html.append( '<h2>{}</h2>'.format( str( item ) ) )
    
    # Trees and graphs
    if isinstance( item, INamedGraph ):
        render_tree( html, item, model )
    
    # Anything with FASTA
    if isinstance( item, IHasFasta ):
        render_fasta( html, item, model )
    
    # Anything with metadata
    render_visualisable( html, item )
    
    html.append( "</body></html>" )
    
    return "\n".join( html )


def render_visualisable( html: HTML, item: object ):
    html.append( "<h3>Data table</h3>" )
    vi = VisualisablePath.from_visualisable_temporary( item )
    
    html.append( "<table>" )
    for i, x in enumerate( vi.iter_children() ):
        html.append( "<tr>" )
        html.append( '<td style="background:#E0E0E0">' )
        html.append( str( x.key ) )
        html.append( "</td>" )
        html.append( '<td style="background:{}">'.format( "#E0FFE0" if (i % 2 == 0) else "#D0FFD0" ) )
        v = x.value
        if array_helper.is_simple_iterable( v ):
            text2 = string_helper.format_array( v )
        else:
            text2 = str( v )
        
        text2 = string_helper.max_width( text2, 100 )
        
        html.append( text2.replace( "\n", "<br/>" ) )
        html.append( "</td>" )
        html.append( "</tr>" )
    html.append( "</table>" )


def render_tree( html: HTML, item: INamedGraph, model: Model ):
    if not isinstance( item, INamedGraph ) or item.graph is None:
        return
    
    visjs = graph_viewing.create( format_str = None,
                                  graph = item,
                                  model = model,
                                  format = global_view.options().gui_tree_view )
    
    visjs = visjs.replace( "</body>", "" )
    visjs = visjs.replace( "</html>", "" )
    
    html.clear()
    html.append( visjs )


def render_fasta( html: HTML, item: IHasFasta, model: Model ):
    if not isinstance( item, IHasFasta ):
        return
    
    html.append( "<h3>FASTA</h3>" )
    html.append( __get_fasta( item.to_fasta(), model ) )


def __get_fasta( fasta, model ):
    return qt_gui_helper.ansi_to_html( cli_view_utils.colour_fasta_ansi( fasta, model.site_type ), _ANSI_SCHEME )
