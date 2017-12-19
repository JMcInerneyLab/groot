from typing import Optional, List

from colorama import Back, Fore, Style

from groot.data import global_view
from groot.data.lego_model import ESiteType, LegoComponent


PROTEIN_COLOUR_TABLE = { "G": Fore.WHITE, "A": Fore.WHITE, "V": Fore.WHITE, "L": Fore.WHITE, "I": Fore.WHITE,
                         "F": Fore.MAGENTA, "Y": Fore.MAGENTA, "W": Fore.MAGENTA,
                         "C": Fore.YELLOW, "M": Fore.YELLOW,
                         "S": Fore.GREEN, "T": Fore.GREEN,
                         "K": Fore.RED, "R": Fore.RED, "H": Fore.RED,
                         "D": Fore.CYAN, "E": Fore.CYAN,
                         "N": Fore.LIGHTMAGENTA_EX, "Q": Fore.LIGHTMAGENTA_EX,
                         "P": Fore.LIGHTRED_EX }

DNA_COLOUR_TABLE = { "A": Fore.YELLOW, "T": Fore.RED, "C": Fore.GREEN, "G": Fore.LIGHTBLUE_EX }
RNA_COLOUR_TABLE = { "A": Fore.YELLOW, "U": Fore.RED, "C": Fore.GREEN, "G": Fore.LIGHTBLUE_EX }


def colour_fasta_ansi( array : str, site_type : Optional[ESiteType ] = None ):
    table = __table_from_type( site_type )
    
    result = [ ]
    
    first = True
    
    for line in array.split( "\n" ):
        if line.startswith( ">" ):
            if first:
                first = False
            else:
                result.append("\n")
            
            result.append( Back.LIGHTBLACK_EX + line.ljust(20) + Back.RESET + "\n" )
        else:
            result_line = [ ]
            
            for char in line:
                result_line.append( table.get( char, Fore.LIGHTBLACK_EX ) + char )
            
            result.append( "".join( result_line ) + Style.RESET_ALL )
    
    return "".join( result )



def __table_from_type( st ):
    if st == ESiteType.PROTEIN:
        table = PROTEIN_COLOUR_TABLE
    elif st == ESiteType.DNA:
        table = DNA_COLOUR_TABLE
    elif st == ESiteType.RNA:
        table = RNA_COLOUR_TABLE
    else:
        table = { }
    return table


def get_component_list( component: Optional[ List[LegoComponent] ] ):
    if component is not None:
        to_do = component
    else:
        to_do = global_view.current_model().components
        
        if not to_do:
            raise ValueError("No components available, consider running `make_components`.")
        
    return to_do