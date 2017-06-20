"""
Holds the Lego model, and its dependencies.

See class `LegoModel`.
"""

from enum import Enum
from typing import Iterable, List, Set, Tuple

from MHelper import ArrayHelper, StringHelper
from MHelper.ExceptionHelper import ImplementationError
from MHelper.LogHelper import Logger


LOG = Logger(False)

def _quantise_int( level, position ):
        half_level = (level // 2)
        position = position + half_level
        position = max( position - position % level, 1 )
        return position

VERIFY = True

class ELetterType( Enum ):
    UNKNOWN=0
    PROTEIN=1
    DNA=2
    RNA=3


class LegoEdge:
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
        self.source = [ ]  # type:List[LegoSubsequence]
        self.destination = [ ]  # type:List[LegoSubsequence]
        self.source_info = set()
        self.is_destroyed = False
        self.extra_data = [] #type: List[str]
    
    
    def to_fasta( self, header ):
        fasta = [ ]
        fasta.append( ";" )
        fasta.append( "; EDGE: {}".format( self ) )
        fasta.append( ";" )
        
        if header:
            fasta.append( ">{} [ {} : {} ]".format( self.source_sequence, self.source_start, self.source_end ) )
            
        fasta.append( self.source_array or ";MISSING" )
        fasta.append( "" )
        
        if header:
            fasta.append( ">{} [ {} : {} ]".format( self.destination_sequence, self.destination_start, self.destination_end ) )
            
        fasta.append( self.destination_array or ";MISSING" )
        fasta.append( "" )
        return "\n".join( fasta )
    
    
    def __contains__( self, item ):
        return item in self.source or item in self.destination
    
    
    def _verify_deconvoluted( self ):
        if not VERIFY:
            return
        
        if len(self.source)==0:
            raise ImplementationError( "An edge has no source." )
        
        if len(self.destination)==0:
            raise ImplementationError( "An edge has no destination." )
            
            
        self._verify()
    
    
    def _verify( self ):
        """
        Internally used to assert the integrity of the edge
        """
        if not VERIFY:
            return
        
        if self.is_destroyed:
            raise ImplementationError( "Edge '{}' has been destroyed.".format( self ) )
        
        if not self.source or not self.destination:
            return
        
        for x in self.source:
            if x.sequence is not self.source[ 0 ].sequence:
                raise ImplementationError( "The source subsequences in the edge '{}' do not all reference the same sequence, e.g. '{}' and '{}'.".format( x, x, self.source[ 0 ] ) )
        
        for x in self.destination:
            if x.sequence is not self.destination[ 0 ].sequence:
                raise ImplementationError( "The destination subsequences in the edge '{}' do not all reference the same sequence, e.g. '{}' and '{}'.".format( x, x, self.destination[ 0 ] ) )
        
        if self.source[ 0 ].sequence is self.destination[ 0 ].sequence:
            # Don't allow this, it's unnecessary and just causes problems further down the line
            raise ImplementationError( "The source and destination sequences of the edge '{}' are the same ('{}').".format( self, self.source[ 0 ].sequence ) )
        
        for x in self.source + self.destination:
            if x.is_destroyed:
                raise ImplementationError( "Edge '{}' contains a destroyed subsequence '{}'".format( self, x ) )
    
    
    @property
    def source_sequence( self ):
        """
        Sequence of the source subsequences
        """
        return self.source[ 0 ].sequence
    
    
    @property
    def destination_sequence( self ):
        """
        Sequence of the destination subsequences
        """
        return self.destination[ 0 ].sequence
    
    
    @property
    def source_array( self ):
        return self.source_sequence.sub_array( self.source_start, self.source_end )
    
    
    @property
    def destination_array( self ):
        return self.source_sequence.sub_array( self.source_start, self.source_end )
    
    
    
    @property
    def source_start( self ):
        """
        Index of the leftmost source subsequence
        """
        return min( x.start for x in self.source )
    
    
    @property
    def source_end( self ):
        """
        Index of the rightmost source subsequence
        """
        return max( x.end for x in self.source )
    
    
    @property
    def destination_start( self ):
        """
        Index of the leftmost destination subsequence
        """
        return min( x.start for x in self.destination )
    
    
    @property
    def destination_end( self ):
        """
        Index of the rightmost destination subsequence
        """
        return max( x.end for x in self.destination )
    
    
    def __repr__( self ):
        """
        OVERRIDE 
        """
        if self.is_destroyed:
            return "DELETED_EDGE"
        
        return "({} [ {} : {} ])-->({} [ {} : {} ])".format( self.source_sequence, self.source_start, self.source_end, self.destination_sequence, self.destination_start, self.destination_end )
    
    
    def position( self, subsequence: "LegoSubsequence" ) ->bool:
        """
        Returns `True` if `subsequence` appears in the `destination` list, or `False` if it appears in the `source` list. Raises `KeyError` if it does not appear in either.
        """
        if subsequence in self.source:
            return False
        
        if subsequence in self.destination:
            return True
        
        raise KeyError( "Not found: '{0}'".format( subsequence ) )
    

    def side( self, position : bool ):
        return self.destination if position else self.source
    
    
    def opposite( self, subsequence ):
        """
        Returns the list (source/destination) opposite the specified subsequence
        """
        return self.side(not self.position( subsequence ))
    
    
    def _deconvolute( self ):
        """
        Deconvolutes the edge:
            * Sorts the source and destination lists by position
            * Verifies the integrity
        """
        # TODO: Edges should never be "convoluted" in the first place
        self.source = sorted( self.source, key = lambda x: x.start )
        self.destination = sorted( self.destination, key = lambda x: x.start )
        self._verify()
    
    
    def unlink_all( self ):
        """
        Removes all references to this edge in the references subsequences
        """
        for x in self.source + self.destination:
            x.edges.remove( self )
        
        self.is_destroyed = True
    
    
    def unlink( self, subsequence: "LegoSubsequence" ):
        """
        Undoes the link created with `link`.
        """
        the_list = self.destination if self.position( subsequence ) else self.source
        
        subsequence.edges.remove( self )
        the_list.remove( subsequence )
        
        if len(the_list)==0:
            self.unlink_all()
    
    
    def link( self, position: bool, subsequences: "List[LegoSubsequence]" ):
        """
        Forms the link between this edge and the specified subsequence.
        """
        with LOG("LINK EDGE #{}".format(id(self))):
            pfx = "-D->" if position else "-S->"
            for x in subsequences:
                 LOG("{} {}".format(pfx, x))
            
            the_list = self.destination if position else self.source
            
            for subsequence in subsequences:
                assert not subsequence.is_destroyed
                
                if subsequence not in the_list:
                    the_list.append( subsequence )
                    subsequence.edges.append( self )
                    
            self._verify()


class LegoSubsequence:
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
        LOG("NEW SUBSEQUENCE {} {}".format(start, end))
            
        assert start >= 1
        assert end >= 1
        
        if start > end:
            raise ValueError( "Attempt to create a subsequence in '{0}' where start ({1}) > end ({2}).".format( sequence, start, end ) )
        
        self.sequence = sequence  # type: LegoSequence
        self.__start = start      # Start position
        self.__end = end          # End position
        self.edges = [ ]          # type: List[LegoEdge] # Edge list
        
        self.ui_position = None
        self.ui_colour = None
        self.source_info = set()
        
        self.is_destroyed = False
        
        self.extra_data = [] #type:List[str]
        self.components = set()
        
    @property
    def start(self) -> int:
        return self.__start
    
    @property
    def end(self) -> int:
        return self.__end
    
    @start.setter
    def start(self, value : int):
        if not (0 < value <= self.__end):
            raise ValueError("Attempt to set `start` to an out-of-bounds value {} in '{}'.".format(value, self))
            
        self.__start = value
        
    @end.setter
    def end(self, value : int):
        if not (self.__start <= value): 
            raise ValueError("Attempt to set `end` to an out-of-bounds value {} in '{}'.".format(value, self))
        
        self.__end = value
        
    
    
    
    def _verify_subsequence( self ):
        if not VERIFY:
            return
        
        if self.start > self.end:
            raise ImplementationError("Subsequence '{}' has start ({}) > end ({}).".format(self, self.start,self.end))
        
        if self.is_destroyed:
            raise ImplementationError("Subsequence '{}' has been flagged as destroyed, but it is still in use.".format(self))
        
        for edge in self.edges:
            edge._verify_deconvoluted()
        
        assert self in self.sequence.subsequences
    
    
    @property
    def index( self ):
        """
        Finds the index of this subsequence in the owning sequence
        (Only works after deconvolution of the owning sequence)
        :return: 
        """
        return self.sequence.subsequences.index( self )
    
    
    @property
    def array( self ):
        """
        Obtains the slice of the sequence array pertinent to this subsequence
        """
        if self.sequence.array:
            return self.sequence.array[ self.start:self.end + 1 ]
        else:
            return None
    
    
    def to_fasta( self, header ):
        fasta = [ ]
        
        if header:
            fasta.append( ">" + str( self ) )
        
        if self.array is not None:
            fasta.append( self.array )
        else:
            fasta.append( "; MISSING" )
        
        return "\n".join( fasta )
    
    
    @property
    def length( self ):
        """
        Calculates the length of this subsequence
        """
        return self.end - self.start + 1
    
    
    def destroy( self ):
        LOG("DESTROY SUBSEQUENCE {}".format(self))
        
        for edge in list( self.edges ):
            edge.unlink( self )
        
        assert len( self.edges ) == 0, self.edges
        self.is_destroyed = True
    
    
    def __repr__( self ):
        if self.is_destroyed:
            return "DELETED_SUBSEQUENCE"
        
        return "{} [ {} : {} ]".format( self.sequence.accession, self.start, self.end )
    
    
    def inherit( self, original: "LegoSubsequence" ):
        LOG("INHERIT SUBSEQUENCE {} --> {}".format(original, self))
        assert original != self
        
        for edge in original.edges:
            edge.link( edge.position( original ), [self] )
    
    
    def _split_subsequence( self, p: int ):
        """
        Splits the subsequence into s..p-1 and p..e

               |p        
        1 2 3 4|5 6 7 8 9
        """
        with LOG("SPLIT {} AT {}".format(self, p)):
            if p <= self.start or p > self.end:
                raise ValueError( "Cannot split a subsequence from {0} to {1} about a point {2}".format( self.start, self.end, p ) )
            
            left = LegoSubsequence( self.sequence, self.start, p - 1 )
            right = LegoSubsequence(self.sequence, p, self.end )
            
            left.inherit( self )
            right.inherit( self )
            
            index = self.sequence.subsequences.index(self)
            self.sequence.subsequences.remove( self )
            self.sequence.subsequences.insert(index, right)
            self.sequence.subsequences.insert(index, left)
            self.destroy()
            return left, right


class LegoSequence:
    """
    Protein (or DNA) sequence
    """
    
    
    def __init__( self, model: "LegoModel", accession: str, id : int, is_composite : bool ):
        self.id = id
        self.accession = accession  # Database accession (ID)
        self.subsequences = [ ]  # type: List[LegoSubsequence]
        self.model = model
        self.array = None
        self.source_info = set()
        self.is_composite = is_composite
        self.is_root = False
        self.extra_data = [] #List[str]
        self.composite_part_start = {}
        self.composite_part_end = {}
        
    @property
    def length(self):
        if len(self.subsequences)==0:
            return 0
        
        return self.subsequences[-1].end
    
    
    def to_fasta( self, header ):
        fasta = [ ]
        
        if header:
            fasta.append( ">" + self.accession )
        
        if self.array is not None:
            fasta.append( self.array )
        else:
            fasta.append( "; MISSING" )
        
        return "\n".join( fasta )
    
    
    def _verify_sequence( self ):
        if not VERIFY:
            return
        
        with LOG("{}".format(self)):
            for x in self.subsequences:
                LOG("{}".format(x))
                x._verify_subsequence()
        
        if len(self.subsequences) == 0:
            raise ImplementationError( "The sequence '{}' has no subsequences.".format( self ) )
        
        for left, right in ArrayHelper.lagged_iterate( self.subsequences ):
            if left.end != right.start - 1:
                raise ImplementationError( "Subsequences '{}' and '{}' in sequence '{}' are not adjacent.".format( left, right, self ) )

        if self.subsequences[ 0 ].start != 1:
            raise ImplementationError( "The first subsequence '{}' in sequence '{}' is not at the start.".format( self.subsequences[ 0 ], self ) )
        
        if self.subsequences[ -1 ].end != self.length:
            raise ImplementationError( "The last subsequence '{}' in sequence '{}' is not at the end.".format( self.subsequences[ 0 ], self ) )
        
        
            
        
             
    
    
    @property
    def index( self ):
        return self.model.sequences.index( self )
    
    
    def __repr__( self ):
        return "{}".format( self.accession )
    
    def _ensure_length( self, new_length ):
        if new_length == 0:
            return 
        
        if self.length < new_length:
            ss = LegoSubsequence(self, self.length+1, new_length) 
            self.subsequences.append(ss)
        
    
    
    def _make_subsequence( self, start, end, extra_data ) -> List[ LegoSubsequence ]:
        assert start > 0, start
        assert end > 0  , end
        
        with LOG( "REQUEST TO MAKE SUBSEQUENCE FROM {} TO {}".format( start, end ) ):    
            if start > end:
                raise ImplementationError( "Cannot make a subsequence in '{0}' which has a start ({1}) > end ({2}) because that doesn't make sense.".format( self, start, end ) )
        
            if self.length < end:
                self._ensure_length( end )
            
            r = []
            
            for subsequence in self.subsequences:
                if subsequence.end >= start:
                    if subsequence.start == start:
                        LOG("FIRST - {}".format(subsequence))
                        first = subsequence
                    else:
                        with LOG("FIRST - {} - ¡SPLIT!".format(subsequence)):
                            _, first = subsequence._split_subsequence( start )
                            LOG("SPLIT ABOUT {} GIVING RIGHT {}".format(start, first))
                            
                    if first.end > end:
                        first, _ = first._split_subsequence( end + 1 )
                        LOG("THEN SPLIT ABOUT {} GIVING LEFT {}".format(end+1, first))
                        
                    LOG("#### {}".format(first))
                    r.append(first)
                    break
            
            for subsequence in self.subsequences:
                if subsequence.start > start:
                    if subsequence.end > end:
                        if subsequence.start != end+1:
                            with LOG("LAST - {} - ¡SPLIT!".format(subsequence)):
                                last, _ = subsequence._split_subsequence( end + 1 )
                                LOG("SPLIT ABOUT {} GIVING LEFT {}".format(end+1, last))
                                
                            LOG("#### {}".format(last))
                            r.append(last)
                            
                        break
                    else:
                        LOG("MIDDLE - {}".format(subsequence))
                        LOG("#### {}".format(subsequence))
                        r.append(subsequence)
                        
                        
                    
            for left, right in ArrayHelper.lagged_iterate(self.subsequences):
                assert left.end +1 == right.start
            
            assert not any(x.is_destroyed for x in r)
            
            for subsequence in r:
                assert r.count(subsequence) == 1, "Multiple copies of {} in result.".format(subsequence)
                
            for ss in r:
                ss.extra_data.append(extra_data)
            
            return r
    
    
    def _find( self, start: int, end: int ):
        for x in self.subsequences:
            if x.start == start and x.end == end:
                return x
        
        raise KeyError( "No such subsequence as {0}-{1}".format( start, end ) )
    
    
    def _quantise( self, level: int ):
        
        with LOG("QUANTISING '{}'".format(self.accession)):
            while self._quantise_implementation( level ):
                pass

        new_length = _quantise_int(level, self.length)
        self._quantise_subsequence( new_length, self.subsequences[-1] )


    def _quantise_implementation( self, level ):
        for previous, next in ArrayHelper.lagged_iterate( list( self.subsequences ) ):
            new_start = _quantise_int( level, next.start )
        
            if new_start == next.start:
                continue
        
            if new_start > next.end:
                LOG( "'{}' START MOVES TO {} => disappeared.".format( next, new_start ) )
                next.destroy()
                self.subsequences.remove( next )
            else:
                LOG( "'{}' START MOVES TO {}".format( next, new_start ) )
                next.start = new_start
        
            self._quantise_subsequence( new_start, previous )
            
            return True
        
        return False


    def _quantise_subsequence( self, new_start, previous ):
        LOG("{} --> {}".format(previous.end + 1, new_start))
        
        new_end = new_start - 1
        
        if new_end >= previous.start:
            LOG("'{}' END MOVES TO {}".format(previous, new_end))
            previous.end = new_end
        else:
            # "previous" has shrunk to nothing
            with LOG( "'{}' END MOVES TO {} => disappeared.".format( previous, new_end ) ):
                previous.destroy()
                self.subsequences.remove( previous )


    def _split( self, split_point: int ):
        for ss in self.subsequences:
            if ss.start <= split_point <= ss.end:
                ss._split_subsequence( split_point )
                break
    
    
    def sub_array( self, start, end ):
        if self.array is None:
            return None
        
        assert start <= end, "{} {}".format( start, end )
        assert 0 < start <= len( self.array ), "{} {} {}".format( start, end, len( self.array ) )
        assert 0 < end <= len( self.array ), "{} {} {}".format( start, end, len( self.array ) )
        
        return self.array[ start:end ]


class LegoModel:
    """
    Model (collection of sequences)
    """
    def __init__( self ):
        """
        CONSTRUCTOR
        Creates a new model with no data
        Use the `import_*` functions to add data from a file.
        """
        self.__incremental_id = 0
        self.sequences = [ ]  # type: List[LegoSequence]
        self.components = [ ]  # type:List[LegoComponent]
        self.comments = ["MODEL CREATED AT {}".format(StringHelper.current_time())]
        self.__seq_type = ELetterType.UNKNOWN


    def letter_type( self ) -> ELetterType:
        """
        API
        Obtains the type of data in the model - protein, DNA or RNA.
        """
        if self.__seq_type != ELetterType.UNKNOWN:
            return self.__seq_type
    
        s = ELetterType.UNKNOWN
    
        for x in self.sequences:
            for y in x.array:
                if y not in "GAC":
                    if y == "T":
                        if s == ELetterType.UNKNOWN:
                            s = ELetterType.DNA
                    elif y == "U":
                        if s == ELetterType.UNKNOWN:
                            s = ELetterType.RNA
                    else:
                        s = ELetterType.PROTEIN
    
        self.__seq_type = s
    
        return s
                    
    def __get_incremental_id(self):
        self.__incremental_id+=1
        return self.__incremental_id
    
    
    def __make_sequence( self, lookup, accession: str, obtain_only, initial_length, is_composite, extra_data ) -> LegoSequence:
        if "|" in accession:
            accession = accession.split( "|" )[ 3 ]
        
        if "." in accession:
            accession = accession.split( ".", 1 )[ 0 ]
        
        accession = accession.strip()
        
        result = lookup.get( accession )
        
        if result is None and not obtain_only:
            result = LegoSequence( self, accession, self.__get_incremental_id(), is_composite )
            lookup[ accession ] = result
            self.sequences.append( result )
            
        if result is not None:
            result._ensure_length( initial_length )
            
            if is_composite:
                result.is_composite = is_composite
                
        result.extra_data.append(extra_data)
        
        return result
    
    
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
    
    def deconvolute(self):
        self.__deconvolute()
    
    
    def __deconvolute( self ):
        for edge in self.all_edges:
            edge._deconvolute()
        
        self.sequences = sorted( self.sequences, key = lambda x: x.accession )
        self.components = LegoComponent.create( self )
        
        with LOG("VERIFY"): 
            for sequence in self.sequences:
                sequence._verify_sequence()
    
    
    def __lookup_table( self ):
        return dict( (x.accession, x) for x in self.sequences )
    
    
    def import_fasta( self, file_name: str ):
        """
        API
        Imports a FASTA file.
        If data already exists in the model, only sequence data matching sequences already in the model is loaded.
        """
        self.comments.append( "IMPORT_FASTA \"{}\"".format( file_name))
        
        with LOG( "IMPORT FASTA FROM '{}'".format( file_name ) ):
            from Bio import SeqIO
            
            obtain_only = self.__has_data()
            num_updates = 0
            lookup_table = self.__lookup_table()
            idle = 0
            idle_counter = 10000
            extra_data = "FASTA from '{}'".format(file_name)
            
            for record in SeqIO.parse( file_name, "fasta" ):
                sequence = self.__make_sequence( lookup_table, str( record.id ), obtain_only, len(record.seq), False, extra_data )
                
                if sequence:
                    LOG( "FASTA UPDATES {} WITH ARRAY OF LENGTH {}".format( sequence, len( record.seq ) ) )
                    num_updates += 1
                    sequence.array = str( record.seq )
                    idle = 0
                else:
                    idle += 1
                    
                    if idle == idle_counter:
                        LOG( "THIS FASTA IS BORING..." )
                        idle_counter *= 2
                        idle = 0
            
            self.__deconvolute()
    
    
    def __has_data( self ):
        return bool( self.sequences )
    
    
    def quantise( self, level ):
        """
        API
        Quantises the subsequence start/end positions in the model
        """
        for sequence in self.sequences:
            # noinspection PyProtectedMember
            sequence._quantise( level )
        
        self.__deconvolute()
    
    
    def import_blast( self, file_name: str ):
        """
        API
        Imports a BLAST file.
        If data already exists in the model, only lines referencing existing sequences are imported.
        """
        self.comments.append( "IMPORT_BLAST \"{}\"".format( file_name))
        
        obtain_only = self.__has_data()
        
        with LOG( "IMPORT {} BLAST FROM '{}'".format( "MERGE" if obtain_only else "NEW", file_name ) ):
            lookup_table = self.__lookup_table()
            
            with open( file_name, "r" ) as file:
                for line in file.readlines():
                    line = line.strip()
                    
                    if line and not line.startswith( "#" ) and not line.startswith(";"):
                        # BLASTN     query acc. | subject acc. |                                 | % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
                        # MEGABLAST  query id   | subject ids  | query acc.ver | subject acc.ver | % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
                        # Fields: 
                        # Fields: 
                        e = line.split( "\t" )
                        
                        if len(e) == 14:
                            del e[2:4]
                        
                        if len(e) != 12:
                            raise ValueError("BLAST file should contain 12 values, but this line contains {}: {}".format(len(e), line))
                        
                        query_accession = e[ 0 ]
                        query_start = int( e[ 6 ] )
                        query_end = int( e[ 7 ] )
                        query_length = query_end-  query_start 
                        subject_accession = e[ 1 ]
                        subject_start = int( e[ 8 ] )
                        subject_end = int( e[ 9 ] )
                        subject_length = subject_end-  subject_start
                        e_value = float(e[10])
                        LOG("BLAST SAYS {} {}:{} ({}) --> {} {}:{} ({})".format(query_accession, query_start, query_end, query_length, subject_accession, subject_start, subject_end, subject_length))
                        
                        if e_value > 1e-10:
                            LOG("REJECTED E VALUE")
                            continue
                        
                        assert query_length>0 and subject_length > 0
                        
                        TOL = int(10 + ((query_length+subject_length)/2)/5)
                        if not (subject_length - TOL) <= query_length <= (subject_length+TOL):
                            raise ValueError("Refusing to process BLAST file because the query length {} is not constant with the subject length {} at the line reading '{}'.".format(query_length, subject_length, line))
                        
                        query_s = self.__make_sequence( lookup_table, query_accession, obtain_only, 0, False, line )
                        subject_s = self.__make_sequence( lookup_table, subject_accession, obtain_only, 0, False, line )
                        
                        if query_s and subject_s and query_s is not subject_s:
                            query = query_s._make_subsequence( query_start, query_end, line ) if query_s else None
                            subject = subject_s._make_subsequence(subject_start, subject_end, line ) if subject_s else None
                            LOG( "BLAST UPDATES AN EDGE THAT JOINS {} AND {}".format( query, subject ) )
                            edge = self.__make_edge( query, subject, line )
                            edge.source_info.add( line )
            
            for z in [x for x in self.sequences if not x.subsequences]:
                self.sequences.remove(z)
            
            self.__deconvolute()
    
    
    def import_composites( self, file_name: str ):
        """
        API
        Imports a COMPOSITES file
        """
        self.comments.append( "IMPORT_COMPOSITES \"{}\"".format( file_name))
        
        with LOG( "IMPORT COMPOSITES FROM '{}'".format( file_name ) ):
            
            lookup_table = self.__lookup_table()
            
            fam_name = "?"
            fam_mean_length = None
            composite_sequence = None
            composite_subsequence = None
            
            with open( file_name, "r" ) as file:
                for line_number, line in enumerate( file ):
                    line = line.strip()
                    
                    if line.startswith( ">" ):
                        if composite_sequence:
                            return
                            
                        # COMPOSITE!
                        composite_name = line[ 1: ]
                        composite_sequence = self.__make_sequence( lookup_table, composite_name, False, 0, True, line )
                        composite_sequence.source_info.add( "FILE '{}' LINE {}".format( file_name, line_number ) )
                    elif "\t" in line:
                        # FAMILY!
                        # Fields: F<comp family id> <mean align> <mean align> <no sequences as component> <no sequences in family> <mean pident> <mean length>
                        e = line.split( "\t" )
                        
                        fam_name = e[ 0 ]
                        fam_mean_start = int( e[ 1 ] )
                        fam_mean_end = int( e[ 2 ] )
                        # fam_num_seq_as_component = int(e[3])
                        # fam_num_seq_in_family = int(e[3])
                        # fam_mean_pident = float(e[4])
                        fam_mean_length = int( float( e[ 5 ] ) )
                        
                        composite_subsequence = composite_sequence._make_subsequence( fam_mean_start, fam_mean_end, line )
                    elif line:
                        # SEQUENCE
                        sequence = self.__make_sequence( lookup_table, line, False, fam_mean_length, False, line )
                        sequence.source_info.add( "Family '{}'".format( fam_name ) )
                        sequence.source_info.add( "Accession '{}'".format( line ) )
                        
                        #subsequence = sequence._make_subsequence( 1, sequence.length )
                        assert composite_subsequence
                        #self.__make_edge( composite_subsequence, subsequence )
            
            self.__deconvolute()
    
    
    def __make_edge( self, source: List[LegoSubsequence], destination: List[LegoSubsequence], extra_data ) -> LegoEdge:
        assert source != destination
        
        for edge in self.all_edges:
            if source in edge and destination in edge:
                edge.extra_data.append(extra_data)
                return edge
            
        assert not any(x in source for x in destination)
        assert not any(x in destination for x in source)
        
        result = LegoEdge()
        result.link( False, source )
        result.link( True, destination )
        result.extra_data.append(extra_data)
        return result
    
    
    def add_new_sequence( self ) -> LegoSequence:
        """
        API
        Creates a new sequence
        """
        sequence = LegoSequence( self, "Untitled", self.__get_incremental_id(), False )
        self.sequences.append( sequence )
        self.__deconvolute()
        return sequence
    
    
    def add_new_edge( self, subsequences: List[ LegoSubsequence ] ) -> LegoEdge:
        """
        API
        Creates a new edge between the specified subsequences.
        The specified subsequences should span two, and only two, sequences.
        """
        sequences = list( set( subsequence.sequence for subsequence in subsequences ) )
        
        if len( sequences ) != 2:
            raise ValueError( "Need two sequences to create an edge, but {0} have been specified: {1}".format( len( subsequences ), subsequences ) )
        
        left_sequence = sequences[ 0 ]
        right_sequence = sequences[ 0 ]
        
        left_subsequences = [ subsequence for subsequence in subsequences if subsequence.sequence is left_sequence ]
        right_subsequences = [ subsequence for subsequence in subsequences if subsequence.sequence is right_sequence ]
        
        edge = LegoEdge()
        
        edge.link( False, left_subsequences )
        edge.link( True, right_subsequences )
            
        self.__deconvolute()
        
        return edge
    
    
    def add_new_subsequence( self, sequence: LegoSequence, split_point: int ) -> None:
        """
        API
        Splits a sequence, creating a new subsequence
        """
        sequence._split( split_point )
        self.__deconvolute()
    
    
    def remove_sequences( self, sequences: Iterable[ LegoSequence ] ):
        """
        API
        Removes the specified sequences
        """
        for sequence in sequences:
            print( "REMOVING SEQUENCE '{}'".format( sequence ) )
            
            for subsequence in sequence.subsequences:
                subsequence.destroy()
            
            self.sequences.remove( sequence )
        
        self.__deconvolute()
    
    
    def remove_edges( self, subsequences:Iterable[LegoSubsequence], edges: Iterable[LegoEdge] ):
        """
        API
        Removes the specified edges from the specified subsequences
        """
        for subsequence in subsequences:
            for edge in edges:
                if not edge.is_destroyed:
                    edge.unlink(subsequence)
            
        self.__deconvolute()
    
    
    def merge_subsequences( self, subsequences: Iterable[ LegoSubsequence ] ) -> List[ LegoSubsequence ]:
        """
        API
        Merges specified subsequences (they should be adjacent)
        """
        to_do = list( subsequences )
        results = [ ]
        
        while len( to_do ) > 0:
            first = to_do.pop()
            second = None
            
            for potential_second in to_do:
                if potential_second.sequence is first.sequence:
                    if potential_second.start == first.end + 1:
                        to_do.remove( potential_second )
                        second = potential_second
                        break
                    elif first.start == potential_second.end + 1:
                        to_do.remove( potential_second )
                        orig_first = first
                        first = potential_second
                        second = orig_first
                        break
            
            if second is None:
                results.append( first )
                continue
            
            sequence = first.sequence  # type:LegoSequence
            combined = LegoSubsequence( sequence, first.start, second.end )
            
            combined.inherit( first )
            first.destroy()
            combined.inherit( second )
            second.destroy()
            
            sequence.subsequences.remove( first )
            sequence.subsequences.remove( second )
            sequence.subsequences.append( combined )
            sequence.subsequences = sorted(sequence.subsequences, key = lambda x: x.start)
            
            to_do.append( combined )
        
        self.__deconvolute()
        return results
    
    
    def __merge_subsequences( self, all: Iterable[ LegoSubsequence ] ):
        all = sorted( all, key = lambda x: x.start )
        
        if len( all ) <= 1:
            raise ValueError( "Cannot merge a list '{}' of less than two elements.".format( all ) )
        
        for left, right in ArrayHelper.lagged_iterate( all ):
            if left.sequence != right.sequence:
                raise ValueError( "merge_subsequences attempted but the subsequences '{}' and '{}' are not in the same sequence.".format( left, right ) )
            
            if right.start != left.end + 1:
                raise ValueError( "merge_subsequences attempted but the subsequences '{}' and '{}' are not adjacent.".format( left, right ) )
        
        first = all[ 0 ]
        first.end = all[ -1 ].end
        
        for other in all[ 1: ]:
            first.inherit( other )
            other.sequence.subsequences.remove( other )
            other.destroy()
    
    
    def compartmentalise( self ):
        """
        API
        Merges adjacent subsequences in the same connected component, composites excluded.
        """
        for component in self.components:
            for line in component.lines:
                if len( line ) >= 2:
                    self.__merge_subsequences( line )
        
        self.__deconvolute()


    def remove_redundant_subsequences( self ):
        """
        API
        Merges adjacent subsequences with identical edges
        """
        
        def it():
            for sequence in self.sequences:
                for previous, next in ArrayHelper.lagged_iterate(sequence.subsequences):
                    if set(previous.edges) == set(next.edges) \
                            and previous.components == next.components:
                         
                         with LOG("EQUIVALENT:"):
                             LOG("X = {}".format(previous))
                             LOG("Y = {}".format(next))
                             self.merge_subsequences((previous, next))
                             return True
            
            return False
        
        with LOG("REMOVE REDUNDANT SUBSEQUENCES"):
            removed = 0
            
            while it():
                removed +=1
                
            return removed


    def remove_redundant_edges( self ):
        """
        API
        Removes edges that have copies elsewhere (either forward or back)
        """
        the_list = list(self.all_edges)
        
        with LOG("REMOVE REDUNDANT EDGES"):
            removed = 0
            
            for x in the_list:
                for y in the_list:
                    if not x.is_destroyed and not y.is_destroyed and x is not y:
                        x_source = set(x.source)
                        x_dest = set(x.destination)
                        y_source = set(y.source)
                        y_dest = set(y.destination)
                        
                        if (x_source == y_source and x_dest==y_dest) or (x_source == y_dest and x_dest == y_source):
                            with LOG("EQUIVALENT:"):
                                LOG("X = {}".format(x))
                                LOG("Y = {}".format(y))
                                y.unlink_all()
                                removed +=1
                                
            return removed


    def find_sequence( self, name : str ) -> "LegoSequence":
        for x in self.sequences:
            if x.accession == name:
                return x
        
        raise KeyError(name)


_GREEK = "αβγδϵζηθικλμνξοπρστυϕχψω"


class LegoComponent:
    """
    Connected component
    """
    
    
    def __init__( self, index: int, subsequences: List[ LegoSubsequence ], is_composite : bool ):
        sequences = set( x.sequence for x in subsequences )
        lines = [ ]
        self.tree = None
        self.index = index
        self.is_composite = is_composite
        
        for sequence in sequences:
            line = [ subsequence for subsequence in subsequences if subsequence.sequence is sequence ]
            line = tuple(sorted(line, key = lambda x: x.start))
            
            # for left, right in ArrayHelper.lagged_iterate(line):
            #     assert left.end + 1 == right.start, "{} {}".format(left, right)
            
            lines.append( line )
            
        self.lines = tuple(lines) # type:Tuple[Tuple[LegoSubsequence]]
        
        # for line in self.lines:
        #     for left, right in ArrayHelper.lagged_iterate(line):
        #         assert left.end + 1 == right.start, "{} {}".format(left, right)
            
    
    
    def __repr__( self ):
        x = _GREEK[ self.index % len( _GREEK ) ]
        
        if self.is_composite:
            return x.upper() 
        else:
            return x.lower()
    
    
    def to_fasta( self, header : bool = True, simplify : bool = False ) -> str:
        """
        Converts the component to FASTA
        :param simplify: Turns on simplified mode to produce output for limited parsers: Names are replaced with short "S*" numbers, comments are removed, errors are raised on failure instead of appending comments to the file 
        :return: FASTA, as a string 
        """
        fasta = [ ]
        
        if header and not simplify:
            fasta.append( ";" )
            fasta.append( "; COMPONENT: " + str( self ) )
            fasta.append( ";" )
        
        for line in self.lines:
            sequence = line[ 0 ].sequence
            
            start = min( x.start for x in line )
            end = max( x.end for x in line )
            array = sequence.sub_array( start, end )
            
            if simplify:
                fasta.append( ">S" + str( sequence.id ) )
            else:
                fasta.append( ">{}".format( sequence ) )
            
            if array is not None:
                fasta.append( array )
                fasta.append( "" )
            elif simplify:
                raise ValueError( "Sequence '{}' has no array data. Have you loaded the FASTA? Have you loaded the correct FASTA?".format( sequence ) )
            else:
                fasta.append( ";MISSING" )
                fasta.append( "" )
        
        return "\n".join( fasta )
    
    
    def all_subsequences( self ) -> List[ LegoSubsequence ]:
        return [ subsequence for line in self.lines for subsequence in line ]
    
    
    def all_sequences( self ) -> List[ LegoSequence ]:
        return [ line[ 0 ].sequence for line in self.lines ]
    
    
    @classmethod
    def create( cls, model: LegoModel ) -> "List[LegoComponent]":
        """
        Calculates the connected components
        """
        for sequence in model.sequences:
            for subsequence in sequence.subsequences:
                if not hasattr(subsequence, "components"):
                    subsequence.components = set()
                    
                subsequence.components.clear()
        
        with LOG( "CREATING CONNECTED COMPONENT COLLECTION" ):
            component_list_regular = [ ]
            component_list_composites = [ ]
            
            for sequence in sorted(model.sequences, key = lambda x: x.is_composite):  # type: LegoSequence
                for subsequence in sequence.subsequences:
                    cls.__connect_components( subsequence, component_list_composites if subsequence.sequence.is_composite else component_list_regular )
            
            results = [ ]  # type:List[LegoComponent]
            
            for component in component_list_regular:
                results.append( LegoComponent( len( results ), component, False ))
                
            for component in component_list_composites:
                results.append( LegoComponent( len( results ), component, True ))
                
            
            return results
    
    
    @classmethod
    def __connect_components( cls, subsequence: LegoSubsequence, component_list: List[ Set[ LegoSubsequence ] ] ):
        """
        Starting with `subsequence`, finds everything connected to it and creates a new `set` of those things, adding it to `component_list`.
        If `subsequence` is already in a set in `component_list`, nothing is done.
        """
        for visited_set in component_list:
            if subsequence in visited_set:
                return
        
        with LOG("CONNECTED COMPONENT #{}".format(len(component_list)+1)):
            LOG("STARTING WITH {} IN {} COMPONENT".format(subsequence, "COMPOSITE" if subsequence.sequence.is_composite else "REGULAR"))
            visited_set = set()
            component_list.append( visited_set )
            component_uid = object()
            cls.__connect_to( subsequence, visited_set, subsequence.sequence.is_composite, -1, -1, component_uid,0 )
    
    
    @classmethod
    def __connect_to( cls, origin: LegoSubsequence, target_set: set, look_for_composites : bool, incoming_start : int, incoming_end : int, component_uid : object, indent : int ):
        """
        Adds the `origin` subsequence, and everything connected to `origin` to the `target_set`.
        """
        # Already visited?
        if origin in target_set:
            return  
            
        print("    "*indent+ "COMPFIND *{}* {}".format(id(component_uid), origin))
        
        # Quick check
        origin._verify_subsequence()
        
        # Add to the list
        target_set.add( origin )
        
        
        for edge in origin.edges: #type: LegoEdge
            # Get the side opposite the `origin`
            side = edge.position(origin)
            destination_side = edge.side( not side )
            assert origin not in destination_side
            
            
            destination_sequence = destination_side[0].sequence
            opposite_is_composite = destination_sequence.is_composite
            
            # If started from a composite, ignore anything that's not
            if look_for_composites and not destination_side[0].sequence.is_composite:
                continue
                
            # If we started from a non-composite, don't leave the composite once we're in
            if not look_for_composites and origin.sequence.is_composite and not destination_side[0 ].sequence.is_composite:
                continue
            
            # (-) removed old code that assumed partial homologies existed
            
            destination_start = min(x.start for x in destination_side)
            destination_end   = max(x.end for x in destination_side )
            
            # Not searching for composites but we are inside one!
            if not look_for_composites and opposite_is_composite:
                if incoming_start == -1:
                    # First incoming to composite
                    comp_start = destination_start
                    comp_end   = destination_end
                else:
                    # Subsequent incoming to composite
                    origin_side = edge.side(side)
                    edge_source_start = min(x.start for x in origin_side)
                    comp_start = destination_start + incoming_start - edge_source_start 
                    comp_end   = destination_start + incoming_end   - edge_source_start # TODO: could assert this by checking `end` too
                    
                for friend in destination_sequence._make_subsequence(comp_start, comp_end, "Auto-component {} to {}".format(comp_start, comp_end)):
                    friend.components.add( component_uid )
                    cls.__connect_to( friend, target_set, look_for_composites, comp_start, comp_end, component_uid,indent+1 )
            else:
                for friend in destination_side:
                    LOG("JOINING {} TO {} IN {} COMPONENT".format( origin, friend, "COMPOSITE" if look_for_composites else "REGULAR" ) )
                    cls.__connect_to( friend, target_set, look_for_composites, -1, -1, component_uid, indent+1 )


    @classmethod
    def __is_close( cls, outgoing_start, incoming_start, outgoing_end, incoming_end ):
        """
        Is the incoming edge commensurate with the outgoing one?
        """
        assert -1 not in (outgoing_start, outgoing_end, incoming_start, incoming_end)
        
        # TODO: Currently determined by length (I don't know if this is a good idea or not :(
        a = outgoing_end - outgoing_start
        b = incoming_end - incoming_start
        return abs(a-b) < 10 #TODO: Don't hardcode
