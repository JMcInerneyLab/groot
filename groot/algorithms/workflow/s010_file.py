import sys
from os import path
from typing import Optional

import groot.data.config
import groot.data.sample_data
from groot.algorithms.gimmicks import wizard
from intermake import ImApplication, Theme, command, visibilities, pr
from mhelper import EFileMode, Filename, MOptional, file_helper, io_helper

from groot import constants
from groot.data import global_view
from groot.data.model import Model
from groot.constants import EChanges




@command( names = ["file_new", "new"], folder = constants.F_FILE )
def file_new() -> EChanges:
    """
    Starts a new model
    """
    global_view.new_model()
    print( "<verbose>New model instantiated.</verbose>" )
    
    return EChanges.MODEL_OBJECT


@command( names = ["file_save", "save"], folder = constants.F_FILE )
def file_save( file_name: MOptional[Filename[EFileMode.WRITE, constants.EXT_GROOT]] = None ) -> EChanges:
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
    
    groot.data.config.remember_file( file_name )
    
    sys.setrecursionlimit( 10000 )
    
    with pr.pr_action( "Saving file to «{}»".format( file_name ) ):
        model.file_name = file_name
        io_helper.save_binary( file_name, model )
    
    model.file_name = file_name
    print( "<verbose>Saved model to «{}»</verbose>".format( file_name ) )
    
    return EChanges.FILE_NAME


@command( folder = constants.F_FILE, visibility = visibilities.ADVANCED )
def export_json( file_name: Filename[EFileMode.WRITE, constants.EXT_JSON] ) -> EChanges:
    """
    Exports the entirety of the current model into a JSON file for reading by external programs.
    
    :param file_name:   Name of file to export to.
    """
    model = global_view.current_model()
    io_helper.save_json( file_name, model )
    return EChanges.NONE


@command( names = ["file_load", "load"], folder = constants.F_FILE )
def file_load( file_name: Filename[EFileMode.READ] ) -> EChanges:
    """
    Loads the model from a file
    
    :param file_name:   File to load.
                        If you don't specify a path, the following folders are attempted (in order):
                        * The current working directory
                        * `$(DATA_FOLDER)sessions`
    """
    
    if path.isfile( file_name ):
        file_name = path.abspath( file_name )
    else:
        file_name = __fix_path( file_name )
    
    try:
        model: Model = io_helper.load_binary( file_name, type_ = Model )
    except Exception as ex:
        raise ValueError( "Failed to load the model «{}». Either this is not a Groot model or this model was saved using a different version of Groot.".format( file_name ) ) from ex
    
    model.file_name = file_name
    
    global_view.set_model( model )
    groot.data.config.remember_file( file_name )
    print( "<verbose>Loaded model: {}</verbose>".format( file_name ) )
    
    return EChanges.MODEL_OBJECT


@command( names = ["file_sample", "sample", "samples"], folder = constants.F_FILE )
def file_sample( name: Optional[str] = None, query: bool = False, load: bool = False ) -> EChanges:
    """
    Lists the available samples, or loads the specified sample.
    
    :param name:    Name of sample. 
    :param query:   When set the sample is viewed but not loaded. 
    :param load:    When set data is imported but any scripts (if present) are not run.
    :return: 
    """
    if name:
        file_name = path.join( groot.data.sample_data.get_sample_data_folder(), name )
        
        if not path.isdir( file_name ):
            raise ValueError( "'{}' is not a valid sample directory.".format( name ) )
        
        if not query:
            print( "<verbose>Loading sample dataset «{}».</verbose>".format( file_name ) )
        else:
            print( "Sample data: «{}».".format( file_name ) )
        
        return wizard.import_directory( file_name, filter = (wizard.EImportFilter.DATA | wizard.EImportFilter.SCRIPT) if not load else wizard.EImportFilter.DATA, query = query )
    else:
        for sample_dir in groot.data.sample_data.get_samples():
            print( file_helper.get_filename( sample_dir ) )
        else:
            print( "No samples available. Please download and add sample data to `{}`.".format( groot.data.sample_data.get_sample_data_folder() ) )
        
        return EChanges.NONE


@command( names = ("file_load_last", "last"), folder = constants.F_FILE )
def file_load_last():
    """
    Loads the last file from the recent list.
    """
    if not groot.data.config.options().recent_files:
        raise ValueError( "Cannot load the last session because there are no recent sessions." )
    
    file_load( groot.data.config.options().recent_files[-1].file_name )


@command( names = ["file_recent", "recent"], folder = constants.F_FILE )
def file_recent():
    """
    Prints the contents of the `sessions` folder
    """
    r = []
    
    r.append( "SESSIONS:" )
    for file in groot.data.sample_data.get_workspace_files():
        r.append( file_helper.highlight_file_name_without_extension( file, Theme.BOLD, Theme.RESET ) )
    
    r.append( "\nRECENT:" )
    for file in reversed( groot.data.config.options().recent_files ):
        r.append( file_helper.highlight_file_name_without_extension( file.file_name, Theme.BOLD, Theme.RESET ) )
    
    print( "\n".join( r ) )


def __fix_path( file_name: str ) -> str:
    """
    Adds the directory to the filename, if not specified.
    """
    if path.sep not in file_name:
        file_name = path.join( ImApplication.ACTIVE.local_data.local_folder( "sessions" ), file_name )
    
    if not file_helper.get_extension( file_name ):
        file_name += ".groot"
    
    return file_name
