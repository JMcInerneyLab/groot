from typing import cast

from os import path

from groot.data.lego_model import LegoModel
from intermake import MENV, PathToVisualisable
from intermake.hosts.console import ConsoleHost
from mhelper import file_helper


__model = cast( LegoModel, None )


def current_model() -> LegoModel:
    return __model


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


def get_sample_data_folder():
    """
    PRIVATE
    Obtains the sample data folder
    """
    return path.join( file_helper.get_directory( __file__, 2 ), "sampledata" )