from legoalign.data.lego_model import LegoModel
from mcommand import MENV, console_explorer, PathToVisualisable
from mcommand.hosts.console import ConsoleHost


__model = None


def current_model() -> LegoModel:
    return __model


def set_model( model ):
    global __model
    __model = model
    MENV.root = model
    
    if isinstance( MENV.host, ConsoleHost ):
        MENV.host.browser_path = PathToVisualisable( [ MENV.root ] )
    
    return __model


def new_model():
    set_model( LegoModel() )


new_model()
