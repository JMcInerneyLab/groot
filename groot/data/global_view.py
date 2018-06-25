import os
import time
from os import path
from typing import List


from intermake import MCMD, ConsoleHost, VisualisablePath
from mhelper import MEnum, array_helper, file_helper, exception_helper, TTristate

from groot import constants
from groot.data.model import Model
from groot.constants import EFormat


__model: Model = None


def current_model() -> Model:
    if __model is None:
        new_model()
    
    return __model


def set_model( model: Model ):
    from groot.application import GROOT_APP
    exception_helper.assert_type( "model", model, Model )
    global __model
    __model = model
    GROOT_APP.root = model
    
    if isinstance( MCMD.host, ConsoleHost ):
        MCMD.host.browser_path = VisualisablePath.get_root()
    
    return __model


def new_model():
    set_model( Model() )


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
    
    for file in os.listdir( path.join( MCMD.environment.local_data.get_workspace(), "sessions" ) ):
        if file.lower().endswith( constants.BINARY_EXTENSION ):
            r.append( file )
    
    return r

def get_test_data_folder(name:str=None):
    sdf = MCMD.environment.local_data.local_folder("test_cases")
    
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
    sdf = MCMD.environment.local_data.local_folder("sample_data")
    
    if not name:
        return sdf
    
    if path.sep in name:
        return name
    
    return path.join( sdf, name )




class EStartupMode( MEnum ):
    """
    Which screen shows when `FrmMain` is shown.
    """
    STARTUP = 0
    WORKFLOW = 1
    SAMPLES = 2
    NOTHING = 3
    
class EWindowMode( MEnum ):
    """
    How `FrmMain` shows sub-windows.
    
    This was introduced because MDI/TDI cause problems on some platforms.
    """
    BASIC = 0
    MDI = 1
    TDI = 2


class RecentFile:
    """
    Holds a file and when it was last accessed.
    """
    def __init__( self, file_name ):
        self.file_name = file_name
        self.time = time.time()


class GlobalOptions:
    """
    :ivar recent_files:             Files recently accessed.
    :ivar startup_mode:             GUI startup window.
    :ivar window_mode:              GUI MDI mode.
    :ivar tool_file:                Toolbar visible: File
    :ivar tool_visualisers:         Toolbar visible: Visualisers 
    :ivar tool_workflow:            Toolbar visible: Workflow 
    :ivar gui_tree_view:            Preferred method of viewing trees in GUI.
    :ivar opengl:                   Use OpenGL rendering. Faster but may cause problems on some devices.
    :ivar share_opengl:             Share OpenGL contexts. Uses less memory but may cause problems on some devices.
    :ivar lego_y_snap:              Lego GUI setting - snap to Y axis.
    :ivar lego_x_snap:              Lego GUI setting - snap to X axis.
    :ivar lego_move_enabled:        Lego GUI setting - permit domain movement using mouse.
    :ivar lego_view_piano_roll:     Lego GUI setting - display gene piano rolls 
    :ivar lego_view_names:          Lego GUI setting - display gene names
    :ivar lego_view_positions:      Lego GUI setting - display domain start and end positions
    :ivar lego_view_components:     Lego GUI setting - display domain components  
    """
    
    
    def __init__( self ):
        self.recent_files: List[RecentFile] = []
        self.startup_mode = EStartupMode.STARTUP
        self.window_mode = EWindowMode.BASIC
        self.tool_file = True
        self.tool_visualisers = True
        self.tool_workflow = True
        self.gui_tree_view = EFormat.CYJS
        self.opengl = True
        self.share_opengl = True
        self.lego_y_snap: TTristate = None
        self.lego_x_snap: TTristate = None
        self.lego_move_enabled: TTristate = None
        self.lego_view_piano_roll: TTristate = None
        self.lego_view_names: TTristate = True
        self.lego_view_positions: TTristate = None
        self.lego_view_components: TTristate = None


__global_options = None


def options() -> GlobalOptions:
    global __global_options
    
    if __global_options is None:
        __global_options = MCMD.environment.local_data.store.bind( "lego-options", GlobalOptions() )
    
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
    MCMD.environment.local_data.store.commit( "lego-options", __global_options )


new_model()
