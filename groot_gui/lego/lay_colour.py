from random import randint
from typing import Callable, cast

from PyQt5.QtGui import QColor

import groot
import mhelper_qt
from groot_gui.lego import ColourBlock, DomainView, ModelView
from mhelper import Sentinel, array_helper


DAlgorithm = Callable[[DomainView], frozenset]
colour_algorithms = groot.AlgorithmCollection( DAlgorithm, "LegoColour" )

DEFAULT_COLOURS = ["#C00000", "#00C000", "#C0C000", "#0000C0", "#C000C0", "#00C0C0", "#FF0000", "#00FF00", "#FFFF00", "#0000FF", "#FF00FF", "#00FFC0"]
"""Default colours to use. After this runs out, random colours are used."""


def apply_colour( model_view: ModelView, algorithm: colour_algorithms.Algorithm ):
    algorithm( model_view )
    model_view.save_all_states()


def get_legend( model_view: ModelView ):
    r = ["<html><body><ul>"]
    
    for set_, colour in model_view.legend.items():
        if len( set_ ) == 1:
            txt = str( array_helper.single( set_ ) )
        else:
            txt = "<ul>" + "".join( sorted( "<li>{}</li>".format( x ) for x in set_ ) ) + "</ul>"
        r.append( '<li><span style="background: {}">&nbsp;&nbsp;&nbsp;&nbsp;</span> - {}</li>'.format( colour.colour.name(), txt ) )
    
    r.append( "</ul></body></html>" )
    return "".join( r )


def __apply_colour_by_set( model_view: ModelView, function: Callable[[DomainView], frozenset] ):
    for domain_view in __get_apply_selection( model_view ):
        set_: frozenset = function( domain_view )
        
        if not set_:
            colour = ColourBlock( mhelper_qt.Colours.GRAY )
        else:
            colour = model_view.legend.get( set_ )
            
            if colour is None:
                index = len( model_view.legend )
                
                if index < len( DEFAULT_COLOURS ):
                    col = QColor( DEFAULT_COLOURS[index] )
                else:
                    col = QColor( randint( 0, 255 ), randint( 0, 255 ), randint( 0, 255 ) )
                
                colour = ColourBlock( col )
                model_view.legend[set_] = colour
        
        domain_view.colour = colour
    
    # Remove unused legend items:
    remove = []
    for k, v in model_view.legend.items():
        for udv in model_view.domain_views.values():
            if udv.colour is v:
                break
        else:
            remove.append( k )
    for key in remove:
        del model_view.legend[key]


def __get_apply_selection( model_view: ModelView ):
    if not model_view.selection:
        return model_view.domain_views.values()
    else:
        return [model_view.domain_views[x] for x in model_view.selection]


@colour_algorithms.register( "colour_by_major_component" )
def __colour_major( model_view: ModelView ) -> None:
    fn = lambda x: frozenset( (model_view.model.components.find_component_for_major_gene( cast( DomainView, x ).domain.gene, default = None ),) )
    __apply_colour_by_set( model_view, fn )


@colour_algorithms.register( "colour_by_minor_component" )
def __colour_minor( model_view: ModelView ) -> None:
    fn = lambda x: frozenset( model_view.model.components.find_components_for_minor_domain( cast( DomainView, x ).domain ) )
    __apply_colour_by_set( model_view, fn )


@colour_algorithms.register( "colour_by_minor_component_formed" )
def __colour_minor( model_view: ModelView ) -> None:
    valid = set()
    
    for fus in model_view.model.fusions:
        valid.add( fus.component_out )
    
    fn = lambda x: frozenset( model_view.model.components.find_components_for_minor_domain( cast( DomainView, x ).domain ) ) - valid
    __apply_colour_by_set( model_view, fn )


@colour_algorithms.register( "colour_by_sequence" )
def __colour_sequence( model_view: ModelView ) -> None:
    fn = lambda x: frozenset( (cast( DomainView, x ).domain.gene,) )
    __apply_colour_by_set( model_view, fn )


@colour_algorithms.register( "colour_by_edges" )
def __colour_edges( model_view: ModelView ) -> None:
    fn = lambda x: frozenset( model_view.model.edges.iter_touching( (cast( DomainView, x ).domain,) ) )
    __apply_colour_by_set( model_view, fn )


@colour_algorithms.register( "colour_by_domains" )
def __colour_domains( model_view: ModelView ) -> None:
    fn = lambda x: frozenset( (cast( DomainView, x ).domain,) )
    __apply_colour_by_set( model_view, fn )


@colour_algorithms.register( "colour_unique" )
def __colour_unique( model_view: ModelView ) -> None:
    xx = Sentinel( "Unique" )  # Unique for this run only
    fn = lambda x: frozenset( (xx,) )
    __apply_colour_by_set( model_view, fn )
