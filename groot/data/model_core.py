import re
import warnings
from typing import Tuple, Optional, List, Iterable, FrozenSet, cast, Any, Set

from groot.data.model_interfaces import EPosition, INamed, IHasFasta, INamedGraph, ILegoNode
from groot.frontends.gui.forms.resources import resources as groot_resources
from intermake.engine.environment import MENV
from intermake.visualisables.visualisable import UiInfo, EColour, IVisualisable
from intermake_qt.forms.designer.resource_files import resources as intermake_resources
from mgraph import MGraph, Split
from mhelper import SwitchError, NotFoundError, string_helper, bio_helper, array_helper, TTristate


_LegoModel_ = "LegoModel"

class LegoEdge( IHasFasta ):
    """
    IMMUTABLE
    
    Edge from one subsequence to another.
    """
    
    
    def __init__( self, source: "LegoSubsequence", destination: "LegoSubsequence" ) -> None:
        """
        CONSTRUCTOR
        :param source:          Source sequence `left` 
        :param destination:     Destination sequence `right` 
        """
        self.left: LegoSubsequence = source
        self.right: LegoSubsequence = destination
    
    
    def to_fasta( self ) -> str:
        fasta = []
        fasta.append( ">{} [ {} : {} ]".format( self.left.sequence.accession, self.left.start, self.left.end ) )
        fasta.append( self.left.site_array or ";MISSING" )
        fasta.append( "" )
        fasta.append( ">{} [ {} : {} ]".format( self.right.sequence.accession, self.right.start, self.right.end ) )
        fasta.append( self.right.site_array or ";MISSING" )
        fasta.append( "" )
        return "\n".join( fasta )
    
    
    def visualisable_info( self ) -> UiInfo:
        """
        OVERRIDE
        """
        return UiInfo( name = str( self ),
                       doc = "",
                       type_name = "Edge",
                       value = "",
                       colour = EColour.CYAN,
                       icon = intermake_resources.folder,
                       extra_named = (self.left, self.right) )
    
    
    def __contains__( self, item: "LegoSequence" ) -> bool:
        """
        OVERRIDE
        Does the edge specify a sequence as either of its endpoints? 
        """
        return item in self.left or item in self.right
    
    
    @staticmethod
    def to_string( sequence: "LegoSequence", start: int, end: int, sequence_b: "LegoSequence", start_b: int, end_b: int ) -> str:
        return LegoSubsequence.to_string( sequence, start, end ) + "--" + LegoSubsequence.to_string( sequence_b, start_b, end_b )
    
    
    def __str__( self ) -> str:
        """
        OVERRIDE 
        """
        return self.to_string( self.left.sequence, self.left.start, self.left.end, self.right.sequence, self.right.start, self.right.end )
    
    
    TSide = "Union[LegoSequence,LegoSubsequence,LegoComponent,bool]"
    
    
    def position( self, item: TSide ) -> bool:
        """
        Returns `True` if `item` appears in the `destination` list, or `False` if it appears in the `source` list.
        
        Supports: Sequence, subsequence or component. Note that only the component of the SEQUENCE is considered, not the individual subsequences.
        
        Raises `KeyError` if it does not appear in either.
        """
        if isinstance( item, LegoSubsequence ):
            if item.sequence is self.left.sequence:
                return False
            
            if item.sequence is self.right.sequence:
                return True
            
            raise KeyError( "I cannot find the subsequence '{}' within this edge.".format( item ) )
        elif isinstance( item, LegoSequence ):
            if item is self.left.sequence:
                return False
            
            if item is self.right.sequence:
                return True
            
            raise KeyError( "I cannot find the sequence '{}' within this edge. This edge's sequences are '{}' and '{}'.".format( item, self.left.sequence, self.right.sequence ) )
        elif isinstance( item, LegoComponent ):
            if self.left.sequence in item.major_sequences:
                if self.right.sequence in item.major_sequences:
                    raise KeyError( "I can find the component '{}' within this edge, but both sides of the edge have this same component. This edge's sequences are '{}' and '{}'.".format( item, self.left.sequence, self.right.sequence ) )
                
                return False
            
            if self.right.sequence in item.major_sequences:
                return True
            
            raise KeyError( "I cannot find the component '{}' within this edge. This edge's sequences are '{}' and '{}'.".format( item, self.left.sequence, self.right.sequence ) )
        elif isinstance( item, bool ):
            return item
        else:
            raise SwitchError( "position.item", item, instance = True )
    
    
    def sides( self, item: TSide ) -> Tuple["LegoSubsequence", "LegoSubsequence"]:
        """
        As `sides` but returns both items.
        """
        position = self.position( item )
        return (self.right, self.left) if position else (self.left, self.right)
    
    
    def side( self, item: TSide, opposite = False ) -> "LegoSubsequence":
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
    
    
    def opposite( self, item: TSide ) -> "LegoSubsequence":
        """
        Convenience function that calls `side` with `opposite = True`.
        """
        return self.side( item, opposite = True )


class LegoSubsequence( IHasFasta, IVisualisable ):
    """
    IMMUTABLE
    
    Portion of a sequence.
    
    Note that we follow the somewhat atypical BLAST convention and so the `start` and `end` range is inclusive.
    """
    
    
    def __init__( self, sequence: "LegoSequence", start: int, end: int ):
        """
        CONSTRUCTOR
        :param sequence: Owning sequence
        :param start: Leftmost position (inclusive) 
        :param end: Rightmost position (inclusive) 
        """
        assert isinstance( sequence, LegoSequence )
        assert isinstance( start, int )
        assert isinstance( end, int )
        
        assert start >= 1
        assert end >= 1
        
        if start > end:
            raise ValueError( "Attempt to create a subsequence in «{0}» where start ({1}) > end ({2}).".format( sequence, start, end ) )
        
        self.sequence: LegoSequence = sequence
        self.__start: int = start  # Start position
        self.__end: int = end  # End position
    
    
    def to_fasta( self ):
        fasta = []
        
        fasta.append( ">" + self.sequence.accession + "[{}:{}]".format( self.start, self.end ) )
        
        if self.site_array is not None:
            fasta.append( self.site_array )
        else:
            fasta.append( "; MISSING" )
        
        return "\n".join( fasta )
    
    
    def has_overlap( self, two: "LegoSubsequence" ) -> bool:
        """
        Returns if the `two` `LegoSubsequence`s overlap.
        """
        if self.sequence is not two.sequence:
            return False
        
        return self.start <= two.end and two.start <= self.end
    
    
    def intersection( self, two: "LegoSubsequence" ) -> "LegoSubsequence":
        """
        Returns a `LegoSubsequence` that is the intersection of the `two`.
        :except NotFoundError: The `two` do not overlap.
        """
        assert self.sequence is two.sequence
        
        start = max( self.start, two.start )
        end = min( self.end, two.end )
        
        if start > end:
            raise NotFoundError( "Cannot create `intersection` for non-overlapping ranges «{}» and «{}».".format( self, two ) )
        
        return LegoSubsequence( self.sequence, start, end )
    
    
    def visualisable_info( self ) -> UiInfo:
        """
        OVERRIDE 
        """
        return UiInfo( name = str( self ),
                       doc = "",
                       type_name = "Subsequence",
                       value = "{} sites".format( self.length ),
                       colour = EColour.RED,
                       icon = intermake_resources.folder,
                       extra = { "sequence": self.sequence,
                                 "start"   : self.start,
                                 "end"     : self.end,
                                 "length"  : self.length,
                                 "sites"   : self.site_array } )
    
    
    @staticmethod
    def to_string( sequence, start, end ) -> str:
        return "{}[{}:{}({})]".format( sequence.accession, start, end, end - start + 1 )
    
    
    def __str__( self ) -> str:
        return self.to_string( self.sequence, self.start, self.end )
    
    
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
        Obtains the slice of the sequence array pertinent to this subsequence
        """
        if self.sequence.site_array:
            result = self.sequence.site_array[self.start - 1:self.end]
            if len( result ) != self.length:
                raise ValueError( "Cannot extract site range {}-{} from site array of length {}.".format( self.start, self.length, self.sequence.length ) )
            
            return result
        else:
            return None
    
    
    @property
    def length( self ) -> int:
        """
        Calculates the length of this subsequence
        """
        return self.end - self.start + 1


class LegoUserDomain( LegoSubsequence ):
    """
    A user-domain is just domain (LegoSubsequence) which the user has defined.
    """
    pass


class LegoSequence( ILegoNode, IHasFasta, IVisualisable, INamed ):
    """
    Protein (or DNA) sequence
    
    :attr id:           Internal ID. An arbitrary number guaranteed to be unique within the model.
    :attr accession:    Database accession. Note that this can't look like an accession produced by the `legacy_accession` property.
    :attr model:        Owning model.
    :attr site_array:   Site data. This can be `None` before the data is loaded in. The length must match `length`.
    :attr comments:     Comments on the sequence.
    :attr length:       Length of the sequence. This must match `site_array`, it that is set.
    """
    
    # Formats for finding and creating legacy accessions
    _LEGACY_IDENTIFIER = re.compile( "^GrtS([0-9]+)$" )
    _LEGACY_FORMAT = "GrtS{}"
    
    
    def __init__( self, model: _LegoModel_, accession: str, id: int ) -> None:
        """
        CONSTRUCTOR
        See class attributes for parameter descriptions.
        """
        if LegoSequence.is_legacy_accession( accession ):
            raise ValueError( "You have a sequence with an accession «{}», but {} has reserved that name for compatibility with legacy Phylip format files. Avoid using accessions that only contain numbers prefixed by an 'S'.".format( accession, MENV.name ) )
        
        self.id: int = id
        self.accession: str = accession  # Database accession (ID)
        self.model: _LegoModel_ = model
        self.site_array: str = None
        self.comments: List[str] = []
        self.length = 1
        self.position = EPosition.NONE
    
    
    def on_get_name( self ):
        return self.accession
    
    
    def iter_edges( self ) -> Iterable[LegoEdge]:
        return (x for x in self.model.edges if x.left is self or x.right is self)
    
    
    def iter_userdomains( self ):
        return (x for x in self.model.user_domains if x.sequence is self)
    
    
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
        return int( LegoSequence._LEGACY_IDENTIFIER.match( name ).groups()[0] )
    
    
    @staticmethod
    def is_legacy_accession( name: str ):
        """
        Determines if an accession was created via the `legacy_accession` function.
        """
        return bool( LegoSequence._LEGACY_IDENTIFIER.match( name ) )
    
    
    @property
    def legacy_accession( self ):
        """
        We make an accession for compatibility with programs that still use Phylip format.
        We can't just use a number because some programs mistake this for a line count.
        """
        return self._LEGACY_FORMAT.format( self.id )
    
    
    def get_totality( self ) -> LegoSubsequence:
        """
        Gets the subsequence spanning the totality of this sequence.
        """
        return LegoSubsequence( self, 1, self.length )
    
    
    def visualisable_info( self ) -> UiInfo:
        """
        OVERRIDE 
        """
        return UiInfo( name = self.accession,
                       doc = "",
                       type_name = "Sequence",
                       value = "{} sites".format( self.length ),
                       colour = EColour.BLUE,
                       icon = intermake_resources.folder,
                       extra = { "id"       : self.legacy_accession,
                                 "length"   : self.length,
                                 "accession": self.accession,
                                 "position" : self.position,
                                 "num_sites": len( self.site_array ) if self.site_array else "?",
                                 "sites"    : self.site_array } )
    
    
    def __str__( self ) -> str:
        """
        OVERRIDE 
        """
        return "G{}".format( self.accession or self.index )
    
    
    @property
    def index( self ) -> int:
        """
        Gets the index of this sequence within the model
        """
        return self.model.sequences.index( self )
    
    
    def __repr__( self ) -> str:
        """
        OVERRIDE 
        """
        return "{}".format( self.accession )
    
    
    def _ensure_length( self, new_length: int ) -> None:
        """
        Ensures the length of the sequence accommodates `new_length`.
        """
        assert isinstance( new_length, int )
        
        if new_length == 0:
            return
        
        if self.length < new_length:
            self.length = new_length
    
    
    def sub_sites( self, start: int, end: int ) -> Optional[str]:
        """
        Retrieves a portion of the sequence.
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


class LegoComponent( INamed, IVisualisable ):
    """
    Stores information about a component of the (:class:`LegoModel`).
    
    :attr model:                      Back-reference to model
    :attr index:                      Index of component within model
    :attr major_sequences:            Major sequences of this component.
                                      i.e. sequences only containing domains in :attr:`minor_subsequences`
    :attr tree:                       Tree generated for this component.
                                      * `None` before it has been calculated.
    :attr alignment:                  Alignment generated for this component, in FASTA format, with sequences
                                      referenced by IID "legacy format" (not accession).
                                      * `None` before it has been calculated.
    :attr minor_subsequences:         Minor subsequences of this component.
                                      i.e. all domains in this component.
                                      * `None` before it has been calculated.
    :attr splits:                     Splits of the component tree.
                                      * `None` before it has been calculated.
    :attr leaves:                     Leaves used in `splits`.
                                      * `None` before it has been calculated.       
    """
    
    
    def __init__( self, model: _LegoModel_, index: int, major_sequences: Tuple[LegoSequence] ):
        """
        CONSTRUCTOR
        See class attributes for parameter descriptions.
        """
        self.model: _LegoModel_ = model
        self.index: int = index
        self.major_sequences: Tuple[LegoSequence] = major_sequences
        self.minor_subsequences: Tuple[LegoSubsequence] = None
        self.alignment: str = None
        self.splits: FrozenSet[LegoSplit] = None
        self.leaves: FrozenSet[ILegoNode] = None
        self.tree: MGraph = None
        self.tree_unrooted: MGraph = None
        self.tree_newick: str = None
    
    
    def get_accid( self ):
        for x in sorted( self.major_sequences, key = cast( Any, str ) ):
            return x.accession
    
    
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
        r.append( "MAJOR-SE: {}".format( string_helper.format_array( self.major_sequences, sort = True ) ) )
        r.append( "MINOR-SE: {}".format( string_helper.format_array( self.minor_sequences, sort = True ) ) )
        r.append( "MINOR-SS: {}".format( string_helper.format_array( self.minor_subsequences ) ) )
        r.append( "INCOMING: {}".format( string_helper.format_array( self.incoming_components(), sort = True ) ) )
        r.append( "OUTGOING: {}".format( string_helper.format_array( self.outgoing_components(), sort = True ) ) )
        return "\n".join( r )
    
    
    def get_aligned_fasta( self ):
        r = []
        
        for name, value in bio_helper.parse_fasta( text = self.alignment ):
            r.append( ">" + self.model.find_sequence_by_legacy_accession( name ).accession )
            r.append( value )
        
        return "\n".join( r )
    
    
    def get_unaligned_fasta( self ):
        fasta = []
        
        if self.minor_subsequences:
            for subsequence in self.minor_subsequences:
                fasta.append( ">{}[{}:{}]".format( subsequence.sequence.accession, subsequence.start, subsequence.end ) )
                fasta.append( subsequence.site_array )
                fasta.append( "" )
        else:
            return ";FASTA not available for {} (requires minor_subsequences)".format( self )
        
        return "\n".join( fasta )
    
    
    def get_unaligned_legacy_fasta( self ):
        fasta = []
        
        if self.minor_subsequences:
            for subsequence in self.minor_subsequences:
                fasta.append( ">{}".format( subsequence.sequence.legacy_accession ) )
                fasta.append( subsequence.site_array )
                fasta.append( "" )
        else:
            raise ValueError( "Cannot obtain FASTA because the component minor subsequences have not yet been generated." )
        
        return "\n".join( fasta )
    
    
    def on_get_graph( self ):
        return self.tree
    
    
    def on_get_name( self ):
        return "comp_{}".format( self.get_accid() )
    
    
    def get_alignment_by_accession( self ) -> str:
        """
        Gets the `alignment` property, but translates sequence IDs into accessions
        """
        if not self.alignment:
            return self.alignment
    
    
    def visualisable_info( self ) -> UiInfo:
        """
        OVERRIDE
        """
        return UiInfo( name = str( self ),
                       type_name = "Component",
                       value = "{} sequences".format( array_helper.count( self.major_sequences ) ),
                       colour = EColour.RED,
                       icon = intermake_resources.folder,
                       extra = { "index"      : self.index,
                                 "major"      : self.major_sequences,
                                 "minor_s"    : self.minor_sequences,
                                 "minor_ss"   : self.minor_subsequences,
                                 "alignment"  : self.alignment,
                                 "tree"       : self.tree,
                                 "tree_newick": self.tree_newick,
                                 "incoming"   : self.incoming_components(),
                                 "outgoing"   : self.outgoing_components() } )
    
    
    def __str__( self ) -> str:
        """
        OVERRIDE 
        """
        return self.name
    
    
    def incoming_components( self ) -> List["LegoComponent"]:
        """
        Returns components which implicitly form part of this component.
        """
        return [component for component in self.model.components if any( x in component.minor_sequences for x in self.major_sequences ) and component is not self]
    
    
    def outgoing_components( self ) -> List["LegoComponent"]:
        """
        Returns components which implicitly form part of this component.
        """
        return [component for component in self.model.components if any( x in component.major_sequences for x in self.minor_sequences ) and component is not self]
    
    
    @property
    def minor_sequences( self ) -> List[LegoSequence]:
        """
        Returns the minor sequences.
        Sequences with at least one subsequence in the minor set.
        See `__detect_minor` for the definition.
        """
        if self.minor_subsequences is None:
            return []
        
        return list( set( subsequence.sequence for subsequence in self.minor_subsequences ) )
    
    
    def get_minor_subsequence_by_sequence( self, sequence: LegoSequence ) -> LegoSubsequence:
        if self.minor_subsequences:
            for subsequence in self.minor_subsequences:
                if subsequence.sequence is sequence:
                    return subsequence
        
        raise NotFoundError( "Sequence «{}» not in component «{}».".format( sequence, self ) )


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
    
    
    def __init__( self, graph: MGraph, subset: "LegoSubset", algorithm: str ):
        """
        CONSTRUCTOR
        :param graph:       The actual graph 
        :param subset:      The subset from whence it came 
        :param algorithm:   The algorithm used to generate the graph 
        """
        self.__graph = graph
        self.__subset = subset
        self.__algorithm = algorithm
    
    
    def on_get_graph( self ) -> Optional[MGraph]:
        return self.__graph
    
    
    def on_get_name( self ) -> str:
        return str( self )
    
    
    def __str__( self ):
        return "subgraph_{}".format( self.__subset.get_accid() )
    
    
    def visualisable_info( self ):
        return UiInfo( name = str( self ),
                       value = str( self.graph ),
                       extra = { "algorithm": self.__algorithm } )


class LegoSplit( INamed, IVisualisable ):
    """
    Wraps a :class:`Split` making it Groot-friendly.
    """
    
    
    def __init__( self, split: Split, index: int ):
        self.split = split
        self.index = index
        self.components: Set[LegoComponent] = set()
        self.evidence_for: FrozenSet[LegoComponent] = None
        self.evidence_against: FrozenSet[LegoComponent] = None
        self.evidence_unused: FrozenSet[LegoComponent] = None
    
    
    def on_get_name( self ):
        return "split_{}".format( self.index )
    
    
    def __str__( self ):
        return self.name
    
    
    def visualisable_info( self ):
        return UiInfo( name = str( self ),
                       doc = "",
                       type_name = "Split",
                       value = self.split.to_string(),
                       colour = EColour.CYAN,
                       icon = groot_resources.black_split,
                       extra = { "inside"          : self.split.inside,
                                 "outside"         : self.split.outside,
                                 "components"      : self.components,
                                 "evidence_for"    : self.evidence_for,
                                 "evidence_against": self.evidence_against,
                                 "evidence_unused" : self.evidence_unused,
                                 } )
    
    
    def __eq__( self, other ):
        if isinstance( other, LegoSplit ):
            return self.split == other.split
        elif isinstance( other, Split ):
            return self.split == other
        else:
            return False
    
    
    def __hash__( self ):
        return hash( self.split )
    
    
    def is_evidenced_by( self, other: "LegoSplit" ) -> TTristate:
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


class LegoReport( INamed, IVisualisable ):
    def __init__( self, title: str, html: str ):
        self.title = title
        self.html = html
    
    
    def on_get_name( self ):
        return self.title
    
    
    def __str__( self ):
        return self.name
    
    
    def visualisable_info( self ):
        return UiInfo( name = self.title,
                       doc = "",
                       type_name = "Report",
                       value = "(HTML report)",
                       colour = EColour.GREEN,
                       icon = groot_resources.black_check )


class LegoSubset( IVisualisable ):
    """
    Represents a subset of leaf nodes (see `ILeaf`).
    """
    
    
    def __init__( self, model: _LegoModel_, index: int, contents: FrozenSet[ILegoNode] ):
        self.model = model
        self.index = index
        self.contents = contents
        self.pregraphs: List[LegoPregraph] = None
    
    
    def get_accid( self ):
        for x in sorted( self.contents, key = cast( Any, str ) ):
            if isinstance( x, LegoSequence ):
                return x.accession
        
        return self.index
    
    
    def __len__( self ):
        return len( self.contents )
    
    
    def __str__( self ):
        return "subset_{}".format( self.get_accid() )
    
    
    def get_details( self ):
        return string_helper.format_array( self.contents )
    
    
    def visualisable_info( self ):
        return UiInfo( name = str( self ),
                       doc = "",
                       type_name = "Subset",
                       value = self.get_details(),
                       colour = EColour.CYAN,
                       icon = groot_resources.black_subset,
                       extra_indexed = self.contents )


class LegoFusion( INamed, IVisualisable ):
    """
    Describes a fusion event
    
    :data component_a:          First component
    :data component_b:          Second component
    :data products:             Generated component (root)
    :data future_products:      Generated component (all possibilities)
    :data point_a:              The name of the node on the first component which the fusion occurs
    :data point_b:              The name of the node on the second component which the fusion occurs
    """
    
    
    def visualisable_info( self ):
        return UiInfo( name = str( self ),
                       doc = "",
                       type_name = "Fusion",
                       value = self.long_name,
                       colour = EColour.RED,
                       icon = groot_resources.black_fusion,
                       extra = { "index"          : self.index,
                                 "component_a"    : self.component_a,
                                 "component_b"    : self.component_b,
                                 "products"       : self.products,
                                 "future_products": self.future_products,
                                 "formations"     : self.formations } )
    
    
    def on_get_name( self ):
        return "F" + str( self.get_accid() )
    
    
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
        self.formations: List[LegoFormation] = []
    
    
    @property
    def component_c( self ) -> LegoComponent:
        return array_helper.single_or_error( self.products )
    
    
    @property
    def long_name( self ):
        return "({}+{}={})".format( self.component_a, self.component_b, ",".join( x.__str__() for x in self.products ) )
    
    
    def __str__( self ):
        return self.name
    
    
    def get_accid( self ):
        return self.component_c.get_accid()


class LegoFormation( INamed, IVisualisable, ILegoNode ):
    
    
    def __init__( self,
                  event: LegoFusion,
                  component: LegoComponent,
                  sequences: FrozenSet[ILegoNode],
                  index: int,
                  pertinent_inner: FrozenSet[ILegoNode] ):
        self.event = event
        self.component = component
        self.sequences = sequences
        self.pertinent_inner = pertinent_inner
        self.points: List[LegoPoint] = []
        self.index = index
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = str( self ),
                       type_name = "Formation",
                       value = "{} points".format( len( self.points ) ),
                       extra = {
                           "component"      : self.component,
                           "sequences"      : self.sequences,
                           "pertinent_inner": self.pertinent_inner,
                           "index"          : self.index,
                           "points"         : self.points } )
    
    
    def get_accid( self ) -> str:
        return string_helper.format_array( self.pertinent_inner )
        # return str( self.index )
    
    
    def __str__( self ):
        return self.name
    
    
    def on_get_name( self ):
        return "{}.{}".format( self.event, self.get_accid() )
    
    
    _LEGACY_IDENTIFIER = re.compile( "^GrtF([0-9]+)F([0-9]+)$" )
    _LEGACY_FORMAT = "GrtF{}F{}"
    
    
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


class LegoPoint( INamed, ILegoNode, IVisualisable ):
    """
    Point of fusion.
    
    :attr pertinent_outer:      The `outer_sequences` which are actually part of the formed component. (using `get_pertinent_outer` also includes `self`).
    :attr formation:            See `__init__`.
    :attr point_component:      See `__init__`.
    :attr outer_sequences:      See `__init__`.
    :attr index:                See `__init__`.
    """
    
    
    # Formats for finding and creating legacy accessions
    
    def __init__( self,
                  formation: LegoFormation,
                  outer_sequences: FrozenSet[ILegoNode],
                  point_component: LegoComponent,
                  index: int ):
        """
        CONSTRUCTOR
        :param formation:             What this point is creating
        :param outer_sequences:       A subset of genes from which this fusion point _originates_
        :param point_component:       The component tree this point resides within
        :param index:                 The index of this point within the owning `formation`
        """
        self.formation = formation
        self.outer_sequences = outer_sequences
        self.pertinent_outer = frozenset( self.outer_sequences.intersection( set( self.formation.event.component_a.major_sequences ).union( set( self.formation.event.component_b.major_sequences ) ) ) )
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
    def sequences( self ):
        warnings.warn( "use .formation.", DeprecationWarning )
        return self.formation.sequences
    
    
    @property
    def pertinent_inner( self ):
        warnings.warn( "use .formation.", DeprecationWarning )
        return self.formation.pertinent_inner
    
    
    @property
    def event( self ):
        warnings.warn( "use .formation.", DeprecationWarning )
        return self.formation.event
    
    
    _LEGACY_IDENTIFIER = re.compile( "^GrtP([0-9]+)P([0-9]+)P([0-9]+)$" )
    _LEGACY_FORMAT = "GrtP{}P{}P{}"
    
    
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
    
    
    def visualisable_info( self ):
        return UiInfo( name = str( self ),
                       doc = "",
                       value = "{} sequences".format( len( self.formation.sequences ) ),
                       colour = EColour.MAGENTA,
                       icon = groot_resources.black_fusion,
                       type_name = "Point",
                       extra = {
                           "outer_sequences": self.outer_sequences,
                           "pertinent_outer": self.pertinent_outer,
                           "index"          : self.index } )
    
    
    @property
    def count( self ):
        return len( self.formation.sequences )
    
    
    def get_pertinent_inner( self ):
        return self.formation.pertinent_inner.union( { self } )
    
    
    def get_pertinent_outer( self ):
        return self.pertinent_outer.union( { self } )


class FixedUserGraph( UserGraph ):
    """
    :class:`UserGraph` that has been saved by the user to the :class:`LegoUserGraphCollection` at :field:`LegoModel.user_graphs`.
    """
    pass


class LegoPregraph( INamedGraph ):
    def on_get_graph( self ) -> Optional[MGraph]:
        return self.__graph
    
    
    def on_get_name( self ):
        return "pregraph_{}_in_{}".format( self.subset.get_accid(), self.component.get_accid() )
    
    
    def __str__( self ):
        return self.name
    
    
    def __init__( self, graph: MGraph, subset: LegoSubset, component: LegoComponent ):
        self.__graph = graph
        self.subset = subset
        self.component = component
