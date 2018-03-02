from colorama import Fore
from ete3 import Tree

from groot.data.lego_model import LegoModel
from intermake import Theme
from mgraph import DNodeToText, MGraph, exporting


def tree_to_ascii( target: MGraph, model: LegoModel, formatter : DNodeToText ):
    ascii = tree_from_newick( exporting.export_newick( target, fnode = formatter ) ).get_ascii( show_internal = True )
    
    for sequence in model.sequences:
        component = model.components.find_component_for_major_sequence(sequence)
        colour = Theme.PROGRESSION_FORE[component.index % Theme.PROGRESSION_COUNT]
        ascii = ascii.replace( sequence.accession, colour + sequence.accession + Fore.RESET )
    
    return ascii


def show_tree( target: MGraph, model: LegoModel, formatter : DNodeToText ):
    tree__ = tree_from_newick( exporting.export_newick( target, fnode = formatter ) )
    colours = ["#C00000", "#00C000", "#C0C000", "#0000C0", "#C000C0", "#00C0C0", "#FF0000", "#00FF00", "#FFFF00", "#0000FF", "#FF00FF", "#00FFC0"]
    
    for n in tree__.traverse():
        n.img_style["fgcolor"] = "#000000"
    
    for node in tree__:
        sequence = model.find_sequence_by_accession( node.name )
        component = model.components.find_component_for_major_sequence(sequence)
        node.img_style["fgcolor"] = colours[component % len( colours )]
    
    tree__.show()


def tree_from_newick( newick: str ) -> Tree:
    try:
        return Tree( newick, format = 0 )
    except:
        try:
            return Tree( newick, format = 1 )
        except:
            raise ValueError( "Cannot understand this tree: {}".format( newick ) )
