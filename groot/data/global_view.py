from typing import cast, List

from os import path
import os
import time
from groot import constants
from groot.data.lego_model import LegoModel
from groot.frontends.gui.gui_view_utils import LegoSelection
from intermake import MENV, PathToVisualisable
from intermake.engine.environment import MENV
from intermake.hosts.console import ConsoleHost
from mhelper import file_helper, MEnum, array_helper


__model: LegoModel = None
__selection: LegoSelection = LegoSelection()
__selection_changed = set()


def subscribe_to_selection_changed( fn ):
    __selection_changed.add( fn )


def unsubscribe_from_selection_changed( fn ):
    __selection_changed.remove( fn )


def current_status():
    return _current_status()


class _current_status:
    def __init__( self ):
        model = current_model()
        self.is_file = bool( model.file_name )
        self.is_align = (not model.components.is_empty and all( x.alignment is not None for x in model.components ))
        self.is_blast = (len( model.edges ) != 0)
        self.is_fasta = (len( model.sequences ) != 0 and all( x.site_array for x in model.sequences ))
        self.is_fusions = (bool( model.fusion_events ))
        self.is_comps = (len( model.components ) != 0)
        self.is_trees = (not model.components.is_empty and all( x.tree is not None for x in model.components ))
        self.is_nrfg = (model.nrfg is not None)
        self.is_any_data = self.is_blast or self.is_fasta
        self.is_empty = not self.is_file and not self.is_any_data
        self.file_name = model.file_name
        self.domains = (len( model.user_domains ) != 0)
        self.num_sequences = len( model.sequences )
        self.num_components = len( model.components )
        self.num_alignments = sum( len( x.minor_subsequences ) for x in model.components if x.alignment )
        self.num_trees = sum( 1 for x in model.components if x.tree )
        self.num_fusions = len( model.fusion_events )
        self.num_domains = len( model.user_domains )


def current_model() -> LegoModel:
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
    MENV.root = model
    
    if isinstance( MENV.host, ConsoleHost ):
        MENV.host.browser_path = PathToVisualisable.root_path( MENV.root )
    
    return __model


def new_model():
    set_model( LegoModel() )


new_model()


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


def get_sample_data_folder():
    """
    PRIVATE
    Obtains the sample data folder
    """
    return path.join( file_helper.get_directory( __file__, 2 ), "sampledata" )


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
    :attr visjs_path:   Path to locate vis-js.
    """
    
    
    def __init__( self ):
        self.recent_files: List[RecentFile] = []
        self.visjs_path = ""
        self.browse_mode = EBrowseMode.ASK
        self.startup_mode = EStartupMode.STARTUP


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
