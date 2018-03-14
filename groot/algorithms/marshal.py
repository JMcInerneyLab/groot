import groot
from intermake.engine.environment import MCMD
from mhelper import io_helper

from groot.data import global_view
from groot.data.lego_model import LegoModel


def save_to_file( file_name: str, model: LegoModel = None ) -> None:
    if model is None:
        model = global_view.current_model()
    
    model.file_name = file_name
    io_helper.save_binary( file_name, model )


def load_from_file( file_name: str, set_current: bool = True ) -> LegoModel:
    model: LegoModel = io_helper.load_binary( file_name )
    model.file_name = file_name
    
    if set_current:
        global_view.set_model( model )
        groot.data.global_view.remember_file( file_name )
        MCMD.progress( "Loaded model: {}".format( file_name ) )
    
    return model
