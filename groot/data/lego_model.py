"""
Holds the Lego model, and its dependencies.

See class `LegoModel`.
"""

import re
from typing import Dict, Iterable, Iterator, List, Optional, Tuple, cast

from groot.frontends.gui.gui_view_support import EMode
from intermake import EColour, IVisualisable, UiInfo, resources
from mgraph import MGraph
from mhelper import MEnum, NotFoundError, SwitchError, TTristate, array_helper, bio_helper, file_helper as FileHelper, string_helper, utf_helper


TEXT_SUBSEQUENCE_FORMAT = "{}[{}:{}]"
TEXT_EDGE_FORMAT = "{}[{}:{}]--{}[{}:{}]"
TEXT_SEQ_FORMAT = "{}"

_LegoModel_ = "LegoModel"
__author__ = "Martin Rusilowicz"


class ILeaf:
    pass


class ILegoSelectable:
    pass


# noinspection PyAbstractClass
class ILegoVisualisable( IVisualisable ):
    pass


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


class LegoEdge( ILegoVisualisable, ILegoSelectable ):
    """
    Edge from one subsequence (or set of subsequences) to another
    
    These undirected edges have a "left" and "right" list:
        * All subsequences in a list (left or right) must reference the same sequence
        * The left and right sequences cannot reference the same sequence
            * This also implies any element in left cannot be in right and vice-versa
    """
    
    
    def __init__( self, source: "LegoSubsequence", destination: "LegoSubsequence" ) -> None:
        """
        CONSTRUCTOR
        """
        self.left: LegoSubsequence = source
        self.right: LegoSubsequence = destination
        self.is_destroyed = False
        self.comments = []  # type: List[str]
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = str( self ),
                       comment = "",
                       type_name = "Edge",
                       value = "",
                       colour = EColour.CYAN,
                       icon = resources.folder,
                       extra_named = (self.left, self.right) )
    
    
    def __contains__( self, item ) -> bool:
        return item in self.left or item in self.right
    
    
    @staticmethod
    def to_string( sequence: "LegoSequence", start: int, end: int, sequence_b: "LegoSequence", start_b: int, end_b: int ) -> str:
        return TEXT_EDGE_FORMAT.format( sequence.accession, start, end, sequence_b.accession, start_b, end_b )
    
    
    def __str__( self ) -> str:
        if self.is_destroyed:
            return "DELETED_EDGE"
        
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


class LegoSubsequence( ILegoVisualisable ):
    """
    Portion of a sequence
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
        self.edges: List[LegoEdge] = []  # Edge list
        
        self.is_destroyed: bool = False
        
        self.comments: List[str] = []
    
    
    @classmethod
    def merge_list( cls, source: List["LegoSubsequence"] ):
        """
        Merges together adjacent subsequences in the same sequence.
        :param source:  Input list of subsequences, the list is directly modified. 
        :return:        The source list, after modification. 
        """
        processing = True
        
        while processing:
            processing = False
            
            for a in source:
                for b in source:
                    if a is not b and a.sequence is b.sequence and a.end + 1 == b.start:
                        source.remove( a )
                        source.remove( b )
                        source.append( cls( a.sequence, a.start, b.end ) )
                        processing = True
                        break
                
                if processing:
                    break
        
        return source
    
    
    @classmethod
    def list_union( cls, options: List["LegoSubsequence"] ):
        a = options[0]
        
        for i in range( 1, len( options ) ):
            a = a.union( options[i] )
        
        return a
    
    
    def has_overlap( self, two: "LegoSubsequence" ):
        if self.sequence is not two.sequence:
            return False
        
        return self.start <= two.end and two.start <= self.end
    
    
    def has_encompass( self, two: "LegoSubsequence" ):
        if self.sequence is not two.sequence:
            return False
        
        return self.start <= two.start and self.end >= two.end
    
    
    def union( self, two: "LegoSubsequence" ):
        assert self.sequence is two.sequence
        return LegoSubsequence( self.sequence, min( self.start, two.start ), max( self.end, two.end ) )  # todo: doesn't account for non-overlapping ranges
    
    
    def intersection( self, two: "LegoSubsequence" ):
        assert self.sequence is two.sequence
        return LegoSubsequence( self.sequence, max( self.start, two.start ), min( self.end, two.end ) )  # todo: doesn't account for non-overlapping ranges
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = str( self ),
                       comment = "",
                       type_name = "Subsequence",
                       value = "{} sites".format( self.length ),
                       colour = EColour.RED,
                       icon = resources.folder,
                       extra = { "sequence": self.sequence,
                                 "start"   : self.start,
                                 "end"     : self.end,
                                 "length"  : self.length,
                                 "sites"   : self.site_array,
                                 "edges"   : self.edges } )
    
    
    @staticmethod
    def to_string( sequence, start, end ) -> str:
        return TEXT_SUBSEQUENCE_FORMAT.format( sequence.accession, start, end )
    
    
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


class LegoUserDomain( LegoSubsequence, ILegoSelectable ):
    """
    A user-domain is just domain (LegoSubsequence) we know exists in the UI.
    """
    
    
    def __init__( self, sequence: "LegoSequence", start: int, end: int ):
        super().__init__( sequence, start, end )


class LegoSequence( ILegoVisualisable, ILeaf, ILegoSelectable ):
    """
    Protein (or DNA) sequence
    """
    
    
    def __init__( self, model: "LegoModel", accession: str, id: int ) -> None:
        self.id: int = id
        self.accession: str = accession  # Database accession (ID)
        self.model: "LegoModel" = model
        self.site_array: str = None
        self.is_root: bool = False
        self.comments: List[str] = []
        self.length = 1
    
    
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
                       comment = "",
                       type_name = "Sequence",
                       value = "{} sites".format( self.length ),
                       colour = EColour.BLUE,
                       icon = resources.folder,
                       extra = { "id"       : self.id,
                                 "length"   : self.length,
                                 "accession": self.accession,
                                 "is_root"  : self.is_root,
                                 "num_sites": len( self.site_array ),
                                 "sites"    : self.site_array } )
    
    
    def __str__( self ) -> str:
        """
        OVERRIDE 
        """
        return self.accession or "(no-accession)"
    
    
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
        assert isinstance( new_length, int )
        
        if new_length == 0:
            return
        
        if self.length < new_length:
            self.length = new_length
    
    
    def sub_sites( self, start: int, end: int ) -> Optional[str]:
        if self.site_array is None:
            return None
        
        assert start <= end, "{} {}".format( start, end )
        assert 0 < start <= len( self.site_array ), "{} {} {}".format( start, end, len( self.site_array ) )
        assert 0 < end <= len( self.site_array ), "{} {} {}".format( start, end, len( self.site_array ) )
        
        return self.site_array[start:end]


_GREEK = "αβγδϵζηθικλμνξοπρστυϕχψω"


class LegoComponent( ILegoVisualisable, ILegoSelectable ):
    """
    Stores information about a component of the (:class:`LegoModel`).
    
    :attr: model:                      Back-reference to model
    :attr: index:                      Index of component within model
    :attr: tree:                       Tree generated for this component (can be None)
    :attr: alignment:                  Alignment generated for this component, in FASTA format, with sequences referenced by IID (not accession). Can be None.
    :attr: major_sequences:            Major sequences of this component. i.e. sequences only containing domains in :attr:`minor_subsequences`
    :attr: minor_subsequences:         Minor subsequences of this component. i.e. all domains in this component.
    """
    
    
    def __init__( self, model: _LegoModel_, index: int, major_sequences: List[LegoSequence] ):
        from mgraph import MGraph
        self.model: LegoModel = model
        self.index: int = index
        self.tree: MGraph = None
        self.alignment: str = None
        self.major_sequences: List[LegoSequence] = major_sequences
        self.minor_subsequences: List[LegoSubsequence] = None
    
    
    def get_alignment_by_accession( self ) -> str:
        """
        Gets the `alignment` property, but translates sequence IDs into accessions
        """
        if not self.alignment:
            return self.alignment
        
        r = []
        
        for name, value in bio_helper.parse_fasta( text = self.alignment ):
            assert name.startswith( "S" ), name
            r.append( ">" + self.model.find_sequence_by_id( int( name[1:] ) ).accession )
            r.append( value )
        
        return "\n".join( r )
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = str( self ),
                       comment = str( self.__doc__ ),
                       type_name = "Component",
                       value = "{} sequences".format( array_helper.count( self.major_sequences ) ),
                       colour = EColour.RED,
                       icon = resources.folder,
                       extra = { "index"    : self.index,
                                 "major"    : self.major_sequences,
                                 "minor_s"  : self.minor_sequences,
                                 "minor_ss" : self.minor_subsequences,
                                 "alignment": self.alignment,
                                 "tree"     : self.tree,
                                 "incoming" : self.incoming_components(),
                                 "outgoing" : self.outgoing_components() } )
    
    
    def __str__( self ) -> str:
        return utf_helper.circled( re.sub( "[0-9]", " ", self.major_sequences[0].accession ) )
        # return _GREEK[self.index % len( _GREEK )].lower() ⨍
    
    
    def minor_subsequences( self ) -> List[LegoSubsequence]:
        """
        Finds subsequences related by this component.
        """
        return self.minor_subsequences
    
    
    def incoming_components( self ) -> "List[LegoComponent]":
        """
        Returns components which implicitly form part of this component.
        """
        return [component for component in self.model.components if any( x in component.minor_sequences for x in self.major_sequences ) and component is not self]
    
    
    def outgoing_components( self ) -> "List[LegoComponent]":
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
        return list( set( subsequence.sequence for subsequence in self.minor_subsequences ) )


class LegoEdgeCollection:
    def __init__( self, model: "LegoModel" ):
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


class LegoComponentCollection:
    def __init__( self, model: "LegoModel" ):
        self.__model = model
        self.__components: List[LegoComponent] = []
    
    
    def __bool__( self ):
        return bool( self.__components )
    
    
    def add( self, component: LegoComponent ):
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
        
        raise NotFoundError( "Sequence does not have a component." )
    
    
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
    def __init__( self, model: "LegoModel" ):
        self.__model = model
        self.__sequences: List[LegoSequence] = []
    
    
    def __bool__( self ):
        return bool( self.__sequences )
    
    
    def __len__( self ):
        return len( self.__sequences )
    
    
    def __iter__( self ) -> Iterator[LegoSequence]:
        return iter( self.__sequences )
    
    
    def __str__( self ):
        return "{} sequences".format( len( self ) )
    
    
    def add( self, sequence: LegoSequence ):
        array_helper.ordered_insert( self.__sequences, sequence, lambda x: x.accession )
    
    
    def index( self, sequence: LegoSequence ):
        return self.__sequences.index( sequence )


class LegoUserDomainCollection:
    def __init__( self, model: "LegoModel" ):
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


class LegoViewOptions:
    """
    Options on the lego view
    
    :attr y_snap:                      Snap movements to the Y axis (yes | no | when no alt)
    :attr x_snap:                      Snap movements to the X axis (yes | no | when no alt)
    :attr move_enabled:                Allow movements (yes | no | when double click)
    :attr view_piano_roll:             View piano roll (yes | no | when selected)
    :attr view_names:                  View sequence names (yes | no | when selected)
    :attr view_positions:              View domain positions (yes | no | when selected)
    :attr view_components:             View domain components (yes | no | when selected)
    :attr mode:                        Edit mode
    :attr domain_function:             Domain generator
    :attr domain_function_parameter:   Parameter passed to domain generator (domain_function dependent)
    :attr domain_positions:            Positions of the domains on the screen - maps (id, site) --> (x, y)
    """
    
    
    def __init__( self ):
        self.y_snap: TTristate = None
        self.x_snap: TTristate = None
        self.move_enabled: TTristate = None
        self.view_piano_roll: TTristate = None
        self.view_names: TTristate = True
        self.view_positions: TTristate = None
        self.view_components: TTristate = None
        self.mode = EMode.SEQUENCE
        self.domain_positions: Dict[Tuple[int, int], Tuple[int, int]] = { }


class LegoNrfg( ILegoSelectable ):
    def __init__( self, graph: MGraph ):
        self.graph = graph
    
    
    def __str__( self ):
        return "NRFG"


class LegoModel( ILegoVisualisable ):
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
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        Creates a new model with no data
        Use the `import_*` functions to add data from a file.
        """
        self.__incremental_id = 0
        self.sequences = LegoSequenceCollection( self )
        self.components = LegoComponentCollection( self )
        self.edges = LegoEdgeCollection( self )
        self.comments = ["MODEL CREATED AT {}".format( string_helper.current_time() )]
        self.__seq_type = ESiteType.UNKNOWN
        self.file_name = None
        from groot.algorithms.classes import FusionEvent
        self.fusion_events = cast( List[FusionEvent], [] )
        self.nrfg: LegoNrfg = None
        self.ui_options = LegoViewOptions()
        self.user_domains = LegoUserDomainCollection( self )
    
    
    def visualisable_info( self ) -> UiInfo:
        return UiInfo( name = self.name,
                       comment = "\n".join( self.comments ),
                       type_name = "Model",
                       value = "{} sequences".format( len( self.sequences ) ),
                       colour = EColour.YELLOW,
                       icon = resources.folder,
                       extra = { "file_name"    : self.file_name,
                                 "documentation": self.__doc__,
                                 "site_type"    : self.site_type,
                                 "sequences"    : self.sequences,
                                 "edges"        : self.edges,
                                 "components"   : self.components,
                                 "nrfg"         : self.nrfg } )
    
    
    def __str__( self ):
        return self.name
    
    
    @property
    def name( self ) -> str:
        from groot.data import global_view
        if self is not global_view.current_model():
            return "Not the current model"
        
        if self.file_name:
            return FileHelper.get_filename_without_extension( self.file_name )
        elif self.sequences:
            return "Unsaved model"
        else:
            return "Empty model"
    
    
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
            if x.site_array:
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
    
    
    def _get_incremental_id( self ) -> int:
        """
        Obtains a unique identifier.
        """
        self.__incremental_id += 1
        return self.__incremental_id
    
    
    def _has_data( self ) -> bool:
        return bool( self.sequences )
    
    
    def find_sequence_by_accession( self, name: str ) -> "LegoSequence":
        for x in self.sequences:
            if x.accession == name:
                return x
        
        raise LookupError( "There is no sequence with the accession «{}».".format( name ) )
    
    
    def find_sequence_by_id( self, id: int ) -> "LegoSequence":
        for x in self.sequences:
            if x.id == id:
                return x
        
        raise LookupError( "There is no sequence with the internal ID «{}».".format( id ) )
