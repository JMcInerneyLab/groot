from typing import Callable

import groot
from groot_gui.lego import ModelView
from groot_gui.utilities.selection import LegoSelection
from mhelper import exception_helper


DAlgorithm = Callable[[ModelView], None]
selection_algorithms = groot.AlgorithmCollection( DAlgorithm, "LegoSelection" )


def apply_select( model_view: ModelView, algorithm: selection_algorithms.Algorithm ):
    algorithm( model_view )


def select_by_selection( model_view: ModelView, intent: LegoSelection ):
    selection = set( model_view.selection )
    assert isinstance( intent, LegoSelection )
    
    sel = intent.single
    
    if isinstance( sel, groot.Gene ):
        for domain_view in model_view.domain_views.values():
            if domain_view.domain.gene is sel:
                selection.add( domain_view.domain )
    elif isinstance( sel, groot.Domain ):
        selection.update( x.domain for x in model_view.find_userdomain_views_for_domain( sel ) )
    else:
        raise exception_helper.SwitchError( "sel", sel, instance = True )
    
    if not selection:
        raise ValueError( "Could not find the element." )
    
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
