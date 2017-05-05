from typing import List, Optional, Tuple


class LegoEdge:
    def __init__( self, source: "List[LegoSubsequence]", destination: "List[LegoSubsequence]" ):
        assert all( x not in destination for x in source ), "{0} / {1}".format( self.source, self.destination )
        assert all( x not in source for x in destination ), "{0} / {1}".format( self.source, self.destination )
        
        self.source = source  # type:List[LegoSubsequence]
        self.destination = destination  # type:List[LegoSubsequence]
    
    
    @property
    def source_sequence( self ):
        return self.source[ 0 ].sequence
    
    
    @property
    def destination_sequence( self ):
        return self.destination[ 0 ].sequence
    
    
    @property
    def source_start( self ):
        return min( x.start for x in self.source )
    
    
    @property
    def source_end( self ):
        return max( x.end for x in self.source )
    
    
    @property
    def destination_start( self ):
        return min( x.start for x in self.destination )
    
    
    @property
    def destination_end( self ):
        return max( x.end for x in self.destination )
    
    
    def __repr__( self ):
        return "{}[{}:{}] --> {}[{}:{}]".format( self.source_sequence, self.source_start, self.source_end, self.destination_sequence, self.destination_start, self.destination_end )
    
    
    def opposite( self, subsequence ):
        if subsequence in self.source:
            return self.destination
        
        if subsequence in self.destination:
            return self.source
        
        raise KeyError( "Not found: '{0}'".format( subsequence ) )
    
    
    def complete( self ):
        self.source = sorted( self.source, key = lambda x: x.start )
        self.destination = sorted( self.destination, key = lambda x: x.start )
        
        assert all( x not in self.destination for x in self.source )
        assert all( x not in self.source for x in self.destination )
        assert all( self.source[ 0 ].sequence is not x.sequence for x in self.destination )
        assert all( self.destination[ 0 ].sequence is not x.sequence for x in self.source )
        assert all( self.source[ 0 ].sequence is x.sequence for x in self.source )
        assert all( self.destination[ 0 ].sequence is x.sequence for x in self.destination )
    
    
    def inherit( self, original, replacement ):
        if original in self.source:
            if replacement not in self.source:
                self.source.append( replacement )
        elif original in self.destination:
            if replacement not in self.destination:
                self.destination.append( replacement )
        else:
            raise KeyError( "Edge cannot inherit because the edge never owned this." )
    
    
    def remove( self, item ):
        if item in self.source:
            self.source.remove( item )
        elif item in self.destination:
            self.destination.remove( item )
        else:
            raise KeyError( "Edge cannot remove because the edge never owned this." )
        
        assert item not in self.source, "{0}: {1}".format( item, self.source )
        assert item not in self.destination, "{0}: {1}".format( item, self.destination )


class LegoSubsequence:
    """
    Portion of a sequence
    """
    
    
    def __init__( self, sequence: "LegoSequence", start: int, end: int ):
        assert start >= 1
        assert end >= 1
        assert start <= end
        self.sequence = sequence  # Sequence itself
        self.start = start  # Start position
        self.end = end  # End position
        self.edges = [ ]  # type:List[LegoEdge]        # Edge list
        
        self.ui_position = None
        self.ui_colour = None
        
        print( "-- NEW {}".format( self ) )
        
    @property
    def index(self):
        return self.sequence.subsequences.index(self)
    
    @property
    def array( self ):
        return self.sequence.array[ self.start:self.end + 1 ]
    
    
    @property
    def length( self ):
        return self.end - self.start + 1
    
    
    def add_edge( self, edge: "LegoEdge" ):
        if edge not in self.edges:
            self.edges.append( edge )
    
    
    def destroy( self ):
        for edge in self.edges:
            edge.remove( self )
        
        self.edges = None
    
    
    def __repr__( self ):
        return "{0}[{1}:{2}]".format( self.sequence.accession, self.start, self.end )
    
    
    def inherit( self, original: "LegoSubsequence" ):
        assert original != self
        
        for edge in original.edges:
            edge.inherit( original, self )
            self.add_edge( edge )
    
    
    def quantise( self, level ):
        hlevel = (level // 2)
        
        start = self.start + hlevel
        start = max( start - start % level, 1 )
        
        end = self.end + hlevel
        end = max( end - end % level - 1, 1 )
        
        self.start = start
        self.end = end


    def _split( self, p : int ):
        """
        Splits the subsequence into s..p-1 and p..e

               |p        
        1 2 3 4|5 6 7 8 9
        """
        
        if p <= self.start or p > self.end:
            raise ValueError("Cannot split a subsequence from {0} to {1} about a point {2}".format(self.start,self.end, p))
        
        left = self.sequence.make_subsequence(self.start, p-1)
        right = self.sequence.make_subsequence(p,self.end)
        
        left.inherit(self)
        right.inherit(self)
        
        self.sequence.subsequences.remove(self)
        self.destroy()
        


class LegoSequence:
    """
    Protein sequence
    """
    
    
    def __init__( self, model: "LegoModel", accession: str ):
        self.accession = accession  # Database accession (ID)
        self.subsequences = [ ]  # type: List[LegoSubsequence]         
        self.length = 1  # Sequence length
        self.model = model
        self.array = None
        self.meta = { }
        
    @property
    def index(self):
        return self.model.sequences.index(self)
    
    
    def __repr__( self ):
        return self.accession
    
    
    def make_subsequence( self, start, end ) -> Optional[ LegoSubsequence ]:
        assert start <= end, "{0} {1}".format( start, end )
        
        print( "NEW SS {} {}".format( start, end ) )
        
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
                print( "PADDING WITH NEW {} {}".format( prev_end, v.start ) )
                to_add.append( LegoSubsequence( self, prev_end, v.start ) )
            
            prev_end = v.end + 1
        
        if self.length + 1 != prev_end:
            print( "PADDING WITH FINAL {} {}".format( prev_end, self.length ) )
            to_add.append( LegoSubsequence( self, prev_end, self.length ) )
        
        self.subsequences.extend( to_add )
        self.subsequences = sorted( self.subsequences, key = lambda x: x.start )
        
        if self.array is None:
            self.array = "X" * self.length
    
    
    def deconvolute( self ):
        while self.__deoverlap_subsequence():
            pass
    
    
    def __deoverlap_subsequence( self ):
        for a in self.subsequences:
            for b in self.subsequences:
                if a is b:
                    continue
                
                if not (b.start <= a.end and b.end >= a.start):
                    continue
                
                print( "{} overlaps {}".format( a, b ) )
                
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
                    print( "CREATE L {} {}".format( pos_1, pos_2 - 1 ) )
                    new_1 = self.make_subsequence( pos_1, pos_2 - 1 )
                    new_1.inherit( own_1 )
                
                print( "CREATE M {} {}".format( pos_2, pos_3 ) )
                new_2 = self.make_subsequence( pos_2, pos_3 )
                new_2.inherit( a )
                new_2.inherit( b )
                
                if pos_3 != pos_4:
                    print( "CREATE R {} {}".format( pos_3 + 1, pos_4 ) )
                    new_3 = self.make_subsequence( pos_3 + 1, pos_4 )
                    new_3.inherit( own_3 )
                
                print( "DESTROY F {}".format( a ) )
                print( "DESTROY S {}".format( b ) )
                a.destroy()
                b.destroy()
                
                return True
        return False
    
    
    def find( self, start:int, end:int ):
        for x in self.subsequences:
            if x.start == start and x.end == end:
                return x
        
        raise KeyError( "No such subsequence as {0}-{1}".format( start, end ) )
    
    
    def _quantise( self, level:int ):
        for x in self.subsequences:
            x.quantise( level )


    def _split( self, split_point :int ):
        for ss in self.subsequences:
            if ss.start <= split_point <= ss.end:
                ss._split(split_point)
                
        self.deconvolute()


    def _remove_subsequence( self, subsequence:LegoSubsequence ):
        subsequence.destroy()
        self.subsequences.remove(subsequence)
        


class LegoModel:
    """
    Model (collection of sequences)
    """
    
    
    def __init__( self ):
        self.sequences = []  # type: List[LegoSequence]
        self.edges = [ ]  # type:List[LegoEdge]
    
    
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
            self.sequences.append(result)
        
        return result
    
    
    def clear( self ):
        self.sequences.clear()
    
    
    def __deconvolute( self ):
        for x in self.sequences:
            x.deconvolute()
        
        for x in self.sequences:
            x.__complete_subsequences()
        
        for x in self.edges:
            x.complete()
            
        self.sequences = sorted( self.sequences, key = lambda x: x.accession )
        
    def __lookup_table(self):
        return dict((x.accession,x) for x in self.sequences)
    
    
    def read_fasta( self, file_name: str ):
        from Bio import SeqIO
        
        obtain_only = self.__has_data()
        lookup_table = self.__lookup_table()
        
        for record in SeqIO.parse( file_name, "fasta" ):
            sequence = self.__make_sequence( lookup_table, str( record.id ), obtain_only )
            
            if sequence:
                sequence.array = str( record.seq )
                sequence.length = len( record.seq )
        
        self.__deconvolute()
    
    
    def __has_data( self ):
        return bool( self.sequences )
    
    
    def quantise( self, level ):
        for sequence in self.sequences:
            # noinspection PyProtectedMember
            sequence._quantise( level )
        
        self.__deconvolute()
    
    
    def import_blast( self, file_name: str ):
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
                    
                    if query_s and subject_s:
                        query = query_s.make_subsequence( int( e[ 6 ] ), int( e[ 7 ] ) ) if query_s else None
                        subject = subject_s.make_subsequence( int( e[ 8 ] ), int( e[ 9 ] ) ) if subject_s else None
                        self.__make_edge( query, subject )
        
        self.__deconvolute()
    
    
    def import_composites( self, file_name: str ):
        COMPOSITE = 1
        FASTA = 2
        NONE = 3
        
        reading = NONE
        seq_len = ""
        comp_name = None
        
        lookup_table = self.__lookup_table()
        
        with open( file_name, "r" ) as file:
            for line in file.readlines():
                if line.startswith( ">" ):
                    if reading == FASTA:
                        # Composite begins
                        reading = COMPOSITE
                        comp_name = line[ 1: ]
                    elif reading == NONE:
                        # FASTA begins
                        seq_len = ""
                        reading = FASTA
                    elif reading == COMPOSITE:
                        break
                elif len( line ) != 0:
                    if reading == COMPOSITE:
                        if line.startswith( "F" ):
                            # Fields: F<comp family id> <mean align> <mean align> <no sequences as component> <no sequences in family> <mean pident> <mean length>
                            
                            e = line.split( "\t" )
                            
                            fam_name = e[ 0 ]
                            mean_start = int( e[ 1 ] )
                            mean_end = int( e[ 2 ] )
                            # num_seq_as_component = int(e[3])
                            # num_seq_in_family = int(e[3])
                            # mean_pident = float(e[4])
                            mean_length = int( float( e[ 5 ] ) )
                            
                            if (mean_end - mean_start) < 30:
                                continue
                            
                            composite = self.__make_sequence( lookup_table, comp_name, False )
                            composite.array = seq_len
                            ss = composite.make_subsequence( mean_start, mean_end )
                            target = self.__make_sequence( lookup_table, fam_name, False )
                            target.length = mean_length
                            ssb = target.make_subsequence( 1, target.length )
                            assert ss is not ssb
                            self.__make_edge( ss, ssb )
                    else:
                        seq_len += line.strip()
        
        self.__deconvolute()
    
    
    def __make_edge( self, source: LegoSubsequence, destination: LegoSubsequence ):
        assert source != destination
        source = [ source ]
        destination = [ destination ]
        
        for edge in self.edges:
            if (edge.source == source and edge.destination == destination) or (edge.destination == source and edge.source == destination):
                return edge
        
        result = LegoEdge( source, destination )
        self.edges.append( result )
        source[ 0 ].add_edge( result )
        destination[ 0 ].add_edge( result )
        return result


    def add_new_sequence( self )->LegoSequence:
        sequence = LegoSequence(self, "Untitled")
        self.sequences.append(sequence)
        return sequence


    def add_new_edge( self, ss:List[LegoSubsequence] )->LegoEdge:
        sequences = list(set(x.sequence for x in ss))
        
        if len(sequences) !=2:
            raise ValueError("Need two sequences to create an edge, but {0} have been specified: {1}".format(len(ss),ss))
        
        left_sequence = sequences[0]
        right_sequence = sequences[0]
        
        left_subsequences = [x for x in ss if x.sequence is left_sequence]
        right_subsequences =[x for x in ss if x.sequence is right_sequence]
        
        edge = LegoEdge(left_subsequences, right_subsequences)
        
        for x in left_subsequences:
            x.add_edge(edge)
            
        for x in right_subsequences:
            x.add_edge(edge)
            
        return edge


    def add_new_subsequence( self, sequence:LegoSequence, split_point:int )->None:
        sequence._split(split_point)


    def remove_sequence( self, x :LegoSequence):
        for ss in x.subsequences:
            x._remove_subsequence(ss)
        
        self.sequences.remove(x)
