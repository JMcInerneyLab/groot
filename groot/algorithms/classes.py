from typing import List, Set

from groot.data.lego_model import LegoComponent, ILeaf, LegoSequence, ILegoSelectable
from mgraph import MGraph
from mhelper import array_helper, string_helper, utf_helper


_FusionPoint_ = "FusionPoint"


class FusionEvent( ILegoSelectable ):
    """
    Describes a fusion event
    
    :data component_a:          First component
    :data component_b:          Second component
    :data products:        Generated component (root)
    :data future_products:   Generated component (all possibilities)
    :data point_a:              The name of the node on the first component which the fusion occurs
    :data point_b:              The name of the node on the second component which the fusion occurs
    """
    
    
    def __init__( self, index: int, component_a: LegoComponent, component_b: LegoComponent, intersections: Set[LegoComponent] ) -> None:
        if component_a is component_b:
            raise ValueError( "FusionEvent component A ({}) cannot be component B ({}).".format( component_a, component_b ) )
        
        if any( x is component_a or x is component_b for x in intersections ):
            raise ValueError( "FusionEvent intersections ({}) cannot contain component A ({}) or component B ({}).".format( string_helper.format_array( intersections ), component_a, component_b ) )
        
        self.index = index
        self.component_a: LegoComponent = component_a
        self.component_b: LegoComponent = component_b
        self.products: Set[LegoComponent] = intersections
        self.future_products: Set[LegoComponent] = set( intersections )
        self.points: List[FusionPoint] = None
    
    
    @property
    def component_c( self ) -> LegoComponent:
        return array_helper.single_or_error( self.products )
    
    
    def __str__( self ) -> str:
        # return "({}+{}={})".format( self.component_a, self.component_b, ",".join( x.__str__() for x in self.products ) )
        return "{}".format( ",".join( x.__str__() for x in self.products ) )


class FusionPoint( ILeaf, ILegoSelectable ):
    def __init__( self, event: FusionEvent, component: LegoComponent, sequences: Set[ILeaf], outer_sequences: Set[ILeaf] ):
        self.event = event
        self.component = component
        self.sequences = sequences
        self.outer_sequences = outer_sequences
        self.pertinent_inner = frozenset( self.sequences.intersection( self.event.component_c.major_sequences ) )
        self.pertinent_outer = frozenset( self.outer_sequences.intersection( set( self.event.component_a.major_sequences ).union( set( self.event.component_b.major_sequences ) ) ) )
    
    
    @property
    def count( self ):
        return len( self.sequences )
    
    
    def __repr__( self ):
        return self.str_short()
    
    
    def __eq__( self, other ):
        if not isinstance( other, FusionPoint ):
            return False
        
        return other.event == self.event and other.pertinent_inner == other.pertinent_inner
    
    
    def __hash__( self ):
        return hash( (self.event, self.pertinent_inner) )
    
    
    def get_pertinent_inner( self ):
        return self.pertinent_inner.union( { self } )
    
    
    def get_pertinent_outer( self ):
        return self.pertinent_outer.union( { self } )
    
    
    def __format_elements( self, y ):
        r = []
        
        for x in y:
            if isinstance( x, LegoSequence ):
                r.append( x.__str__() )
            elif isinstance( x, FusionPoint ):
                r.append( x.str_id() )
        
        return string_helper.format_array( r, sort = True )
    
    
    def str_id( self ):
        return "{}{}".format( self.event, utf_helper.subscript( str( self.count ) ) )
    
    
    def str_short( self ):
        return self.event.__str__()
    
    
    def str_long( self ):
        return "¨{} ⊇ {} ⊅ {}¨".format( self.event, self.__format_elements( self.pertinent_inner ), self.__format_elements( self.pertinent_outer ) )
