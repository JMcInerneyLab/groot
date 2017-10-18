from colorama import Fore
from ete3 import Tree

from groot import constants
from groot.data.graphing import MGraph
from groot.data.lego_model import LegoModel




def tree_to_ascii( target : MGraph, model:LegoModel):
    ascii = tree_from_newick( target.to_newick() ).get_ascii( show_internal = True )
    
    for sequence in model.sequences:
        colour = constants.COMPONENT_COLOURS_ANSI[ sequence.component.index % len( constants.COMPONENT_COLOURS_ANSI ) ]
        ascii = ascii.replace( sequence.accession, colour + sequence.accession + Fore.RESET )
        
    return ascii 


def show_tree( target : MGraph, model:LegoModel ):
    tree__ = tree_from_newick( target.to_newick() )
    colours = [ "#C00000", "#00C000", "#C0C000", "#0000C0", "#C000C0", "#00C0C0", "#FF0000", "#00FF00", "#FFFF00", "#0000FF", "#FF00FF", "#00FFC0" ]
    
    for n in tree__.traverse():
        n.img_style[ "fgcolor" ] = "#000000"
    
    for node in tree__:
        sequence = model.find_sequence( node.name )
        node.img_style[ "fgcolor" ] = colours[ sequence.component.index % len( colours ) ]
    
    tree__.show()
    
def tree_from_newick( newick: str ) -> Tree:
    try:
        return Tree( newick, format = 0 )
    except:
        return Tree( newick, format = 1 )