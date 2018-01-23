from typing import Optional, List

from groot.algorithms.classes import FusionPoint
from mgraph import MNode
from mhelper import ansi, bio_helper
from groot.data import global_view
from groot.data.lego_model import ESiteType, LegoComponent, LegoModel, LegoSequence


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

COMPONENT_COLOURS_ANSI_FORE = [ansi.FORE_RED, ansi.FORE_GREEN, ansi.FORE_YELLOW, ansi.FORE_BLUE, ansi.FORE_MAGENTA, ansi.FORE_CYAN, ansi.FORE_BRIGHT_RED, ansi.FORE_BRIGHT_GREEN, ansi.FORE_BRIGHT_BLUE, ansi.FORE_BRIGHT_MAGENTA, ansi.FORE_BRIGHT_CYAN]
COMPONENT_COLOURS_ANSI_BACK = [ansi.BACK_RED, ansi.BACK_GREEN, ansi.BACK_YELLOW, ansi.BACK_BLUE, ansi.BACK_MAGENTA, ansi.BACK_CYAN, ansi.BACK_BRIGHT_RED, ansi.BACK_BRIGHT_GREEN, ansi.BACK_BRIGHT_BLUE, ansi.BACK_BRIGHT_MAGENTA, ansi.BACK_BRIGHT_CYAN]
COMPONENT_COLOURS_ANSI_COUNT = len( COMPONENT_COLOURS_ANSI_FORE )


def component_to_ansi( component: LegoComponent ) -> str:
    return component_to_ansi_fore( component ) + str( component ) + ansi.RESET


def component_to_ansi_fore( component: LegoComponent ):
    return COMPONENT_COLOURS_ANSI_FORE[component.index % len( COMPONENT_COLOURS_ANSI_FORE )]


def component_to_ansi_back( component: LegoComponent ):
    return COMPONENT_COLOURS_ANSI_BACK[component.index % len( COMPONENT_COLOURS_ANSI_BACK )]


def colour_fasta_ansi( array: str, site_type: Optional[ESiteType] = None, model: LegoModel = None ):
    table = __table_from_type( site_type )
    
    result = []
    
    first = True
    
    for name, sites in bio_helper.parse_fasta( text = array ):
        if first:
            first = False
        else:
            result.append( "\n" )
        
        if model is not None:
            if name.startswith( "S" ) and all( x.isdigit() for x in name[1:] ):
                name = model.find_sequence_by_id( int( name[1:] ) ).accession
        
        result.append( ansi.BACK_BRIGHT_BLACK + name.ljust( 20 ) + ansi.BACK_RESET + "\n" )
        
        result_line = []
        
        for char in sites:
            result_line.append( table.get( char, ansi.FORE_BRIGHT_BLACK ) + char )
        
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


def get_component_list( component: Optional[List[LegoComponent]] ):
    if component is not None:
        to_do = component
    else:
        to_do = global_view.current_model().components
        
        if not to_do:
            raise ValueError( "No components available, consider running `make_components`." )
    
    return to_do
