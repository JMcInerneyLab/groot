import time
from typing import List

from groot.constants import EFormat, EStartupMode, EWindowMode, EDomainNames, EGeneNames, EFusionNames, EComponentNames
from intermake.engine.abstract_controller import Controller
from mhelper import TTristate, array_helper


class RecentFile:
    """
    Holds a file and when it was last accessed.
    """
    
    
    def __init__( self, file_name ):
        self.file_name = file_name
        self.time = time.time()
    
    
    def __repr__( self ):
        return repr( self.file_name )


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
    :ivar debug_external_tool:      Do not remove files created when invoking external tools.
    :ivar domain_namer:             How the names of various entities are displayed.
    :ivar fusion_namer:             How the names of various entities are displayed.
                                    Affects fusion events, formations, and points; pregraphs; subsets; supertrees; and the NRFG.
    :ivar gene_namer:               How the names of various entities are displayed.
    :ivar fusion_namer:             How the names of various entities are displayed.
    :ivar component_namer:          How the names of various entities are displayed.      
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
        self.debug_external_tool: bool = False
        self.domain_namer = EDomainNames.START_END
        self.fusion_namer = EFusionNames.ACCID
        self.gene_namer = EGeneNames.DISPLAY
        self.component_namer = EComponentNames.ACCID


__global_options = None


def options() -> GlobalOptions:
    global __global_options
    
    if __global_options is None:
        __global_options = Controller.ACTIVE.app.local_data.store.bind( "lego_options", GlobalOptions() )
    
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
    Controller.ACTIVE.app.local_data.store.commit( __global_options )
