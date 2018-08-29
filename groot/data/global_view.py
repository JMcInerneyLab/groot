from intermake import MCMD, ConsoleHost, VisualisablePath
from mhelper import exception_helper
from groot.data.model import Model



__model: Model = None


def current_model() -> Model:
    if __model is None:
        new_model()
    
    return __model


def set_model( model: Model ):
    from groot.application import GROOT_APP
    exception_helper.assert_type( "model", model, Model )
    global __model
    __model = model
    GROOT_APP.root = model
    
    if isinstance( MCMD.host, ConsoleHost ):
        MCMD.host.browser_path = VisualisablePath.get_root()
    
    return __model


def new_model():
    set_model( Model() )


new_model()
