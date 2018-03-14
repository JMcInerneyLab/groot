import os
import time
from os import path
from typing import List

from groot import constants
from groot.data.lego_model import LegoModel
from groot.frontends.gui.gui_view_utils import LegoSelection
from intermake import PathToVisualisable
from intermake.engine.environment import MENV
from intermake.hosts.console import ConsoleHost
from mhelper import MEnum, array_helper, file_helper


__model: LegoModel = None
__selection: LegoSelection = LegoSelection()
__selection_changed = set()


def subscribe_to_selection_changed( fn ):
    __selection_changed.add( fn )


def unsubscribe_from_selection_changed( fn ):
    __selection_changed.remove( fn )

def current_model() -> LegoModel:
    if __model is None:
        new_model()
    
    return __model


def current_selection() -> LegoSelection:
    return __selection


def set_selection( value: LegoSelection ):
    global __selection
    __selection = value
    
    for fn in __selection_changed:
        fn()


def set_model( model ):
    global __model
    __model = model
    MENV.configure( using = constants.APP_NAME,
                    root = model )
    
    if isinstance( MENV.host, ConsoleHost ):
        MENV.host.browser_path = PathToVisualisable.root_path( MENV.root )
    
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


def get_sample_data_folder( name: str = None ):
    """
    PRIVATE
    Obtains the sample data folder
    """
    sdf = path.join( file_helper.get_directory( __file__, 2 ), "sample_data" )
    
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
        self.visjs_component_view = False


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
