from mhelper import exception_helper
from groot.data.model import Model



__model: Model = None


def current_model() -> Model:
    if __model is None:
        new_model()
    
    return __model


def set_model( model: Model ):
    exception_helper.safe_cast( "model", model, Model )
    global __model
    __model = model
    return __model


def new_model():
    set_model( Model() )


new_model()
