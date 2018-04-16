"""
Imports or creates the BLAST data.

More generically called the "similarity matrix" or "edge" data, we allow the user to load an existing file or run their own algorithm.
BLAST is the default algorithm and this invocation can be found in the `groot_ex` project. 
"""
from typing import Callable
from intermake import MCMD
from mhelper import Logger

from groot.data import LegoModel, LegoSubsequence
from groot.utilities import external_runner, AlgorithmCollection


LOG = Logger( "import/blast" )

DAlgorithm = Callable[[str], str]
"""
Task:
    A similarity of FASTA sequences.

Input:
    str (default): FASTA sequences for two or more genes
    
Output:
    str: A similarity matrix in BLAST format 6 TSV.
"""

similarity_algorithms = AlgorithmCollection[DAlgorithm]( "Similarity" )


def create_similarity( model: LegoModel, algorithm_name: str, evalue: float = None, length: int = None ):
    """
    Create and imports similarity matrix created using the specified algorithm.
    """
    algorithm = similarity_algorithms[algorithm_name]
    
    input = model.sequences.to_fasta()
    
    output = external_runner.run_in_temporary( algorithm, input )
    
    __import_blast_format_6( evalue, output, "untitled_blast_data", length, model, True )


def import_similarity( model: LegoModel, file_name: str, evalue: float = None, length: int = None ) -> None:
    """
    Imports a similarity matrix.
    If data already exists in the model, only lines referencing existing sequences are imported.
    """
    obtain_only = model._has_data()
    
    with LOG:
        with open( file_name, "r" ) as file:
            __import_blast_format_6( evalue, file.readlines(), file_name, length, model, obtain_only )


def __import_blast_format_6( evalue, file, file_title, length, model, obtain_only ):
    from groot import algorithms
    
    LOG( "IMPORT {} BLAST FROM '{}'", "MERGE" if obtain_only else "NEW", file_title )
    
    for line in file:
        line = line.strip()
        
        if line and not line.startswith( "#" ) and not line.startswith( ";" ):
            # BLASTN     query acc. | subject acc. |                                 | % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
            # MEGABLAST  query id   | subject ids  | query acc.ver | subject acc.ver | % identity, alignment length, mismatches, gap opens, q. start, q. end, s. start, s. end, evalue, bit score
            # Fields: 
            
            # Split by tabs or spaces 
            if "\t" in line:
                e = line.split( "\t" )
            else:
                e = [x for x in line.split( " " ) if x]
            
            if len( e ) == 14:
                del e[2:4]
            
            # Assertion
            if len( e ) != 12:
                raise ValueError( "BLAST file '{}' should contain 12 values, but this line contains {}: {}".format( file_title, len( e ), line ) )
            
            query_accession = e[0]
            query_start = int( e[6] )
            query_end = int( e[7] )
            query_length = query_end - query_start
            subject_accession = e[1]
            subject_start = int( e[8] )
            subject_end = int( e[9] )
            subject_length = subject_end - subject_start
            e_value = float( e[10] )
            LOG( "BLAST SAYS {} {}:{} ({}) --> {} {}:{} ({})".format( query_accession, query_start, query_end, query_length, subject_accession, subject_start, subject_end, subject_length ) )
            
            if evalue is not None and e_value > evalue:
                LOG( "REJECTED E VALUE" )
                continue
            
            if length is not None and query_length < length:
                LOG( "REJECTED LENGTH" )
                continue
            
            assert query_length > 0 and subject_length > 0
            
            query_s = algorithms.s999_editor.make_sequence( model, query_accession, obtain_only, 0, line, False, True )
            subject_s = algorithms.s999_editor.make_sequence( model, subject_accession, obtain_only, 0, line, False, True )
            
            if query_s and subject_s and query_s is not subject_s:
                query = LegoSubsequence( query_s, query_start, query_end )
                subject = LegoSubsequence( subject_s, subject_start, subject_end )
                LOG( "BLAST UPDATES AN EDGE THAT JOINS {} AND {}".format( query, subject ) )
                algorithms.s999_editor.make_edge( model, query, subject, False )
    
    MCMD.progress( "Imported Blast from «{}».".format( file_title ) )
