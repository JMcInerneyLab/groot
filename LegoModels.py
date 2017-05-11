from typing import List, Optional, Set

from DisposalHelper import ManagedWith
from MHelper.ExceptionHelper import ImplementationError
from MHelper import ArrayHelper


__incremental_id = 0


def _incremental_id():
    global __incremental_id
    __incremental_id += 1
    return __incremental_id


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
    
    
    def __contains__( self, item ):
        return item in self.source or item in self.destination
    
    def _verify_deconvoluted(self):
        assert self.source and self.destination
        self._verify()
    
    def _verify( self ):
        """
        Internally used to assert the integrity of the edge
        """
        if self.is_destroyed:
            raise ImplementationError("Edge '{}' has been destroyed.".format(self))
        
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
        
        for x in self.source+self.destination:
            if x.is_destroyed:
                raise ImplementationError("Edge '{}' contains a destroyed subsequence '{}'".format(self,x))
    
    
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
    
    
    def position( self, subsequence: "LegoSubsequence" ):
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
        print( "DECONVOLUTE {} BEGINS".format( self ) )
        self.source = sorted( self.source, key = lambda x: x.start )
        self.destination = sorted( self.destination, key = lambda x: x.start )
        self._verify()
        print( "DECONVOLUTE {} ENDS".format( self ) )
    
    
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
    
    
    def link( self, position: bool, subsequence: "LegoSubsequence" ):
        """
        Forms the link between this edge and the specified subsequence.
        """
        the_list = self.destination if position else self.source
        
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
        assert start >= 1
        assert end >= 1
        
        if start > end:
            raise ValueError( "Attempt to create a subsequence in '{0}' where start ({1}) > end ({2}).".format( sequence, start, end ) )
        
        self.id = _incremental_id()
        self.sequence = sequence  # Sequence itself
        self.start = start  # Start position
        self.end = end  # End position
        self.edges = [ ]  # type:List[LegoEdge]        # Edge list
        
        self.ui_position = None
        self.ui_colour = None
        self.source_info = set()
        
        self.is_destroyed = False
        
        print( "SUBSEQUENCE '{}' INITIALISED".format( self ) )
        
    def _verify_deconvoluted(self):
        assert self.start <= self.end
        assert not self.is_destroyed
        
        for edge in self.edges:
            edge._verify()
            assert edge in self.sequence.model.all_edges
    
    
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
        return self.sequence.array[ self.start:self.end + 1 ]
    
    
    @property
    def length( self ):
        """
        Calculates the length of this subsequence
        """
        return self.end - self.start + 1
    
    
    def destroy( self ):
        for edge in list( self.edges ):
            edge.unlink( self )
        
        assert len( self.edges ) == 0, self.edges
        self.is_destroyed = True
    
    
    def __repr__( self ):
        if self.is_destroyed:
            return "DELETED_SUBSEQUENCE"
        
        return "{} [ {} : {} ]".format( self.sequence.accession, self.start, self.end )
    
    
    def inherit( self, original: "LegoSubsequence" ):
        assert original != self
        
        print( "{} INHERITS {}".format( self, original ) )
        
        for edge in original.edges:
            edge.link( edge.position( original ), self )
    
    
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
        
        if p <= self.start or p > self.end:
            raise ValueError( "Cannot split a subsequence from {0} to {1} about a point {2}".format( self.start, self.end, p ) )
        
        left = self.sequence._make_subsequence( self.start, p - 1 )
        right = self.sequence._make_subsequence( p, self.end )
        
        left.inherit( self )
        right.inherit( self )
        
        self.sequence.subsequences.remove( self )
        self.destroy()


class LegoSequence:
    """
    Protein (or DNA) sequence
    """
    
    
    def __init__( self, model: "LegoModel", accession: str ):
        self.id = _incremental_id()
        self.accession = accession  # Database accession (ID)
        self.subsequences = [ ]  # type: List[LegoSubsequence]         
        self.length = 1  # Sequence length
        self.model = model
        self.array = None
        self.source_info = set()
        
    def _verify_deconvoluted(self):
        if self.subsequences[0].start!=1:
            raise ImplementationError("The first subsequence '{}' in sequence '{}' is not at the start.".format(self.subsequences[0],self))

        if self.subsequences[-1].end!=self.length:
            raise ImplementationError("The last subsequence '{}' in sequence '{}' is not at the end.".format(self.subsequences[0],self))
        
        for left, right in ArrayHelper.lagged_iterate( self.subsequences):
            if left.end != right.start - 1:
                raise ImplementationError("Subsequences '{}' and '{}' in sequence '{}' are not adjancent.".format(left,right,self))
            
        for x in self.subsequences:
            x._verify_deconvoluted()
    
    
    @property
    def index( self ):
        return self.model.sequences.index( self )
    
    
    def __repr__( self ):
        return "{}".format( self.accession )
    
    
    def _make_subsequence( self, start, end ) -> Optional[ LegoSubsequence ]:
        if start > end:
            raise ValueError( "Cannot make a subsequence in '{0}' which has a start ({1}) > end ({2}).".format( self, start, end ) )
        
        print( "MAKING SUBSEQUENCE {}:{}".format( start, end ) )
        
        result = LegoSubsequence( self, start, end )
        self.subsequences.append( result )
        
        self.length = max( self.length, result.end )
        
        return result
    
    
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
        
        if self.array is None:
            self.array = "?" * self.length
    
    
    def _deconvolute( self ):
        print( "DECONVOLUTION {} BEGINS".format( self ) )
        while self.__deoverlap_subsequence():
            pass
        
        self.__complete_subsequences()
        print( "DECONVOLUTION {} ENDS".format( self ) )
    
    
    def __deoverlap_subsequence( self ):
        for a in self.subsequences:
            for b in self.subsequences:
                if a is b:
                    continue
                
                if not (b.start <= a.end and b.end >= a.start):
                    continue
                
                print( "DEOVERLAPPING {} AND {}".format( a, b ) )
                
                # They overlap
                if a.start < b.start:
                    pos_1 = a.start
                    pos_2 = b.start
                    own_1 = a
                else:
                    pos_1 = b.start
                    pos_2 = a.start
                    own_1 = b
                
                if a.end < b.end:
                    pos_3 = a.end
                    pos_4 = b.end
                    own_3 = b
                else:
                    pos_3 = b.end
                    pos_4 = a.end
                    own_3 = a
                
                self.subsequences.remove( a )
                self.subsequences.remove( b )
                
                if pos_1 != pos_2:
                    print( "DEOVERLAPPING LEFT TO {}:{}".format( pos_1, pos_2 - 1 ) )
                    new_1 = self._make_subsequence( pos_1, pos_2 - 1 )
                    new_1.inherit( own_1 )
                
                print( "DEOVERLAPPING CENTRE TO  {}:{}".format( pos_2, pos_3 ) )
                new_2 = self._make_subsequence( pos_2, pos_3 )
                new_2.inherit( a )
                new_2.inherit( b )
                
                if pos_3 != pos_4:
                    print( "DEOVERLAPPING RIGHT TO  {}:{}".format( pos_3 + 1, pos_4 ) )
                    new_3 = self._make_subsequence( pos_3 + 1, pos_4 )
                    new_3.inherit( own_3 )
                
                print( "DEOVERLAPPING DESTROYING OLD LEFT '{}'".format( a ) )
                print( "DEOVERLAPPING DESTROYING OLD RIGHT '{}'".format( b ) )
                a.destroy()
                b.destroy()
                
                return True
        return False
    
    
    def _find( self, start: int, end: int ):
        for x in self.subsequences:
            if x.start == start and x.end == end:
                return x
        
        raise KeyError( "No such subsequence as {0}-{1}".format( start, end ) )
    
    
    def _quantise( self, level: int ):
        for x in self.subsequences:
            x.quantise( level )
        
        self.length = max( x.end for x in self.subsequences )
    
    
    def _split( self, split_point: int ):
        for ss in self.subsequences:
            if ss.start <= split_point <= ss.end:
                ss._split( split_point )
        
        self._deconvolute()
    
    
    def _remove_subsequence( self, subsequence: LegoSubsequence ):
        subsequence.destroy()
        self.subsequences.remove( subsequence )


class LegoModel:
    """
    Model (collection of sequences)
    """
    
    
    def __init__( self ):
        self.sequences = [ ]  # type: List[LegoSequence]
        self.components = [ ]  # type:List[LegoComponent]
    
    
    def __make_sequence( self, lookup, accession: str, obtain_only ) -> LegoSequence:
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
        print( "IMPORT FASTA FROM '{}'".format( file_name ) )
        from Bio import SeqIO
        
        obtain_only = self.__has_data()
        num_updates = 0
        lookup_table = self.__lookup_table()
        idle = 0
        idlec = 10000
        
        for record in SeqIO.parse( file_name, "fasta" ):
            sequence = self.__make_sequence( lookup_table, str( record.id ), obtain_only )
            
            if sequence:
                print( "FASTA UPDATES {} WITH ARRAY OF LENGTH {}".format( sequence, len( record.seq ) ) )
                num_updates += 1
                sequence.array = str( record.seq )
                sequence.length = len( record.seq )
                idle = 0
            else:
                idle += 1
                
                if idle == idlec:
                    print( "THIS FASTA IS BORING..." )
                    idlec *= 2
                    idle = 0
        
        self.__deconvolute()
        return "{} sequences updated.".format( num_updates )
    
    
    def __has_data( self ):
        return bool( self.sequences )
    
    
    def quantise( self, level ):
        for sequence in self.sequences:
            # noinspection PyProtectedMember
            sequence._quantise( level )
        
        self.__deconvolute()
    
    
    def import_blast( self, file_name: str ):
        print( "IMPORT BLAST FROM '{}'".format( file_name ) )
        obtain_only = self.__has_data()
        
        lookup_table = self.__lookup_table()
        
        with open( file_name, "r" ) as file:
            for line in file.readlines():
                line = line.strip()
                
                if line and not line.startswith( "#" ):
                    # Fields: query acc., subject acc., % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
                    e = line.split( "\t" )
                    
                    query_s = self.__make_sequence( lookup_table, e[ 0 ], obtain_only )
                    subject_s = self.__make_sequence( lookup_table, e[ 1 ], obtain_only )
                    
                    if query_s and subject_s and query_s is not subject_s:
                        query = query_s._make_subsequence( int( e[ 6 ] ), int( e[ 7 ] ) ) if query_s else None
                        subject = subject_s._make_subsequence( int( e[ 8 ] ), int( e[ 9 ] ) ) if subject_s else None
                        print( "BLAST UPDATES AN EDGE THAT JOINS {} AND {}".format( query, subject ) )
                        edge = self.__make_edge( query, subject )
                        edge.source_info.add( line )
        
        self.__deconvolute()
    
    
    def import_composites( self, file_name: str ):
        print( "IMPORT COMPOSITES FROM '{}'".format( file_name ) )
        
        lookup_table = self.__lookup_table()
        
        fam_name = "?"
        fam_mean_length = None
        composite = None
        composite_subsequence = None
        
        with open( file_name, "r" ) as file:
            for line_number, line in enumerate( file ):
                line = line.strip()
                
                if line.startswith( ">" ):
                    if composite:
                        return
                        
                        # COMPOSITE!
                    comp_name = line[ 1: ]
                    composite = self.__make_sequence( lookup_table, comp_name, False )
                    composite.source_info.add( "FILE '{}' LINE {}".format( file_name, line_number ) )
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
                    
                    composite_subsequence = composite._make_subsequence( fam_mean_start, fam_mean_end )
                elif line:
                    # SEQUENCE
                    sequence = self.__make_sequence( lookup_table, line, False )
                    sequence.length = fam_mean_length
                    sequence.source_info.add( "Family '{}'".format( fam_name ) )
                    sequence.source_info.add( "Accession '{}'".format( line ) )
                    
                    subsequence = sequence._make_subsequence( 1, sequence.length )
                    assert composite_subsequence
                    self.__make_edge( composite_subsequence, subsequence )
        
        self.__deconvolute()
    
    
    def __make_edge( self, source: LegoSubsequence, destination: LegoSubsequence ) -> LegoEdge:
        assert source != destination
        
        for edge in self.all_edges:
            if source in edge and destination in edge:
                return edge
        
        result = LegoEdge()
        result.link( False, source )
        result.link( True, destination )
        return result
    
    
    def add_new_sequence( self ) -> LegoSequence:
        sequence = LegoSequence( self, "Untitled" )
        self.sequences.append( sequence )
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
        
        return edge
    
    
    def add_new_subsequence( self, sequence: LegoSequence, split_point: int ) -> None:
        sequence._split( split_point )
    
    
    def remove_sequence( self, x: LegoSequence ):
        for ss in x.subsequences:
            x._remove_subsequence( ss )
        
        self.sequences.remove( x )
    
    
    def remove_edge( self, edge: LegoEdge ):
        edge.unlink_all()
    
    
    def remove_subsequence( self, subsequence: LegoSubsequence ):
        subsequence.sequence.subsequences.remove( subsequence )
        subsequence.destroy()
        self.__deconvolute()
    
    
    def remove_all_edges( self ):
        for edge in self.all_edges:
            edge.unlink_all()
        
        for sequence in self.sequences:
            sequence.subsequences.clear()
        
        self.__deconvolute()
    
    
    def __merge_subsequences( self, all: List[ LegoSubsequence ] ):
        all = sorted(all, key=lambda x: x.start)
        
        if len(all)<=1:
            raise ValueError("Cannot merge a list '{}' of less than two elements.".format(all))
        
        for left, right in ArrayHelper.lagged_iterate(all):
            if left.sequence != right.sequence:
                raise ValueError( "merge_subsequences attempted but the subsequences '{}' and '{}' are not in the same sequence.".format( left, right ) )
            
            if right.start != left.end + 1:
                raise ValueError( "merge_subsequences attempted but the subsequences '{}' and '{}' are not adjacent.".format( left, right ) )
        
        first = all[0]
        first.end = all[-1].end
        
        for other in all[1:]:
            first.inherit( other )
            other.sequence.subsequences.remove( other )
            other.destroy()
    
    
    def compartmentalise( self ):
        for component in self.components:
            for line in component.lines:
                if len(line)>=2:
                    self.__merge_subsequences( line )
                
        self.__deconvolute()


class LegoComponent:
    """
    Connected component
    """
    
    
    def __init__( self, index: int, subsequences: List[ LegoSubsequence ] ):
        sequences = set( x.sequence for x in subsequences )
        self.lines = [ ]  # type:List[List[LegoSubsequence]]
        self.tree = None
        self.index = index
        
        for sequence in sequences:
            self.lines.append( [ subsequence for subsequence in subsequences if subsequence.sequence is sequence ] )
            
    def __repr__(self):
        return "{} ({} subsequences)".format(self.index, sum(len(x) for x in self.lines))
    
    
    def all_subsequences( self )->List[LegoSubsequence]:
        return [ x for y in self.lines for x in y ]
    
    def all_sequences(self)->List[LegoSequence]:
        return [x[0].sequence for x in self.lines]
    
    
    @classmethod
    def create( cls, model: LegoModel )->"List[LegoComponent]":
        print("CREATING CONNECTED COMPONENT COLLECTION")
        the_list = [ ]
        
        for s in model.sequences:  # type: LegoSequence
            for ss in s.subsequences:
                cls.__connect_components( ss, the_list )
        
        results = []  #type:List[LegoComponent]
        
        for x in the_list:
            y = LegoComponent( len(results), x )
            
            if len(y.lines) >1:
                results.append(y)
                
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
        
        target.add( subsequence )
        
        for edge in subsequence.edges:
            for friend in edge.source + edge.destination:
                cls.__connect_to( friend, target )
