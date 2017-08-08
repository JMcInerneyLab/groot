from os import path

import mcommand
from mcommand.engine.environment import Environment
from mcommand.hosts.console import ConsoleHost
from mhelper import FileHelper



def main( ) -> None:
    """
    Entry point
    """

    from legoalign.mcommand_extensions.lego_controller import _current_model
    env = Environment( ConsoleHost.default_command_interactive(), "glego", "0.0.0.0", _current_model(), None, None)
    
    folder = path.join(    FileHelper.get_directory( __file__ ), "mcommand_extensions") 
    
    env.plugins.load_defaults()
    env.plugins.load_folder(folder, "legoalign.mcommand_extensions")
    
    mcommand.initialise(env)
    
    mcommand.start_cli(history_file = "~/.legoalign_history")
    





# As executable only
if __name__ == "__main__":
    main( )
