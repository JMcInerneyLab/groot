from typing import Iterable, List, Optional

from ExceptionHelper import SwitchError
from MHelper import StringHelper


class LegoQueuedFile:
    BLAST = "Blast"
    COMPOSITES = "Composites"
    FASTA = "Fasta"
    
    
    def __init__( self, filename, filetype ):
        self.filename = filename
        self.filetype = filetype
        
        
class LegoEdge:
    def __init__(self, source:"List[LegoSubsequence]", destination:"List[LegoSubsequence]"):
        assert all(x not in destination for x in source) , "{0} / {1}".format(self.source, self.destination)
        assert all(x not in source for x in destination)  , "{0} / {1}".format(self.source, self.destination)
        
        self.source=source        #type:List[LegoSubsequence]
        self.destination=destination#type:List[LegoSubsequence]
        
    @property
    def source_sequence(self):
        return self.source[0].sequence
    
    @property
    def destination_sequence(self):
        return self.destination[0].sequence
        
    @property
    def source_start(self):
        return min(x.start for x in self.source)
    
    @property
    def source_end(self):
        return max(x.end for x in self.source)
    
    @property
    def destination_start(self):
        return min(x.start for x in self.destination)
    
    @property
    def destination_end(self):
        return max(x.end for x in self.destination)
        
    def __repr__(self):
        return "{}[{}:{}] --> {}[{}:{}]".format(self.source_sequence, self.source_start, self.source_end, self.destination_sequence, self.destination_start, self.destination_end)
        
    
    def opposite(self, subsequence):
        if subsequence in self.source:
            return self.destination
    
        if subsequence in self.destination:
            return self.source
        
        raise KeyError("Not found: '{0}'".format(subsequence))
    
        
    def complete(self):
        self.source = sorted( self.source, key = lambda x: x.start )
        self.destination = sorted( self.destination, key = lambda x: x.start )
        
        assert all(x not in self.destination for x in self.source)
        assert all(x not in self.source for x in self.destination)
        assert all(self.source[0].sequence is not x.sequence for x in self.destination)
        assert all(self.destination[0].sequence is not x.sequence for x in self.source)
        assert all(self.source[0].sequence is x.sequence for x in self.source)
        assert all(self.destination[0].sequence is x.sequence for x in self.destination)


    def inherit( self, original, replacement ):
        if original in self.source:
            if replacement not in self.source:
                self.source.append( replacement )
        elif original in self.destination:
            if replacement not in self.destination:
                self.destination.append( replacement )
        else:
            raise KeyError("Edge cannot inherit because the edge never owned this.")
        
    def remove(self, item):
        if item in self.source:
            self.source.remove( item )
        elif item in self.destination:
            self.destination.remove( item )
        else:
            raise KeyError("Edge cannot remove because the edge never owned this.")
        
        assert item not in self.source , "{0}: {1}".format( item, self.source )
        assert item not in self.destination , "{0}: {1}".format( item, self.destination )


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
        
        print("-- NEW {}".format(self))
        
    @property
    def array(self):
        return self.sequence.array[self.start:self.end+1]
    
    
    @property
    def length( self ):
        return self.end - self.start + 1
    
    
    def add_edge( self, edge: "LegoEdge" ):
        if edge not in self.edges:
            self.edges.append( edge )
    
    
    def destroy( self ):
        for edge in self.edges:
            edge.remove(self)
        
        self.edges = None
    
    
    def __repr__(self):
        return "{0}[{1}:{2}]".format( self.sequence.accession, self.start, self.end )


    def inherit( self, original :"LegoSubsequence"):
        assert original != self
        
        for edge in original.edges:
            edge.inherit(original, self)
            self.add_edge(edge)


class LegoSequence:
    """
    Protein sequence
    """
    
    
    def __init__( self, model:"LegoModel", accession: str ):
        self.accession = accession  # Database accession (ID)
        self.subsequences = [ ]  # type: List[LegoSubsequence]         
        self.length = 1  # Sequence length
        self.model=model
        self.array = None
        self.meta = {}
        
    def __repr__(self):
        return self.accession
    
    
    def make_subsequence( self, start, end, obtain_only, quantise ) -> Optional[LegoSubsequence]:
        assert start <= end , "{0} {1}".format(start,end)
        if quantise and False:
            start = start + 10
            start = max(start - start % 20,1)
            
            end= end+ 10
            end= max(end-end% 20-1,1)
            
        if obtain_only:
            return None
        
        print ("NEW SS {} {}".format(start, end))
        
        result = LegoSubsequence( self, start, end )
        self.subsequences.append( result )
        
        self.length = max( self.length, result.end )
        
        return result
    
    
    def complete_subsequences( self ):
        self.subsequences = list( sorted( self.subsequences, key = lambda x: x.start ) )
        to_add = [ ]
        
        prev_end = 1
        
        for i, v in enumerate( self.subsequences ):
            assert isinstance( v, LegoSubsequence )
            
            if v.start != prev_end:
                # Insert new!
                print("PADDING WITH NEW {} {}".format(prev_end, v.start))
                to_add.append( LegoSubsequence( self, prev_end, v.start ) )
            
            prev_end = v.end + 1
        
        if self.length + 1 != prev_end:
            print("PADDING WITH FINAL {} {}".format(prev_end, self.length))
            to_add.append( LegoSubsequence( self, prev_end, self.length ) )
        
        self.subsequences.extend( to_add )
        self.subsequences = sorted( self.subsequences, key = lambda x: x.start )
        
        if self.array is None:
            self.array="X"*self.length
    
    
    def deoverlap_subsequences( self ):
        while self.__deoverlap_subsequence():
            pass
    
    
    def __deoverlap_subsequence( self ):
        for a in self.subsequences:
            for b in self.subsequences:
                if a is b:
                    continue
                
                if not (b.start <= a.end and b.end >= a.start):
                    continue
                    
                print ("{} overlaps {}".format(a,b))
                
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
                    print ("CREATE L {} {}".format(pos_1, pos_2-1))
                    new_1 = self.make_subsequence( pos_1, pos_2-1, False, False )
                    new_1.inherit( own_1 )
                
                print ("CREATE M {} {}".format(pos_2, pos_3))
                new_2 = self.make_subsequence( pos_2, pos_3, False , False)
                new_2.inherit( a )
                new_2.inherit( b )
                
                if pos_3!=pos_4:
                    print ("CREATE R {} {}".format(pos_3+1, pos_4))
                    new_3 = self.make_subsequence( pos_3+1, pos_4, False, False )
                    new_3.inherit( own_3 )
                
                
                
                print ("DESTROY F {}".format(a))
                print ("DESTROY S {}".format(b))
                a.destroy()
                b.destroy()
                
                return True
        return False
    
    
    def find( self, start, end ):
        for x in self.subsequences:
            if x.start == start and x.end == end:
                return x
        
        raise KeyError( "No such subsequence as {0}-{1}".format( start, end ) )


class LegoModel:
    """
    Model (collection of sequences)
    """
    
    
    def __init__( self ):
        self.__sequences = { }  # type: Dict[str, LegoSequence]  # Sequences (by accession)
        self.edges = [] #type:List[LegoEdge]
    
    
    @property
    def sequences( self ) -> List[ LegoSequence ]:
        return sorted( self.__sequences.values(), key = lambda x: x.accession)
    
    
    def make_sequence( self, accession: str, obtain_only ) -> LegoSequence:
        if "|" in accession:
            accession = accession.split( "|" )[ 3 ]
        
        if "." in accession:
            accession = accession.split( ".", 1 )[ 0 ]
            
        accession=accession.strip()
            
        
        result = self.__sequences.get( accession )
        
        if result is None and not obtain_only:
            result = LegoSequence( self, accession )
            self.__sequences[ accession ] = result
        
        return result
    
    
    def clear( self ):
        self.__sequences.clear()
    
    
    def dump( self ):
        for seq in self.__sequences.values():
            seq.dump()
    
    
    def deoverlap( self ):
        for x in self.sequences:
            x.deoverlap_subsequences()
        
        for x in self.sequences:
            x.complete_subsequences()
            
        for x in self.edges:
            x.complete()
        
    
    
    def read_file( self, file: LegoQueuedFile ):
        if file.filetype == LegoQueuedFile.BLAST:
            self.read_blast( file.filename )
        elif file.filetype == LegoQueuedFile.COMPOSITES:
            self.read_composites( file.filename )
        elif file.filetype == LegoQueuedFile.FASTA:
            self.read_fasta( file.filename )
        else:
            raise SwitchError( "file.filetype", file.filetype )
    
    
    def read_fasta( self, file_name: str ):
        from Bio import SeqIO
        
        obtain_only = self.has_data()
        
        for record in SeqIO.parse( file_name, "fasta" ):
            sequence = self.make_sequence( str( record.id ), obtain_only )
            
            if sequence:
                sequence.data = str( record.seq )
                sequence.length = len( record.seq )
                
    def has_data(self):
        return len(self.__sequences)!=0
    
    
    def read_blast( self, file_name: str ):
        obtain_only = self.has_data()
        
        with open( file_name, "r" ) as file:
            for line in file.readlines():
                line = line.strip()
                
                if line and not line.startswith( "#" ):
                    # Fields: query acc., subject acc., % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
                    e = line.split( "\t" )
                    
                    query_s = self.make_sequence( e[ 0 ], obtain_only )
                    query = query_s.make_subsequence( int( e[ 6 ] ), int( e[ 7 ] ), obtain_only, True )   if query_s else None
                    subject_s = self.make_sequence( e[ 1 ], obtain_only )
                    subject = subject_s.make_subsequence( int( e[ 8 ] ), int( e[ 9 ] ), obtain_only, True ) if subject_s else None
                    self.make_edge(query,subject)
    
    
    def read_composites( self, file_name: str ):
        COMPOSITE = 1
        FASTA = 2
        NONE = 3
        
        reading = NONE
        seq_len = ""
        comp_name = None
        
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
                        return
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
                            
                            composite = self.make_sequence( comp_name,False )
                            composite.array = seq_len
                            ss = composite.make_subsequence( mean_start, mean_end,False , True)
                            target = self.make_sequence( fam_name,False )
                            target.length = mean_length
                            ssb = target.make_subsequence( 1, target.length,False, True )
                            assert ss is not ssb
                            self.make_edge( ss, ssb )
                    else:
                        seq_len +=  line.strip()
    
    
    def find( self, text ) -> LegoSequence:
        return self.__sequences.get( text )


    def make_edge( self, source:LegoSubsequence, destination:LegoSubsequence):
        assert source!=destination
        source = [source]
        destination =[destination]
        
        for edge in self.edges:
            if (edge.source==source and edge.destination==destination) or (edge.destination == source and edge.source == destination):
                return edge
        
        result=LegoEdge(source, destination)
        self.edges.append(result)
        source[0].add_edge(result)
        destination[0].add_edge(result)
        return result


    
