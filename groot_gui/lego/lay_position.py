from typing import Callable, Iterable, List, cast, Dict

import groot
from groot_gui.lego import ModelView
from groot_gui.lego.views import EdgeView, DomainView


DAlgorithm = Callable[[ModelView], None]
position_algorithms = groot.AlgorithmCollection( DAlgorithm, "LegoPosition" )


def leftmost_per_gene( domain_views: Iterable[DomainView], rightmost : bool = False ) -> List[DomainView]:
    """
    Given a set of `domain_views` returns the set of views containing the leftmost view for each gene.
    """
    pg = { }
    
    cp = (lambda x, y: x > y) if rightmost else (lambda x, y: x < y) 
    
    for dv in domain_views:
        g = dv.domain.gene
        bdv: DomainView = pg.get( g )
        
        if bdv is None or cp(dv.domain.start, bdv.domain.start):
            pg[g] = dv
    
    return list( pg.values() )


def make_contiguous( domain_views: List[DomainView], backwards: bool = False ):
    """
    Positions the `domain_views` such that they all are positioned to follow their predecessor.
    """
    if not backwards:
        for domain_view in sorted( domain_views, key = lambda x: cast( DomainView, x ).domain.start ):
            if domain_view.sibling_previous:
                x = domain_view.sibling_previous.x() + domain_view.sibling_previous.rect.width()
                domain_view.setX( x )
                domain_view.save_state()
    else:
        for domain_view in sorted( domain_views, key = lambda x: cast( DomainView, x ).domain.start, reverse = True ):
            if domain_view.sibling_next:
                x = domain_view.sibling_next.x() - domain_view.rect.width()
                domain_view.setX( x )
                domain_view.save_state()


def make_extra_contiguous( model_view: ModelView, domain_views: List[DomainView] ):
    """
    Positions domains not in `domain_views` such that they are in-line with those in `domain_views`.
    """
    domain_views: Dict[groot.Gene, DomainView] = { x.domain.gene: x for x in leftmost_per_gene( domain_views ) }
    
    for gene, view in domain_views.items():
        left = [x for x in model_view.domain_views.values() if x.domain.gene is gene and x.domain.start < view.domain.start]
        right = [x for x in model_view.domain_views.values() if x.domain.gene is gene and x.domain.start > view.domain.start]
        
        make_contiguous( left, backwards = True )
        make_contiguous( right )


def apply_position( model_view: ModelView, algorithm: position_algorithms.Algorithm ):
    algorithm( model_view )
    model_view.save_all_states()


def get_views( model_view: ModelView, domains: Iterable[groot.UserDomain] ) -> List[DomainView]:
    return [model_view.domain_views[x] for x in domains]


def get_selection( model_view: ModelView ) -> List[DomainView]:
    return get_views( model_view, model_view.selection or model_view.all )


@position_algorithms.register( "align_all_domains_in_this_component" )
def pos_align_all_domains_in_this_component( model_view: ModelView ) -> None:
    """
    Repositions all domains in the same component as the selected domain to be in line.
    """
    sel = leftmost_per_gene( get_selection( model_view ) )
    
    if len( sel ) != 1:
        raise ValueError( "You must specify only one domain for this function to work." )
    
    sel_domain_view = sel[0]
    comp = model_view.model.components.find_components_for_minor_domain( sel_domain_view )
    valid = []
    
    for domain_view in model_view.domain_views.values():
        if domain_view.domain.gene is sel_domain_view.domain.gene:
            continue
        
        comp2 = model_view.model.components.find_components_for_minor_domain( sel_domain_view )
        
        if any( x in comp for x in comp2 ):
            valid.append( domain_view )
    
    valid: List[DomainView] = leftmost_per_gene( valid )
    
    for domain_view in valid:
        domain_view.setX( sel_domain_view.x() )
    
    make_extra_contiguous( model_view, valid )


@position_algorithms.register( "make_contiguous_around_selection" )
def pos_make_selection_contiguous( model_view: ModelView ):
    """
    Aligns domains next to the selected domains such that the view is contiguous.
    """
    make_extra_contiguous( model_view, get_selection( model_view ) )
    
@position_algorithms.register( "make_contiguous_within_selection" )
def pos_make_selection_contiguous( model_view: ModelView ):
    """
    Aligns the selected domains such that the view is contiguous (left first).
    """
    make_contiguous( get_selection( model_view ) )


@position_algorithms.register( "align_left" )
def position_align_left( model_view: ModelView ):
    """
    Aligns all selected domains left.
    """
    sel = leftmost_per_gene( get_selection( model_view ) )
    
    x = min( x.pos().x() for x in sel )
    
    for dom_view in sel:
        dom_view.setX( x )
        dom_view.save_state()
        
@position_algorithms.register( "align_right" )
def position_align_right( model_view: ModelView ):
    """
    Aligns all selected domains right.
    """
    sel = leftmost_per_gene( get_selection( model_view ), rightmost = True )
    
    x = max( x.pos().x() for x in sel )
    
    for dom_view in sel:
        dom_view.setX( x )
        dom_view.save_state()


@position_algorithms.register( "align_automatically" )
def position_align_automatically( model_view: ModelView ):
    for n in range( 0, 100 ):
        for edge_view in model_view.overlay_view.edge_views.values():
            assert isinstance( edge_view, EdgeView )
            left = edge_view.left_view.first_domain_view
            right = edge_view.right_view.first_domain_view
            
            diff = left.get_x_for_site( edge_view.left_view.domain.start ) - right.get_x_for_site( edge_view.right_view.domain.start )
            
            if diff > 10:
                # Move left left
                left.setX( left.x() - 5 )
            elif diff < -10:
                # Move left right
                left.setX( left.x() + 5 )
            
            make_extra_contiguous( model_view, [left] )
