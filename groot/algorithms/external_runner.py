import inspect
import os
import shutil
from collections import defaultdict
from typing import Callable, Dict, Optional

from groot.algorithms import external_tools
from intermake.engine import constants
from intermake.engine.environment import MENV
from mhelper import MEnum, file_helper


class EAlgoType( MEnum ):
    TREE = 1
    ALIGN = 2


def run_in_temporary( function, *args, **kwargs ):
    """
    Sets the working directory to a temporary folder inside the current working directory.
    Calls `function`
    Then deletes the temporary folder and returns to the original working directory. 
    """
    temp_folder_name = os.path.join( MENV.local_data.local_folder( constants.FOLDER_TEMPORARY ), "generate-tree" )
    
    if os.path.exists( temp_folder_name ):
        shutil.rmtree( temp_folder_name )
    
    file_helper.create_directory( temp_folder_name )
    os.chdir( temp_folder_name )
    
    try:
        return function( *args, **kwargs )
    finally:
        os.chdir( ".." )
        shutil.rmtree( temp_folder_name )


def get_tool( prefix, tool: Optional[str] ):
    """
    Gets the specified function from the `external_tools` module.
    """
    if not tool:
        tool = "default"
    
    name = prefix + "_" + tool
    
    try:
        return getattr( external_tools, name )
    except AttributeError:
        raise ValueError( "No such «{}» algorithm as «{}». (the «{}» function does not exist in the `external_tools` module.)".format( prefix, tool, name ) )


def list_algorithms() -> Dict[EAlgoType, Dict[str, Callable]]:
    d = defaultdict( dict )
    
    for attr_name, attr_value in external_tools.__dict__.items():
        if not attr_name.startswith( "_" ) and "_" in attr_name and inspect.isfunction( attr_value ):
            prefix, suffix = attr_name.split( "_", 1 )
            
            if prefix == "tree":
                algo_type = EAlgoType.TREE
            elif prefix == "align":
                algo_type = EAlgoType.ALIGN
            else:
                continue
            
            d[algo_type][suffix] = attr_value
    
    return dict( d )
