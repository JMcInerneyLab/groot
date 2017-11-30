from typing import Set, List, Tuple

from groot.data.graphing import IsolationPoint, MGraph
from groot.data.lego_model import LegoComponent, LegoSequence
from mhelper import array_helper


class NotCommensurateError( Exception ):
    pass


class FusionEvent:
    """
    Describes a fusion event
    
    :data component_a:          First component
    :data component_b:          Second component
    :data intersections:        Generated component (root)
    :data orig_intersections:   Generated component (all possibilities)
    :data point_a:              The name of the node on the first component which the fusion occurs
    :data point_b:              The name of the node on the second component which the fusion occurs
    """
    
    
    def __init__( self, component_a: LegoComponent, component_b: LegoComponent, intersections: Set[LegoComponent] ):
        self.component_a: LegoComponent = component_a
        self.component_b: LegoComponent = component_b
        self.intersections: Set[LegoComponent] = intersections
        self.orig_intersections: Set[LegoComponent] = set( intersections )
        self.points_a: List[FusionPoint] = None
        self.points_b: List[FusionPoint] = None
    
    
    def get_commensurate_points( self ) -> List[Tuple[IsolationPoint, IsolationPoint]]:
        """
        Gets tuples of points that look like they are commensurate, or raises a `NotCommensurateError`. 
        """
        if len( self.points_a ) != len( self.points_b ):
            raise NotCommensurateError( "The two sets of fusion points for this event are not the same length, so at least one will be non-commensurate.".format( len( self.points_a ), len( self.points_b ) ) )
        
        results = []
        
        for point_a in self.points_a:
            found = False
            for point_b in self.points_b:
                if point_a.genes == point_b.genes:
                    if found:
                        raise NotCommensurateError( "In the fusion point A there are multiple commensurate points in the B set. A = «{}», B = «{}».".format( point_a, self.points_b ) )
                    
                    results.append( (point_a, point_b) )
                    found = True
            
            if not found:
                raise NotCommensurateError( "In the fusion point A there is no commensurate point in the B set. A = «{}», B = «{}».".format( point_a, self.points_b ) )
        
        return results
    
    
    @property
    def component_c( self ) -> LegoComponent:
        return array_helper.extract_single_item_or_error( self.intersections )
    
    
    def __str__( self ) -> str:
        intersections = ", ".join( x.__str__() for x in self.intersections )
        return "{} COMBINES WITH {} TO FORM {}".format( self.component_a, self.component_b, intersections )


class FusionPoint:
    def __init__( self, node: int, direction_uid: int, event: FusionEvent, genes: Set[LegoSequence], component: LegoComponent, opposite_component: LegoComponent ):
        self.node_uid = node
        self.direction_uid = direction_uid
        self.opposite_component = opposite_component
        self.component = component
        self.event = event
        self.genes = genes
    
    
    @property
    def count( self ):
        return len( self.genes )
    
    
    def __repr__( self ):
        return "({})-AND-({})-FORM-({}):{}_GENES=[{}]".format( self.component,
                                                               self.opposite_component,
                                                               ",".join( sorted( str( x ) for x in self.event.intersections ) ),
                                                               self.count,
                                                               ",".join( sorted( str( x ) for x in self.genes ) ) )


class NrfgEvent:
    def __init__( self, event: FusionEvent, aπ: FusionPoint, bπ: FusionPoint, aΛ: MGraph, aΔ: MGraph, bΛ: MGraph, bΔ: MGraph, dΔ: MGraph ) -> None:
        self.event = event
        self.aπ = aπ
        self.bπ = bπ
        self.aΛ = aΛ
        self.aΔ = aΔ
        self.bΔ = bΔ
        self.bΛ = bΛ
        self.dΔ = dΔ


class Nrfg:
    def __init__( self, graph: MGraph, events: List[NrfgEvent] ) -> None:
        self.graph = graph
        self.events = events
