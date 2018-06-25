"""
File importation functions.

Generally just FASTA is imported here, but we also have the generic `import_file`
and `import_directory`, as well as some miscellaneous imports such as Composite
Search and Newick imports, that don't belong anywhere else. 
"""
import warnings
from typing import List, Optional, Set
import re

from groot.constants import STAGES, EChanges
from intermake import MCMD, command
from mhelper import Logger, bio_helper, Filename

from groot import Gene, Model, constants
from groot.data import IHasFasta, global_view
from groot.utilities import cli_view_utils


LOG = Logger( "import" )
__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME


@command( folder = constants.F_IMPORT )
def import_genes( file_name: str ) -> EChanges:
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
            sequence = _make_gene( model, str( name ), obtain_only, len( sequence_data ), True )
            
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


_T = Filename["r", ".csv"]


@command( folder = constants.F_IMPORT )
def import_gene_names( file: _T ):
    """
    Loads in the displayed gene names from a file.
    
    :param file:    Path to a CSV or TSV file with two columns: accessions, display name.
    """
    model = global_view.current_model()
    
    tot = 0
    
    with open( file ) as in_:
        for row in in_:
            if "\t" in row:
                accession, name = row.split( "\t", 1 )
            elif "," in row:
                accession, name = row.split( ",", 1 )
            else:
                accession, name = None, None
            
            if accession:
                accession = accession.strip()
                name = name.strip()
                gene = model.genes.get( accession )
                
                if gene is None:
                    warnings.warn( "No such gene: {}".format( accession ), UserWarning )
                    continue
                
                gene.display_name = name
                tot += 1
    
    MCMD.progress( "{} genes renamed".format( tot ) )


@command( folder = constants.F_SET )
def set_gene_name( gene: Gene, name: str ) -> EChanges:
    """
    Changes the display name of the gene (_not_ the accession).
    :param gene:        Gene to set the name of 
    :param name:    New name of the gene. If set to an empty string the accession will be used as the name. 
    """
    gene.display_name = name
    return EChanges.MODEL_DATA


@command( folder = constants.F_SET )
def set_genes( accessions: List[str], sites: Optional[List[str]] ) -> EChanges:
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
        sequence = __add_new_gene( model, accession )
        
        if sites:
            site = sites[i]
            sequence.site_array = site
            sequence.length = len( site )
        
        MCMD.progress( "Added: {} (n={})".format( sequence, sequence.site_array.__len__() ) )
    
    return EChanges.MODEL_ENTITIES


@command( folder = constants.F_DROP )
def drop_genes( genes: List[Gene] ) -> EChanges:
    """
    Removes one or more sequences from the model.
    
    It is safe to use this function up to and including the `create_major` stage.
    
    References to this gene(s) will be removed from any extant edges or components.
    
    :param genes:    One or more genes to drop.
    """
    # Get the model
    model = global_view.current_model()
    
    # Delete the previous MAJOR components
    has_major = model.get_status( STAGES.MAJOR_3 )
    
    if has_major:
        from . import s040_major
        
        old_comps: List[Set[Gene]] = list( set( component.major_genes ) for component in model.components )
        s040_major.drop_major( None )  # = drop all!
    else:
        old_comps = None
    
    # Drop the edges 
    to_drop = set()
    
    for edge in model.edges:
        if edge.left.gene in genes or edge.right.gene in genes:
            to_drop.add( edge )
    
    from . import s030_similarity
    s030_similarity.drop_similarity( list( to_drop ) )
    
    # Assert the drop (this should pass now we have removed the components and edges!)
    model.get_status( STAGES.FASTA_1 ).assert_drop()
    
    # Drop the genes
    for gene in genes:
        assert isinstance( gene, Gene ), gene
        gene.display_name = "DROPPED"
        gene.model.genes.remove( gene )
    
    # Create new components
    if has_major:
        for comp in old_comps:
            for gene in genes:
                if gene in comp:
                    comp.remove( gene )
            
            if comp:
                from . import s040_major
                s040_major.set_major( list( comp ) )
    
    return EChanges.MODEL_ENTITIES


@command( folder = constants.F_PRINT )
def print_genes( find: Optional[str] = None, targets: Optional[List[IHasFasta]] = None ) -> EChanges:
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
        
        genes = []
        rx = re.compile( find, re.IGNORECASE )
        for s in model.genes:
            if rx.search( s.accession ):
                genes.append( s )
        
        if not genes:
            MCMD.print( "No matching genes." )
        else:
            for gene in genes:
                MCMD.print( gene )
            
            MCMD.print( "Found {} genes.".format( len( genes ) ) )
        
        return EChanges.INFORMATION
    elif targets is not None:
        for target in targets:
            if isinstance( target, IHasFasta ):
                MCMD.information( cli_view_utils.colour_fasta_ansi( target.to_fasta(), global_view.current_model().site_type ) )
            else:
                MCMD.warning( "Target «{}» does not have FASTA data.".format( target ) )
    
    return EChanges.INFORMATION


def _make_gene( model: Model,
                accession: str,
                obtain_only: bool,
                initial_length: int,
                retrieve: bool ) -> Gene:
    """
    Creates the specified sequence, or returns it if it already exists.
    """
    assert isinstance( initial_length, int )
    
    if "|" in accession:
        accession = accession.split( "|" )[3]
    
    accession = accession.strip()
    
    result: Gene = None
    
    if retrieve:
        for sequence in model.genes:
            if sequence.accession == accession:
                result = sequence
    
    if result is None and not obtain_only:
        result = Gene( model, accession, len( model.genes ) )
        model.genes.add( result )
    
    if result is not None:
        result._ensure_length( initial_length )
    
    return result


def __add_new_gene( model: Model, accession: str ) -> Gene:
    """
    Creates a new sequence
    """
    return _make_gene( model, accession, False, 0, False )
