"""
MVC architecture.

Classes that manage the data (model) behind the UI.
"""
from typing import Optional, List, Dict, Set, Tuple, Iterable

import numpy


def mprint( x ):
    pass


class IModel:
    def __init__( self ):
        self.dead = False


    def kill( self ):
        self.dead = True


class LegoBlast( IModel ):
    """
    BLAST result
    """


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


    def __repr__( self ):
        return "Blast"


class LegoCut:
    def __init__( self, sequence: "LegoSequence", positions: List[ int ] ):
        self.sequence = sequence
        self.positions = positions
        self.targets = [ ]
        self.merged_into = None
        self.minimum = 0
        self.maximum = 0
        self.centre = 0

        self.update( )


    def merge_into_cut( self, b: "LegoCut" ):
        assert not self.merged_into

        # Update our targets to point to the replacement
        for target in self.targets:
            target.replace_cut( self, b )

        # Our replacement gets our positions and targets
        b.positions += self.positions
        b.targets += self.targets
        b.update( )

        # We get removed from our sequence
        self.sequence.cuts.remove( self )
        self.merged_into = b


    def update( self ):
        if self.positions:
            self.centre = sum( self.positions ) / len( self.positions )
            self.minimum = min( self.positions )
            self.maximum = max( self.positions )  # todo: multiple enumerations


    def __repr__( self ):
        result = "C{0}".format( self.positions )
        if self.merged_into:
            result += "*MERGED*"

        return result


    def only( self ):
        assert self.minimum == self.maximum

        return self.minimum


class LegoTarget:
    """
    BLAST target
    """
    ___next_id = 1


    def __init__( self, sequence: "LegoSequence", start: LegoCut, end: LegoCut ):
        self.id = LegoTarget.___next_id
        LegoTarget.___next_id += 1

        self.sequence = sequence
        self.original_start = start.only( )
        self.original_end = end.only( )
        self.start_cut = start
        self.end_cut = end
        self.merged_into = None
        self.merges = [ ]

        self.edge_targets = [ ]  # type:List[LegoTarget]


    def start( self ) -> int:
        return self.start_cut.minimum


    def end( self ) -> int:
        return self.end_cut.maximum


    def length( self ) -> int:
        return self.end( ) - self.start( )


    def replace_cut( self, find: LegoCut, replace: LegoCut ):
        """
        Replaces the specified cut
        """
        if find == self.start_cut:
            self.start_cut = replace

        if find == self.end_cut:
            self.end_cut = replace


    def merged_set( self ):
        """
        The set of merged elements (including this one)
        """
        return self.merges + [ self ]


    def path_targets( self ) -> "Set[LegoTarget]":
        """
        Everything this is connected to through a series of edges
        """
        results = set( )
        self._path_targets( results )
        return results


    def _path_targets( self, results: set ):
        results.add( self )

        for x in self.edge_targets:
            if x not in results:
                x._path_targets( results )


    def merge_into( self, b: "LegoTarget" ):
        """
        Merges this into another target

        The targets pointing at this target are also updated
        """
        mprint( "MERGE_INTO {0} --> {1}".format( self, b ) )
        assert self.sequence == b.sequence
        assert not self.merged_into

        # All the other targets pointing to us need updating
        for x in self.edge_targets:
            mprint( "{0} now has an edge to {1} instead of {2}".format( x, b, self ) )
            x.edge_targets.remove( self )
            x.edge_targets.append( b )

        # Our replacement gets whatever queries we have
        mprint( "{0} now has new targets: {1}".format( b, self.edge_targets ) )
        b.edge_targets += self.edge_targets

        # Make sure b isn't now pointing at itself
        while b in b.edge_targets:
            mprint( "Note: {0} now references itself, fixing.".format( b ) )
            b.edge_targets.remove( b )

        # Our replacement gets to keep us as a record
        b.merges.append( self )

        # We get removed from our owner
        self.sequence.targets.remove( self )

        self.merged_into = b


    def __repr__( self ):

        result = "Target#{0}({1}-{2})".format( self.id, self.start( ), self.end( ) )

        if self.merged_into:
            result += "*MERGED*"

        return result


class LegoSequence:
    """
    Sequence
    """
    ___next_id = 1


    def __init__( self, model, accession ):
        self.model = model
        self.id = LegoSequence.___next_id
        LegoSequence.___next_id += 1
        self.accession = accession
        self.name = accession.split( "|" )[ -2 ]
        self.length = 0
        self.targets = [ ]  # List[LegoTarget]
        self.cuts = [ ]


    @staticmethod
    def quantise( value: int ) -> int:
        LEVEL = 25
        value += (LEVEL // 2)
        return value - (value % LEVEL)


    def get_target( self, start: int, end: int ) -> LegoTarget:
        # start = self.quantise( start )
        # end = self.quantise( end )

        start_cut = self.get_cut( start )
        end_cut = self.get_cut( end )

        result = None

        for target in self.targets:
            if target.start_cut == start_cut and target.end_cut == end_cut:
                # Already exists
                result = target

        if not result:
            result = LegoTarget( self, start_cut, end_cut )
            self.targets.append( result )

        if not result in start_cut.targets:
            start_cut.targets.append( result )

        if not result in end_cut.targets:
            end_cut.targets.append( result )

        return result


    def get_cut( self, position: int ):
        self.ensure_capacity( position )

        for cut in self.cuts:
            if cut.only( ) == position:
                return cut

        cut = LegoCut( self, [ position ] )
        self.cuts.append( cut )
        return cut


    def ensure_capacity( self, value: int ):
        self.length = max( self.length, value )


    def __repr__( self ):
        return "{0}".format( self.name )


    def simplify( self, min_separation: int ) -> bool:
        """
        1. Use HCA to combine similar cuts
        2. Combine identical targets
        """
        mprint( "*** SIMPLIFYING SEQUENCE {0}".format( self ) )

        while True:
            a, b, d = self.closest_cut( )

            if not a:
                break

            if d > min_separation:
                break

            c = LegoCut( self, [ ] )
            self.cuts.append( c )

            a.merge_into_cut( c )
            b.merge_into_cut( c )

            mprint( "Merge cuts with distance {0} < {1}: {2} and {3} --> {4}".format( round( d, 2 ), min_separation, a, b, c ) )

        # Cuts are combined, but now we probably have identical targets
        to_merge = [ ]

        i = 0
        while i < len( self.targets ):
            a = self.targets[ i ]
            matches = [ ]

            for j in range( i + 1, len( self.targets ) ):
                b = self.targets[ j ]
                if a.start_cut == b.start_cut and a.end_cut == b.end_cut:
                    matches.append( b )

            for match in matches:
                mprint( "Merge sequences: {0} --> {1}".format( a, b ) )
                match.merge_into( a )  # this modifies self.targets

            i += 1

        return bool( to_merge )


    def closest_cut( self ) -> Tuple[ Optional[ LegoCut ], Optional[ LegoCut ], int ]:

        closest = 9999999
        closest_a = None
        closest_b = None

        for i, a in enumerate( self.cuts ):
            for j in range( i + 1, len( self.cuts ) ):
                b = self.cuts[ j ]
                # if b.direction == a.direction:
                distance = abs( b.centre - a.centre )
                if distance < closest:
                    closest = distance
                    closest_a = a
                    closest_b = b

        return closest_a, closest_b, closest


class LegoEdge:
    """
    Connects two LegoTargets
    """


    def __init__( self, blast: LegoBlast, query: LegoTarget, subject: LegoTarget ):
        self.query = query
        self.subject = subject
        self.blast = blast


    def __iter__( self ):
        return (self.query, self.subject)


    def __repr__( self ):
        return "Edge"


class LegoGroup:
    def __init__( self, targets: List[ LegoTarget ] ):
        self.targets = targets


    def __iter__( self ):
        return self.targets.__iter__( )


    def matches( self, targets: List[ LegoTarget ] ):
        if len( targets ) != len( self.targets ):
            return False

        temp = set( self.targets )

        for x in targets:
            if not x in temp:
                return False

            temp.remove( x )

        if temp:
            return False

        return True


    def __repr__( self ):
        return "Group of " + str( len( self.targets ) )


class LegoModelOptions:
    def __init__( self ):
        self.file_name = None
        self.ignore_transitions = True
        self.combine_cuts = 25


class LegoList:
    def __init__( self, type ):
        self._contents = [ ]


    def replace( self, new_list ):
        for x in self._contents:
            x.kill( )

        self._contents.clear( )
        self._contents += new_list

    def __len__(self):
        return self._contents.__len__()


    def __iter__( self ):
        return self._contents.__iter__( )


class LegoModel:
    """
    The model
    """


    def __init__( self, options: LegoModelOptions ):
        self.file_name = None
        self.edges = LegoList( LegoEdge )
        self.blasts = LegoList( LegoBlast )
        self.sequences = LegoList( LegoSequence )
        self.groups = LegoList( Set[ LegoGroup ] )

        if options:
            self.update( options )


    def read_blasts( self, file_name ) -> List[ LegoBlast ]:
        blasts = [ ]

        with open( file_name, "r" ) as file:
            for line in file.readlines( ):
                result = LegoBlast( line )
                blasts.append( result )

        return blasts


    def update( self, options: LegoModelOptions ):
        # Blasts need updating?
        if self.file_name != options.file_name:
            self.blasts.replace( self.read_blasts( options.file_name ) )
            self.file_name = options.file_name

        # Convert BLAST to sequences
        sequences = { }  # type:Dict[str, LegoSequence]
        self.edges = [ ]

        for blast in self.blasts:
            if blast.query_accession == blast.subject_accession:
                # Ignore self references, they mess merging up
                continue
            query = self.create_target( sequences, blast.query_accession, blast.query_start, blast.query_end )
            subject = self.create_target( sequences, blast.subject_accession, blast.subject_start, blast.subject_end )

            if any( [ x.query == query and x.subject == subject for x in self.edges ] ):
                # Ignore duplicates
                mprint( "Warning: Ignoring duplicate" )
                continue

            if any( [ x.query == subject and x.subject == query for x in self.edges ] ):
                # Ignore reversals
                mprint( "Warning: Ignoring reverse" )
                continue

            edge = LegoEdge( blast, query, subject )
            self.edges.append( edge )
            mprint( "{0} subjects {1} ".format( query, subject ) )
            mprint( "{0} queries {1} ".format( subject, query ) )

            assert subject not in query.edge_targets
            assert query not in query.edge_targets
            query.edge_targets.append( subject )
            subject.edge_targets.append( query )

        self.sequences.replace( sequences.values( ) )

        # Compact our cuts
        for sequence in self.sequences:
            sequence.simplify( options.combine_cuts )

        # Create our groups
        groups = [ ]

        if options.ignore_transitions:
            visited = set( )  # type: Set[LegoTarget]

            for target in self.targets( ):
                if target not in visited:
                    this_group = target.path_targets( )
                    assert not any( (x in visited) for x in this_group )
                    visited.update( this_group )
                    groups.append( LegoGroup( this_group ) )
        else:
            for target in self.targets( ):
                this_group = target.edge_targets

                if not any( [ x.matches( this_group ) for x in groups ] ):
                    groups.append( LegoGroup( this_group ) )

        self.groups.replace( groups )

        # Find best permutation
        bestp = None
        bests = -999999

        for n in range(5000):
            p = numpy.random.permutation( self.sequences._contents )
            s = self.score_perm( p )
            print( "PERMUTATION {0} {1} = {2}".format( n, p, s ) )
            if s > bests:
                bests = s
                bestp = p

        self.sequences._contents = list( p )


    def score_perm( self, p: List[ LegoSequence ] ) -> float:
        score = 0

        for i in range( 1, len( p ) - 1 ):
            prev = p[ i - 1 ]  # type:LegoSequence
            current = p[ i ]  # type:LegoSequence
            next = p[ i + 1 ]  # type:LegoSequence

            for t in current.targets:  # type: LegoTarget
                for tt in t.edge_targets:
                    if tt in prev.targets:
                        score += 1

                    if tt in next.targets:
                        score += 1

        return score


    def targets( self ):
        for sequence in self.sequences:
            yield from sequence.targets


    def __iter__( self ):
        return self.sequences.__iter__( )


    def __repr__( self ):
        return "Model"


    def create_target( self, sequences: Dict[ str, LegoSequence ], accession: str, start: int, end: int ) -> LegoTarget:
        if accession in sequences:
            sequence = sequences[ accession ]
        else:
            sequence = LegoSequence( self, accession )
            sequences[ accession ] = sequence

        target = sequence.get_target( start, end )
        return target
