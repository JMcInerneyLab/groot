from typing import List, Dict, Iterator, Iterable
from mhelper import array_helper, NotFoundError, exception_helper, NOT_PROVIDED

from groot.data.model_core import Domain, FixedUserGraph, Edge, Gene, Component, UserDomain, Fusion, Point, Formation


_Model_ = "Model"


class EdgeCollection:
    """
    The collection of edges, held by the model.
    
    :ivar __model:          Owning model.
    :ivar __edges:          Edge list
    :ivar __by_gene:    Lookup table, gene to edge list.
    """
    
    
    def __init__( self, model: _Model_ ):
        """
        CONSTRUCTOR
        See class attributes for parameter descriptions. 
        """
        self.__model = model
        self.__edges: List[Edge] = []
        self.__by_gene: Dict[Gene, List[Edge]] = { }
    
    
    def __bool__( self ):
        """
        False when empty/
        """
        return bool( self.__edges )
    
    
    def __len__( self ):
        """
        Number of edges.
        """
        return len( self.__edges )
    
    
    def __iter__( self ):
        """
        Iterates edges.
        """
        return iter( self.__edges )
    
    
    def __str__( self ):
        """
        Descriptive text.
        """
        return "{} edges".format( len( self ) )
    
    
    def find_gene( self, gene: Gene ) -> List[Edge]:
        """
        Obtains the list of edges crossing a specified `gene`.
        """
        return self.__by_gene.get( gene, [] )
    
    
    def iter_touching( self, domains: Iterable[Domain] ) -> Iterator[Edge]:
        """
        Yields all `Edge`s that overlap the specified `domains`. 
        """
        if not domains:
            return
        
        for edge in self.__edges:
            for domain in domains:
                if not edge.left.has_overlap( domain ) and not edge.right.has_overlap( domain ):
                    break
            else:
                yield edge
    
    
    def add( self, edge: Edge ):
        """
        Adds an edge to the collection.
        """
        self.__edges.append( edge )
        array_helper.add_to_listdict( self.__by_gene, edge.left.gene, edge )
        array_helper.add_to_listdict( self.__by_gene, edge.right.gene, edge )
    
    
    def remove( self, edge: Edge ):
        """
        Removes an edge from the collection.
        """
        self.__edges.remove( edge )
        array_helper.remove_from_listdict( self.__by_gene, edge.left.gene, edge )
        array_helper.remove_from_listdict( self.__by_gene, edge.right.gene, edge )


class ComponentCollection:
    def __init__( self, model: _Model_ ):
        self.__model = model
        self.__components: List[Component] = []
    
    
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
    
    
    def add( self, component: Component ):
        assert isinstance( component, Component ), component
        self.__components.append( component )
    
    
    def remove( self, component: Component ):
        self.__components.remove( component )
    
    
    def __getitem__( self, item ):
        return self.__components[item]
    
    
    def __len__( self ):
        return len( self.__components )
    
    
    @property
    def is_empty( self ):
        return len( self.__components ) == 0
    
    
    def find_components_for_minor_domain( self, domain: Domain ) -> List[Component]:
        r = []
        
        for component in self:
            if component.minor_domains is not None:
                for minor_domain in component.minor_domains:
                    if minor_domain.has_overlap( domain ):
                        r.append( component )
                        break
        
        return r
    
    
    def find_components_for_minor_gene( self, gene: Gene ) -> List[Component]:
        r = []
        
        for component in self:
            if component.minor_domains:
                for minor_domain in component.minor_domains:
                    if minor_domain.gene is gene:
                        r.append( component )
                        break
        
        return r
    
    
    def has_major_gene_got_component( self, gene: Gene ) -> bool:
        try:
            self.find_component_for_major_gene( gene )
            return True
        except NotFoundError:
            return False
    
    
    def find_component_for_major_gene( self, gene: Gene, *, default: object = NOT_PROVIDED ) -> Component:
        for component in self.__components:
            if gene in component.major_genes:
                return component
        
        if default is not NOT_PROVIDED:
            # noinspection PyTypeChecker
            return default
        
        raise NotFoundError( "Gene «{}» does not have a component.".format( gene ) )
    
    
    def find_component_by_name( self, name: str ) -> Component:
        for component in self.__components:
            if str( component ) == name:
                return component
        
        raise NotFoundError( "Cannot find the component with the name «{}».".format( name ) )
    
    
    def has_gene( self, gene: Gene ) -> bool:
        try:
            self.find_component_for_major_gene( gene )
            return True
        except NotFoundError:
            return False
    
    
    def __iter__( self ) -> Iterator[Component]:
        return iter( self.__components )
    
    
    def __str__( self ):
        return "{} components".format( len( self.__components ) )
    
    
    def clear( self ):
        self.__components.clear()


class GeneCollection:
    def __init__( self, model: _Model_ ):
        self.__model = model
        self.__genes: List[Gene] = []
    
    
    def remove( self, gene: Gene ):
        self.__genes.remove( gene )
    
    
    @property
    def num_fasta( self ):
        return sum( x.site_array is not None for x in self )
    
    
    def to_fasta( self ):
        r = []
        
        for s in self:
            r.append( s.to_fasta() )
        
        return "\n".join( r )
    
    
    def by_legacy_accession( self, name: str ) -> Gene:
        id = Gene.read_legacy_accession( name )
        
        for x in self:
            if x.index == id:
                return x
        
        raise NotFoundError( "There is no gene with the internal ID «{}».".format( id ) )
    
    
    def __getitem__( self, accession: str ):
        r = self.get( accession )
        
        if r is None:
            raise NotFoundError( "No gene with the accession «{}» exists.".format( accession ) )
        
        return r
    
    
    def get( self, accession: str ):
        for s in self.__genes:
            if s.accession == accession:
                return s
        
        return None
    
    
    def __bool__( self ):
        return bool( self.__genes )
    
    
    def __len__( self ):
        return len( self.__genes )
    
    
    def __iter__( self ) -> Iterator[Gene]:
        return iter( self.__genes )
    
    
    def __str__( self ):
        return "{} genes".format( len( self ) )
    
    
    def add( self, gene: Gene ):
        if any( x.accession == gene.accession for x in self.__genes ):
            raise ValueError( "Cannot add a gene «{}» to the model because its accession is already in use.".format( gene ) )
        
        array_helper.ordered_insert( self.__genes, gene, lambda x: x.accession )
    
    
    def index( self, gene: Gene ):
        return self.__genes.index( gene )


class UserDomainCollection:
    def __init__( self, model: _Model_ ):
        self.__model = model
        self.__user_domains: List[UserDomain] = []
        self.__by_gene: Dict[Gene, List[UserDomain]] = { }
    
    
    def add( self, domain: UserDomain ):
        self.__user_domains.append( domain )
        
        if domain.gene not in self.__by_gene:
            self.__by_gene[domain.gene] = []
        
        self.__by_gene[domain.gene].append( domain )
    
    
    def __str__( self ):
        return "{} domains".format( len( self ) )
    
    
    def clear( self ):
        self.__user_domains.clear()
        self.__by_gene.clear()
    
    
    def __bool__( self ):
        return bool( self.__user_domains )
    
    
    def __len__( self ):
        return len( self.__user_domains )
    
    
    def __iter__( self ) -> Iterator[UserDomain]:
        return iter( self.__user_domains )
    
    
    def by_gene( self, gene: Gene ) -> Iterable[UserDomain]:
        list = self.__by_gene.get( gene )
        
        if list is None:
            return [UserDomain( gene, 1, gene.length )]
        else:
            return list


class FusionCollection:
    def __init__( self ):
        self.events: List[Fusion] = []
    
    
    def add( self, item: Fusion ):
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
    
    
    def find_point_by_legacy_accession( self, name: str ) -> Point:
        i_event, i_formation, i_point = Point.read_legacy_accession( name )
        
        for event in self:
            if event.index == i_event:
                for formation in event.formations:
                    if formation.index == i_formation:
                        for point in formation.points:
                            if point.index == i_point:
                                return point
        
        raise NotFoundError( "There is no fusion point with the internal ID «{}».".format( id ) )
    
    
    def find_formation_by_legacy_accession( self, name: str ) -> Formation:
        i_event, i_formation = Formation.read_legacy_accession( name )
        
        for event in self:
            if event.index == i_event:
                for formation in event.formations:
                    if formation.index == i_formation:
                        return formation
        
        raise NotFoundError( "There is no fusion formation with the internal ID «{}».".format( id ) )


class UserGraphCollection:
    def __init__( self, model: _Model_ ):
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
    
    
    def __str__( self ):
        return "{} graphs".format( len( self ) )
