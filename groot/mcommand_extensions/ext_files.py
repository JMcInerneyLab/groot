import os
import sys
from os import path
from typing import Optional

from colorama import Fore

from groot import constants
from groot.algorithms import importation
from groot.data import global_view, user_options
from groot.frontends.gui.gui_view_utils import Changes
from mcommand import MCMD, MENV, PathToVisualisable, command, console_explorer
from mhelper import file_helper, io_helper


@command(names=["file_sample", "sample"])
def file_sample( name: Optional[ str ] = None, view: bool = False ) -> Changes:
    """
    Lists the available samples, or loads the specified sample
    :param view:    When set the sample is viewed but not loaded.
    :param name:    Name of sample 
    :return: 
    """
    if name:
        file_name = path.join( global_view.get_sample_data_folder(), name )
        
        if not path.isdir( file_name ):
            raise ValueError( "'{}' is not a valid sample directory.".format( name ) )
        
        if view:
            MCMD.print( 'import_directory "{}"'.format( file_name ) )
        else:
            MCMD.print( "Loading sample dataset. This is the same as running 'import.directory' on \"{}\".".format( file_name ) )
            return import_directory( file_name )
    else:
        for sample_dir in global_view.get_samples():
            MCMD.print( file_helper.get_filename( sample_dir ) )
        
        return Changes( Changes.NONE )


@command(names=["file_new", "new"])
def file_new() -> Changes:
    """
    Starts a new model
    """
    global_view.new_model()
    MCMD.print( "New model instantiated." )
    
    return Changes( Changes.MODEL_OBJECT )


@command()
def import_blast( file_name: str ) -> Changes:
    """
    Imports a BLAST file into the model 
    :param file_name:   File to import 
    :return: 
    """
    with MCMD.action( "Importing BLAST" ):
        importation.import_blast( global_view.current_model(), file_name )
    
    return Changes( Changes.MODEL_ENTITIES )


@command()
def import_composites( file_name: str ) -> Changes:
    """
    Imports a composites file into the model
    :param file_name:   File to import 
    :return: 
    """
    with MCMD.action( "Importing composites" ):
        importation.import_composites( global_view.current_model(), file_name )
        
    return Changes( Changes.MODEL_ENTITIES )


@command()
def import_fasta( file_name: str ) -> Changes:
    """
    Imports a FASTA file into the model
    :param file_name:   File to import 
    :return: 
    """
    with MCMD.action( "Importing FASTA" ):
        importation.import_fasta( global_view.current_model(), file_name )
    
    return Changes( Changes.MODEL_ENTITIES )

@command()
def import_file( file_name: str ) -> Changes:
    """
    Imports a file into the model
    :param file_name:   File to import 
    :return: 
    """
    with MCMD.action( "Importing file" ):
        importation.import_file( global_view.current_model(), file_name )
    
    return Changes ( Changes.MODEL_ENTITIES )


@command(names=["file_recent", "recent"])
def file_recent():
    """
    Prints the contents of the `sessions` folder
    """
    r = [ ]
    
    r.append( "SESSIONS:" )
    for file in os.listdir( path.join( MENV.local_data.workspace(), "sessions" ) ):
        if file.lower().endswith(constants.BINARY_EXTENSION):
            r.append( file_helper.highlight_file_name_without_extension( file, Fore.YELLOW, Fore.RESET ) )
    
    r.append( "\nRECENT:" )
    for file in user_options.options().recent_files:
        if file.lower().endswith(constants.BINARY_EXTENSION):
            r.append( file_helper.highlight_file_name_without_extension( file, Fore.YELLOW, Fore.RESET ) )
    
    MCMD.information( "\n".join( r ) )



@command(names=["file_save", "save"])
def file_save( file_name: Optional[ str ] = None ) -> Changes:
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
    
    user_options.remember_file( file_name )
    
    sys.setrecursionlimit( 10000 )
    
    with MCMD.action( "Saving file" ):
        io_helper.save_binary( file_name, model )
    
    model.file_name = file_name
    MCMD.print("Saved model: {}".format(file_name))
    
    return Changes( Changes.FILE_NAME )


@command()
def import_directory( directory: str, reset: bool = True ):
    """
    Imports all importable files from a specified directory
    :param reset:     Whether to clear data from the model first.
    :param directory: Name of directory to import
    :return: 
    """
    if reset:
        file_new()
    
    with MCMD.action( "Importing directory" ):
        importation.import_directory( global_view.current_model(), directory )
    
    if reset:
        console_explorer.re_cd( PathToVisualisable.root_path( MENV.root  ) )
        return Changes( Changes.MODEL_OBJECT )
    else:
        return Changes( Changes.MODEL_ENTITIES )


@command(names=["file_load", "load"])
def file_load( file_name: str) -> Changes:
    """
    Loads the model from a file
    :param file_name:   File to load.
                        The `sessions` folder will also assumed if you don't specify a path.
                        Prefix `./` to force a write to the working directory instead.
    """
    file_name = __fix_path( file_name )
    model = io_helper.load_binary( file_name )
    model.file_name = file_name
    global_view.set_model( model )
    user_options.remember_file( file_name )
    MCMD.print( "Loaded model: {}".format(file_name) )
    
    return Changes( Changes.MODEL_OBJECT )





def __fix_path( file_name: str ) -> str:
    """
    Adds the directory to the filename, if not specified.
    """
    if path.sep not in file_name:
        file_name = path.join( MENV.local_data.local_folder( "sessions" ), file_name )
    
    if not file_helper.get_extension(file_name):
        file_name += ".groot"
    
    return file_name


