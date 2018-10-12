"""
Converts Lego entities to HTML.
"""
from typing import List

import groot.data.config

from mhelper_qt import qt_gui_helper

from groot.data import Model, IHasFasta, INamedGraph, Report
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
    elif isinstance( item, IHasFasta ):
        render_fasta( html, item, model )
    
    # Anything with metadata
    else:
        import intermake_qt
        html.append( intermake_qt.visualisation.visualisable_to_html( item, header = False ) )
    
    html.append( "</body></html>" )
    
    return "\n".join( html )


def render_tree( html: HTML, item: INamedGraph, model: Model ):
    if not isinstance( item, INamedGraph ) or item.graph is None:
        return
    
    visjs = graph_viewing.create( format_str = None,
                                  graph = item,
                                  model = model,
                                  format = groot.data.config.options().gui_tree_view )
    
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
