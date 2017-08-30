from colorama import Fore, Back, Style

from legoalign.LegoModels import LegoModel, ESiteType


PROTEIN_COLOUR_TABLE = { "G"  : Fore.WHITE           , "A" : Fore.WHITE,                "V" : Fore.WHITE,   "L" : Fore.WHITE,   "I" : Fore.WHITE,
                         "F"  : Fore.MAGENTA         , "Y" : Fore.MAGENTA,              "W" : Fore.MAGENTA,
                         "C"  : Fore.YELLOW          , "M" : Fore.YELLOW,               
                         "S"  : Fore.GREEN           , "T" : Fore.GREEN,                
                         "K"  : Fore.RED             , "R" : Fore.RED,                  "H" : Fore.RED,
                         "D"  : Fore.CYAN            , "E" : Fore.CYAN,
                         "N"  : Fore.LIGHTMAGENTA_EX , "Q" : Fore.LIGHTMAGENTA_EX,
                         "P"  : Fore.LIGHTRED_EX }

DNA_COLOUR_TABLE     = { "A": Fore.YELLOW,"T":Fore.RED,"C":Fore.GREEN,"G":Fore.LIGHTBLUE_EX }
RNA_COLOUR_TABLE     = { "A": Fore.YELLOW,"U":Fore.RED,"C":Fore.GREEN,"G":Fore.LIGHTBLUE_EX }


def colour_fasta_ansi( model:LegoModel,array ):
    if model.site_type == ESiteType.PROTEIN:
        table = PROTEIN_COLOUR_TABLE
    elif model.site_type == ESiteType.DNA:
        table = DNA_COLOUR_TABLE
    elif model.site_type == ESiteType.RNA:
        table = RNA_COLOUR_TABLE
    else:
        table = {}
    
    result = []
    
    for line in array.split("\n"):
        if line.startswith(">"):
            result.append(Back.LIGHTBLACK_EX+ line+Back.RESET)
        else:
            result_line = []
            
            for char in line:
                result_line.append( table.get(char, Fore.LIGHTBLACK_EX) + char )
                
            result.append("".join(result_line) + Style.RESET_ALL )
    
    return "\n".join( result )