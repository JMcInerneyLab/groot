from typing import Callable, cast

from groot import data
from groot.utilities import  AlgorithmCollection
from groot_gui.lego import ModelView


DAlgorithm = Callable[[ModelView], None]
selection_algorithms = AlgorithmCollection( DAlgorithm, "selection_algorithms" )


def apply_select( model_view: ModelView, algorithm: selection_algorithms.Algorithm ):
    algorithm( model_view )


def select_by_entity( model_view: ModelView, target: object ):
    if isinstance( target, data.Gene ):
        predicate = (lambda x: cast( data.UserDomain, x ).gene is target)
    elif isinstance( target, data.Domain ):
        predicate = (lambda x: cast( data.UserDomain, x ).has_overlap( cast( data.Domain, target ) ))
    elif isinstance( target, data.Component ):
        comp = cast( data.Component, target )
        predicate = (lambda x: any( y.has_overlap( x ) for y in comp.minor_domains ))
    elif isinstance( target, data.Edge ):
        edge = cast( data.Edge, target )
        predicate = (lambda x: any( y.has_overlap( x ) for y in (edge.left, edge.right) ))
    else:
        return False
    
    selection = set()
    
    for domain in model_view.domain_views.keys():
        if predicate( domain ):
            selection.add( domain )
    
    model_view.selection = frozenset( selection )


@selection_algorithms.register( "select_full_sequence" )
def __select_sequence( model_view: ModelView ):
    selection = set( model_view.selection )
    
    ss = { x.gene for x in model_view.selection }
    
    for domain_view in model_view.domain_views.values():
        if domain_view.domain.gene in ss:
            selection.add( domain_view.domain )
    
    model_view.selection = frozenset( selection )


@selection_algorithms.register( "select_nothing" )
def __select_nothing( model_view: ModelView ):
    model_view.selection = frozenset()


@selection_algorithms.register( "select_major_siblings" )
def __select_major( model_view: ModelView ):
    selection = set( model_view.selection )
    
    major_components = { model_view.model.components.find_component_for_major_gene( x.gene ) for x in model_view.selection }
    
    for domain_view in model_view.domain_views.values():
        if any( domain_view.domain.gene in component.major_genes for component in major_components ):
            selection.add( domain_view.domain )
    
    model_view.selection = frozenset( selection )


@selection_algorithms.register( "select_minor_siblings" )
def __select_minor( model_view: ModelView ):
    selection = set( model_view.selection )
    
    minor_components = { model_view.model.components.find_components_for_minor_domain( x ) for x in model_view.selection }
    
    for domain_view in model_view.domain_views.values():
        if any( domain_view.domain in component.minor_domains for component in minor_components ):
            selection.add( domain_view.domain )
    
    model_view.selection = frozenset( selection )
