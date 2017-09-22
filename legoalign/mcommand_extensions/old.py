from os import path
from typing import Optional, TypeVar

from legoalign.data.lego_model import LegoComponent, LegoModel
from legoalign.data.user_options import GlobalOptions
from mcommand.engine.environment import MENV
from mhelper import file_helper, io_helper


T = TypeVar( "T" )









def _current_model() -> LegoModel:
    """
    INTERNAL
    Retrieves the current model 
    """
    return __model


def _current_options() -> GlobalOptions:
    """
    INTERNAL
    Retrieves the current options
    """
    return __global_options









def _save_global_options():
    """
    INTERNAL
    Saves the global options file
    """
    io_helper.save_binary( __global_options_file_name(), __global_options )


__model = LegoModel()

