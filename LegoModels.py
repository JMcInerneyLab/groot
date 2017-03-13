"""
MVC architecture.

Classes that manage the data (model) behind the UI.
"""
from itertools import permutations
from typing import Optional, List, Dict, Set, Tuple, Iterable

import numpy


def mprint( x ):
    pass


class IModel:
    def __init__( self ):
        self.dead = False
    
    
    def kill( self ):
        self.dead = True


class LegoBlastTarget:
    def __init__( self ):
        self.accession = ""
        self.start = 0
        self.end = 0
        self.length = 0


class LegoBlast( IModel ):
    """
    BLAST result
    """
    
    
    def __init__( self ):
        self.query = LegoBlastTarget( )
        self.subject = LegoBlastTarget( )
        self.percent_identity = 0.0
        self.alignment_length = 0
        self.mismatches = 0
        self.gap_opens = 0
        self.e_value = 0.0
        self.bit_score = 0
    
    
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


class LegoSubsequence:
    """
    BLAST target
    """
    ___next_id = 1
    
    
    def __init__( self, sequence: "LegoSequence", start: LegoCut, end: LegoCut ):
        self.id = LegoSubsequence.___next_id
        LegoSubsequence.___next_id += 1
        
        self.sequence = sequence
        self.original_start = start.only( )
        self.original_end = end.only( )
        self.start_cut = start
        self.end_cut = end
        self.merged_into = None
        self.merges = [ ]
        
        self.edge_targets = [ ]  # type:List[LegoSubsequence]
    
    
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
    
    
    def path_targets( self ) -> "Set[LegoSubsequence]":
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
    
    
    def merge_into( self, b: "LegoSubsequence" ):
        """
        Merges this into another target

        The targets pointing at this target are also updated
        """
        mprint( "MERGE_INTO {0} --> {1}".format( self, b ) )
        assert self.sequence == b.sequence
        assert not self.merged_into
        
        # All the other targets pointing to us need updating
        for x in self.edge_targets:  # type: LegoSubsequence
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
        self.sequence.subsequences.remove( self )
        
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
        
        if "|" in accession:
            self.name = accession.split( "|" )[ -2 ]
        else:
            self.name = accession
        
        self.length = 0
        self.subsequences = [ ]  # List[LegoSubsequence]
        self.cuts = [ ]
    
    
    @staticmethod
    def quantise( value: int ) -> int:
        LEVEL = 25
        value += (LEVEL // 2)
        return value - (value % LEVEL)
    
    
    def get_subsequence( self, target: LegoBlastTarget ) -> LegoSubsequence:
        # start = self.quantise( start )
        # end = self.quantise( end )
        
        self.ensure_capacity( target.length )
        start_cut = self.get_cut( target.start )
        end_cut = self.get_cut( target.end )
        
        result = None
        
        for target in self.subsequences:
            if target.start_cut == start_cut and target.end_cut == end_cut:
                # Already exists
                result = target
        
        if not result:
            result = LegoSubsequence( self, start_cut, end_cut )
            self.subsequences.append( result )
        
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
    
    
    def simplify( self, min_separation: int, no_overlap: bool ) -> bool:
        """
        1. Use HCA to combine similar cuts
        2. Combine identical targets
        """
        mprint( "*** SIMPLIFYING SEQUENCE {0}".format( self ) )
        
        #
        # Use HCA to combine similar cuts
        #
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
        
        #
        # Cuts are combined, but now we probably have identical subsequences
        #
        to_merge = [ ]
        
        i = 0
        while i < len( self.subsequences ):
            a = self.subsequences[ i ]
            matches = [ ]
            
            for j in range( i + 1, len( self.subsequences ) ):
                b = self.subsequences[ j ]
                if a.start_cut == b.start_cut and a.end_cut == b.end_cut:
                    matches.append( b )
            
            for match in matches:
                mprint( "Merge sequences: {0} --> {1}".format( a, b ) )
                match.merge_into( a )  # this modifies self.targets
            
            i += 1
            
        #
        # Pull apart our subsequences such that they never overlap
        #
        if no_overlap:
            new_subsequences = []
            
            for cut in self.cuts:
                
        
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
    
    
    def __init__( self, blast: LegoBlast, query: LegoSubsequence, subject: LegoSubsequence ):
        self.query = query
        self.subject = subject
        self.blast = blast
    
    
    def __iter__( self ):
        return (self.query, self.subject)
    
    
    def __repr__( self ):
        return "Edge"


class LegoGroup:
    def __init__( self, targets: List[ LegoSubsequence ] ):
        self.targets = targets
    
    
    def __iter__( self ):
        return self.targets.__iter__( )
    
    
    def matches( self, targets: List[ LegoSubsequence ] ):
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
        self.no_overlap = True


class LegoList:
    def __init__( self, type ):
        self.contents = [ ]
    
    
    def replace( self, new_list ):
        for x in self.contents:
            x.kill( )
        
        self.contents.clear( )
        self.contents += new_list
    
    
    def __len__( self ):
        return self.contents.__len__( )
    
    
    def __iter__( self ):
        return self.contents.__iter__( )


class LegoModel:
    """
    The model
    """
    
    
    def __init__( self, options: LegoModelOptions ):
        self.__file_name = None
        self.edges = LegoList( LegoEdge )
        self.blasts = LegoList( LegoBlast )
        self.other_subsequences = LegoList( LegoBlastTarget )
        self.sequences = LegoList( LegoSequence )
        self.groups = LegoList( Set[ LegoGroup ] )
        
        if options:
            self.update( options )
    
    
    def __read_file( self, file_name ):
        if file_name.endswith( ".blast" ):
            blasts = [ ]
            
            with open( file_name, "r" ) as file:
                for line in file.readlines( ):
                    result = self.__read_line_from_blast( line )
                    blasts.append( result )
            
            self.blasts = blasts
        elif file_name.endswith( ".composites" ):
            reading = False
            targets = [ ]
            seq_len = 0
            comp_name = None
            
            with open( file_name, "r" ) as file:
                for line in file.readlines( ):
                    if reading:
                        # In composite
                        if line.startswith( ">" ):
                            # Next FASTA/composite - end
                            break
                        
                        if line.startswith( "F" ):
                            target = self.__read_line_from_composites( line, seq_len, comp_name )
                            targets.append( target )
                    elif line.startswith( ">C" ):
                        # Composite begins
                        reading = True
                        comp_name = line[ 1: ]
                    elif not line.startswith( ">" ) and len( line ) != 0:
                        # FASTA sequence
                        seq_len += len( line )
                    elif line.startswith( ">" ):
                        # FASTA begins
                        seq_len = 0
            
            self.other_subsequences = targets
    
    
    @staticmethod
    def __read_line_from_composites( line, seq_len, comp_name ) -> LegoBlastTarget:
        # 0 F<comp family id>
        # 1 <mean align>
        # 2 <mean align>
        # 3 <no sequences as component>
        # 4 <no sequences in family>
        # 5 <mean pident>
        # 6 <mean length>
        
        e = line.split( "\t" )
        
        result = LegoBlastTarget( )
        result.accession = comp_name
        result.start = float( e[ 1 ] )
        result.end = float( e[ 2 ] )
        result.length = seq_len
        
        return result
    
    
    @staticmethod
    def __read_line_from_blast( line ) -> LegoBlast:
        # Fields: query acc., subject acc., % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
        e = line.split( "\t" )
        
        result = LegoBlast( )
        result.query.accession = e[ 0 ]
        result.subject.accession = e[ 1 ]
        result.percent_identity = float( e[ 2 ] )
        result.alignment_length = int( e[ 3 ] )
        result.mismatches = int( e[ 4 ] )
        result.gap_opens = int( e[ 5 ] )
        result.query.start = int( e[ 6 ] )
        result.query.end = int( e[ 7 ] )
        result.subject.start = int( e[ 8 ] )
        result.subject.end = int( e[ 9 ] )
        result.e_value = float( e[ 10 ] )
        result.bit_score = float( e[ 11 ] )
        
        return result
    
    
    def update( self, options: LegoModelOptions ):
        #
        # Load data
        #
        if self.__file_name != options.file_name:
            self.__read_file( options.file_name )
            self.__file_name = options.file_name
        
        #
        # Create subsequences
        #
        sequences = { }  # type:Dict[str, LegoSequence]
        self.edges = [ ]
        
        for subsequence in self.other_subsequences:
            self.create_subsequence( sequences, subsequence )
        
        for blast in self.blasts:
            if blast.query.accession == blast.subject.accession:
                # Ignore self references, they mess merging up
                continue
            
            query = self.create_subsequence( sequences, blast.query )
            subject = self.create_subsequence( sequences, blast.subject )
            
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
        
        #
        # Compact our cuts
        #
        for sequence in self.sequences:
            sequence.simplify( options.combine_cuts, options.no_overlap )
        
        #
        # Create our families (islands, groups of connected subsequences, etc) 
        #
        groups = [ ]
        
        if options.ignore_transitions:
            visited = set( )  # type: Set[LegoSubsequence]
            
            for subsequence in self.subsequences( ):
                if subsequence not in visited:
                    this_group = subsequence.path_targets( )
                    assert not any( (x in visited) for x in this_group )
                    visited.update( this_group )
                    groups.append( LegoGroup( this_group ) )
        else:
            for subsequence in self.subsequences( ):
                this_group = subsequence.edge_targets
                
                if not any( [ x.matches( this_group ) for x in groups ] ):
                    groups.append( LegoGroup( this_group ) )
        
        self.groups.replace( groups )
        
        # Find best permutation
        self.sequences.contents = sorted( self.sequences.contents, key = lambda x: x.length )
    
    
    def subsequences( self ):
        for sequence in self.sequences:
            yield from sequence.subsequences
    
    
    def __iter__( self ):
        return self.sequences.__iter__( )
    
    
    def __repr__( self ):
        return "Model"
    
    
    def create_subsequence( self, sequences: Dict[ str, LegoSequence ], target: LegoBlastTarget ) -> LegoSubsequence:
        if target.accession in sequences:
            sequence = sequences[ target.accession ]
        else:
            sequence = LegoSequence( self, target.accession )
            sequences[ target.accession ] = sequence
        
        result = sequence.get_subsequence( target )
        return result
