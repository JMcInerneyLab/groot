import os
from os import path
from typing import List

from groot import constants
from intermake.engine.environment import Controller
from mhelper import file_helper


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
    return file_helper.list_sub_dirs( sample_data_folder )


def get_workspace_files() -> List[str]:
    """
    INTERNAL
    
    Obtains the list of workspace files
    """
    r = []
    
    for file in os.listdir( path.join( Controller.ACTIVE.app.local_data.get_workspace(), "sessions" ) ):
        if file.lower().endswith( constants.EXT_MODEL ):
            r.append( file )
    
    return r


def get_sample_data_folder( name: str = None ):
    """
    PRIVATE
    
    Obtains the sample data folder
    """
    sdf = Controller.ACTIVE.app.local_data.local_folder( "sample_data" )
    
    if not name:
        return sdf
    
    if path.sep in name:
        return name
    
    return path.join( sdf, name )
