from typing import Optional

from groot import algorithms
from groot.algorithms.s020_importation import EImportFilter
from groot.data import global_view
from groot.constants import EXT_FASTA, EXT_BLAST
from groot.data.model_interfaces import INamedGraph
from groot.data.model_core import FixedUserGraph
from groot.frontends.gui.gui_view_utils import EChanges
from intermake.engine.environment import MCMD, MENV
from intermake.plugins import console_explorer
from intermake.plugins.command_plugin import command
from intermake.visualisables.visualisable import VisualisablePath
from mhelper import Filename, EFileMode


__mcmd_folder_name__ = "Importation"


@command()
def import_graph( graph: INamedGraph, name: str = "" ):
    """
    Imports a graph or tree as a user-graph.
    
    User graphs are graphs that can be viewed and explored but do not, by default, form part of the model.
    
    :param graph:   Graph to import. See `format_help`. If you specify an existing user-graph or a graph
                    that is already part of the model, a copy will be made. 
    :param name:    Name of the graph. If not provided your graph will be assigned a default name. 
    """
    model = global_view.current_model()
    
    graph = FixedUserGraph( graph.graph.copy(), name or "usergraph{}".format( len( model.user_graphs ) ) )
    
    model.user_graphs.append( graph )


@command()
def import_blast( file_name: Filename[EFileMode.READ, EXT_BLAST], evalue: Optional[float] = 1e-10, length: Optional[int] = None ) -> EChanges:
    """
    Imports a BLAST file into the model 
    :param length:      Cutoff on alignment (query) length `None` for no filter. 
    :param evalue:      Cutoff on evalue. `None` for no filter (this is not the default). 
    :param file_name:   File to import 
    :return: 
    """
    with MCMD.action( "Importing BLAST" ):
        algorithms.s030_similarity.import_similarity( global_view.current_model(), file_name, evalue, length )
    
    return EChanges.MODEL_ENTITIES


@command()
def import_composites( file_name: Filename[EFileMode.READ] ) -> EChanges:
    """
    Imports a composites file into the model
    :param file_name:   File to import 
    :return: 
    """
    with MCMD.action( "Importing composites" ):
        algorithms.s020_importation.import_composites( global_view.current_model(), file_name )
    
    return EChanges.MODEL_ENTITIES


@command()
def import_fasta( file_name: Filename[EFileMode.READ, EXT_FASTA] ) -> EChanges:
    """
    Imports a FASTA file into the model
    :param file_name:   File to import 
    :return: 
    """
    with MCMD.action( "Importing FASTA" ):
        algorithms.s020_importation.import_fasta( global_view.current_model(), file_name )
    
    return EChanges.MODEL_ENTITIES


@command()
def import_file( file_name: Filename[EFileMode.READ] ) -> EChanges:
    """
    Imports a file into the model.
    How it is imported is based on the extension:
        `.groot`     --> `file_load`
        `.fasta`     --> `import_fasta`
        `.blast`     --> `import_blast`
        `.composite` --> `import_composite`
        `.imk`       --> `source` (runs the script)
    
    :param file_name:   File to import.
    """
    with MCMD.action( "Importing file" ):
        algorithms.s020_importation.import_file( global_view.current_model(), file_name, skip_bad_extensions = False, filter = EImportFilter.ALL, query = False )
    
    return EChanges.MODEL_ENTITIES


@command()
def import_directory( directory: str,
                      reset: bool = True,
                      filter: EImportFilter = (EImportFilter.DATA | EImportFilter.SCRIPT),
                      query: bool = False
                      ) -> EChanges:
    """
    Imports all importable files from a specified directory
    
    :param reset:       Whether to clear data from the model first.
    :param directory:   Name of directory to import
    :param filter:      Filter files to import.
    :param query:       Query the directory (don't import anything).
    """
    if reset:
        if not query:
            from groot.extensions import ext_files
            ext_files.file_new()
        else:
            MCMD.print( "Importing will start a new model." )
    
    algorithms.s020_importation.import_directory( global_view.current_model(), directory, query, filter )
    
    if query:
        return EChanges.NONE
    
    if reset:
        if MENV.host.is_cli:
            console_explorer.re_cd( VisualisablePath.get_root() )
        
        return EChanges.MODEL_OBJECT
    else:
        return EChanges.MODEL_ENTITIES
