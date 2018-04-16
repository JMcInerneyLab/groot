from typing import List, Dict, Iterator, Iterable
from mhelper import array_helper, NotFoundError, exception_helper

from groot.data.model_core import LegoSubsequence, FixedUserGraph, LegoEdge, LegoSequence, LegoComponent, LegoUserDomain, LegoFusion


_LegoModel_ = "LegoModel"

class LegoEdgeCollection:
    """
    The collection of edges, held by the model.
    
    :attr __model:          Owning model.
    :attr __edges:          Edge list
    :attr __by_sequence:    Lookup table, sequence to edge list.
    """
    
    
    def __init__( self, model: _LegoModel_ ):
        """
        CONSTRUCTOR
        See class attributes for parameter descriptions. 
        """
        self.__model = model
        self.__edges: List[LegoEdge] = []
        self.__by_sequence: Dict[LegoSequence, List[LegoEdge]] = { }
    
    
    def __bool__( self ):
        return bool( self.__edges )
    
    
    def __len__( self ):
        return len( self.__edges )
    
    
    def __iter__( self ):
        return iter( self.__edges )
    
    
    def __str__( self ):
        return "{} edges".format( len( self ) )
    
    
    def find_sequence( self, sequence: LegoSequence ) -> List[LegoEdge]:
        return self.__by_sequence.get( sequence, [] )
    
    
    def add( self, edge: LegoEdge ):
        self.__edges.append( edge )
        array_helper.add_to_listdict( self.__by_sequence, edge.left.sequence, edge )
        array_helper.add_to_listdict( self.__by_sequence, edge.right.sequence, edge )
    
    
    def remove( self, edge: LegoEdge ):
        self.__edges.remove( edge )
        array_helper.remove_from_listdict( self.__by_sequence, edge.left.sequence, edge )
        array_helper.remove_from_listdict( self.__by_sequence, edge.right.sequence, edge )


class LegoComponentCollection:
    def __init__( self, model: _LegoModel_ ):
        self.__model = model
        self.__components: List[LegoComponent] = []
    
    
    @property
    def count( self ):
        return len( self )
    
    
    @property
    def num_aligned( self ):
        return sum( x.alignment is not None for x in self )
    
    
    @property
    def num_trees( self ):
        return sum( x.tree is not None for x in self )
    
    
    def __bool__( self ):
        return bool( self.__components )
    
    
    def add( self, component: LegoComponent ):
        assert isinstance( component, LegoComponent ), component
        self.__components.append( component )
    
    
    def __getitem__( self, item ):
        return self.__components[item]
    
    
    def __len__( self ):
        return len( self.__components )
    
    
    @property
    def is_empty( self ):
        return len( self.__components ) == 0
    
    
    def find_components_for_minor_subsequence( self, subsequence: LegoSubsequence ) -> List[LegoComponent]:
        r = []
        
        for component in self:
            for minor_subsequence in component.minor_subsequences:
                if minor_subsequence.has_overlap( subsequence ):
                    r.append( component )
                    break
        
        return r
    
    
    def find_components_for_minor_sequence( self, sequence: LegoSequence ) -> List[LegoComponent]:
        r = []
        
        for component in self:
            for minor_subsequence in component.minor_subsequences:
                if minor_subsequence.sequence is sequence:
                    r.append( component )
                    break
        
        return r
    
    
    def find_component_for_major_sequence( self, sequence: LegoSequence ) -> LegoComponent:
        for component in self.__components:
            if sequence in component.major_sequences:
                return component
        
        raise NotFoundError( "Sequence «{}» does not have a component.".format( sequence ) )
    
    
    def find_component_by_name( self, name: str ) -> LegoComponent:
        for component in self.__components:
            if str( component ) == name:
                return component
        
        raise NotFoundError( "Cannot find the component with the name «{}».".format( name ) )
    
    
    def has_sequence( self, sequence: LegoSequence ) -> bool:
        try:
            self.find_component_for_major_sequence( sequence )
            return True
        except NotFoundError:
            return False
    
    
    def __iter__( self ) -> Iterator[LegoComponent]:
        return iter( self.__components )
    
    
    def __str__( self ):
        return "{} components".format( len( self.__components ) )
    
    
    def clear( self ):
        self.__components.clear()


class LegoSequenceCollection:
    def __init__( self, model: _LegoModel_ ):
        self.__model = model
        self.__sequences: List[LegoSequence] = []
    
    
    @property
    def num_fasta( self ):
        return sum( x.site_array is not None for x in self )
    
    
    def to_fasta( self ):
        r = []
        
        for s in self:
            r.append( s.to_fasta() )
        
        return "\n".join( r )
    
    
    def __bool__( self ):
        return bool( self.__sequences )
    
    
    def __len__( self ):
        return len( self.__sequences )
    
    
    def __iter__( self ) -> Iterator[LegoSequence]:
        return iter( self.__sequences )
    
    
    def __str__( self ):
        return "{} sequences".format( len( self ) )
    
    
    def add( self, sequence: LegoSequence ):
        if any( x.accession == sequence.accession for x in self.__sequences ):
            raise ValueError( "Cannot add a sequence «{}» to the model because its accession is already in use.".format( sequence ) )
        
        array_helper.ordered_insert( self.__sequences, sequence, lambda x: x.accession )
    
    
    def index( self, sequence: LegoSequence ):
        return self.__sequences.index( sequence )


class LegoUserDomainCollection:
    def __init__( self, model: _LegoModel_ ):
        self.__model = model
        self.__user_domains: List[LegoUserDomain] = []
        self.__by_sequence: Dict[LegoSequence, List[LegoUserDomain]] = { }
    
    
    def add( self, domain: LegoUserDomain ):
        self.__user_domains.append( domain )
        
        if domain.sequence not in self.__by_sequence:
            self.__by_sequence[domain.sequence] = []
        
        self.__by_sequence[domain.sequence].append( domain )
    
    
    def clear( self ):
        self.__user_domains.clear()
        self.__by_sequence.clear()
    
    
    def __bool__( self ):
        return bool( self.__user_domains )
    
    
    def __len__( self ):
        return len( self.__user_domains )
    
    
    def __iter__( self ) -> Iterator[LegoUserDomain]:
        return iter( self.__user_domains )
    
    
    def by_sequence( self, sequence: LegoSequence ) -> Iterable[LegoUserDomain]:
        list = self.__by_sequence.get( sequence )
        
        if list is None:
            return [LegoUserDomain( sequence, 1, sequence.length )]
        else:
            return list


class LegoFusionEventCollection:
    def __init__( self ):
        self.events: List[LegoFusion] = []
    
    
    def add( self, item: LegoFusion ):
        self.events.append( item )
    
    
    def clear( self ):
        self.events.clear()
    
    
    def __len__( self ):
        return len( self.events )
    
    
    def __iter__( self ):
        return iter( self.events )
    
    
    def __bool__( self ):
        return bool( self.events )
    
    
    @property
    def num_points( self ):
        return sum( sum( y.points.__len__() for y in x.formations ) for x in self )


class LegoUserGraphCollection:
    def __init__( self, model: _LegoModel_ ):
        self.__model = model
        self.__contents = []
    
    
    def __len__( self ):
        return len( self.__contents )
    
    
    def append( self, graph: FixedUserGraph ):
        exception_helper.assert_type( "graph", graph, FixedUserGraph )
        
        for graph2 in self.__model.iter_graphs():
            if graph2.name == graph.name:
                raise ValueError( "Your graph is called '{}' but there is already a graph with this name." )
        
        self.__contents.append( graph )
    
    
    def remove( self, graph: FixedUserGraph ):
        self.__contents.remove( graph )
    
    
    def __iter__( self ):
        return iter( self.__contents )