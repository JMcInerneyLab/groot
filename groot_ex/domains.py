from typing import List, Iterable
from groot import Gene, UserDomain, Model, domain_algorithms, Component, Domain
from mhelper import array_helper


@domain_algorithms.register( "Edge based" )
def create_userdomains_from_edges( gene: Gene ) -> List[UserDomain]:
    """
    Sequences are split up at boundaries delimited by their BLAST origins and destinations. 
    """
    domains: List[Domain] = []
    
    for edge in gene.model.edges:
        for side in (edge.left, edge.right):
            if side.gene is gene:
                domains.append( side )
    
    return __userdomains_from_domains( domains )


@domain_algorithms.register( "Fixed width" )
def create_fixed_sized_userdomains( gene: Gene, width: int = 25 ) -> List[UserDomain]:
    """
    Sequences are split up into fixed width domains. 
    """
    r = []
    
    for i in range( 1, gene.length + 1, width ):
        r.append( UserDomain( gene, i, min( i + width, gene.length ) ) )
    
    return r


@domain_algorithms.register( "Fixed count" )
def create_fixed_number_of_userdomains( gene: Gene, count: int = 4 ) -> List[UserDomain]:
    """
    Sequences are split up into a fixed number of equal width domains.
    """
    r = []
    
    for s, e in array_helper.divide_workload( gene.length, count ):
        r.append( UserDomain( gene, s + 1, e + 1 ) )
    
    return r


@domain_algorithms.register( "Component" )
def create_userdomains_from_minor_domains( gene: Gene ) -> List[UserDomain]:
    """
    Sequences are split at the component boundaries. This usually provides the best view.
    """
    model: Model = gene.model
    components: List[Component] = model.components.find_components_for_minor_gene( gene )
    todo: List[Domain] = []
    
    for component in components:
        for domain in component.minor_domains:
            if domain.gene is not gene:
                continue
            
            todo.append( domain )
    
    if not todo:
        return [UserDomain( gene, 1, gene.length )]
    
    return __userdomains_from_domains( todo )


def __userdomains_from_domains( subsequences: List[Domain] ) -> List[UserDomain]:
    cuts = set()
    
    for subsequence in subsequences:
        cuts.add( subsequence.start )
        cuts.add( subsequence.end + 1 )
    
    return __userdomains_from_cuts( subsequences[0].gene, cuts )


def __userdomains_from_cuts( gene: Gene, cuts: Iterable[int] ):
    """
    Creates domains by cutting up the sequence at the cut points.
    """
    r = []
    
    cuts = set( cuts )
    cuts.add( 1 )
    cuts.add( gene.length + 1)
    cuts = sorted( cuts )
    
    for left, right in array_helper.lagged_iterate( cuts ):
        r.append( UserDomain( gene, left, right - 1 ) )
    
    return r
