from collections import defaultdict
from typing import List


class LegoSubsequence:
    def __init__( self, sequence: "LegoSequence", start: int, end: int ):
        self.sequence = sequence
        self.start = start
        self.end = end
        self.edges = [ ]# type:List[LegoSubsequence]

    @property
    def length( self ):
        return self.end - self.start

    def make_edge( self, target: "LegoSubsequence" ):
        if target not in self.edges:
            self.edges.append( target )

        if self not in target.edges:
            target.edges.append( self )

    def inherit( self, source: "LegoSubsequence" ):
        for edge in source.edges:
            self.make_edge(edge)
            edge.make_edge(self)

    def destroy(self):
        for edge in self.edges:
            edge.edges.remove(self)

        self.edges = None




class LegoSequence:
    def __init__( self, accession: str ):
        self.accession = accession
        self.subsequences = [ ]  # type: List[LegoSubsequence]
        self.length = 1

    def make_subsequence( self, start, end ) -> LegoSubsequence:
        for subsequence in self.subsequences:
            if subsequence.start == subsequence.start and subsequence.end == subsequence.end:
                return subsequence

        result = LegoSubsequence( self, start, end )
        self.subsequences.append( result )

        self.length = max(self.length, result.end)

        return result

    def deoverlap_subsequences( self ):
        while self.__deoverlap_subsequence( ):
            pass

    def __deoverlap_subsequence( self ):
        for a in self.subsequences:
            for b in self.subsequences:
                if a is b:
                    continue

                if not (b.start < a.end and b.end > a.start):
                    continue

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

                new_1 = self.make_subsequence( pos_1, pos_2 )
                new_2 = self.make_subsequence( pos_2, pos_3 )
                new_3 = self.make_subsequence( pos_3, pos_4 )

                new_1.inherit( own_1 )
                new_2.inherit( a )
                new_2.inherit( b )
                new_3.inherit( own_3 )

                a.destroy()
                b.destroy()

                return True
        return False


class LegoModel:
    def __init__( self ):
        self.sequences = { } #type: Dict[str, LegoSequence]

    def make_sequence( self, accession ):
        result = self.sequences.get( accession )

        if result is None:
            result = LegoSequence( accession )
            self.sequences[ accession ] = result

        return result

    def clear(self):
        self.sequences.clear()

    def read_fasta( self, file_name ):
        pass

    def read_blast( self, file_name ):
        with open( file_name, "r" ) as file:
            for line in file.readlines( ):
                # Fields: query acc., subject acc., % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
                e = line.split( "\t" )

                query = self.make_sequence( e[ 0 ] ).make_subsequence( int( e[ 6 ] ), int( e[ 7 ] ) )
                subject = self.make_sequence( e[ 1 ] ).make_subsequence( int( e[ 8 ] ), int( e[ 9 ] ) )
                query.make_edge( subject )

    def read_composites( self, file_name ):
        reading = False
        seq_len = 0
        comp_name = None

        with open( file_name, "r" ) as file:
            for line in file.readlines( ):
                if line.startswith( ">C" ):
                    # Composite begins
                    reading = True
                    comp_name = line[ 1: ]
                elif line.startswith( ">" ):
                    # FASTA begins
                    seq_len = 0
                elif len( line ) != 0:
                    if reading:
                        if line.startswith( "F" ):
                            # Fields: F<comp family id> <mean align> <mean align> <no sequences as component> <no sequences in family> <mean pident> <mean length>

                            e = line.split( "\t" )

                            target = self.make_sequence( comp_name ).make_subsequence( float( e[ 1 ] ),
                                                                                       float( e[ 2 ] ) )

                            # TODO: We actually need to join the target to the original sequence
                    else:
                        seq_len += len( line )
