import os
import shutil
from uuid import uuid4
from warnings import warn
import groot.data.config
import intermake
from mhelper import file_helper


def run_in_temporary( function, *args, **kwargs ):
    """
    Sets the working directory to a temporary folder inside the current working directory.
    Calls `function`
    Then deletes the temporary folder and returns to the original working directory. 
    """
    #
    # Create and switch to temporary folder
    #
    id = uuid4()
    temp_folder_name = os.path.join( intermake.Controller.ACTIVE.app.local_data.local_folder( intermake.constants.FOLDER_TEMPORARY ), "temporary_{}".format( id ) )
    
    if os.path.exists( temp_folder_name ):
        shutil.rmtree( temp_folder_name )
    
    file_helper.create_directory( temp_folder_name )
    os.chdir( temp_folder_name )
    
    #
    # Run the command
    #
    try:
        return function( *args, **kwargs )
    except Exception:
        for file in file_helper.list_dir( "." ):
            intermake.pr.printx( "*** DUMPING FILE BECAUSE AN ERROR OCCURRED: {} ***".format( intermake.pr.fmt_file( file ) ) )
            for index, line in enumerate( file_helper.read_all_lines( file ) ):
                intermake.pr.printx( "LINE {}: {} ".format( index, intermake.pr.escape( line ) ) )
            intermake.pr.printx( "*** END OF FILE ***" )
        
        raise
    finally:
        os.chdir( ".." )
        if groot.data.config.options().debug_external_tool:
            warn( "The directory '{}' has not been deleted because of the `debug_external_tool` flag.".format( temp_folder_name ), UserWarning )
        else:
            #
            # Remove temporary folder
            #
            shutil.rmtree( temp_folder_name )
