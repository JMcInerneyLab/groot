from typing import List, Set, Tuple

from groot.data.lego_model import LegoComponent, LegoSequence
from mgraph import MGraph
from mhelper import array_helper, string_helper


_FusionPoint_ = "FusionPoint"


class NotCommensurateError( Exception ):
    pass

class IFusion:
    pass

class FusionEvent(IFusion):
    """
    Describes a fusion event
    
    :data component_a:          First component
    :data component_b:          Second component
    :data intersections:        Generated component (root)
    :data orig_intersections:   Generated component (all possibilities)
    :data point_a:              The name of the node on the first component which the fusion occurs
    :data point_b:              The name of the node on the second component which the fusion occurs
    """
    
    
    def __init__( self, index: int, component_a: LegoComponent, component_b: LegoComponent, intersections: Set[LegoComponent] ) -> None:
        if component_a is component_b:
            raise ValueError("FusionEvent component A ({}) cannot be component B ({}).".format(component_a, component_b))
        
        if any(x is component_a or x is component_b for x in intersections):
            raise ValueError("FusionEvent intersections ({}) cannot contain component A ({}) or component B ({}).".format(string_helper.format_array(intersections), component_a, component_b))
        
        self.index = index
        self.component_a: LegoComponent = component_a
        self.component_b: LegoComponent = component_b
        self.intersections: Set[LegoComponent] = intersections
        self.orig_intersections: Set[LegoComponent] = set( intersections )
        self.points_a: List[FusionPoint] = None
        self.points_b: List[FusionPoint] = None
    
    
    def get_commensurate_points( self ) -> List[Tuple[_FusionPoint_, _FusionPoint_]]:
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
        return array_helper.single_or_error( self.intersections )
    
    
    def __str__( self ) -> str:
        intersections = ", ".join( x.__str__() for x in self.intersections )
        return intersections
        #return "{}+{}->{}".format( self.component_a, self.component_b, intersections )


class FusionPoint(IFusion):
    def __init__( self, is_left: bool, fusion_node_uid: int, internal_node_uid: int, event: FusionEvent, genes: Set[LegoSequence], component: LegoComponent, opposite_component: LegoComponent ):
        self.is_left = is_left
        self.fusion_node_uid = fusion_node_uid
        self.internal_node_uid = internal_node_uid
        self.opposite_component = opposite_component
        self.component = component
        self.event = event
        self.genes = genes
    
    
    @property
    def count( self ):
        return len( self.genes )
    
    
    def __repr__( self ):
        return "F.{}:{}.{}".format( self.event, "L" if self.is_left else "R", self.count )


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
