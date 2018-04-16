import os
import time
from os import path
from typing import List
from intermake import MENV, ConsoleHost, VisualisablePath
from mhelper import MEnum, array_helper, file_helper, exception_helper

from groot import constants
from groot.data.model import LegoModel
from groot.constants import EFormat


__model: LegoModel = None


def current_model() -> LegoModel:
    if __model is None:
        new_model()
    
    return __model


def set_model( model: LegoModel ):
    exception_helper.assert_type( "model", model, LegoModel )
    global __model
    __model = model
    MENV.configure( using = constants.APP_NAME,
                    root = model )
    
    if isinstance( MENV.host, ConsoleHost ):
        MENV.host.browser_path = VisualisablePath.get_root()
    
    return __model


def new_model():
    set_model( LegoModel() )


def get_sample_contents( name: str ) -> List[str]:
    if not path.sep in name:
        name = path.join( get_sample_data_folder(), name )
    
    all_files = file_helper.list_dir( name )
    
    return [x for x in all_files if x.endswith( ".blast" ) or x.endswith( ".fasta" )]


def get_samples():
    """
    INTERNAL
    Obtains the list of samples
    """
    sample_data_folder = get_sample_data_folder()
    return file_helper.sub_dirs( sample_data_folder )


def get_workspace_files() -> List[str]:
    """
    INTERNAL
    Obtains the list of workspace files
    """
    r = []
    
    for file in os.listdir( path.join( MENV.local_data.get_workspace(), "sessions" ) ):
        if file.lower().endswith( constants.BINARY_EXTENSION ):
            r.append( file )
    
    return r

def get_test_data_folder(name:str=None):
    sdf = MENV.local_data.local_folder("test_cases")
    
    if not name:
        return sdf
    
    if path.sep in name:
        return name
    
    return path.join( sdf, name )

def get_sample_data_folder( name: str = None ):
    """
    PRIVATE
    Obtains the sample data folder
    """
    sdf = MENV.local_data.local_folder("sample_data")
    
    if not name:
        return sdf
    
    if path.sep in name:
        return name
    
    return path.join( sdf, name )


class EBrowseMode( MEnum ):
    ASK = 0
    SYSTEM = 1
    INBUILT = 2


class EStartupMode( MEnum ):
    STARTUP = 0
    WORKFLOW = 1
    SAMPLES = 2
    NOTHING = 3
    
class EWindowMode( MEnum ):
    BASIC = 0
    MDI = 1
    TDI = 2


class RecentFile:
    def __init__( self, file_name ):
        self.file_name = file_name
        self.time = time.time()


class GlobalOptions:
    """
    :attr recent_files: Files recently accessed.
    """
    
    
    def __init__( self ):
        self.recent_files: List[RecentFile] = []
        self.browse_mode = EBrowseMode.ASK
        self.startup_mode = EStartupMode.STARTUP
        self.window_mode = EWindowMode.BASIC
        self.tool_file = True
        self.tool_visualisers = True
        self.tool_workflow = True
        self.gui_tree_view = EFormat.CYJS 


__global_options = None


def options() -> GlobalOptions:
    global __global_options
    
    if __global_options is None:
        __global_options = MENV.local_data.store.bind( "lego-options", GlobalOptions() )
    
    return __global_options


def remember_file( file_name: str ) -> None:
    """
    PRIVATE
    Adds a file to the recent list
    """
    opt = options()
    
    array_helper.remove_where( opt.recent_files, lambda x: not isinstance( x, RecentFile ) )  # remove legacy data
    
    for recent_file in opt.recent_files:
        if recent_file.file_name == file_name:
            opt.recent_files.remove( recent_file )
            break
    
    opt.recent_files.append( RecentFile( file_name ) )
    
    while len( opt.recent_files ) > 10:
        del opt.recent_files[0]
    
    save_global_options()


def save_global_options():
    MENV.local_data.store.commit( "lego-options" )


new_model()
