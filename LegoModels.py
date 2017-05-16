from collections import defaultdict
from typing import List, Optional, Set, Tuple

from MHelper.ExceptionHelper import ImplementationError
from MHelper import ArrayHelper, NameHelper ,StringHelper
from MHelper.DisposalHelper import ManagedWith
from MHelper.LogHelper import Logger

LOG = Logger()


__incremental_id = 0


def _incremental_id():
    global __incremental_id
    __incremental_id += 1
    return __incremental_id


VERIFY = True


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
        self.id = _incremental_id()
        self.source = [ ]  # type:List[LegoSubsequence]
        self.destination = [ ]  # type:List[LegoSubsequence]
        self.source_info = set()
        self.is_destroyed = False
    
    
    def to_fasta( self ):
        fasta = [ ]
        fasta.append( ";" )
        fasta.append( "; EDGE: {}".format( self ) )
        fasta.append( ";" )
        
        fasta.append( ">{} [ {} : {} ]".format( self.source_sequence, self.source_start, self.source_end ) )
        fasta.append( self.source_array or ";MISSING" )
        fasta.append( "" )
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
    
    
    def opposite( self, subsequence ):
        """
        Returns the list (source/destination) opposite the specified subsequence
        """
        return self.destination if self.position( subsequence ) else self.source
    
    
    def _deconvolute( self ):
        """
        Deconvolutes the edge:
            * Sorts the source and destination lists by position
            * Verifies the integrity
        """
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
        with LOG("LINK EDGE #{}".format(self.id)):
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
        
        self.id = _incremental_id()
        self.sequence = sequence  # type:LegoSequence  
        self.start = start  # Start position
        self.end = end  # End position
        self.edges = [ ]  # type:List[LegoEdge]        # Edge list
        
        self.ui_position = None
        self.ui_colour = None
        self.source_info = set()
        
        self.is_destroyed = False
    
    
    def _verify_deconvoluted( self ):
        if not VERIFY:
            return
        
        assert self.start <= self.end
        assert not self.is_destroyed
        
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
    
    
    def to_fasta( self ):
        fasta = [ ]
        fasta.append( ">" + str( self ) )
        
        if self.array is not None:
            fasta.append( self.array )
        else:
            fasta.append( ";MISSING" )
        
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
    
    
    def quantise( self, level ):
        hlevel = (level // 2)
        
        start = self.start + hlevel
        start = max( start - start % level, 1 )
        
        end = self.end + hlevel
        end = max( end - end % level - 1, 1 )
        
        if start >= end:
            end = (start - start % level) + level - 1
        
        print( "QUANTISED '{}' TO {}:{}".format( self, start, end ) )
        
        self.start = start
        self.end = end
    
    
    def _split( self, p: int ):
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
    
    
    def __init__( self, model: "LegoModel", accession: str ):
        self.id = _incremental_id()
        self.accession = accession  # Database accession (ID)
        self.subsequences = [ ]  # type: List[LegoSubsequence]
        self.model = model
        self.array = None
        self.source_info = set()
        
    @property
    def length(self):
        if len(self.subsequences)==0:
            return 0
        
        return self.subsequences[-1].end
    
    
    def to_fasta( self ):
        fasta = [ ]
        fasta.append( ">" + self.accession )
        
        if self.array is not None:
            fasta.append( self.array )
        else:
            fasta.append( ";MISSING" )
        
        return "\n".join( fasta )
    
    
    def _verify_deconvoluted( self ):
        if not VERIFY:
            return
        
        if len(self.subsequences) == 0:
            raise ImplementationError( "The sequence '{}' has no subsequences.".format( self ) )
        
        if self.subsequences[ 0 ].start != 1:
            raise ImplementationError( "The first subsequence '{}' in sequence '{}' is not at the start.".format( self.subsequences[ 0 ], self ) )
        
        for left, right in ArrayHelper.lagged_iterate( self.subsequences ):
            if left.end != right.start - 1:
                raise ImplementationError( "Subsequences '{}' and '{}' in sequence '{}' are not adjancent.".format( left, right, self ) )
        
        for x in self.subsequences:
            x._verify_deconvoluted()
    
    
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
        
    
    
    def _make_subsequence( self, start, end ) -> List[ LegoSubsequence ]:
        with LOG( "REQUEST TO MAKE SUBSEQUENCE FROM {} TO {}".format( start, end ) ):    
            if start > end:
                raise ImplementationError( "Cannot make a subsequence in '{0}' which has a start ({1}) > end ({2}) because that doesn't make sense.".format( self, start, end ) )
        
            if self.length < end:
                self._ensure_length( end )
            
            r = []
            
            for x in self.subsequences:
                if x.end >= start:
                    if x.start == start:
                        LOG("FIRST - {}".format(x))
                        first = x
                    else:
                        with LOG("FIRST - {} - ¡SPLIT!".format(x)):
                            _, first = x._split(start)
                            LOG("SPLIT ABOUT {} GIVING RIGHT {}".format(start, first))
                            
                    if first.end > end:
                        first, _ = first._split(end+1)
                        LOG("THEN SPLIT ABOUT {} GIVING LEFT {}".format(end+1, first))
                        
                    LOG("#### {}".format(first))
                    r.append(first)
                    break
            
            for x in self.subsequences:
                if x.start > start:
                    if x.end > end:
                        if x.start != end+1:
                            with LOG("LAST - {} - ¡SPLIT!".format(x)):
                                last, _ = x._split(end+1)
                                LOG("SPLIT ABOUT {} GIVING LEFT {}".format(end+1, last))
                                
                            LOG("#### {}".format(last))
                            r.append(last)
                            
                        break
                    else:
                        LOG("MIDDLE - {}".format(x))
                        LOG("#### {}".format(x))
                        r.append(x)
                        
                        
                    
            for left, right in ArrayHelper.lagged_iterate(self.subsequences):
                assert left.end +1 == right.start
            
            assert not any(x.is_destroyed for x in r)
            
            for x in r:
                assert r.count(x) == 1, "Multiple copies of {} in result.".format(x)
            
            return r
    
    
    def __complete_subsequences( self ):
        self.subsequences = list( sorted( self.subsequences, key = lambda x: x.start ) )
        to_add = [ ]
        
        prev_end = 1
        
        for i, v in enumerate( self.subsequences ):
            assert isinstance( v, LegoSubsequence )
            
            if v.start != prev_end:
                # Insert new!
                print( "COMPLETE_SEQUENCE (INTERIM) {}:{}".format( prev_end, v.start - 1 ) )
                to_add.append( LegoSubsequence( self, prev_end, v.start - 1 ) )
            
            prev_end = v.end + 1
        
        if self.length + 1 != prev_end:
            print( "COMPLETE_SEQUENCE (FINAL) {}:{}".format( prev_end, self.length ) )
            to_add.append( LegoSubsequence( self, prev_end, self.length ) )
        
        self.subsequences.extend( to_add )
        self.subsequences = sorted( self.subsequences, key = lambda x: x.start )
    
    
    def _deconvolute( self ):
        self.__complete_subsequences()
    
    
    def _find( self, start: int, end: int ):
        for x in self.subsequences:
            if x.start == start and x.end == end:
                return x
        
        raise KeyError( "No such subsequence as {0}-{1}".format( start, end ) )
    
    
    def _quantise( self, level: int ):
        for x in self.subsequences:
            x.quantise( level )
    
    
    def _split( self, split_point: int ):
        for ss in self.subsequences:
            if ss.start <= split_point <= ss.end:
                ss._split( split_point )
                break
    
    
    def _remove_subsequence( self, subsequence: LegoSubsequence ):
        subsequence.destroy()
        self.subsequences.remove( subsequence )
    
    
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
        self.sequences = [ ]  # type: List[LegoSequence]
        self.components = [ ]  # type:List[LegoComponent]
        self.comments = ["MODEL CREATED AT {}".format(StringHelper.current_time())]
    
    
    def __make_sequence( self, lookup, accession: str, obtain_only, initial_length ) -> LegoSequence:
        if "|" in accession:
            accession = accession.split( "|" )[ 3 ]
        
        if "." in accession:
            accession = accession.split( ".", 1 )[ 0 ]
        
        accession = accession.strip()
        
        result = lookup.get( accession )
        
        if result is None and not obtain_only:
            result = LegoSequence( self, accession )
            lookup[ accession ] = result
            self.sequences.append( result )
            
        if result is not None:
            result._ensure_length( initial_length )
        
        return result
    
    
    def clear( self ):
        self.sequences.clear()
    
    
    @property
    def all_edges( self ) -> Set[ LegoEdge ]:
        r = set()
        
        for x in self.sequences:
            for xx in x.subsequences:
                for xxx in xx.edges:
                    r.add( xxx )
        
        return r
    
    def deconvolute(self):
        self.__deconvolute()
    
    
    def __deconvolute( self ):
        for x in self.sequences:
            x._deconvolute()
        
        for x in self.all_edges:
            x._deconvolute()
        
        self.sequences = sorted( self.sequences, key = lambda x: x.accession )
        self.components = LegoComponent.create( self )
        
        for x in self.sequences:
            x._verify_deconvoluted()
    
    
    def __lookup_table( self ):
        return dict( (x.accession, x) for x in self.sequences )
    
    
    def import_fasta( self, file_name: str ):
        self.comments.append( "IMPORT_FASTA \"{}\"".format( file_name))
        
        with LOG( "IMPORT FASTA FROM '{}'".format( file_name ) ):
            from Bio import SeqIO
            
            obtain_only = self.__has_data()
            num_updates = 0
            lookup_table = self.__lookup_table()
            idle = 0
            idlec = 10000
            
            for record in SeqIO.parse( file_name, "fasta" ):
                sequence = self.__make_sequence( lookup_table, str( record.id ), obtain_only, len(record.seq) )
                
                if sequence:
                    LOG( "FASTA UPDATES {} WITH ARRAY OF LENGTH {}".format( sequence, len( record.seq ) ) )
                    num_updates += 1
                    sequence.array = str( record.seq )
                    idle = 0
                else:
                    idle += 1
                    
                    if idle == idlec:
                        LOG( "THIS FASTA IS BORING..." )
                        idlec *= 2
                        idle = 0
            
            self.__deconvolute()
    
    
    def __has_data( self ):
        return bool( self.sequences )
    
    
    def quantise( self, level ):
        for sequence in self.sequences:
            # noinspection PyProtectedMember
            sequence._quantise( level )
        
        self.__deconvolute()
    
    
    def import_blast( self, file_name: str ):
        self.comments.append( "IMPORT_BLAST \"{}\"".format( file_name))
        
        obtain_only = self.__has_data()
        
        with LOG( "IMPORT {} BLAST FROM '{}'".format( "MERGE" if obtain_only else "NEW", file_name ) ):
            lookup_table = self.__lookup_table()
            
            with open( file_name, "r" ) as file:
                for line in file.readlines():
                    line = line.strip()
                    
                    if line and not line.startswith( "#" ) and not line.startswith(";"):
                        # Fields: query acc., subject acc., % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
                        e = line.split( "\t" )
                        query_accession = e[ 0 ]
                        query_start = int( e[ 6 ] )
                        query_end = int( e[ 7 ] )
                        query_length = query_end-  query_start 
                        subject_accession = e[ 1 ]
                        subject_start = int( e[ 8 ] )
                        subject_end = int( e[ 9 ] )
                        subject_length = subject_end-  subject_start
                        LOG("BLAST SAYS {} {}:{} ({}) --> {} {}:{} ({})".format(query_accession, query_start, query_end, query_length, subject_accession, subject_start, subject_end, subject_length))
                        
                        assert query_length>0 and subject_length > 0
                        
                        TOL = int(10 + ((query_length+subject_length)/2)/5)
                        if not (subject_length - TOL) <= query_length <= (subject_length+TOL):
                            raise ValueError("Refusing to process BLAST file because the query length {} is not constantant with the subject length {} at the line reading '{}'.".format(query_length, subject_length, line))
                        
                        query_s = self.__make_sequence( lookup_table, query_accession, obtain_only, 0 )
                        subject_s = self.__make_sequence( lookup_table, subject_accession, obtain_only, 0 )
                        
                        if query_s and subject_s and query_s is not subject_s:
                            query = query_s._make_subsequence( query_start, query_end ) if query_s else None
                            subject = subject_s._make_subsequence(subject_start, subject_end ) if subject_s else None
                            LOG( "BLAST UPDATES AN EDGE THAT JOINS {} AND {}".format( query, subject ) )
                            edge = self.__make_edge( query, subject )
                            edge.source_info.add( line )
            
            for z in [x for x in self.sequences if not x.subsequences]:
                self.sequences.remove(z)
            
            self.__deconvolute()
    
    
    def import_composites( self, file_name: str ):
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
                        composite_sequence = self.__make_sequence( lookup_table, composite_name, False, 0 )
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
                        
                        composite_subsequence = composite_sequence._make_subsequence( fam_mean_start, fam_mean_end )
                    elif line:
                        # SEQUENCE
                        sequence = self.__make_sequence( lookup_table, line, False, fam_mean_length )
                        sequence.source_info.add( "Family '{}'".format( fam_name ) )
                        sequence.source_info.add( "Accession '{}'".format( line ) )
                        
                        #subsequence = sequence._make_subsequence( 1, sequence.length )
                        assert composite_subsequence
                        #self.__make_edge( composite_subsequence, subsequence )
            
            self.__deconvolute()
    
    
    def __make_edge( self, source: List[LegoSubsequence], destination: List[LegoSubsequence] ) -> LegoEdge:
        assert source != destination
        
        for edge in self.all_edges:
            if source in edge and destination in edge:
                return edge
            
        assert not any(x in source for x in destination)
        assert not any(x in destination for x in source)
        
        result = LegoEdge()
        result.link( False, source )
        result.link( True, destination )
        return result
    
    
    def add_new_sequence( self ) -> LegoSequence:
        sequence = LegoSequence( self, "Untitled" )
        self.sequences.append( sequence )
        self.__deconvolute()
        return sequence
    
    
    def add_new_edge( self, ss: List[ LegoSubsequence ] ) -> LegoEdge:
        sequences = list( set( x.sequence for x in ss ) )
        
        if len( sequences ) != 2:
            raise ValueError( "Need two sequences to create an edge, but {0} have been specified: {1}".format( len( ss ), ss ) )
        
        left_sequence = sequences[ 0 ]
        right_sequence = sequences[ 0 ]
        
        left_subsequences = [ x for x in ss if x.sequence is left_sequence ]
        right_subsequences = [ x for x in ss if x.sequence is right_sequence ]
        
        edge = LegoEdge()
        
        for x in left_subsequences:
            edge.link( False, x )
        
        for x in right_subsequences:
            edge.link( True, x )
            
        self.__deconvolute()
        
        return edge
    
    
    def add_new_subsequence( self, sequence: LegoSequence, split_point: int ) -> None:
        sequence._split( split_point )
        self.__deconvolute()
    
    
    def remove_sequences( self, sequences: List[ LegoSequence ] ):
        for sequence in sequences:
            print( "REMOVING SEQUENCE '{}'".format( sequence ) )
            
            for subsequence in list( sequence.subsequences ):
                sequence._remove_subsequence( subsequence )
            
            self.sequences.remove( sequence )
        
        self.__deconvolute()
    
    
    def remove_edges( self, subsequences:List[LegoSubsequence], edges: List[LegoEdge] ):
        
        for subsequence in subsequences:
            for edge in edges:
                if not edge.is_destroyed:
                    edge.unlink(subsequence)
            
        self.__deconvolute()
    
    
    def merge_subsequences( self, subsequences: List[ LegoSubsequence ] ) -> List[ LegoSubsequence ]:
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
            
            to_do.append( combined )
        
        self.__deconvolute()
        return results
    
    
    def __merge_subsequences( self, all: List[ LegoSubsequence ] ):
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
        for component in self.components:
            for line in component.lines:
                if len( line ) >= 2:
                    self.__merge_subsequences( line )
        
        self.__deconvolute()


_GREEK = NameHelper.load_name_list( NameHelper.EName.GREEK )


class LegoComponent:
    """
    Connected component
    """
    
    
    def __init__( self, index: int, subsequences: List[ LegoSubsequence ] ):
        sequences = set( x.sequence for x in subsequences )
        lines = [ ]
        self.tree = None
        self.index = index
        
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
        return "{}.{}".format( _GREEK[ self.index % len( _GREEK ) ].upper(), sum( len( x ) for x in self.lines ) )
    
    
    def to_fasta( self, simplify : bool = False ) -> str:
        """
        Converts the component to FASTA
        :param simplify: Turns on simplified mode to produce output for limited parsers: Names are replaced with short "S*" numbers, comments are removed, errors are raised on failure instead of appending comments to the file 
        :return: FASTA, as a string 
        """
        model = self.lines[ 0 ][ 0 ].sequence.model
        
        fasta = [ ]
        if not simplify:
            fasta.append( ";" )
            fasta.append( "; COMPONENT: " + str( self ) )
            fasta.append( ";" )
        
        num_sequence_components = defaultdict( list )
        
        for component_2 in model.components:
            for sequence in component_2.all_sequences():
                num_sequence_components[ sequence ].append( component_2 )
        
        composite_sequence = None
        
        for line in self.lines:
            sequence = line[ 0 ].sequence
            if len( num_sequence_components[ sequence ] ) != 1:
                if composite_sequence:
                    if simplify:
                        raise ValueError( "There are more than one composites in this component: At least '{}' and '{}'. Consider removing extraenuous sequences.".format( composite_sequence, sequence ) )
                
                composite_sequence = sequence
            
            start = min( x.start for x in line )
            end = max( x.end for x in line )
            array = sequence.sub_array( start, end )
            
            if simplify:
                fasta.append( ">S" + str( sequence.id ) )
            elif sequence is composite_sequence:
                fasta.append( ">{} [ {} : {} ] (COMPOSITE)".format( sequence.accession, start, end ) )
            else:
                fasta.append( ">{} [ {} : {} ]".format( sequence.accession, start, end ) )
            
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
        with LOG( "CREATING CONNECTED COMPONENT COLLECTION" ):
            the_list = [ ]
            
            for s in model.sequences:  # type: LegoSequence
                for ss in s.subsequences:
                    cls.__connect_components( ss, the_list )
            
            results = [ ]  # type:List[LegoComponent]
            
            for x in the_list:
                y = LegoComponent( len( results ), x )
                
                if len( y.lines ) > 1:
                    results.append( y )
            
            return results
    
    
    @classmethod
    def __connect_components( cls, subsequence: LegoSubsequence, set_list: List[ Set[ LegoSubsequence ] ] ):
        for set_ in set_list:
            if subsequence in set_:
                return
        
        set_ = set()
        set_list.append( set_ )
        cls.__connect_to( subsequence, set_ )
    
    
    @classmethod
    def __connect_to( cls, subsequence: LegoSubsequence, target: set ):
        if subsequence in target:
            return  # Already visited
        
        subsequence._verify_deconvoluted()
        
        target.add( subsequence )
        
        for edge in subsequence.edges:
            for friend in edge.source + edge.destination:
                cls.__connect_to( friend, target )
