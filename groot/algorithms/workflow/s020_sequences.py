"""
File importation functions.

Generally just FASTA is imported here, but we also have the generic `import_file`
and `import_directory`, as well as some miscellaneous imports such as Composite
Search and Newick imports, that don't belong anywhere else. 
"""
from typing import List, Optional
import re

from groot.constants import STAGES, EChanges
from intermake import MCMD, command
from mhelper import Logger, bio_helper

from groot import LegoSequence, LegoModel
from groot.data import IHasFasta, global_view
from groot.utilities import cli_view_utils


LOG = Logger( "import" )


@command()
def import_sequences( file_name: str ) -> EChanges:
    """
    Imports a FASTA file into your model.
    If data already exists in the model, only sequence data matching sequences already in the model is loaded.
    
    :param file_name:   File to import
    """
    model = global_view.current_model()
    model.get_status( STAGES.FASTA_1 ).assert_import()
    
    model.user_comments.append( "IMPORT_FASTA \"{}\"".format( file_name ) )
    
    with LOG( "IMPORT FASTA FROM '{}'".format( file_name ) ):
        obtain_only = model._has_data()
        num_updates = 0
        idle = 0
        idle_counter = 10000
        
        for name, sequence_data in bio_helper.parse_fasta( file = file_name ):
            sequence = _make_sequence( model, str( name ), obtain_only, len( sequence_data ), True )
            
            if sequence:
                LOG( "FASTA UPDATES {} WITH ARRAY OF LENGTH {}".format( sequence, len( sequence_data ) ) )
                num_updates += 1
                sequence.site_array = str( sequence_data )
                idle = 0
            else:
                idle += 1
                
                if idle == idle_counter:
                    LOG( "THIS FASTA IS BORING..." )
                    idle_counter *= 2
                    idle = 0
    
    MCMD.progress( "Imported Fasta from «{}».".format( file_name ) )
    
    return EChanges.MODEL_ENTITIES


@command()
def set_sequences( accessions: List[str], sites: Optional[List[str]] ) -> EChanges:
    """
    Adds a new sequence to the model
    
    :param sites:       Sequence sites.
                        Optional.
                        If specified, the same number of `sites` as `accessions` must be provided. 
    :param accessions:  Sequence accession(s)
    """
    model = global_view.current_model()
    model.get_status( STAGES.FASTA_1 ).assert_set()
    
    for i, accession in enumerate( accessions ):
        sequence = __add_new_sequence( model, accession )
        
        if sites:
            site = sites[i]
            sequence.site_array = site
            sequence.length = len( site )
        
        MCMD.progress( "Added: {} (n={})".format( sequence, sequence.site_array.__len__() ) )
    
    return EChanges.MODEL_ENTITIES


@command()
def drop_sequences( sequences: List[LegoSequence] ):
    """
    Removes one or more sequences from the model.
    
    :param sequences:    One or more sequences to drop.
    """
    model = global_view.current_model()
    model.get_status( STAGES.FASTA_1 ).assert_drop()
    
    for sequence in sequences:
        sequence.model.sequences.remove( sequence )


@command()
def print_sequences( find: Optional[str] = None, targets: Optional[List[IHasFasta]] = None ) -> EChanges:
    """
    List sequences or presents their FASTA data.
    If no parameters are specified the accessions of all current sequences are listed.
    
    :param targets:      Object(s) to present.
                        If specified FASTA data for these objects are listed.
    :param find:        Regular expression.
                        If specified sequences with matching accessions will be listed. 
    """
    if find is None and targets is None:
        find = ".*"
    
    if find is not None:
        model = global_view.current_model()
        
        sequences = []
        rx = re.compile( find, re.IGNORECASE )
        for s in model.sequences:
            if rx.search( s.accession ):
                sequences.append( s )
        
        if not sequences:
            MCMD.print( "No matching sequences." )
        else:
            for sequence in sequences:
                MCMD.print( sequence )
            
            MCMD.print( "Found {} sequences.".format( len( sequences ) ) )
        
        return EChanges.INFORMATION
    elif targets is not None:
        for target in targets:
            if isinstance( target, IHasFasta ):
                MCMD.information( cli_view_utils.colour_fasta_ansi( target.to_fasta(), global_view.current_model().site_type ) )
            else:
                MCMD.warning( "Target «{}» does not have FASTA data.".format( target ) )
    
    return EChanges.INFORMATION


def _make_sequence( model: LegoModel,
                    accession: str,
                    obtain_only: bool,
                    initial_length: int,
                    retrieve: bool ) -> LegoSequence:
    """
    Creates the specified sequence, or returns it if it already exists.
    """
    assert isinstance( initial_length, int )
    
    if "|" in accession:
        accession = accession.split( "|" )[3]
    
    if "." in accession:
        accession = accession.split( ".", 1 )[0]
    
    accession = accession.strip()
    
    result: LegoSequence = None
    
    if retrieve:
        for sequence in model.sequences:
            if sequence.accession == accession:
                result = sequence
    
    if result is None and not obtain_only:
        result = LegoSequence( model, accession, len( model.sequences ) )
        model.sequences.add( result )
    
    if result is not None:
        result._ensure_length( initial_length )
    
    return result


def __add_new_sequence( model: LegoModel, accession: str ) -> LegoSequence:
    """
    Creates a new sequence
    """
    return _make_sequence( model, accession, False, 0, False )
