import os
import shutil
from typing import Sequence

from intermake.engine import constants
from intermake.engine.constants import EStream
from intermake.engine.environment import MCMD, MENV
from mhelper import file_helper, async_helper

def _print_1(x):
    MCMD.print(x, stream = EStream.EXTERNAL_STDOUT)
    
def _print_2(x):
    MCMD.print(x, stream = EStream.EXTERNAL_STDERR)

def run_subprocess( command: Sequence[str] ):
    """
    Runs the specified subprocess
    :param command: Commands and arguments 
    :return: 
    """
    async_helper.async_run(command, _print_1, _print_2, check = True)


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