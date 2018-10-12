from groot import constants
from intermake import command, printx, pr

from groot.constants import STAGES, EChanges
from groot.data import global_view





@command( names = ["print_status", "status"], highlight = True, folder = constants.F_PRINT )
def print_status() -> EChanges:
    """
    Prints the status of the model. 
    :return: 
    """
    model = global_view.current_model()
    
    with pr.pr_section( model.name ):
        r = []
        r.append( "<table>" )
        
        for stage in STAGES:
            status = model.get_status( stage )
            
            r.append( "<tr>" )
            r.append( "<td>{}</td>".format( ("{}. {}:".format( stage.index, stage.name )).ljust( 20 ) ) )
            
            if status.is_complete:
                r.append( "<td><positive>{}</positive></td>".format( status ) )
            else:
                if status.is_hot:
                    ex = " - Consider running <command>create_{}</command>".format( stage.name.lower() )
                else:
                    ex = ""
                
                if status.is_partial:
                    r.append( "<td><neutral>{}</neutral>{}".format( status, ex ) )
                else:
                    r.append( "<td><negative>{}</negative>{}".format( status, ex ) )
                
                r.append( "</td>" )
            
            r.append( "</tr>" )
        
        r.append( "</table>" )
        
        printx( "".join( r ) )
    
    return EChanges.INFORMATION
