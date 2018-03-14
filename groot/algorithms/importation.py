from typing import Optional, cast

from groot.algorithms import editor, marshal
from groot.data.lego_model import LegoModel, LegoSubsequence, LegoSequence
from intermake import MCMD, common_commands
from mgraph import MGraph, MNode, importing
from mhelper import file_helper, bio_helper, ByRef, Logger, MFlags


LOG = Logger( "import" )


class EImportFilter( MFlags ):
    """
    :data DATA: Data files (`.fasta`, `.blast`, `.composites`)
    :data MODE: Model files (`.groot`)
    :data SCRIPT: Scripts (`.imk`)
    """
    DATA: "EImportFilter" = 1 << 0
    MODEL: "EImportFilter" = 1 << 1
    SCRIPT: "EImportFilter" = 1 << 2


def import_directory( model: LegoModel, directory: str, query: bool, filter: EImportFilter ) -> None:
    """
    Imports all importable files from a specified directory
    
    :param query:     When true, nothing will change but output will be sent to MCMD. 
    :param model:     Model to import into
    :param directory: Directory to import
    :param filter:      Filter on import
    :return: 
    """
    contents = file_helper.list_dir( directory )
    
    if filter.DATA:
        for file_name in contents:
            import_file( model, file_name, skip_bad_extensions = True, filter = EImportFilter.DATA, query = query )
    
    if filter.SCRIPT:
        for file_name in contents:
            import_file( model, file_name, skip_bad_extensions = True, filter = EImportFilter.SCRIPT, query = query )


def import_file( model: LegoModel, file_name: str, skip_bad_extensions: bool, filter: EImportFilter, query: bool ) -> None:
    ext = file_helper.get_extension( file_name ).lower()
    
    if filter.DATA:
        if ext == ".blast":
            if not query:
                import_blast( model, file_name )
                return
            else:
                MCMD.print( "BLAST: «{}».".format( file_name ) )
                return
        elif ext in (".fasta", ".fa", ".faa"):
            if not query:
                import_fasta( model, file_name )
                return
            else:
                MCMD.print( "FASTA: «{}».".format( file_name ) )
                return
        elif ext in (".composites", ".comp"):
            if not query:
                import_composites( model, file_name )
                return
            else:
                MCMD.progress( "Composites «{}».".format( file_name ) )
                return
    
    if filter.SCRIPT:
        if ext == ".imk":
            if not query:
                MCMD.progress( "Run script «{}».".format( file_name ) )
                common_commands.source( file_name )
                return
            else:
                MCMD.print( "Script: «{}».".format( file_name ) )
                return
    
    if filter.MODEL:
        if ext == ".groot":
            if not query:
                marshal.load_from_file( file_name )
                return
            else:
                MCMD.print( "Model: «{}».".format( file_name ) )
                return
    
    if skip_bad_extensions:
        return
    
    raise ValueError( "Cannot import the file '{}' because I don't recognise the extension '{}'.".format( file_name, ext ) )


def import_fasta( model: LegoModel, file_name: str ) -> None:
    """
    API
    Imports a FASTA file.
    If data already exists in the model, only sequence data matching sequences already in the model is loaded.
    """
    model.comments.append( "IMPORT_FASTA \"{}\"".format( file_name ) )
    
    with LOG( "IMPORT FASTA FROM '{}'".format( file_name ) ):
        obtain_only = model._has_data()
        num_updates = 0
        idle = 0
        idle_counter = 10000
        extra_data = "FASTA from '{}'".format( file_name )
        
        for name, sequence_data in bio_helper.parse_fasta( file = file_name ):
            sequence = editor.make_sequence( model, str( name ), obtain_only, len( sequence_data ), extra_data, False, True )
            
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


def import_blast( model: LegoModel, file_name: str, evalue: float = None, length: int = None ) -> None:
    """
    API
    Imports a BLAST file.
    If data already exists in the model, only lines referencing existing sequences are imported.
    """
    obtain_only = model._has_data()
    
    LOG( "IMPORT {} BLAST FROM '{}'", "MERGE" if obtain_only else "NEW", file_name )
    
    with LOG:
        with open( file_name, "r" ) as file:
            for line in file.readlines():
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
                        raise ValueError( "BLAST file '{}' should contain 12 values, but this line contains {}: {}".format( file_name, len( e ), line ) )
                    
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
                    
                    TOL = int( 10 + ((query_length + subject_length) / 2) / 5 )
                    if not (subject_length - TOL) <= query_length <= (subject_length + TOL):
                        raise ValueError( "Refusing to process BLAST file because the query length {} is not constant with the subject length {} at the line reading '{}'.".format( query_length, subject_length, line ) )
                    
                    query_s = editor.make_sequence( model, query_accession, obtain_only, 0, line, False, True )
                    subject_s = editor.make_sequence( model, subject_accession, obtain_only, 0, line, False, True )
                    
                    if query_s and subject_s and query_s is not subject_s:
                        query = LegoSubsequence( query_s, query_start, query_end )
                        subject = LegoSubsequence( subject_s, subject_start, subject_end )
                        LOG( "BLAST UPDATES AN EDGE THAT JOINS {} AND {}".format( query, subject ) )
                        editor.make_edge( model, query, subject, line, False )
    
    MCMD.progress( "Imported Blast from «{}».".format( file_name ) )


def import_composites( model: LegoModel, file_name: str ) -> None:
    """
    API
    Imports a COMPOSITES file
    """
    MCMD.progress( "Import composites from «{}».".format( file_name ) )
    model.comments.append( "IMPORT_COMPOSITES \"{}\"".format( file_name ) )
    
    with LOG( "IMPORT COMPOSITES FROM '{}'".format( file_name ) ):
        fam_name = "?"
        fam_mean_length = None
        composite_sequence = None
        
        with open( file_name, "r" ) as file:
            for line_number, line in enumerate( file ):
                line = line.strip()
                
                if line.startswith( ">" ):
                    if composite_sequence:
                        return
                    
                    # COMPOSITE!
                    composite_name = line[1:]
                    composite_sequence = editor.make_sequence( model, composite_name, False, 0, line, False, True )
                    composite_sequence.comments.append( "FILE '{}' LINE {}".format( file_name, line_number ) )
                elif "\t" in line:
                    # FAMILY!
                    # Fields: F<comp family id> <mean align> <mean align> <no sequences as component> <no sequences in family> <mean pident> <mean length>
                    e = line.split( "\t" )
                    
                    fam_name = e[0]
                    # fam_mean_start = int( e[ 1 ] )
                    # fam_mean_end = int( e[ 2 ] )
                    # fam_num_seq_as_component = int(e[3])
                    # fam_num_seq_in_family = int(e[3])
                    # fam_mean_pident = float(e[4])
                    fam_mean_length = int( float( e[5] ) )
                    
                    # composite_subsequence = editor.make_subsequence( composite_sequence, fam_mean_start, fam_mean_end, line, True, False )
                elif line:
                    # SEQUENCE
                    sequence = editor.make_sequence( model, line, False, fam_mean_length, line, False, True )
                    sequence.comments.append( "Family '{}'".format( fam_name ) )
                    sequence.comments.append( "Accession '{}'".format( line ) )
                    
                    # subsequence = sequence._make_subsequence( 1, sequence.length )
                    # assert composite_subsequence
                    # self._make_edge( composite_subsequence, subsequence )
    
    MCMD.progress( "Imported Composites from «{}».".format( file_name ) )


def import_newick( newick: str, model: LegoModel, root_ref: ByRef[MNode] = None ) -> MGraph:
    """
    Imports a newick string as an MGraph object.
    """
    g: MGraph = importing.import_newick( newick, root_ref = root_ref )
    
    for node in g.nodes:
        node.data = import_sequence_reference( cast( str, node.data ), model, allow_empty = True )
    
    return g


def import_sequence_reference( name: str, model: LegoModel, *, allow_empty: bool = False ) -> Optional[LegoSequence]:
    """
    Converts a sequence name to a sequence reference.
    
    :param name:        Name, either:
                            i.  The accession
                            ii. The ID, of the form `"S[0-9]+"`
    :param model:       The model to find the sequence in 
    :param allow_empty: Allow `None` or `""` to denote a missing sequence, `None`. 
    :return:            The sequence, or `None` if `allow_empty` is set.
    """
    if allow_empty and name is None:
        return None
    
    assert isinstance( name, str )
    
    if allow_empty and name == "" or name == "root" or name.startswith( "clade" ):
        return None
    elif LegoSequence.is_legacy_accession( name ):
        return model.find_sequence_by_id( int( name[1:] ) )
    else:
        return model.find_sequence_by_accession( name )
