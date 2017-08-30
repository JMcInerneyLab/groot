import os
import shutil

from mcommand import current_environment, constants
from mhelper import FileHelper


def run_in_temporary(command, *args, **kwargs):
    temp_folder_name = os.path.join( current_environment().local_data.local_folder( constants.FOLDER_TEMPORARY ), "generate-tree" )
    
    if os.path.exists( temp_folder_name ):
        shutil.rmtree( temp_folder_name )
        
    FileHelper.create_directory( temp_folder_name )
    os.chdir( temp_folder_name )
    
    try:
        return command(*args, **kwargs)
    finally:
        os.chdir( ".." )
        shutil.rmtree(temp_folder_name)
