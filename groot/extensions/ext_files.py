import sys
from os import path
from typing import Optional

import groot.data.global_view
from groot.algorithms import importation, marshal
from groot.algorithms.importation import EImportFilter
from groot.data import global_view
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import MCMD, MENV, PathToVisualisable, command, console_explorer
from intermake.engine.theme import Theme
from mhelper import EFileMode, Filename, MOptional, file_helper


__mcmd_folder_name__ = "Files"
EXT_GROOT = ".groot"
EXT_FASTA = ".fasta"
EXT_BLAST = ".blast"


@command( names = ["file_sample", "sample"] )
def file_sample( name: Optional[str] = None, query: bool = False, load: bool = False ) -> EChanges:
    """
    Lists the available samples, or loads the specified sample.
    
    :param name:    Name of sample. 
    :param query:   When set the sample is viewed but not loaded. 
    :param load:    When set data is imported but any scripts (if present) are not run.
    :return: 
    """
    if name:
        file_name = path.join( global_view.get_sample_data_folder(), name )
        
        if not path.isdir( file_name ):
            raise ValueError( "'{}' is not a valid sample directory.".format( name ) )
        
        if not query:
            MCMD.progress( "Loading sample dataset «{}».".format( file_name ) )
        else:
            MCMD.print( "Sample data: «{}».".format( file_name ) )
        
        return import_directory( file_name, filter = (EImportFilter.DATA | EImportFilter.SCRIPT) if not load else EImportFilter.DATA, query = query )
    else:
        for sample_dir in global_view.get_samples():
            MCMD.print( file_helper.get_filename( sample_dir ) )
        
        return EChanges.NONE


@command( names = ["file_new", "new"] )
def file_new() -> EChanges:
    """
    Starts a new model
    """
    global_view.new_model()
    MCMD.progress( "New model instantiated." )
    
    return EChanges.MODEL_OBJECT


@command()
def import_blast( file_name: Filename[EFileMode.READ, EXT_BLAST], evalue: Optional[float] = 1e-10, length: Optional[int] = None ) -> EChanges:
    """
    Imports a BLAST file into the model 
    :param length:      Cutoff on alignment (query) length `None` for no filter. 
    :param evalue:      Cutoff on evalue. `None` for no filter (this is not the default). 
    :param file_name:   File to import 
    :return: 
    """
    with MCMD.action( "Importing BLAST" ):
        importation.import_blast( global_view.current_model(), file_name, evalue, length )
    
    return EChanges.MODEL_ENTITIES


@command()
def import_composites( file_name: Filename[EFileMode.READ] ) -> EChanges:
    """
    Imports a composites file into the model
    :param file_name:   File to import 
    :return: 
    """
    with MCMD.action( "Importing composites" ):
        importation.import_composites( global_view.current_model(), file_name )
    
    return EChanges.MODEL_ENTITIES


@command()
def import_fasta( file_name: Filename[EFileMode.READ, EXT_FASTA] ) -> EChanges:
    """
    Imports a FASTA file into the model
    :param file_name:   File to import 
    :return: 
    """
    with MCMD.action( "Importing FASTA" ):
        importation.import_fasta( global_view.current_model(), file_name )
    
    return EChanges.MODEL_ENTITIES


@command()
def import_file( file_name: Filename[EFileMode.READ] ) -> EChanges:
    """
    Imports a file into the model.
    How it is imported is based on the extension:
        `.groot`     --> `file_load`
        `.fasta`     --> `import_fasta`
        `.blast`     --> `import_blast`
        `.composite` --> `import_composite`
        `.imk`       --> `source` (runs the script)
    
    :param file_name:   File to import.
    """
    with MCMD.action( "Importing file" ):
        importation.import_file( global_view.current_model(), file_name, skip_bad_extensions = False, filter = EImportFilter.ALL, query = False )
    
    return EChanges.MODEL_ENTITIES


@command( names = ("file_load_last", "last") )
def file_load_last():
    """
    Loads the last file from the recent list.
    """
    if not groot.data.global_view.options().recent_files:
        raise ValueError( "Cannot load the last session because there are no recent sessions." )
    
    file_load( groot.data.global_view.options().recent_files[-1] )


@command( names = ["file_recent", "recent"] )
def file_recent():
    """
    Prints the contents of the `sessions` folder
    """
    r = []
    
    r.append( "SESSIONS:" )
    for file in groot.data.global_view.get_workspace_files():
        r.append( file_helper.highlight_file_name_without_extension( file, Theme.BOLD, Theme.RESET ) )
    
    r.append( "\nRECENT:" )
    for file in reversed( groot.data.global_view.options().recent_files ):
        r.append( file_helper.highlight_file_name_without_extension( file, Theme.BOLD, Theme.RESET ) )
    
    MCMD.information( "\n".join( r ) )


@command( names = ["file_save", "save"] )
def file_save( file_name: MOptional[Filename[EFileMode.WRITE, EXT_GROOT]] = None ) -> EChanges:
    """
    Saves the model
    :param file_name: Filename. File to load. Either specify a complete path, or the name of the file in the `sessions` folder. If not specified the current filename is used.
    :return: 
    """
    model = global_view.current_model()
    
    if file_name:
        file_name = __fix_path( file_name )
    else:
        file_name = model.file_name
    
    if not file_name:
        raise ValueError( "Cannot save because a filename has not been specified." )
    
    groot.data.global_view.remember_file( file_name )
    
    sys.setrecursionlimit( 10000 )
    
    with MCMD.action( "Saving file to «{}»".format( file_name ) ):
        marshal.save_to_file( file_name, model )
    
    model.file_name = file_name
    MCMD.progress( "Saved model to «{}»".format( file_name ) )
    
    return EChanges.FILE_NAME


@command()
def import_directory( directory: str,
                      reset: bool = True,
                      filter: EImportFilter = (EImportFilter.DATA | EImportFilter.SCRIPT),
                      query: bool = False
                      ) -> EChanges:
    """
    Imports all importable files from a specified directory
    
    :param reset:       Whether to clear data from the model first.
    :param directory:   Name of directory to import
    :param filter:      Filter files to import.
    :param query:       Query the directory (don't import anything).
    """
    if reset:
        if not query:
            file_new()
        else:
            MCMD.print( "Importing will start a new model." )
    
    importation.import_directory( global_view.current_model(), directory, query, filter )
    
    if query:
        return EChanges.NONE
    
    if reset:
        if MENV.host.is_cli:
            console_explorer.re_cd( PathToVisualisable.root_path( MENV.root ) )
        
        return EChanges.MODEL_OBJECT
    else:
        return EChanges.MODEL_ENTITIES


@command( names = ["file_load", "load"] )
def file_load( file_name: Filename[EFileMode.READ] ) -> EChanges:
    """
    Loads the model from a file
    
    :param file_name:   File to load.
                        If you don't specify a path, the `$(DATA_FOLDER)sessions` folder will be assumed
                        (If you'd like to use the current "working" directory, use the prefix `./`)
    """
    file_name = __fix_path( file_name )
    marshal.load_from_file( file_name )
    
    return EChanges.MODEL_OBJECT


def __fix_path( file_name: str ) -> str:
    """
    Adds the directory to the filename, if not specified.
    """
    if path.sep not in file_name:
        file_name = path.join( MENV.local_data.local_folder( "sessions" ), file_name )
    
    if not file_helper.get_extension( file_name ):
        file_name += ".groot"
    
    return file_name
