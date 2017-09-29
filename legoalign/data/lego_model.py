"""
Holds the Lego model, and its dependencies.

See class `LegoModel`.
"""

from typing import Iterable, Iterator, List, Optional, Set

from colorama import Back, Fore

from mcommand import EColour, IVisualisable, UiInfo, resources
from mhelper import Logger, SwitchError, array_helper, file_helper as FileHelper, string_helper, MEnum


LOG = Logger( False )

# EDGE_FORMAT = "❮ {}·𝑛{} {}…{} ❮❯ {}·𝑛{} {}…{} ❯"
# SIDE_FORMAT = "{}·𝑛{}~{}…{}·𝓂{}"
# SEQ_FORMAT = "{}·𝑛{}"
# SUBSEQUENCE_FORMAT = "{}·𝑛{}~{}…{}"

SIDE_FORMAT = Fore.CYAN + "{}" + Fore.WHITE + "·𝑛" + Fore.GREEN + "{} " + Fore.LIGHTYELLOW_EX + "{}" + Fore.WHITE + "…" + Fore.YELLOW + "{}" + Fore.WHITE + "·𝓂" + Fore.GREEN + "{}" + Fore.RESET
SUBSEQUENCE_FORMAT = Fore.CYAN + "{}" + Fore.WHITE + "·𝑛" + Fore.GREEN + "{} " + Fore.LIGHTYELLOW_EX + "{}" + Fore.WHITE + "…" + Fore.YELLOW + "{}" + Fore.RESET
EDGE_FORMAT = Back.BLUE + "❮ " + SUBSEQUENCE_FORMAT + " ❮ " + Back.RED + "❯ " + SUBSEQUENCE_FORMAT + " ❯" + Back.RESET
SEQ_FORMAT = Fore.CYAN + "{}" + Fore.WHITE + "·" + Fore.GREEN + "{}" + Fore.RESET


class ESiteType( MEnum ):
    """
    Type of sites.
    
    :data UNKNOWN:  Unknown site type. Placeholder only until the correct value is identified. Not usually a valid option. 
    :data PROTEIN:  Protein sites:  IVLFCMAGTSWYPHEQDNKR
    :data DNA:      DNA sites:      ATCG
    :data RNA:      RNA sites:      AUCG
    """
    UNKNOWN = 0
    PROTEIN = 1
    DNA = 2
    RNA = 3


class ETristate( MEnum ):
    """
    General tristate. More specific to the user than `True`, `False`, `None`.
    
    :data UNKNOWN: Not specified or unknown
    :data YES:     The affirmative
    :data NO:      Opposite of yes
    """
    UNKNOWN = 0
    YES = 1
    NO = -1


class LegoSide( IVisualisable ):
    def __init__( self, is_source: bool ):
        self.__list = [ ]  # type:List[LegoSubsequence]
        self.is_source = is_source
    
    
    def visualisable_info( self ):
        return UiInfo( name = "source" if self.is_source else "destination",
                       comment = None,
                       type_name = "Side",
                       value = "{}--{}".format( self.start, self.end ),
                       colour = EColour.GREEN,
                       icon = resources.folder,
                       extra = { "start"       : self.start,
                                 "end"         : self.end,
                                 "length"      : self.length,
                                 "sites"       : self.sites,
                                 "component"   : self.component,
                                 "sequence"    : self.sequence,
                                 "subsequences": self.__list } )
    
    
    def add( self, subsequence: "LegoSubsequence" ):
        array_helper.ordered_insert( self.__list, subsequence, lambda x: x.start )
    
    
    def __len__( self ):
        return len( self.__list )
    
    
    @property
    def sequence( self ):
        """
        Sequence of the subsequences
        """
        return self.__list[ 0 ].sequence
    
    
    @property
    def component( self ):
        """
        Major component of the sequence
        """
        return self.__list[ 0 ].sequence.component
    
    
    @property
    def sites( self ):
        return self.sequence.sub_sites( self.start, self.end )
    
    
    @property
    def start( self ):
        """
        Index of the leftmost subsequence
        """
        return min( x.start for x in self.__list )
    
    
    @property
    def end( self ):
        """
        Index of the rightmost subsequence
        """
        return max( x.end for x in self.__list )
    
    
    @staticmethod
    def to_string( sequence, start, end, count ):
        return SIDE_FORMAT.format( sequence.accession, sequence.length, start, end, count )
    
    
    def __str__( self ):
        return self.to_string( self.sequence, self.start, self.end, len( self.__list ) )
    
    
    def __contains__( self, item ):
        if isinstance( item, LegoSubsequence ):
            return item in self.__list
        
        raise TypeError( "Cannot tell if LegoSide contains the item because the item is of type '{}', not '{}'.".format( type( item ).__name__, LegoSubsequence.__name__ ) )
    
    
    def remove( self, subsequence: "LegoSubsequence" ):
        self.__list.remove( subsequence )
    
    
    def __iter__( self ) -> "Iterator[LegoSubsequence]":
        return iter( self.__list )
    
    
    def __getitem__( self, item ):
        return self.__list[ item ]
    
    
    @property
    def length( self ):
        return 1 + self.end - self.start


class LegoEdge( IVisualisable ):
    """
    Edge from one subsequence (or set of subsequences) to another
    
    These undirected edges have a "left" and "right" list:
        * All subsequences in a list (left or right) must reference the same sequence
        * The left and right sequences cannot reference the same sequence
            * This also implies any element in left cannot be in right and vice-versa
    """
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        """
        self.left = LegoSide( True )
        self.right = LegoSide( False )
        self.is_destroyed = False
        self.comments = [ ]  # type: List[str]
    
    
    def visualisable_info( self ):
        return UiInfo( name = self,
                       comment = None,
                       type_name = "Edge",
                       value = None,
                       colour = EColour.CYAN,
                       icon = resources.folder,
                       extra_iter = (self.left, self.right) )
    
    
    def __contains__( self, item ):
        return item in self.left or item in self.right
    
    
    @staticmethod
    def to_string( sequence, start, end, sequence_b, start_b, end_b ):
        return EDGE_FORMAT.format( sequence.accession, sequence.length, start, end, sequence_b.accession, sequence_b.length, start_b, end_b )
    
    
    def __str__( self ):
        if self.is_destroyed:
            return "DELETED_EDGE"
        
        return self.to_string( self.left.sequence, self.left.start, self.left.end, self.right.sequence, self.right.start, self.right.end )
    
    
    def __repr__( self ):
        """
        OVERRIDE 
        """
        if self.is_destroyed:
            return "DELETED_EDGE"
        
        return "({} [ {} : {} ])<-->({} [ {} : {} ])".format( self.left.sequence.accession, self.left.start, self.left.end, self.right.sequence.accession, self.right.start, self.right.end )
    
    
    TSide = "Union[LegoSequence,LegoSubsequence,LegoComponent,bool]"
    
    
    def position( self, item: TSide ) -> bool:
        """
        Returns `True` if `item` appears in the `destination` list, or `False` if it appears in the `source` list.
        
        Supports: Sequence, subsequence or component. Note that only the component of the SEQUENCE is considered, not the individual subsequences.
        
        Raises `KeyError` if it does not appear in either.
        """
        if isinstance( item, LegoSubsequence ):
            if item in self.left:
                return False
            
            if item in self.right:
                return True
            
            raise KeyError( "I cannot find the subsequence '{}' within this edge.".format( item ) )
        elif isinstance( item, LegoSequence ):
            if item is self.left.sequence:
                return False
            
            if item is self.right.sequence:
                return True
            
            raise KeyError( "I cannot find the sequence '{}' within this edge. This edge's sequences are '{}' and '{}'.".format( item, self.left.sequence, self.right.sequence ) )
        elif isinstance( item, LegoComponent ):
            if item is self.left.sequence.component:
                return False
            
            if item is self.right.sequence.component:
                return True
            
            raise KeyError( "I cannot find the component '{}' within this edge. This edge's sequences are '{}' and '{}' and their components are '{}' and '{}'.".format( item, self.left.sequence, self.right.sequence, self.left.component, self.right.component ) )
        elif isinstance( item, bool ):
            return item  # redundant support for bool for compatibility with `side`
        else:
            raise SwitchError( "item", item, instance = True )
    
    
    def side( self, item: TSide, opposite = False ) -> LegoSide:
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
    
    
    def opposite( self, item: TSide ) -> LegoSide:
        """
        Convenience function that calls `side` with `opposite = True`.
        """
        return self.side( item, opposite = True )


class LegoSubsequence( IVisualisable ):
    """
    Portion of a sequence
    """
    
    
    def __init__( self, sequence: "LegoSequence", start: int, end: int, components: "Optional[ Iterable[ LegoComponent ] ]" ):
        """
        CONSTRUCTOR
        :param sequence: Owning sequence 
        :param start: Leftmost position (inclusive) 
        :param end: Rightmost position (inclusive) 
        """
        LOG( "NEW SUBSEQUENCE {} {}".format( start, end ) )
        
        assert isinstance( sequence, LegoSequence )
        assert isinstance( start, int )
        assert isinstance( end, int )
        
        assert start >= 1
        assert end >= 1
        
        if start > end:
            raise ValueError( "Attempt to create a subsequence in '{0}' where start ({1}) > end ({2}).".format( sequence, start, end ) )
        
        self.sequence = sequence  # type: LegoSequence
        self.__start = start  # Start position
        self.__end = end  # End position
        self.edges = [ ]  # type: List[LegoEdge] # Edge list
        
        self.ui_position = None
        self.ui_colour = None
        
        self.is_destroyed = False
        
        self.comments = [ ]  # type:List[str]
        
        if components:
            self.components = set( components )  # type: Set[LegoComponent]
        else:
            self.components = set()  # type: Set[LegoComponent]
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = "{}:{}".format( self.__start, self.__end ),
                       comment = None,
                       type_name = "Subsequence",
                       value = "{} sites".format( self.length ),
                       colour = EColour.RED,
                       icon = resources.folder,
                       extra = { "sequence"  : self.sequence,
                                 "start"     : self.start,
                                 "end"       : self.end,
                                 "length"    : self.length,
                                 "index"     : self.index,
                                 "sites"     : self.site_array,
                                 "edges"     : self.edges,
                                 "components": self.components } )
    
    
    def to_string( self, sequence, start, end ):
        return SUBSEQUENCE_FORMAT.format( sequence.accession, sequence.length, start, end )
    
    
    def __str__( self ):
        return self.to_string( self.sequence, self.start, self.end )
    
    
    @property
    def start( self ) -> int:
        return self.__start
    
    
    @property
    def end( self ) -> int:
        return self.__end
    
    
    @start.setter
    def start( self, value: int ):
        assert isinstance( value, int )
        
        if not (0 < value <= self.__end):
            raise ValueError( "Attempt to set `start` to an out-of-bounds value {} in '{}'.".format( value, self ) )
        
        self.__start = value
    
    
    @end.setter
    def end( self, value: int ):
        assert isinstance( value, int )
        
        if not (self.__start <= value):
            raise ValueError( "Attempt to set `end` to an out-of-bounds value {} in '{}'.".format( value, self ) )
        
        self.__end = value
    
    
    @property
    def index( self ):
        """
        Finds the index of this subsequence in the owning sequence
        (Only works after deconvolution of the owning sequence)
        :return: 
        """
        return self.sequence.subsequences.index( self )
    
    
    @property
    def site_array( self ):
        """
        Obtains the slice of the sequence array pertinent to this subsequence
        """
        if self.sequence.site_array:
            return self.sequence.site_array[ self.start:self.end + 1 ]
        else:
            return None
    
    
    @property
    def length( self ):
        """
        Calculates the length of this subsequence
        """
        return self.end - self.start + 1
    
    
    def __repr__( self ):
        if self.is_destroyed:
            return "DELETED_SUBSEQUENCE"
        
        return "{} [ {} : {} ]".format( self.sequence.accession, self.start, self.end )


class LegoSequence( IVisualisable ):
    """
    Protein (or DNA) sequence
    """
    
    
    def __init__( self, model: "LegoModel", accession: str, id: int ):
        self.id = id
        self.accession = accession  # Database accession (ID)
        self.subsequences = [ ]  # type: List[LegoSubsequence]
        self.model = model
        self.site_array = None
        self.is_root = False
        self.comments = [ ]  # List[str]
        self.component = None  # type: Optional[LegoComponent]
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.accession,
                       comment = None,
                       type_name = "Sequence",
                       value = "{} sites in {} parts".format( self.subsequences[ -1 ].end, len( self.subsequences ) ),
                       colour = EColour.BLUE,
                       icon = resources.folder,
                       extra = { "id"              : self.id,
                                 "accession"       : self.accession,
                                 "is_composite"    : self.is_composite(),
                                 "is_root"         : self.is_root,
                                 "sites"           : self.site_array,
                                 "major_component" : self.component,
                                 "minor_components": self.minor_components(),
                                 "subsequences"    : self.subsequences } )
    
    
    def is_composite( self ) -> ETristate:
        l = len( self.minor_components() )
        
        if l == 1:
            return ETristate.NO
        elif l == 0:
            return ETristate.UNKNOWN
        else:
            return ETristate.YES
    
    
    def minor_components( self ):
        return set( y for x in self.subsequences for y in x.components )
    
    
    def all_edges( self ) -> Set[ LegoEdge ]:
        result = set()
        
        for ss in self.subsequences:
            for e in ss.edges:
                result.add( e )
        
        return result
    
    
    def to_string( self, sequence ):
        return SEQ_FORMAT.format( sequence.accession, sequence.length )
    
    
    def __str__( self ):
        return self.to_string( self )
    
    
    def connected_sequences( self ) -> "Set[LegoSequence]":
        result = set()
        
        for edge in self.all_edges():
            for subsequence in edge.opposite( self ):
                result.add( subsequence.sequence )
        
        return result
    
    
    @property
    def length( self ):
        if len( self.subsequences ) == 0:
            return 0
        
        return self.subsequences[ -1 ].end
    
    
    @property
    def index( self ):
        return self.model.sequences.index( self )
    
    
    def __repr__( self ):
        return "{}".format( self.accession )
    
    
    def _ensure_length( self, new_length: int ):
        assert isinstance( new_length, int )
        
        if new_length == 0:
            return
        
        if self.length < new_length:
            ss = LegoSubsequence( self, self.length + 1, new_length, None )
            self.subsequences.append( ss )
    
    
    def _find( self, start: int, end: int ):
        for x in self.subsequences:
            if x.start == start and x.end == end:
                return x
        
        raise KeyError( "No such subsequence as {0}-{1}".format( start, end ) )
    
    
    def sub_sites( self, start, end ):
        if self.site_array is None:
            return None
        
        assert start <= end, "{} {}".format( start, end )
        assert 0 < start <= len( self.site_array ), "{} {} {}".format( start, end, len( self.site_array ) )
        assert 0 < end <= len( self.site_array ), "{} {} {}".format( start, end, len( self.site_array ) )
        
        return self.site_array[ start:end ]


class LegoModel( IVisualisable ):
    """
    At it's apex, the model comprises:
    
        1. The set of sequences
            i. Their FASTA (or "site") data
        
        2. The the set of edges (or "similarity network")
        
        3. The subsequences as defined by the edge-sequence relations
            
        4. The set of connected components
              i. Their major sequences
              ii. Their minor subsequences
              iii. Their FASTA alignment
              iiii. Their trees
              v. Their consensus trees
                
        5. The NRF graph
    """
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        Creates a new model with no data
        Use the `import_*` functions to add data from a file.
        """
        self.__incremental_id = 0
        self.sequences = [ ]  # type: List[LegoSequence]
        self.components = [ ]  # type: List[LegoComponent]
        self.comments = [ "MODEL CREATED AT {}".format( string_helper.current_time() ) ]
        self.__seq_type = ESiteType.UNKNOWN
        self.file_name = None
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.name,
                       comment = self.comments,
                       type_name = "Model",
                       value = "{} sequences".format( len( self.sequences ) ),
                       colour = EColour.YELLOW,
                       icon = resources.folder,
                       extra = { "file_name"    : self.file_name,
                                 "documentation": self.__doc__,
                                 "site_type"    : self.site_type,
                                 "sequences"    : self.sequences,
                                 "components"   : self.components } )
    
    
    @property
    def name( self ):
        return FileHelper.get_filename_without_extension( self.file_name ) if self.file_name else "Unsaved model"
    
    
    
    
    @property
    def site_type( self ) -> ESiteType:
        """
        API
        Obtains the type of data in the model - protein, DNA or RNA.
        """
        if self.__seq_type != ESiteType.UNKNOWN:
            return self.__seq_type
        
        s = ESiteType.UNKNOWN
        
        for x in self.sequences:
            for y in x.site_array:
                if y not in "GAC":
                    if y == "T":
                        if s == ESiteType.UNKNOWN:
                            s = ESiteType.DNA
                    elif y == "U":
                        if s == ESiteType.UNKNOWN:
                            s = ESiteType.RNA
                    else:
                        s = ESiteType.PROTEIN
        
        self.__seq_type = s
        
        return s
    
    
    def _get_incremental_id( self ):
        """
        Obtains a unique identifier.
        """
        self.__incremental_id += 1
        return self.__incremental_id
    
    
    @property
    def all_edges( self ) -> Set[ LegoEdge ]:
        """
        API
        Returns the set of all edges in the model.
        """
        r = set()
        
        for x in self.sequences:
            for xx in x.subsequences:
                for xxx in xx.edges:
                    r.add( xxx )
        
        return r
    
    
    def all_subsequences( self ) -> Iterator[ LegoSubsequence ]:
        for sequence in self.sequences:
            yield from sequence.subsequences
    
    
    def _has_data( self ):
        return bool( self.sequences )
    
    
    def count_subsequences( self ):
        return sum( len( sequence.subsequences ) for sequence in self.sequences )
    
    
    def find_sequence( self, name: str ) -> "LegoSequence":
        for x in self.sequences:
            if x.accession == name:
                return x
        
        raise KeyError( name )
    
    
    def find_sequence_by_id( self, id: int ) -> "LegoSequence":
        for x in self.sequences:
            if x.id == id:
                return x
        
        raise KeyError( id )


_GREEK = "αβγδϵζηθικλμνξοπρστυϕχψω"


class LegoComponentElement:
    def __init__( self, is_major, sequence, start, end, subsequences ):
        self.is_major = is_major
        self.sequence = sequence
        self.start = start
        self.end = end
        self.subsequences = subsequences
    
    
    def __str__( self ):
        return ("⎅" if self.is_major else "⎕") + LegoSide.to_string( self.sequence, self.start, self.end, len( self.subsequences ) )
    
    
    def sites( self ):
        return self.sequence.sub_sites( self.start, self.end )


class LegoComponent( IVisualisable ):
    """
    A component represents a `major` and `minor` set.
    
    The `major` comprises the set of sequences that are deemed to be wholly similar.
    
    The `minor` comprises the set of sequences and subsequences that are deemed to represent a smaller subsequence of `major`.
    
    The exact definition of "wholly similar" and "a smaller subsequence" is described in more detail alongside the algorithms
    present in the `__detect_major` and `__detect_minor` subroutines of the source code (`LegoModels.py`).
    """
    
    
    def __init__( self, model: LegoModel, index: int ):
        self.model = model  # Source model
        self.index = index  # Index of component
        self.tree = None  # Tree generated for component, in Newick format
        self.alignment = None  # Alignment generated for component, in FASTA format
        self.consensus = None  # Consensus tree, in Newick format
        self.consensus_intersection = None  # type: List[LegoSequence]
    
    
    def visualisable_info( self ):
        return UiInfo( name = self,
                       comment = self.__doc__,
                       type_name = "Component",
                       value = "{} sequences".format( array_helper.count( self.major_sequences() ) ),
                       colour = EColour.RED,
                       icon = resources.folder,
                       extra = {"index":self.index, 
                                "major":self.major_sequences(),
                                "minor_s":self.minor_sequences(),
                                "minor_ss":self.minor_subsequences()})
    
    
    def __str__( self ):
        return repr( self )
    
    
    def __repr__( self ):
        return _GREEK[ self.index % len( _GREEK ) ].lower()
    
    
    def elements( self ) -> List[ LegoComponentElement ]:
        r = [ ]
        minor = set( self.minor_sequences() )
        
        for sequence in self.model.sequences:
            if sequence.component is self:
                r.append( LegoComponentElement( True, sequence, 1, sequence.length, sequence.subsequences ) )
            elif sequence in minor:
                rss = [ x for x in sequence.subsequences if self in x.components ]
                r.append( LegoComponentElement( False, sequence, rss[ 0 ].start, rss[ -1 ].end, rss ) )
        
        return r
    
    
    def minor_subsequences( self ) -> List[ LegoSubsequence ]:
        """
        Finds subsequences related by this component.
        """
        return [ subsequence for subsequence in self.model.all_subsequences() if self in subsequence.components ]
    
    
    def incoming_components( self ) -> "List[LegoComponent]":
        """
        Returns components which implicitly form part of this component.
        """
        return [ component for component in self.model.components if any( x in component.minor_sequences() for x in self.major_sequences() ) ]
    
    
    def outgoing_components( self ) -> "List[LegoComponent]":
        """
        Returns components which implicitly form part of this component.
        """
        return [ component for component in self.model.components if any( x in component.major_sequences() for x in self.minor_sequences() ) ]
    
    
    def major_sequences( self ) -> List[ LegoSequence ]:
        """
        Returns the major sequences.
        Sequences in the major set.
        See `__detect_major` for the definition. 
        """
        return [ sequence for sequence in self.model.sequences if sequence.component is self ]
    
    
    def minor_sequences( self ) -> List[ LegoSequence ]:
        """
        Returns the minor sequences.
        Sequences with at least one subsequence in the minor set.
        See `__detect_minor` for the definition.
        """
        return list( set( subsequence.sequence for subsequence in self.minor_subsequences() ) )
