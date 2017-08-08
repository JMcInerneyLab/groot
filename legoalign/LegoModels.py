"""
Holds the Lego model, and its dependencies.

See class `LegoModel`.
"""
from typing import Iterable, Iterator, List, Optional, Set

from editorium import MEnum
from mcommand import EColour, IVisualisable, UiInfo, resources
from mcommand.visualisables.visualisable import NamedValue
from mhelper import ArrayHelper, FileHelper, StringHelper
from mhelper.ExceptionHelper import SwitchError
from mhelper.LogHelper import Logger


LOG = Logger( False )


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


class _NamedList( IVisualisable ):
    """
    The list version of `NamedValue`.
    """
    
    
    def __init__( self, name: str, list: Iterable, element_name: Optional[ str ] = None ):
        self.name = name
        self.ext_name = element_name or name
        self.list = list
        self.length = ArrayHelper.count( list )
    
    
    def ui_info( self ) -> UiInfo:
        return UiInfo( self.name, None, "List", "{} {}".format( self.length, self.ext_name ), EColour.MAGENTA, resources.folder )
    
    
    def ui_items( self ):
        return self.list


class LegoSide( IVisualisable ):
    def __init__( self, is_source: bool ):
        self.__list = [ ]  # type:List[LegoSubsequence]
        self.is_source = is_source
    
    
    def ui_info( self ):
        return UiInfo( "source" if self.is_source else "destination",
                       None,
                       "Side",
                       "{}--{}".format( self.start, self.end ),
                       EColour.GREEN,
                       resources.folder )
    
    
    def ui_items( self ):
        yield NamedValue( "start", self.start, is_property = True )
        yield NamedValue( "end", self.end, is_property = True )
        yield NamedValue( "length", self.length, is_property = True )
        yield NamedValue( "sites", self.sites, is_property = True )
        yield NamedValue( "component", self.component, is_property = True )
        yield NamedValue( "sequence", self.sequence, is_property = True )
        
        yield _NamedList( "subsequences", self.__list )
    
    
    def add( self, subsequence: "LegoSubsequence" ):
        ArrayHelper.ordered_insert( self.__list, subsequence, lambda x: x.start )
    
    
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
    
    
    def __str__( self ):
        return "{}[{}:{}]".format( self.sequence.accession, self.start, self.end )
    
    
    def __contains__( self, item ):
        if isinstance( item, LegoSubsequence ):
            return item in self.__list
        
        raise TypeError( "Cannot tell if LegoSide contains the item because the item is of type '{}', not '{}'.".format( type( item ).__name__, LegoSubsequence.__name__ ) )
    
    
    def remove( self, subsequence: "LegoSubsequence" ):
        self.__list.remove( subsequence )
    
    
    def __iter__( self ):
        return iter( self.__list )
    
    
    def __getitem__( self, item ):
        return self.__list[ item ]
    
    
    @property
    def length( self ):
        return 1 + self.end - self.start


class LegoEdge( IVisualisable ):
    """
    Edge from one subsequence (or set of subsequences) to another
    
    Edges have a Source and Destination list:
        * All subsequences in a list (Source or Destination) must reference the same sequence
        * The Source and Destination sequences cannot reference the same sequence
            * This also implies any element in Source cannot be in Destination and vice-versa
    """
    
    
    def __init__( self ):
        """
        CONSTRUCTOR
        """
        self.source = LegoSide( True )
        self.destination = LegoSide( False )
        self.is_destroyed = False
        self.comments = [ ]  # type: List[str]
    
    
    def ui_info( self ):
        return UiInfo( self,
                       None,
                       "Edge",
                       None,
                       EColour.CYAN,
                       resources.folder )
    
    
    def ui_items( self ):
        yield _NamedList( "comments", self.comments, "elements" )
        yield self.source
        yield self.destination
    
    
    def __contains__( self, item ):
        return item in self.source or item in self.destination
    
    
    def __str__( self ):
        if self.is_destroyed:
            return "DELETED_EDGE"
        
        return "{}+{}".format( self.source, self.destination )
    
    
    def __repr__( self ):
        """
        OVERRIDE 
        """
        if self.is_destroyed:
            return "DELETED_EDGE"
        
        return "({} [ {} : {} ])-->({} [ {} : {} ])".format( self.source.sequence.accession, self.source.start, self.source.end, self.destination.sequence.accession, self.destination.start, self.destination.end )
    
    
    TSide = "Union[LegoSequence,LegoSubsequence,LegoComponent,bool]"
    
    
    def position( self, item: TSide ) -> bool:
        """
        Returns `True` if `item` appears in the `destination` list, or `False` if it appears in the `source` list.
        
        Supports: Sequence, subsequence or component. Note that only the component of the SEQUENCE is considered, not the individual subsequences.
        
        Raises `KeyError` if it does not appear in either.
        """
        if isinstance( item, LegoSubsequence ):
            if item in self.source:
                return False
            
            if item in self.destination:
                return True
            
            raise KeyError( "I cannot find the subsequence '{}' within this edge.".format( item ) )
        elif isinstance( item, LegoSequence ):
            if item is self.source.sequence:
                return False
            
            if item is self.destination.sequence:
                return True
            
            raise KeyError( "I cannot find the sequence '{}' within this edge. This edge's sequences are '{}' and '{}'.".format( item, self.source.sequence, self.destination.sequence ) )
        elif isinstance( item, LegoComponent ):
            if item is self.source.sequence.component:
                return False
            
            if item is self.destination.sequence.component:
                return True
            
            raise KeyError( "I cannot find the component '{}' within this edge. This edge's sequences are '{}' and '{}' and their components are '{}' and '{}'.".format( item, self.source.sequence, self.destination.sequence, self.source.component, self.destination.component ) )
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
        
        return self.destination if position else self.source
    
    
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
        
        assert isinstance(sequence, LegoSequence)
        assert isinstance(start, int)
        assert isinstance(end, int)
        
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
    
    
    def ui_info( self ) -> UiInfo:
        return UiInfo( "{}:{}".format( self.__start, self.__end ),
                       None,
                       "Subsequence",
                       "{} sites".format( self.length ),
                       EColour.RED,
                       resources.folder )
    
    
    def ui_items( self ):
        yield NamedValue( "sequence", self.sequence, is_property = True )
        yield NamedValue( "start", self.start, is_property = True )
        yield NamedValue( "end", self.end, is_property = True )
        yield NamedValue( "length", self.length, is_property = True )
        yield NamedValue( "index", self.index, is_property = True )
        yield NamedValue( "sites", self.site_array, is_property = True )
        
        yield _NamedList( "comments", self.comments, "elements" )
        yield _NamedList( "edges", self.edges )
        yield _NamedList( "minor_components", self.components )
    
    
    def __str__( self ):
        return "{}[{}:{}]".format( self.sequence.accession, self.__start, self.__end )
    
    
    @property
    def start( self ) -> int:
        return self.__start
    
    
    @property
    def end( self ) -> int:
        return self.__end
    
    
    @start.setter
    def start( self, value: int ):
        assert isinstance(value, int)
        
        if not (0 < value <= self.__end):
            raise ValueError( "Attempt to set `start` to an out-of-bounds value {} in '{}'.".format( value, self ) )
        
        self.__start = value
    
    
    @end.setter
    def end( self, value: int ):
        assert isinstance(value, int)
        
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
    
    
    def ui_info( self ) -> UiInfo:
        return UiInfo( self.accession,
                       None,
                       "Sequence",
                       "{} sites in {} parts".format( self.subsequences[ -1 ].end, len( self.subsequences ) ),
                       EColour.BLUE,
                       resources.folder )
    
    
    def ui_items( self ):
        yield NamedValue( "id", self.id, is_property = True )
        yield NamedValue( "accession", self.accession, is_property = True )
        yield NamedValue( "is_composite", self.is_composite(), is_property = True )
        yield NamedValue( "is_root", self.is_root, is_property = True )
        yield NamedValue( "sites", self.site_array, is_property = True )
        yield NamedValue( "comments", self.comments, is_property = True )
        
        yield NamedValue( "major_component", self.component )
        yield _NamedList( "minor_components", self.minor_components(), "components" )
        yield _NamedList( "subsequences", self.subsequences, "subsequences" )
    
    
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
    
    
    def __str__( self ):
        return "{}[{}]".format( self.accession, self.length )
    
    
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
    
    
    def _ensure_length( self, new_length : int ):
        assert isinstance(new_length, int)
        
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
    The model comprises:
        1. The similarity network:
            i.  The set of sequences
            ii. The set of edges
            
        2. The component analysis
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
        self.comments = [ "MODEL CREATED AT {}".format( StringHelper.current_time() ) ]
        self.__seq_type = ESiteType.UNKNOWN
        self.file_name = None
    
    
    def ui_info( self ) -> UiInfo:
        return UiInfo( self.name,
                       self.comments,
                       "Model",
                       "{} sequences".format( len( self.sequences ) ),
                       EColour.YELLOW,
                       resources.folder )
    
    
    @property
    def name( self ):
        return FileHelper.get_filename_without_extension( self.file_name ) if self.file_name else "Unsaved model"
    
    
    def ui_items( self ):
        yield NamedValue( "name", self.name )
        yield NamedValue( "file_name", self.file_name )
        yield NamedValue( "comments", self.comments )
        yield NamedValue( "documentation", self.__doc__ )
        yield NamedValue( "site_type", self.site_type )
        
        yield _NamedList( "sequences", self.sequences )
        yield _NamedList( "components", self.components )
    
    
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


_GREEK = "αβγδϵζηθικλμνξοπρστυϕχψω"


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
        self.tree = None  # Tree generated for component
    
    
    def ui_info( self ):
        return UiInfo( self,
                       self.__doc__,
                       "Component",
                       "{} sequences".format( ArrayHelper.count( self.major_sequences() ) ),
                       EColour.RED,
                       resources.folder )
    
    
    def ui_items( self ):
        yield NamedValue( "name", str( self ), is_property = True )
        yield NamedValue( "index", self.index, is_property = True )
        
        yield _NamedList( "major", self.major_sequences(), element_name = "major sequences" )
        yield _NamedList( "minor_s", self.minor_sequences(), element_name = "minor sequences" )
        yield _NamedList( "minor_ss", self.minor_subsequences(), element_name = "minor subsequences" )
    
    
    def __str__( self ):
        return repr( self )
    
    
    def __repr__( self ):
        return _GREEK[ self.index % len( _GREEK ) ].lower()
    
    
    def minor_subsequences( self ) -> List[ LegoSubsequence ]:
        """
        Finds subsequences related by this component.
        """
        return [ subsequence for subsequence in self.model.all_subsequences() if self in subsequence.components ]
    
    
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
