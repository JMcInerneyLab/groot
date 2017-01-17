from typing import Optional, List, Dict, Set

from PyQt5.QtCore import QRect
from PyQt5.QtGui import QColor

import Monkey


class BlastResult:
    def __init__( self, line ):
        # Fields: query acc., subject acc., % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
        e = line.split( "\t" )

        self.query_accession = e[ 0 ]
        self.subject_accession = e[ 1 ]
        self.percent_identity = float( e[ 2 ] )
        self.alignment_length = int( e[ 3 ] )
        self.mismatches = int( e[ 4 ] )
        self.gap_opens = int( e[ 5 ] )
        self.query_start = int( e[ 6 ] )
        self.query_end = int( e[ 7 ] )
        self.subject_start = int( e[ 8 ] )
        self.subject_end = int( e[ 9 ] )
        self.e_value = float( e[ 10 ] )
        self.bit_score = float( e[ 11 ] )


class Target:
    def __init__( self, sequence: "Sequence", start: int, end: int ):
        self.sequence = sequence
        self.start = start
        self.end = end
        self.length = end - start
        self.edges = [ ]
        self.incoming = [ ]


    def create_edge_to( self, b: "Target" ):
        # if b in self.all_edges( ):
        #     # Already exists
        #      return

        # if b in self.all_vias( ):
        #    # Already a pathway to
        #    return

        self.edges.append( b )
        b.incoming.append( self )


    def all_edges( self ) -> "List[ Target ]":
        return self.edges + self.incoming


    def all_vias( self ) -> "Set[Target]":
        results = set( )
        self._all_vias( results )
        return results


    def _all_vias( self, results: set ):
        results.add( self )

        for x in self.all_edges( ):
            if x not in results:
                x._all_vias( results )


    def __repr__( self ):
        return "Target #{0} ({1}-{2}={3})".format( self.sequence.id, self.start, self.end, self.length )


class Cut:
    def __init__( self, position: int ):
        self.position = position


class Sequence:
    ___next_id = 1


    def __init__( self, accession ):
        self.id = Sequence.___next_id
        Sequence.___next_id += 1
        self.accession = accession
        self.name = accession.split( "|" )[ -2 ]
        self.length = 0
        self.targets = [ ]  # List[Target]
        self.cuts = [ ]


    @staticmethod
    def quantise( value: int ) -> int:
        LEVEL = 1
        value += (LEVEL // 2)
        return value - (value % LEVEL)


    def get_target( self, start: int, end: int ) -> Target:
        start = self.quantise( start )
        end = self.quantise( end )

        self.ensure_capacity( start )
        self.ensure_capacity( end )

        for target in self.targets:
            if target.start == start and target.end == end:
                # Already exists
                return target

        result = Target( self, start, end )
        self.targets.append( result )
        return result


    def ensure_capacity( self, value: int ):
        self.length = max( self.length, value )


    def add_cut( self, position: int ):
        if not position in [ x.position for x in self.cuts ]:
            self.cuts.append( Cut( position ) )


    def sort( self ):
        for target in self.targets:
            self.add_cut( target.start )
            self.add_cut( target.end )

        self.cuts = list( sorted( self.cuts, key = lambda x: x.position ) )


    def __repr__( self ):
        return "Sequence # (length {1})".format( self.id, self.length )


class SequenceMananager:
    def __init__( self, blasts: List[ BlastResult ] ):


        # Convert BLAST to sequences
        sequences = { }  # type:Dict[str, Sequence]

        for blast in blasts:
            # Ignore self-references
            if blast.query_accession == blast.subject_accession:
                continue

            query = self.create_target( sequences, blast.query_accession, blast.query_start, blast.query_end )
            subject = self.create_target( sequences, blast.subject_accession, blast.subject_start, blast.subject_end )

            query.create_edge_to( subject )

        # Create our "target sets"
        visited = set( )
        self.groups = [ ]  # List[Set[Target]]

        for seq in sequences.values( ):
            for tar in seq.targets:
                if tar not in visited:
                    this_group = tar.all_vias( )
                    assert not any( (x in visited) for x in this_group )
                    self.groups.append( this_group )

        for sequence in sequences.values( ):
            sequence.sort( )

        self.sequences = list( sorted( sequences.values( ), key = lambda x: x.length ) )


    def __iter__( self ):
        return self.sequences.__iter__( )


    @staticmethod
    def create_target( sequences: Dict[ str, Sequence ], accession: str, start: int, end: int ) -> Target:
        if accession in sequences:
            sequence = sequences[ accession ]
        else:
            sequence = Sequence( accession )
            sequences[ accession ] = sequence

        return sequence.get_target( start, end )
