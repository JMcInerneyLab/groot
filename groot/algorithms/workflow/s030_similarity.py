"""
Imports or creates the BLAST data.

More generically called the "similarity matrix" or "edge" data, we allow the user to load an existing file or run their own algorithm.
BLAST is the default algorithm and this invocation can be found in the `groot_ex` project. 
"""
from typing import Callable, List, Optional

import re

from groot.algorithms.workflow.s020_sequences import _make_gene
from intermake import MCMD, command
from mhelper import EFileMode, Filename, Logger

from groot import Edge, constants
from groot.constants import EXT_BLAST, STAGES, EChanges
from groot.data import Model, Domain, global_view
from groot.utilities import AlgorithmCollection, external_runner


LOG = Logger( "import/blast" )
__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME

DAlgorithm = Callable[[str], str]
"""
Task:
    A similarity of FASTA sequences.

Input:
    str (default): FASTA sequences for two or more genes
    
Output:
    str: A similarity matrix in BLAST format 6 TSV.
"""

similarity_algorithms = AlgorithmCollection( DAlgorithm, "Similarity" )


@command( folder = constants.F_CREATE )
def create_similarity( algorithm: similarity_algorithms.Algorithm, evalue: float = None, length: int = None ):
    """
    Create and imports similarity matrix created using the specified algorithm.
    
    :param algorithm:   Algorithm to use. See `algorithm_help`. 
    :param evalue:      e-value cutoff. 
    :param length:      length cutoff.
    """
    model: Model = global_view.current_model()
    model.get_status( STAGES.BLAST_2 ).assert_create()
    
    input = model.genes.to_fasta()
    
    output = external_runner.run_in_temporary( algorithm, input )
    
    __import_blast_format_6( evalue, output, "untitled_blast_data", length, model, True )


@command( folder = constants.F_SET )
def set_similarity( left: Domain, right: Domain ) -> EChanges:
    """
    Adds a new edge to the model.
    :param left:     Subsequence to create the edge from 
    :param right:    Subsequence to create the edge to
    """
    model: Model = global_view.current_model()
    model.get_status( STAGES.BLAST_2 ).assert_set()
    
    edge = Edge( left, right )
    left.gene.model.edges.add( edge )
    
    return EChanges.MODEL_ENTITIES


@command( folder = constants.F_IMPORT )
def import_similarity( file_name: Filename[EFileMode.READ, EXT_BLAST], evalue: Optional[float] = 1e-10, length: Optional[int] = None ) -> EChanges:
    """
    Imports a similarity matrix.
    If data already exists in the model, only lines referencing existing sequences are imported.
    :param file_name:   File to import 
    :param evalue:      e-value cutoff 
    :param length:      Length cutoff 
    :return: 
    """
    model: Model = global_view.current_model()
    model.get_status( STAGES.BLAST_2 ).assert_create()
    
    obtain_only = model._has_data()
    
    with LOG:
        with open( file_name, "r" ) as file:
            __import_blast_format_6( evalue, file.readlines(), file_name, length, model, obtain_only )
    
    return EChanges.MODEL_ENTITIES


@command( folder = constants.F_DROP )
def drop_similarity( edges: Optional[List[Edge]] = None ):
    """
    Detaches the specified edges from the specified subsequences.
    
    :param edges:           Edges to affect.
                            If `None` then all edges are dropped.
    """
    model: Model = global_view.current_model()
    model.get_status( STAGES.BLAST_2 ).assert_drop()
    
    if edges is not None:
        for edge in edges:
            edge.left.gene.model.edges.remove( edge )
    else:
        model.edges = []


@command( names = ["print_similarity", "similarity"], folder = constants.F_PRINT )
def print_similarity( find: str = "" ) -> EChanges:
    """
    Prints model edges.
    
    :param find: If specified, only edges with accessions matching this regular expression are given.
    """
    model = global_view.current_model()
    
    if not find:
        find = ".*"
    
    f = re.compile( find )
    
    for edge in model.edges:
        if f.search( edge.left.sequence.accession ) or f.search( edge.right.sequence.accession ):
            MCMD.print( str( edge ) )
    
    return EChanges.NONE


def __import_blast_format_6( e_value_tol, file, file_title, length_tol, model, obtain_only ):
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
            
            if e_value_tol is not None and e_value > e_value_tol:
                LOG( "REJECTED E VALUE" )
                continue
            
            if length_tol is not None and query_length < length_tol:
                LOG( "REJECTED LENGTH" )
                continue
            
            assert query_length > 0 and subject_length > 0
            
            query_s = _make_gene( model, query_accession, obtain_only, 0, True )
            subject_s = _make_gene( model, subject_accession, obtain_only, 0, True )
            
            if query_s and subject_s and query_s is not subject_s:
                query = Domain( query_s, query_start, query_end )
                subject = Domain( subject_s, subject_start, subject_end )
                LOG( "BLAST UPDATES AN EDGE THAT JOINS {} AND {}".format( query, subject ) )
                __make_edge( model, query, subject )
    
    MCMD.progress( "Imported Blast from «{}».".format( file_title ) )


def __make_edge( model: Model, source: Domain, destination: Domain ) -> Edge:
    """
    Creates the specified edge, or returns it if it already exists.
    """
    assert source != destination
    
    for edge in model.edges:
        if (edge.left == source and edge.right == destination) \
                or (edge.left == destination and edge.right == source):
            return edge
    
    result = Edge( source, destination )
    model.edges.add( result )
    
    return result
