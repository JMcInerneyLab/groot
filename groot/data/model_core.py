import re
import warnings
from itertools import combinations, chain
from typing import Tuple, Optional, List, Iterable, FrozenSet, cast, Any, Set

from groot.data.model_interfaces import EPosition, INamed, IHasFasta, INamedGraph, INode
from groot import resources as groot_resources
from intermake.engine.environment import MENV
from intermake.visualisables.visualisable import UiInfo, EColour, IVisualisable, UiHint
from mgraph import MGraph, MSplit
from mhelper import SwitchError, NotFoundError, string_helper, bio_helper, array_helper, TTristate, assert_type


_Model_ = "Model"


class Edge( IHasFasta ):
    """
    IMMUTABLE
    
    Edge from one domain to another.
    """
    TSide = "Union[Gene,Domain,Component,bool]"
    
    
    def __init__( self, source: "Domain", destination: "Domain" ) -> None:
        """
        CONSTRUCTOR
        :param source:          Source domain `left` 
        :param destination:     Destination domain `right` 
        """
        self.left: Domain = source
        self.right: Domain = destination
    
    
    def to_fasta( self ) -> str:
        fasta = []
        fasta.append( ">{} [ {} : {} ]".format( self.left.gene.accession, self.left.start, self.left.end ) )
        fasta.append( self.left.site_array or ";MISSING" )
        fasta.append( "" )
        fasta.append( ">{} [ {} : {} ]".format( self.right.gene.accession, self.right.start, self.right.end ) )
        fasta.append( self.right.site_array or ";MISSING" )
        fasta.append( "" )
        return "\n".join( fasta )
    
    
    def __contains__( self, item: "Gene" ) -> bool:
        """
        OVERRIDE
        Does the edge specify a gene as either of its endpoints? 
        """
        return item in self.left or item in self.right
    
    
    @staticmethod
    def to_string( gene: "Gene", start: int, end: int, gene_b: "Gene", start_b: int, end_b: int ) -> str:
        return Domain.to_string( gene, start, end ) + "--" + Domain.to_string( gene_b, start_b, end_b )
    
    
    def __str__( self ) -> str:
        """
        OVERRIDE 
        """
        return self.to_string( self.left.gene, self.left.start, self.left.end, self.right.gene, self.right.start, self.right.end )
    
    
    def position( self, item: TSide ) -> bool:
        """
        Returns `True` if `item` appears in the `destination` list, or `False` if it appears in the `source` list.
        
        Supports: Gene, domain or component. Note that only the component of the _gene_ is considered, not the individual domains.
        
        Raises `KeyError` if it does not appear in either.
        """
        if isinstance( item, Domain ):
            if item.gene is self.left.gene:
                return False
            
            if item.gene is self.right.gene:
                return True
            
            raise KeyError( "I cannot find the domain '{}' within this edge.".format( item ) )
        elif isinstance( item, Gene ):
            if item is self.left.gene:
                return False
            
            if item is self.right.gene:
                return True
            
            raise KeyError( "I cannot find the domain '{}' within this edge. This edge's genes are '{}' and '{}'.".format( item, self.left.gene, self.right.gene ) )
        elif isinstance( item, Component ):
            if self.left.gene in item.major_genes:
                if self.right.gene in item.major_genes:
                    raise KeyError( "I can find the component '{}' within this edge, but both sides of the edge have this same component. This edge's genes are '{}' and '{}'.".format( item, self.left.gene, self.right.gene ) )
                
                return False
            
            if self.right.gene in item.major_genes:
                return True
            
            raise KeyError( "I cannot find the component '{}' within this edge. This edge's genes are '{}' and '{}'.".format( item, self.left.gene, self.right.gene ) )
        elif isinstance( item, bool ):
            return item
        else:
            raise SwitchError( "position.item", item, instance = True )
    
    
    def sides( self, item: TSide ) -> Tuple["Domain", "Domain"]:
        """
        As `sides` but returns both items.
        """
        position = self.position( item )
        return (self.right, self.left) if position else (self.left, self.right)
    
    
    def side( self, item: TSide, opposite = False ) -> "Domain":
        """
        Returns the side of the given item.
        :param item:        See `position` for accepted values. 
        :param opposite:    When `true` the side opposing `item` is returned. 
        :return:            The requested side. 
        """
        position = self.position( item )
        
        if opposite:
            position = not position
        
        return self.right if position else self.left
    
    
    def opposite( self, item: TSide ) -> "Domain":
        """
        Convenience function that calls `side` with `opposite = True`.
        """
        return self.side( item, opposite = True )


class Domain( IHasFasta, IVisualisable ):
    """
    IMMUTABLE
    
    Portion of a gene sequence.
    
    Note that we follow the somewhat atypical BLAST convention and so the `start` and `end` range is inclusive.
    """
    
    
    def __init__( self, gene: "Gene", start: int, end: int ):
        """
        CONSTRUCTOR
        :param gene: Owning gene
        :param start: Leftmost position (inclusive) 
        :param end: Rightmost position (inclusive) 
        """
        assert isinstance( gene, Gene )
        assert isinstance( start, int )
        assert isinstance( end, int )
        
        assert start >= 1
        assert end >= 1
        
        if start > end:
            raise ValueError( "Attempt to create a domain in «{0}» where start ({1}) > end ({2}).".format( gene, start, end ) )
        
        self.gene: Gene = gene
        self.__start: int = start  # Start position
        self.__end: int = end  # End position
    
    
    def to_fasta( self ):
        fasta = []
        
        fasta.append( ">" + self.gene.accession + "[{}:{}]".format( self.start, self.end ) )
        
        if self.site_array is not None:
            fasta.append( self.site_array )
        else:
            fasta.append( "; MISSING" )
        
        return "\n".join( fasta )
    
    
    def has_overlap( self, two: "Domain" ) -> bool:
        """
        Returns if the `two` `Domain`s overlap.
        """
        if self.gene is not two.gene:
            return False
        
        return self.start <= two.end and two.start <= self.end
    
    
    def intersection( self, two: "Domain" ) -> "Domain":
        """
        Returns a `Domain` that is the intersection of the `two`.
        :except NotFoundError: The `two` do not overlap.
        """
        assert self.gene is two.gene
        
        start = max( self.start, two.start )
        end = min( self.end, two.end )
        
        if start > end:
            raise NotFoundError( "Cannot create `intersection` for non-overlapping ranges «{}» and «{}».".format( self, two ) )
        
        return Domain( self.gene, start, end )
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        """
        OVERRIDE 
        """
        super().on_get_vis_info( u )
        u.hint = u.Hints.FOLDER
        u.text = "{} sites".format( self.length )
        u.properties += { "gene"  : self.gene,
                          "start" : self.start,
                          "end"   : self.end,
                          "length": self.length,
                          "sites" : self.site_array }
    
    
    @staticmethod
    def to_string( gene, start, end ) -> str:
        return "{}[{}:{}({})]".format( gene.accession, start, end, end - start + 1 )
    
    
    def __str__( self ) -> str:
        return self.to_string( self.gene, self.start, self.end )
    
    
    def __repr__( self ):
        return "{}({}, {}, {})".format( type( self ).__name__, repr( self.gene.accession ), repr( self.start ), repr( self.end ) )
    
    
    @property
    def start( self ) -> int:
        return self.__start
    
    
    @property
    def end( self ) -> int:
        return self.__end
    
    
    @start.setter
    def start( self, value: int ) -> None:
        assert isinstance( value, int )
        
        if not (0 < value <= self.__end):
            raise ValueError( "Attempt to set `start` to an out-of-bounds value {} in '{}'.".format( value, self ) )
        
        self.__start = value
    
    
    @end.setter
    def end( self, value: int ) -> None:
        assert isinstance( value, int )
        
        if not (self.__start <= value):
            raise ValueError( "Attempt to set `end` to an out-of-bounds value {} in '{}'.".format( value, self ) )
        
        self.__end = value
    
    
    @property
    def site_array( self ) -> Optional[str]:
        """
        Obtains the slice of the gene array pertinent to this domain
        """
        if self.gene.site_array:
            result = self.gene.site_array[self.start - 1:self.end]
            if len( result ) != self.length:
                raise ValueError( "Cannot extract site range {}-{} from site array of length {}.".format( self.start, self.length, self.gene.length ) )
            
            return result
        else:
            return None
    
    
    @property
    def length( self ) -> int:
        """
        Calculates the length of this domain
        """
        return self.end - self.start + 1


class UserDomain( Domain ):
    """
    A user-domain is just a domain (`Domain`) which the user has defined.
    """
    pass


class Gene( INode, IHasFasta, IVisualisable, INamed ):
    """
    Protein (or DNA) gene sequence
    
    :ivar index:        Index within model.
    :ivar accession:    Database accession. Note that this can't look like an accession produced by any of the `legacy_accession` functions.
    :ivar model:        Owning model.
    :ivar site_array:   Site data. This can be `None` before the data is loaded in. The length must match `length`.
    :ivar length:       Length of the gene. This must match `site_array`, it that is set.
    """
    
    # Formats for finding and creating legacy accessions
    _LEGACY_IDENTIFIER = re.compile( "^GrtS([0-9]+)$" )
    _LEGACY_FORMAT = "GrtS{}"
    
    
    def __init__( self, model: _Model_, accession: str, index: int ) -> None:
        """
        CONSTRUCTOR
        See class attributes for parameter descriptions.
        """
        if Gene.is_legacy_accession( accession ):
            raise ValueError( "You have a gene with an accession «{}», but {} has reserved that name for compatibility with legacy Phylip format files. Avoid using such names.".format( accession, MENV.name ) )
        
        self.index: int = index
        self.accession: str = accession
        self.model: _Model_ = model
        self.site_array: str = None
        self.length = 1
        self.position = EPosition.NONE
        self.display_name: str = None
    
    
    @property
    def is_outgroup( self ):
        return self.position == EPosition.OUTGROUP
    
    
    def on_get_name( self ):
        return self.accession
    
    
    def iter_edges( self ) -> Iterable[Edge]:
        return (x for x in self.model.edges if x.left.gene is self or x.right.gene is self)
    
    
    def iter_userdomains( self ):
        return (x for x in self.model.user_domains if x.gene is self)
    
    
    @property
    def is_positioned( self ):
        return self.position != EPosition.NONE
    
    
    def to_fasta( self ):
        fasta = []
        
        fasta.append( ">" + self.accession )
        
        if self.site_array:
            fasta.append( self.site_array )
        else:
            fasta.append( "; MISSING" )
        
        return "\n".join( fasta )
    
    
    @staticmethod
    def read_legacy_accession( name: str ) -> int:
        return int( Gene._LEGACY_IDENTIFIER.match( name ).groups()[0] )
    
    
    @staticmethod
    def is_legacy_accession( name: str ):
        """
        Determines if an accession was created via the `legacy_accession` function.
        """
        return bool( Gene._LEGACY_IDENTIFIER.match( name ) )
    
    
    @property
    def legacy_accession( self ):
        """
        We make an accession for compatibility with programs that still use Phylip format.
        We can't just use a number because some programs mistake this for a line count.
        """
        return self._LEGACY_FORMAT.format( self.index )
    
    
    def get_totality( self ) -> Domain:
        """
        Gets the domain spanning the totality of this gene.
        """
        return Domain( self, 1, self.length )
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        """
        OVERRIDE 
        """
        super().on_get_vis_info( u )
        u.hint = UiHint( colour = EColour.BLUE, icon = groot_resources.black_gene )
        u.value = "{} sites".format( self.length )
        u.properties += { "id"          : self.legacy_accession,
                          "display_name": self.display_name,
                          "length"      : self.length,
                          "accession"   : self.accession,
                          "position"    : self.position,
                          "num_sites"   : len( self.site_array ) if self.site_array else "?",
                          "sites"       : self.site_array,
                          "domains"     : list( self.iter_userdomains() ),
                          "edges"       : list( self.iter_edges() ),
                          "major"       :  self.find_major(),
                          "minor"       : list( self.iter_minor() ), }
    
    
    def find_major( self ):
        return self.model.components.find_component_for_major_gene( self )
    
    
    def iter_minor( self ):
        return self.model.components.find_components_for_minor_gene( self )
    
    
    def __str__( self ) -> str:
        """
        OVERRIDE 
        """
        if self.display_name:
            return self.display_name
        elif self.accession:
            return self.accession
        else:
            return "G{}".format( self.index )
    
    
    def __repr__( self ) -> str:
        """
        OVERRIDE 
        """
        return "Gene({}, n={})".format( repr( self.accession ), repr( self.length ) )
    
    
    def _ensure_length( self, new_length: int ) -> None:
        """
        Ensures the length of the gene's sequence accommodates `new_length`.
        """
        assert isinstance( new_length, int )
        
        if new_length == 0:
            return
        
        if self.length < new_length:
            self.length = new_length
    
    
    def sub_sites( self, start: int, end: int ) -> Optional[str]:
        """
        Retrieves a portion of this gene's sequence.
        Indices are 1 based and inclusive.
        
        :param start:       Start index 
        :param end:         End index 
        :return:            Substring, or `None` if no site array is available. 
        """
        if self.site_array is None:
            return None
        
        assert start <= end, "{} {}".format( start, end )
        assert 0 < start <= len( self.site_array ), "{} {} {}".format( start, end, len( self.site_array ) )
        assert 0 < end <= len( self.site_array ), "{} {} {}".format( start, end, len( self.site_array ) )
        
        return self.site_array[start:end]


class UserGraph( INamedGraph ):
    def on_get_graph( self ) -> Optional[MGraph]:
        return self.__graph
    
    
    def on_get_name( self ) -> str:
        return self.__name
    
    
    def __init__( self, graph: MGraph, name = "user_graph" ):
        assert isinstance( graph, MGraph )
        assert isinstance( name, str )
        self.__graph = graph
        self.__name = name
    
    
    def __str__( self ):
        return self.name


class Component( INamed, IVisualisable ):
    """
    Stores information about a component of the (:class:`LegoModel`).
    
    :ivar model:                      Back-reference to model
    :ivar index:                      Index of component within model
    :ivar major_genes:                Major genes of this component.
                                      i.e. genes only containing domains in :ivar:`minor_domains`
    :ivar tree:                       Tree generated for this component.
                                      * `None` before it has been calculated.
    :ivar alignment:                  Alignment generated for this component, in FASTA format, with genes
                                      referenced by IID "legacy format" (not accession).
                                      * `None` before it has been calculated.
    :ivar minor_domains:              Minor domains of this component.
                                      i.e. all domains in this component.
                                      * `None` before it has been calculated.
    :ivar splits:                     Splits of the component tree.
                                      * `None` before it has been calculated.
    :ivar leaves:                     Leaves used in `splits`.
                                      * `None` before it has been calculated.       
    """
    
    
    def __init__( self, model: _Model_, index: int, major_genes: Tuple[Gene, ...] ):
        """
        CONSTRUCTOR
        See class attributes for parameter descriptions.
        """
        self.model: _Model_ = model
        self.index: int = index
        self.major_genes: Tuple[Gene, ...] = major_genes
        self.minor_domains: Tuple[Domain, ...] = None
        self.alignment: str = None
        self.splits: FrozenSet[Split] = None
        self.leaves: FrozenSet[INode] = None
        self.tree: MGraph = None
        self.tree_unrooted: MGraph = None
        self.tree_newick: str = None
    
    
    def get_accid( self ):
        return "COM{}".format( self.index )
        # for x in sorted( self.major_genes, key = cast( Any, str ) ):
        #     return x.accession
    
    
    @property
    def named_tree( self ):
        if self.tree:
            from groot.data.model_meta import _ComponentAsGraph
            return _ComponentAsGraph( self, False )
    
    
    @property
    def named_tree_unrooted( self ):
        if self.tree_unrooted:
            from groot.data.model_meta import _ComponentAsGraph
            return _ComponentAsGraph( self, True )
    
    
    @property
    def named_aligned_fasta( self ):
        if self.alignment:
            from groot.data.model_meta import _ComponentAsFasta
            return _ComponentAsFasta( self, True )
    
    
    @property
    def named_unaligned_fasta( self ):
        from groot.data.model_meta import _ComponentAsFasta
        return _ComponentAsFasta( self, False )
    
    
    def to_details( self ):
        r = []
        r.append( "MAJOR-SE: {}".format( string_helper.format_array( self.major_genes, sort = True ) ) )
        r.append( "MINOR-SE: {}".format( string_helper.format_array( self.minor_genes, sort = True ) ) )
        r.append( "MINOR-SS: {}".format( string_helper.format_array( self.minor_domains ) ) )
        r.append( "INCOMING: {}".format( string_helper.format_array( self.incoming_components(), sort = True ) ) )
        r.append( "OUTGOING: {}".format( string_helper.format_array( self.outgoing_components(), sort = True ) ) )
        return "\n".join( r )
    
    
    def get_aligned_fasta( self ):
        r = []
        
        for name, value in bio_helper.parse_fasta( text = self.alignment ):
            r.append( ">" + self.model.genes.by_legacy_accession( name ).accession )
            r.append( value )
        
        return "\n".join( r )
    
    
    def get_unaligned_fasta( self ):
        fasta = []
        
        if self.minor_domains:
            for domain in self.minor_domains:
                fasta.append( ">{}[{}:{}]".format( domain.gene.accession, domain.start, domain.end ) )
                fasta.append( domain.site_array )
                fasta.append( "" )
        else:
            return ";FASTA not available for {} (requires minor_domains)".format( self )
        
        return "\n".join( fasta )
    
    
    def get_unaligned_legacy_fasta( self ):
        fasta = []
        
        if self.minor_domains:
            for domain in self.minor_domains:
                fasta.append( ">{}".format( domain.gene.legacy_accession ) )
                fasta.append( domain.site_array )
                fasta.append( "" )
        else:
            raise ValueError( "Cannot obtain FASTA because the component minor domains have not yet been generated." )
        
        return "\n".join( fasta )
    
    
    def on_get_graph( self ):
        return self.tree
    
    
    def on_get_name( self ):
        return self.get_accid()
    
    
    def get_alignment_by_accession( self ) -> str:
        """
        Gets the `alignment` property, but translates gene IDs into accessions
        """
        if not self.alignment:
            return self.alignment
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        """
        OVERRIDE
        """
        super().on_get_vis_info( u )
        u.hint = UiHint( colour = EColour.RED, icon = groot_resources.black_major )
        u.value = "{} genes".format( array_helper.count( self.major_genes ) )
        u.properties += { "index"      : self.index,
                          "major"      : self.major_genes,
                          "minor_s"    : self.minor_genes,
                          "minor_ss"   : self.minor_domains,
                          "alignment"  : self.alignment,
                          "tree"       : self.tree,
                          "tree_newick": self.tree_newick,
                          "incoming"   : self.incoming_components(),
                          "outgoing"   : self.outgoing_components() }
    
    
    def __str__( self ) -> str:
        """
        OVERRIDE 
        """
        return self.name
    
    
    def incoming_components( self ) -> List["Component"]:
        """
        Returns components which implicitly form part of this component.
        """
        return [component for component in self.model.components if any( x in component.minor_genes for x in self.major_genes ) and component is not self]
    
    
    def outgoing_components( self ) -> List["Component"]:
        """
        Returns components which implicitly form part of this component.
        """
        return [component for component in self.model.components if any( x in component.major_genes for x in self.minor_genes ) and component is not self]
    
    
    @property
    def minor_genes( self ) -> List[Gene]:
        """
        Returns the minor genes.
        Genes with at least one domain in the minor set.
        See `__detect_minor` for the definition.
        """
        if self.minor_domains is None:
            return []
        
        return list( set( domain.gene for domain in self.minor_domains ) )
    
    
    def get_minor_domain_by_gene( self, gene: Gene ) -> Domain:
        if self.minor_domains:
            for domain in self.minor_domains:
                if domain.gene is gene:
                    return domain
        
        raise NotFoundError( "Gene «{}» not in component «{}».".format( gene, self ) )
    
    
    def has_overlap( self, d: Domain ):
        return any( d.has_overlap( ss ) for ss in self.minor_domains )


class FusionGraph( INamedGraph ):
    def __init__( self, graph, is_clean ):
        self.__graph = graph
        self.is_clean = is_clean
    
    
    def on_get_graph( self ):
        return self.__graph
    
    
    def on_get_name( self ):
        return str( self )
    
    
    def __str__( self ):
        return "nrfg" if self.is_clean else "nrfg_unclean"


class Subgraph( INamedGraph ):
    
    
    def __init__( self, graph: MGraph, subset: "Subset", algorithm_desc: str ):
        """
        CONSTRUCTOR
        :param graph:          The actual graph 
        :param subset:         The subset from whence it came 
        :param algorithm_desc: String describing the algorithm used to generate the graph 
        """
        self.__graph = graph
        self.__subset = subset
        self.__algorithm_desc = algorithm_desc
    
    
    def on_get_graph( self ) -> Optional[MGraph]:
        return self.__graph
    
    
    def on_get_name( self ) -> str:
        return str( self )
    
    
    def __str__( self ):
        return "subgraph_{}".format( self.__subset.get_accid() )


class Split( INamed, IVisualisable ):
    """
    Wraps a :class:`MSplit` making it Groot-friendly.
    """
    
    
    def __init__( self, split: MSplit, index: int ):
        self.split = split
        self.index = index
        self.components: Set[Component] = set()
        self.evidence_for: FrozenSet[Component] = None
        self.evidence_against: FrozenSet[Component] = None
        self.evidence_unused: FrozenSet[Component] = None
    
    
    def on_get_name( self ):
        return "split_{}".format( self.index )
    
    
    def __str__( self ):
        return self.name
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        super().on_get_vis_info( u )
        u.hint = UiHint( colour = EColour.CYAN, icon = groot_resources.black_split )
        u.text = self.split.to_string()
        u.properties += { "inside"          : self.split.inside,
                          "outside"         : self.split.outside,
                          "components"      : self.components,
                          "evidence_for"    : self.evidence_for,
                          "evidence_against": self.evidence_against,
                          "evidence_unused" : self.evidence_unused }
    
    
    def __eq__( self, other ):
        if isinstance( other, Split ):
            return self.split == other.split
        elif isinstance( other, Split ):
            return self.split == other
        else:
            return False
    
    
    def __hash__( self ):
        return hash( self.split )
    
    
    def is_evidenced_by( self, other: "Split" ) -> TTristate:
        """
        A split is evidenced by an `other` if it is a subset of the `other`.
        No evidence can be provided if the `other` set of leaves is not a subset
        
        :return: TTristate where:
                    True = Supports
                    False = Rejects
                    None = Cannot evidence 
        """
        if not self.split.all.issubset( other.split.all ):
            return None
        
        return self.split.inside.issubset( other.split.inside ) and self.split.outside.issubset( other.split.outside ) \
               or self.split.inside.issubset( other.split.inside ) and self.split.outside.issubset( other.split.outside )


class Report( INamed, IVisualisable ):
    def __init__( self, title: str, html: str ):
        self.title = title
        self.html = html
    
    
    def on_get_name( self ):
        return self.title
    
    
    def __str__( self ):
        return self.name
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        super().on_get_vis_info( u )
        u.hint = UiHint( colour = EColour.GREEN, icon = groot_resources.black_check )
        u.text = "(HTML report)"


class Subset( IVisualisable ):
    """
    Represents a subset of leaf nodes (see `ILeaf`).
    """
    
    
    def __init__( self, model: _Model_, index: int, contents: FrozenSet[INode] ):
        self.model = model
        self.index = index
        self.contents = contents
        self.pregraphs: List[Pregraph] = None
    
    
    def get_accid( self ):
        for x in sorted( self.contents, key = cast( Any, str ) ):
            if isinstance( x, Gene ):
                return x.accession
        
        return self.index
    
    
    def __len__( self ):
        return len( self.contents )
    
    
    def __str__( self ):
        return "subset_{}".format( self.get_accid() )
    
    
    def get_details( self ):
        return string_helper.format_array( self.contents )
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        super().on_get_vis_info( u )
        u.hint = UiHint( colour = EColour.CYAN, icon = groot_resources.black_subset )
        u.contents += lambda: self.contents


class Fusion( INamed, IVisualisable ):
    """
    Describes a fusion event
    
    :ivar components_in:       Input component(s) (usually more than one if it's a fusion! but the others may not be present in our data)
    :ivar component_out:       Output component
    """
    
    
    def __init__( self, index: int, components_in: Tuple[Component, ...], component_out: Component ) -> None:
        assert_type( "components_in", components_in, tuple )
        assert_type( "component_out", component_out, Component )
        
        self.index: int = index
        self.components_in: Tuple[Component] = components_in
        self.component_out: Component = component_out
        self.formations: List[Formation] = []
        
        if not self.components_in:
            raise ValueError( "Invalid Fusion. Cannot have an empty input list." )
        
        for x, y in combinations( chain( self.components_in, [self.component_out] ), 2 ):
            if x is y:
                raise ValueError( "Invalid Fusion. Two edges cannot refer to the same component, '{}'.".format( self, x ) )
    
    
    @property
    def long_name( self ):
        return "({}={})".format( "+".join( str( x ) for x in self.components_in ), self.component_out )
    
    
    def __str__( self ):
        return self.name
    
    
    def get_accid( self ):
        return self.component_out.get_accid()
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        super().on_get_vis_info( u )
        u.hint = UiHint( colour = EColour.RED, icon = groot_resources.black_fusion )
        u.text = self.long_name
        u.properties += { "index"        : self.index,
                          "components_in": self.components_in,
                          "component_out": self.component_out }
    
    
    def on_get_name( self ):
        return "F." + str( self.get_accid() )


class Formation( INamed, IVisualisable, INode ):
    # Formats for finding and creating legacy accessions
    _LEGACY_IDENTIFIER = re.compile( "^GrtF([0-9]+)F([0-9]+)$" )
    _LEGACY_FORMAT = "GrtF{}F{}"
    
    
    def __init__( self,
                  event: Fusion,
                  component: Component,
                  genes: FrozenSet[INode],
                  index: int,
                  pertinent_inner: FrozenSet[INode] ):
        """
        CONSTRUCTOR
        
        :param event:               The fusion event to which this `Formation` belongs.
        :param component:           The component we are _forming_.
                                    In a correctly operating process, this should be the same as `event.component_out`.
        :param genes:               The total set of _output_ genes in the tree, formed _by_ the fusion event.
                                    i.e. those that are formed by this fusion event,
        :param index:               Index of this `Formation` within the `Fusion` event (arbitrary).
        :param pertinent_inner:     The subset of `genes` that reside in the output component.
                                    i.e. the intersection of `event.component_out` and `genes`.
        """
        self.event = event
        self.component = component
        self.genes = genes
        self.pertinent_inner = pertinent_inner
        self.points: List[Point] = []
        self.index = index
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        super().on_get_vis_info( u )
        u.text = "{} points".format( len( self.points ) )
        u.properties += {
            "component"      : self.component,
            "genes"          : self.genes,
            "pertinent_inner": self.pertinent_inner,
            "index"          : self.index,
            "points"         : self.points }
    
    
    def get_accid( self ) -> str:
        return str( self.index )
    
    
    def __str__( self ):
        return self.name
    
    
    def on_get_name( self ):
        return "{}.{}".format( self.event, self.get_accid() )
    
    
    @property
    def legacy_accession( self ):
        return self._LEGACY_FORMAT.format( self.event.index, self.index )
    
    
    @classmethod
    def read_legacy_accession( cls, name: str ) -> Tuple[int, int]:
        g = cls._LEGACY_IDENTIFIER.match( name ).groups()
        return int( g[0] ), int( g[1] )
    
    
    @classmethod
    def is_legacy_accession( cls, name: str ):
        """
        Determines if an accession was created via the `legacy_accession` property.
        """
        return bool( cls._LEGACY_IDENTIFIER.match( name ) )


class Point( INamed, INode, IVisualisable ):
    """
    Point of fusion.
    
    :ivar pertinent_outer:      The `outer_genes` which are actually part of the formed component. (using `get_pertinent_outer` also includes `self`).
    :ivar formation:            See `__init__`.
    :ivar point_component:      See `__init__`.
    :ivar outer_genes:      See `__init__`.
    :ivar index:                See `__init__`.
    """
    # Formats for finding and creating legacy accessions
    _LEGACY_IDENTIFIER = re.compile( "^GrtP([0-9]+)P([0-9]+)P([0-9]+)$" )
    _LEGACY_FORMAT = "GrtP{}P{}P{}"
    
    
    def __init__( self,
                  formation: Formation,
                  outer_genes: FrozenSet[INode],
                  point_component: Component,
                  index: int ):
        """
        CONSTRUCTOR
        :param formation:               What this point is creating
        :param outer_genes:             A subset of genes from which this fusion point _originates_
        :param point_component:         The component tree this point resides within
        :param index:                   The index of this point within the owning `formation`
        """
        u = set.union( *[set( x.major_genes ) for x in formation.event.components_in] )
        
        self.formation = formation
        self.outer_genes = outer_genes
        self.pertinent_outer = frozenset( self.outer_genes.intersection( u ) )
        self.point_component = point_component
        self.index = index
    
    
    def on_get_name( self ):
        return "{}.{}".format( self.formation, self.point_component.get_accid() )
    
    
    def __str__( self ):
        return self.name
    
    
    @property
    def component( self ):
        warnings.warn( "`LegoPoint.component` is ambiguous. Use `LegoPoint.formation.event.component` or `LegoPoint.point_component` instead.", DeprecationWarning )
        return self.formation.component
    
    
    @property
    def genes( self ):
        warnings.warn( "use .formation.", DeprecationWarning )
        return self.formation.genes
    
    
    @property
    def pertinent_inner( self ):
        warnings.warn( "use .formation.", DeprecationWarning )
        return self.formation.pertinent_inner
    
    
    @property
    def event( self ):
        warnings.warn( "use .formation.", DeprecationWarning )
        return self.formation.event
    
    
    @property
    def legacy_accession( self ):
        return self._LEGACY_FORMAT.format( self.formation.event.index, self.formation.index, self.index )
    
    
    @classmethod
    def read_legacy_accession( cls, name: str ) -> Tuple[int, int, int]:
        g = cls._LEGACY_IDENTIFIER.match( name ).groups()
        return int( g[0] ), int( g[1] ), int( g[2] )
    
    
    @classmethod
    def is_legacy_accession( cls, name: str ):
        """
        Determines if an accession was created via the `legacy_accession` property.
        """
        return bool( cls._LEGACY_IDENTIFIER.match( name ) )
    
    
    def on_get_vis_info( self, u: UiInfo ) -> None:
        super().on_get_vis_info( u )
        u.hint = UiHint( colour = EColour.MAGENTA, icon = groot_resources.black_fusion )
        u.text = "{} genes".format( len( self.formation.genes ) )
        u.properties += {
            "outer_genes"    : self.outer_genes,
            "pertinent_outer": self.pertinent_outer,
            "index"          : self.index }
    
    
    @property
    def count( self ):
        return len( self.formation.genes )
    
    
    def get_pertinent_inner( self ):
        return self.formation.pertinent_inner.union( { self } )
    
    
    def get_pertinent_outer( self ):
        return self.pertinent_outer.union( { self } )


class FixedUserGraph( UserGraph ):
    """
    :class:`UserGraph` that has been saved by the user to the :class:`LegoUserGraphCollection` at :field:`LegoModel.user_graphs`.
    """
    pass


class Pregraph( INamedGraph ):
    def on_get_graph( self ) -> Optional[MGraph]:
        return self.__graph
    
    
    def on_get_name( self ):
        return "pregraph_{}_in_{}".format( self.subset.get_accid(), self.component.get_accid() )
    
    
    def __str__( self ):
        return self.name
    
    
    def __init__( self, graph: MGraph, subset: Subset, component: Component ):
        self.__graph = graph
        self.subset = subset
        self.component = component
