"""
Sets up Intermake to run Groot.
This is called in `groot.__init__`.
"""
import intermake

from groot import constants
from . import coercers


#
# Override the basic console-UI to change the prompt to reflect the model
#
class _GrootConsoleController( intermake.ConsoleController ):
    def on_get_prompt( self ):
        from groot.data import global_view
        return "{}>".format( global_view.current_model() )


#
# Override the basic application to provide our custom UI and store the command
# history in the model itself
#
class Application( intermake.Application ):
    INSTANCE = None
    
    
    def on_executed( self, args: intermake.Result ):
        super().on_executed( args )
        
        from groot import global_view
        model = global_view.current_model()
        
        if model:
            model.command_history.append( "{}".format( args ) )
    
    
    def on_create_controller( self, mode: str ):
        if mode in (intermake.EImRunMode.ARG, intermake.EImRunMode.CLI, intermake.EImRunMode.PYI, intermake.EImRunMode.PYS, intermake.EImRunMode.JUP):
            r = _GrootConsoleController( self, mode )
        elif mode == intermake.EImRunMode.GUI:
            import groot_gui
            r = groot_gui.LegoGuiController( self, mode )
        else:
            r = super().on_create_controller( mode )
        
        coercers.setup( r.coercers )
        
        return r


#
# Define our application
#
Application.INSTANCE = Application( name = "groot",
                                    version = "0.0.0.61" )
