from typing import Optional, List


from intermake import Theme
from mhelper import ansi, bio_helper

from groot.data import global_view, Model, Gene, Component, ESiteType


PROTEIN_COLOUR_TABLE = { "G": ansi.FORE_WHITE, "A": ansi.FORE_WHITE, "V": ansi.FORE_WHITE, "L": ansi.FORE_WHITE, "I": ansi.FORE_WHITE,
                         "F": ansi.FORE_MAGENTA, "Y": ansi.FORE_MAGENTA, "W": ansi.FORE_MAGENTA,
                         "C": ansi.FORE_YELLOW, "M": ansi.FORE_YELLOW,
                         "S": ansi.FORE_GREEN, "T": ansi.FORE_GREEN,
                         "K": ansi.FORE_RED, "R": ansi.FORE_RED, "H": ansi.FORE_RED,
                         "D": ansi.FORE_CYAN, "E": ansi.FORE_CYAN,
                         "N": ansi.FORE_BRIGHT_MAGENTA, "Q": ansi.FORE_BRIGHT_MAGENTA,
                         "P": ansi.FORE_BRIGHT_RED,
                         "-": ansi.FORE_BRIGHT_BLACK }

DNA_COLOUR_TABLE = { "A": ansi.FORE_YELLOW, "T": ansi.FORE_RED, "C": ansi.FORE_GREEN, "G": ansi.FORE_BRIGHT_BLUE, "-": ansi.FORE_BRIGHT_BLACK }
RNA_COLOUR_TABLE = { "A": ansi.FORE_YELLOW, "U": ansi.FORE_RED, "C": ansi.FORE_GREEN, "G": ansi.FORE_BRIGHT_BLUE, "-": ansi.FORE_BRIGHT_BLACK }


def component_to_ansi( component: Component ) -> str:
    return component_to_ansi_fore( component ) + str( component ) + ansi.RESET


def component_to_ansi_fore( component: Component ):
    return Theme.PROGRESSION_FORE[component.index % len( Theme.PROGRESSION_FORE )]


def component_to_ansi_back( component: Component ):
    return Theme.PROGRESSION_BACK[component.index % len( Theme.PROGRESSION_BACK )]


def colour_fasta_ansi( array: str, site_type: Optional[ESiteType] = None, model: Model = None, x = 1, n = 99999 ):
    table = __table_from_type( site_type )
    
    result = []
    
    first = True
    
    for name, sites in bio_helper.parse_fasta( text = array ):
        if first:
            first = False
        else:
            result.append( "\n" )
        
        if model is not None:
            if Gene.is_legacy_accession( name ):
                name = model.genes.by_legacy_accession( name ).accession
        
        result.append( ansi.BACK_BRIGHT_BLACK + name.ljust( 20 ) + ansi.BACK_RESET + "\n" )
        
        result_line = []
        
        s = (x - 1)
        
        if s != 0:
            result_line.append( ansi.FORE_WHITE + ansi.BACK_BLUE + "…" + ansi.RESET )
        
        e = s + n
        
        for char in sites[s:e]:
            result_line.append( table.get( char, ansi.FORE_BRIGHT_BLACK ) + char )
        
        if e < len( sites ) - 1:
            result_line.append( ansi.FORE_WHITE + ansi.BACK_BLUE + "…" )
        
        result.append( "".join( result_line ) + ansi.RESET )
    
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


def get_component_list( component: Optional[List[Component]] ):
    if component is not None:
        to_do = component
    else:
        to_do = global_view.current_model().components
        
        if not to_do:
            raise ValueError( "No components available, consider running `create_major`." )
    
    return to_do


