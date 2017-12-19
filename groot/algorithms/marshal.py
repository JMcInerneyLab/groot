from mhelper import io_helper

from groot.data.lego_model import LegoModel


def save_to_file( file_name: str, model: LegoModel ) -> None:
    io_helper.save_binary( file_name, model )


def load_from_file( file_name: str ) -> LegoModel:
    model: LegoModel = io_helper.load_binary( file_name )
    
    for edge in model.all_edges:
        edge.left.restore_state( model )
        edge.right.restore_state( model )
    
    model.file_name = file_name
    return model
