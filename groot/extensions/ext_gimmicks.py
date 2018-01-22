from groot.data import global_view
from groot.data.lego_model import ESiteType
from groot.extensions.ext_viewing import EFormat
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import MCMD, command, visibilities
from mhelper import EFileMode, Filename, file_helper


__mcmd_folder_name__ = "Gimmicks"


@command( visibility = visibilities.ADVANCED )
def print_sites( type: ESiteType, text: str ) -> EChanges:
    """
    Prints a sequence in colour
    :param type: Type of sites to display.
    :param text: Sequence (raw data without headers) 
    """
    MCMD.information( cli_view_utils.colour_fasta_ansi( text, type ) )
    
    return EChanges.NONE


__EXT_FASTA = ".fasta"


@command( visibility = visibilities.ADVANCED )
def print_file( type: ESiteType, file: Filename[EFileMode.READ, __EXT_FASTA] ) -> EChanges:
    """
    Prints a FASTA file in colour
    :param type: Type of sites to display.
    :param file: Path to FASTA file to display. 
    """
    text = file_helper.read_all_text( file )
    MCMD.information( cli_view_utils.colour_fasta_ansi( text, type ) )
    
    return EChanges.NONE


@command( visibility = visibilities.ADVANCED )
def update_model() -> EChanges:
    """
    Update model to new version.
    """
    _ = global_view.current_model()
    
    # ...
    
    return EChanges.COMP_DATA


@command( visibility = visibilities.ADVANCED )
def walkthrough():
    from groot.extensions import ext_files, ext_generating, ext_viewing
    
    ext_files.file_new()
    ext_files.file_sample( "manny" )
    ext_files.file_save( "manny" )
    ext_generating.make_components()
    ext_generating.make_alignments()
    ext_generating.make_trees()
    ext_generating.make_fusions()
    ext_generating.make_nrfg()
    ext_viewing.print_trees()
    ext_files.file_save( "manny" )