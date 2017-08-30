from os import path
import os
from typing import Optional, Iterable, TypeVar, Callable, List

import sys

from colorama import Fore, Style
from ete3 import Tree
from flags import Flags

from editorium import MEnum
from legoalign.GlobalOptions import GlobalOptions
from legoalign.LegoModels import LegoModel, LegoComponent
from legoalign.mcommand_extensions import console_view
from mcommand import command, Mandate, current_environment
from mcommand.engine.plugin import Plugin
from mcommand.helpers.table_draw import Table
from mcommand.plugins import common_commands
from mcommand.plugins import console_explorer

from mcommand.visualisables.visualisable import IVisualisable
from mcommand.visualisables.visualisable_operations import PathToVisualisable
from mhelper import FileHelper, IoHelper
from legoalign.algorithms import importation, quantisation, components, verification, deconvolution, fastaiser, alignment, tree, consensus, fuse
from mhelper.ExceptionHelper import SwitchError

T = TypeVar("T")

class EChanges( Flags ):
    MODEL = 1  # type:EChanges
    FILE = 2  # type:EChanges
    RECENT = 4  # type:EChanges
    ATTRS = 8  # type:EChanges


@command()
def gui( _: Mandate ):
    """
    Starts the LegoDiagram GUI
    """
    from mcommand import start_qt_gui
    from legoalign.FrmMain import FrmMain
    
    if not start_qt_gui( window_class = FrmMain ):
        common_commands.cmd_exit()


def _get_samples():
    """
    INTERNAL
    Obtains the list of samples
    """
    sample_data_folder = __sample_data_folder()
    return FileHelper.sub_dirs( sample_data_folder )


def __sample_data_folder():
    """
    PRIVATE
    Obtains the sample data folder
    """
    return path.join( FileHelper.get_directory( __file__, 2 ), "sampledata" )


@command()
def sample( e: Mandate, name: Optional[ str ] = None ) -> EChanges:
    """
    Lists the available samples, or loads the specified sample
    :param e:       Internal 
    :param name:    Name of sample 
    :return: 
    """
    if name:
        file_name = path.join( __sample_data_folder(), name )
        e.print("Loading sample dataset. This is the same as running 'import.directory' on \"{}\".".format(file_name))
        return import_directory( e, file_name )
    else:
        for sample_dir in _get_samples():
            e.print( FileHelper.get_filename( sample_dir ) )
            
        return EChanges.no_flags


@command()
def new_model( e: Mandate ) -> EChanges:
    """
    Starts a new model
    :param e:   Internal
    """
    global __model
    __model = LegoModel()
    current_environment().root_object = __model
    console_explorer.re_cd(e,PathToVisualisable([current_environment().root_object]))
    return EChanges.MODEL | EChanges.FILE | EChanges.ATTRS


@command()
def import_blast( e: Mandate, file_name: str ) -> EChanges:
    """
    Imports a BLAST file into the model
    :param e:           Internal 
    :param file_name:   File to import 
    :return: 
    """
    with e.action("Importing BLAST"):
        importation.import_blast( __model, file_name )
        
    return EChanges.ATTRS


@command()
def import_composites( e: Mandate, file_name: str ) -> EChanges:
    """
    Imports a composites file into the model
    :param e:           Internal 
    :param file_name:   File to import 
    :return: 
    """
    with e.action("Importing composites"):
        importation.import_composites( __model, file_name )
    return EChanges.ATTRS


@command()
def import_fasta( e: Mandate, file_name: str ) -> EChanges:
    """
    Imports a FASTA file into the model
    :param e:           Internal 
    :param file_name:   File to import 
    :return: 
    """
    with e.action("Importing FASTA"):
        importation.import_fasta( __model, file_name )
        
    return EChanges.ATTRS

@command()
def sessions(e:Mandate):
    """
    Prints the contents of the `sessions` folder
    """                                       
    folder = __fix_path(".")
    
    r = []
    
    r.append("SESSIONS:")
    for file in os.listdir(folder):
        r.append(file)
        
    r.append("\nRECENT:")
    for file in __global_options.recent_files:
        r.append(file)
        
    e.information("\n".join(r))
        
@command()
def session(e:Mandate):
    if __model.file_name:
        e.information(__model.file_name)
    else:
        e.information("Model not saved.")


@command()
def save( e: Mandate, file_name: Optional[ str ] = None ) -> EChanges:
    """
    Saves the model
    :param e:           Internal 
    :param file_name: Filename. File to load. Either specify a complete path, or the name of the file in the `sessions` folder. If not specified the current filename is used.
    :return: 
    """
    if file_name:
        file_name = __fix_path(file_name)
    else:
        file_name = __model.file_name
        
    if not file_name:
        raise ValueError("Cannot save because a filename has not been specified.")
    
    __remember_file( file_name )
    
    sys.setrecursionlimit( 10000 )
    
    with e.action("Saving file"):
        IoHelper.save_binary( file_name, __model )
        
    __model.file_name = file_name
    
    return EChanges.FILE


@command()
def quantise( e: Mandate, level: int ) -> EChanges:
    """
    Quantises the model
    :param e: 
    :param level:   Quantisation level, in sites 
    :return: 
    """
    before, after = quantisation.quantise( __model, level )
    
    e.print("Quantised applied. Reduced the model from {} to {} subsequences.".format(before, after))
    
    return EChanges.ATTRS

@command()
def detect(e:Mandate, tolerance:int= 0)->EChanges:
    """
    Detects composites in the model.
    :param e:           Internal
    :param tolerance:   Tolerance on overlap
    """
    with e.action("Component detection"):
        components.detect( e,__model, tolerance )
        
    return EChanges.ATTRS

@command()
def fasta(e:Mandate, x : IVisualisable):
    """
    Presents the FASTA sequences for an object.
    :param e: 
    :param x:   Object to present.
    """
    e.information( console_view.colour_fasta_ansi(__model, fastaiser.to_fasta(x) ))
    
@command()
def align( e:Mandate, component:Optional[ LegoComponent ] = None ):
    """
    Aligns the component. If no component is specified, aligns all components.
    
    :param e:
    :param component: Component to align, or `None` for all.
    """
    to_do = __get_component_list( component )
    
    for component_ in e.iterate(to_do, "Aligning", interesting = True):
        alignment.align( component_ )


def __get_component_list( component : Optional[ LegoComponent ]):
    if component is not None:
        to_do = [ component ]
    else:
        to_do = __model.components
    return to_do


@command(name="tree")
def tree_( e:Mandate, component:Optional[LegoComponent ] = None ):
    """
    Generates the tree for the component. If no component is specified, all trees are generated.
    
    :param e: 
    :param component:  Component, or `None` for all.
    :return: 
    """
    to_do = __get_component_list( component )
    
    for component_ in e.iterate(to_do, "Generating trees", interesting = True):
        tree.generate_tree(component_)
        
@command()
def estimate(e:Mandate):
    """
    Estimates model fusions. Does not affect the model.
    :param e: Internal
    """
    results = []
    
    for fusion in fuse.find_events( __model ):
        results.append(str(fusion))
        
    e.information("\n".join(results))
    
    fuse.find_points(__model)
        
        
@command()
def status( e: Mandate ):
    """
    Prints the status of the model.
    :param e: 
    :return: 
    """
    p = []
    r = []
    r.append("Sequences")
    r.append( "Sequences:     {}".format( __value( p, __model.sequences, lambda _: True, import_blast ) ) )
    r.append( "FASTA:         {}".format( __value( p, __model.sequences, lambda x: x.site_array, import_fasta ) ) )
    r.append( "Components:    {}".format( __value( p, __model.sequences, lambda x: x.component, detect ) ) )
    r.append("")
    r.append("Components")
    r.append( "Components:    {}".format( __value( p, __model.components, lambda x: True, detect ) ) )
    r.append( "Alignments:    {}".format( __value( p, __model.components, lambda x: x.alignment, align ) ) )
    r.append( "Trees:         {}".format( __value( p, __model.components, lambda x: x.tree, tree_ ) ) )
    r.append( "Consensus:     {}".format( __value( p, __model.components, lambda x: x.consensus, consensus ) ) )
    e.print("\n".join(r))


def __value( target : List[Plugin], the_list: Iterable[ T ], test: Callable[ [ T ], bool ], plugin : Plugin ) -> str:
    total = 0
    filtered = 0
    
    for x in the_list:
        total += 1
        if test( x ):
            filtered += 1
    
    if filtered and filtered == total:
        style = Fore.GREEN
        suffix = ""
    else:
        if filtered == 0:
            style = Fore.RED
        else:
            style = Fore.YELLOW
            
        if not target:
            suffix = Fore.WHITE + Style.DIM + " - Consider running '{}'.".format(current_environment().host.translate_name(plugin.name))
            target.append(plugin)
        else:
            suffix = ""
    
    return style + "{}/{}".format( filtered, total ) + suffix + Style.RESET_ALL
        
@command(name="consensus")
def consensus_(e:Mandate, component : Optional[ LegoComponent ] = None):
    """
    Fuses the component trees to create the basis for our fusion graph.
    :param component:   Component, or `None` for all.
    :param e: 
    :return: 
    """
    components = __get_component_list(component)
    
    for component_ in e.iterate(components, "Consensus"):
        consensus.consensus(component_)
    
        
@command()
def print_alignment( e:Mandate, component:LegoComponent ):
    """
    Prints the alignment for a component.
    :param e: 
    :param component:   Component to print alignment for. 
    :return: 
    """
    if component.alignment is None:
        raise ValueError("No alignment is available for this component. Did you remember to run `align` first?")
    else:
        e.information( console_view.colour_fasta_ansi( __model, component.alignment ) )
        
        
class EPrintTree(MEnum):
    """
    :data NEWICK: Newick format
    :data ASCII:  ASCII diagram
    :data GUI:    Interactive diagram
    """
    NEWICK = 1
    ASCII = 2
    GUI = 3

@command()
def print_tree( e:Mandate, component:LegoComponent, consensus : bool = False, view : EPrintTree = EPrintTree.ASCII):
    """
    Prints the tree for a component.
    
    :param view:        How to view the tree
    :param consensus:   When set, prints the consensus tree.
    :param e: 
    :param component:   Component to print.  
    :return: 
    """
    e.information("COMPONENT {}".format( component))
    target = component.consensus if consensus else component.tree
    
    if consensus:
        e.information("Consensus tree:\nSources     : '{}'\nIntersection: '{}'\n".format(", ".join(str(x) for x in component.incoming_components()), ", ".join(str(x) for x in component.consensus_intersection)))
    
    if target is None:
        raise ValueError("Cannot draw this tree because the tree has not yet been created. Please create the tree first.")
    
    if view == EPrintTree.ASCII:
        tree_ = tree.tree_from_newick(target).get_ascii(show_internal = True)
        colours = [Fore.RED,Fore.GREEN,Fore.YELLOW,Fore.BLUE,Fore.MAGENTA,Fore.CYAN, Fore.LIGHTRED_EX, Fore.LIGHTGREEN_EX, Fore.LIGHTBLUE_EX, Fore.LIGHTMAGENTA_EX, Fore.LIGHTCYAN_EX]
        
        for sequence in __model.sequences:
            colour = colours[sequence.component.index % len(colours)]
            tree_= tree_.replace(sequence.accession, colour + sequence.accession + Fore.RESET) 
        
        e.information(tree_ )
    elif view == EPrintTree.NEWICK:
        e.information(target)
    elif view == EPrintTree.GUI:
        tree__ = tree.tree_from_newick(target)
        colours = ["#C00000","#00C000","#C0C000","#0000C0","#C000C0","#00C0C0", "#FF0000","#00FF00","#FFFF00","#0000FF","#FF00FF","#00FFC0"]
        
        for n in tree__.traverse():
           n.img_style["fgcolor"] = "#000000"
        
        for node in tree__:
            sequence = __model.find_sequence(node.name)
            node.img_style["fgcolor"] = colours[sequence.component.index % len(colours)]
        
        tree__.show()
    else:
        raise SwitchError("view", view)


@command()
def print_minor( e:Mandate, component : Optional[LegoComponent] = None ):
    """
    Prints the edges between the component subsequences.
    
    Each line is of the form:
    
        `FROM <minor> TO <major> [ <start> : <end> ] <length>`
        
    Where:
    
        `minor`  is the source component
        `major`  is the destination component
        `start`  is the average of the start of the destination entry point
        `end`    is the average of the end of the destination entry point
        `length` is the average length of the sequences in the destination 

    :param e:         Internal
    :param component: Component to print. If not specified prints a summary of all components.    
    """
    if not __model.components:
        raise ValueError("Cannot print minor components because components have not been calculated.")
    
    message = Table()
    
    average_lengths = components.average_component_lengths( __model )
    
    if component:
        message.add_title(component)
    else:
        message.add_title("all components")
        
    message.add_row("source","destination", "sequence", "seq-length", "start", "end" )
    message.add_hline()
    
    for major in __model.components:
        if component is not None and component is not major:
            continue
            
        major_sequences = list(major.major_sequences())
        
        for minor in __model.components:
            if major is minor:
                continue
            
            start  = 0
            end    = 0
            failed = False
            
            for sequence in major_sequences:
                subsequences = [ x for x in sequence.subsequences if minor in x.components ]
                
                if subsequences:
                    start  += subsequences[0].start
                    end    += subsequences[-1].end
                    
                    if component is not None:
                        message.add_row(minor, major, sequence.accession, sequence.length, subsequences[0].start, subsequences[-1].end)
                else:
                    failed = True
                    
            if failed:
                continue
                
            start  /= len(major_sequences)
            end    /= len(major_sequences)
        
            message.add_row(  minor, major, "AVG*{}".format(len(major_sequences)), round(average_lengths[major]), round(start), round(end) )
                    
    e.print( message.to_string() )


@command()
def print_major( e :Mandate):
    """
    Prints the major components.
    
    Each line takes the form:
    
        `COMPONENT <major> = <sequences>`
        
    Where:
    
        `major` is the component name
        `sequences` is the list of components in that sequence
    
    """
    if not __model.components:
        raise ValueError("Cannot print major components because components have not been calculated.")
    
    message = Table()
    
    message.add_title("major elements of components")
    message.add_row("component", "major elements")
    message.add_hline()
    
    
    for component in __model.components:
        message.add_row( component, ", ".join( x.accession for x in component.major_sequences() ) )
        
    e.print( message.to_string() )
    


@command()
def verify(e:Mandate) -> None:
    """
    Verifies the integrity of the model.
    :param e:   Internal
    """
    verification.verify(__model)
    e.print( "Verified OK.")
    



@command()
def clean_edges( e: Mandate, edges : bool = True, subsequences : bool = True ) -> EChanges:
    """
    Removes redundancies (duplicates) from the model.
    
    :param e:            Internal
    :param subsequences: When `True`, redundant subsequences are removed. 
    :param edges:        When `True`, redundant edges are removed.
    :return: 
    """
    if not edges and not subsequences:
        raise ValueError("You must specify at least one item to clean.")
    
    if edges:
        with e.action("Removing redundant edges"):
            deconvolution.remove_redundant_edges(__model)
        
    if subsequences:
        with e.action("Removing redundant subsequences"):
            deconvolution.remove_redundant_subsequences(__model)
    
    return EChanges.ATTRS


@command()
def import_directory( e: Mandate, directory: str, reset : bool = True ):
    """
    Imports all importable files from a specified directory
    :param reset:     Whether to clear data from the model first.
    :param e:         Internal 
    :param directory: Name of directory to import
    :return: 
    """
    if reset:
        global __model
        __model = LegoModel()
        current_environment().root_object = __model
    
    with e.action("Importing directory"):
        importation.import_directory(__model, directory)
    
    if reset:
        console_explorer.re_cd(e, PathToVisualisable([current_environment().root_object]))
        return EChanges.MODEL | EChanges.FILE | EChanges.ATTRS
    else:
        return EChanges.ATTRS


def _current_model() -> LegoModel:
    """
    INTERNAL
    Retrieves the current model 
    """
    return __model

def _current_options() -> GlobalOptions:
    """
    INTERNAL
    Retrieves the current options
    """
    return __global_options


def __fix_path( file_name : str ) -> str:
    """
    Adds the directory to the filename, if not specified.
    """
    if path.sep not in file_name:
        return path.join(current_environment().local_data.local_folder("sessions"), file_name)
    else:
        return file_name


@command()
def load( e: Mandate, file_name: str ) -> EChanges:
    """
    Loads the model from a file
    :param e:           Internal
    :param file_name:   File to load. Either specify a complete path, or the name of the file in the `sessions` folder.
    """
    global __model
    
    file_name = __fix_path(file_name)
    __model = IoHelper.load_binary( file_name )
    __model.file_name = file_name
    current_environment().root_object = __model
    __remember_file( file_name )
    console_explorer.re_cd(e,PathToVisualisable([current_environment().root_object]))
    
    return EChanges.MODEL | EChanges.RECENT | EChanges.FILE | EChanges.ATTRS


def __global_options_file_name():
    """
    PRIVATE
    The filename of the options file
    """
    dir = path.expanduser( "~/legoalign" )
    FileHelper.create_directory( dir )
    
    return path.join( dir, "options.p" )


def __remember_file( file_name : str ):
    """
    PRIVATE
    Adds a file to the recent list
    """
    if file_name in __global_options.recent_files:
        __global_options.recent_files.remove( file_name )
    
    __global_options.recent_files.append( file_name )
    
    while len( __global_options.recent_files ) > 10:
        del __global_options.recent_files[ 0 ]
    
    _save_global_options()


def _save_global_options():
    """
    INTERNAL
    Saves the global options file
    """
    IoHelper.save_binary( __global_options_file_name(), __global_options )


__model = LegoModel()
__global_options = IoHelper.default_values( IoHelper.load_binary( __global_options_file_name(), default = None ), GlobalOptions() )  # type: GlobalOptions
