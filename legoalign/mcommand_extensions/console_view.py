from colorama import Fore, Back

from legoalign.LegoModels import LegoModel, ESiteType


PROTEIN_COLOUR_TABLE = { "G"  : Fore.WHITE           , "A" : Fore.WHITE,                "V" : Fore.WHITE,   "L" : Fore.WHITE,   "I" : Fore.WHITE,
                         "F"  : Fore.MAGENTA         , "Y" : Fore.MAGENTA,              "W" : Fore.MAGENTA,
                         "C"  : Fore.YELLOW          , "M" : Fore.YELLOW,               
                         "S"  : Fore.GREEN           , "T" : Fore.GREEN,                
                         "K"  : Fore.RED             , "R" : Fore.RED,                  "H" : Fore.RED,
                         "D"  : Fore.CYAN            , "E" : Fore.CYAN,
                         "N"  : Fore.LIGHTMAGENTA_EX , "Q" : Fore.LIGHTMAGENTA_EX,
                         "P"  : Fore.LIGHTRED_EX }

DNA_COLOUR_TABLE     = { "A": Fore.YELLOW,"T":Fore.RED,"C":Fore.GREEN,"G":Fore.LIGHT_BLUE }
RNA_COLOUR_TABLE     = { "A": Fore.YELLOW,"U":Fore.RED,"C":Fore.GREEN,"G":Fore.LIGHT_BLUE }


def colour_fasta_ansi( model:LegoModel,array ):
    if model.site_type == ESiteType.PROTEIN:
        table = PROTEIN_COLOUR_TABLE
    elif model.site_type == ESiteType.DNA:
        table = DNA_COLOUR_TABLE
    elif model.site_type == ESiteType.RNA:
        table = RNA_COLOUR_TABLE
    else:
        table = {}
    
    res = []
    
    for line in array.split("\n"):
        if line.startswith(">"):
            res.append(Back.LIGHTBLACK_EX+ line+Back.RESET)
        else:
            strr = []
            
            for char in line:
                strr.append( table.get(char, Fore.LIGHTBLACK_EX) )
                
            res.append("".join(strr))
    
    return "\n".join( res )