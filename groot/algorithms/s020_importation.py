"""
File importation functions.

Generally just FASTA is imported here, but we also have the generic `import_file`
and `import_directory`, as well as some miscellaneous imports such as Composite
Search and Newick imports, that don't belong anywhere else. 
"""
from typing import cast
from intermake import MCMD, common_commands
from mgraph import MGraph, MNode, analysing, exporting, importing
from mhelper import ByRef, Logger, MFlags, bio_helper, file_helper

from groot import algorithms
from groot.data import LegoPoint, LegoModel
from groot.utilities import lego_graph


LOG = Logger( "import" )


class EImportFilter( MFlags ):
    """
    Mask on importing files.
    
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
    """
    Imports a file.
    _How_ the file is imported is determined by its extension.
    
    :param model:                   Model to import file into. 
    :param file_name:               Name of file to import. 
    :param skip_bad_extensions:     When set, if the file has an extension we don't recognise, no error is raised. 
    :param filter:                  Specifies what kind of files we are allowed to import.
    :param query:                   When set the kind of the file is printed to `MCMD` and the file is not imported. 
    :return:                        Nothing is returned, the file data is incorporated into the model and messages are sent via `MCMD`.
    """
    ext = file_helper.get_extension( file_name ).lower()
    
    if filter.DATA:
        if ext == ".blast":
            if not query:
                algorithms.s030_similarity.import_similarity( model, file_name )
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
                algorithms.s010_file.load_from_file( file_name )
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
            sequence = algorithms.s999_editor.make_sequence( model, str( name ), obtain_only, len( sequence_data ), extra_data, False, True )
            
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
                    composite_sequence = algorithms.s999_editor.make_sequence( model, composite_name, False, 0, line, False, True )
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
                    sequence = algorithms.s999_editor.make_sequence( model, line, False, fam_mean_length, line, False, True )
                    sequence.comments.append( "Family '{}'".format( fam_name ) )
                    sequence.comments.append( "Accession '{}'".format( line ) )
                    
                    # subsequence = sequence._make_subsequence( 1, sequence.length )
                    # assert composite_subsequence
                    # self._make_edge( composite_subsequence, subsequence )
    
    MCMD.progress( "Imported Composites from «{}».".format( file_name ) )


def export_newick( graph: MGraph ):
    """
    Exports Newick into a format suitable for use with other programs.
    
    * We use legacy accessions to cope with programs still relying on the old PHYLIP format, which limits gene names
    * We pull fusion clades into leaves to cope with programs that don't account for named clades
    * We don't label the other clades
    """
    # Declade fusion nodes
    nodes = analysing.realise_node_predicate_as_set( graph, lego_graph.is_fusion_like )
    
    for node in nodes:
        node.add_child( node.data )
        node.data = None
    
    # Ensure the root of the graph is not something weird
    if not lego_graph.is_clade( graph.root ):
        child = graph.root.child
        assert lego_graph.is_clade( child )
        child.make_root()
    
    # Write newick
    return exporting.export_newick( graph,
                                    fnode = lambda x: x.data.legacy_accession if x.data else "",
                                    internal = False )


def import_newick( newick: str, model: LegoModel, root_ref: ByRef[MNode] = None, reclade: bool = True ) -> MGraph:
    """
    Imports a newick string as an MGraph object.
    
    The format is expected to be the same as that produced by `export_newick`, but we make accommodations
    for additional information programs might have added, such as clade names and branch lengths.
    """
    # Read newick
    graph: MGraph = importing.import_newick( newick,
                                             root_ref = root_ref )
    
    # Convert node names back to references
    for node in graph.nodes:
        node.data = lego_graph.import_leaf_reference( cast( str, node.data ),
                                                      model,
                                                      allow_empty = True )
    
    # Reclade fusion nodes
    if reclade:
        fusion_nodes = analysing.realise_node_predicate_as_set( graph, lambda x: isinstance( x.data, LegoPoint ) )
        
        for node in fusion_nodes:
            node.parent.data = node.data
            node.remove_node()
    
    return graph
