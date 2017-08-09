from os import path
from typing import Optional

import sys

from flags import Flags


from legoalign.GlobalOptions import GlobalOptions
from legoalign.LegoModels import LegoModel, LegoComponent
from mcommand import command, Mandate, current_environment
from mcommand.helpers.table_draw import Table
from mcommand.plugins import common_commands
from mcommand.plugins import console_explorer

from mcommand.engine.constants import EVisibility
from mhelper import FileHelper, IoHelper
from legoalign.algorithms import importation, quantisation, components, verification, deconvolution


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
    console_explorer.re_cd(e,"/")
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
def save_model( e: Mandate, file_name: Optional[ str ] = None ) -> EChanges:
    """
    Saves the model
    :param e:           Internal 
    :param file_name: Filename. If not specified the current filename is used.
    :return: 
    """
    if file_name:
        __model.file_name = file_name
    
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
        components.detect( __model, tolerance )
        
    return EChanges.ATTRS


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
    :param subsequences: When `True`, redundant subsequenes are removed. 
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
        console_explorer.re_cd(e,"/")
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


@command()
def load_model( e: Mandate, file_name: str ) -> EChanges:
    """
    Loads the model from a file
    :param e:           Internal
    :param file_name:   File to load
    """
    global __model
    
    __model = IoHelper.load_binary( file_name )
    __model.file_name = file_name
    current_environment().root_object = __model
    __remember_file( file_name )
    console_explorer.re_cd(e,"/")
    
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
