from groot import constants
from intermake import command, MCMD, Theme

from groot.constants import STAGES, EChanges
from groot.data import global_view


__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME_EXTRA

@command( names = ["print_status", "status"], highlight = True, folder = constants.F_PRINT )
def print_status() -> EChanges:
    """
    Prints the status of the model. 
    :return: 
    """
    model = global_view.current_model()
    r = []
    
    r.append( Theme.HEADING + model.name + Theme.RESET + "\n" )
    if model.file_name:
        r.append( "File name:          {}\n".format( model.file_name ) )
    else:
        r.append( Theme.WARNING + "Not saved" + Theme.RESET + "\n" )
    for stage in STAGES:
        status = model.get_status( stage )
        
        r.append( ("{}. {}:".format( stage.index, stage.name )).ljust( 20 ) )
        
        if status.is_complete:
            r.append( Theme.STATUS_YES + str( status ) + Theme.RESET )
        else:
            if status.is_partial:
                r.append( Theme.STATUS_INTERMEDIATE + str( status ) + Theme.RESET )
            else:
                r.append( Theme.STATUS_NO + str( status ) + Theme.RESET )
            
            if status.is_hot:
                r.append( " - Consider running " + Theme.COMMAND_NAME + "create_" + MCMD.host.translate_name( stage.name ) + Theme.RESET )
        
        r.append( "\n" )
    
    MCMD.print( "".join( r ) )
    return EChanges.INFORMATION
