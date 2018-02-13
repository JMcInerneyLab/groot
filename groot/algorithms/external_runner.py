import os
import shutil
from typing import Optional
from intermake.engine import constants
from intermake.engine.environment import MENV
from mhelper import file_helper


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


