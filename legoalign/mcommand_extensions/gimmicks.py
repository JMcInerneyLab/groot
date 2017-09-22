from editorium import Filename
from editorium.special_types import EFileMode
from legoalign.data.lego_model import ESiteType
from legoalign.frontends.cli import cli_view_utils
from mcommand.engine.environment import MCMD
from mcommand.plugins.command_plugin import command
from mhelper import file_helper


@command(visibility = False)
def print_sites( type: ESiteType, text: str ):
    """
    Prints a sequence in colour
    :param type: Type of sites to display.
    :param text: Sequence (raw data without headers) 
    """
    MCMD.information( cli_view_utils.colour_fasta_ansi( text, type ) )

__EXT_FASTA = ".fasta"

@command(visibility = False)
def print_file( type: ESiteType, file: Filename[EFileMode.READ, __EXT_FASTA] ):
    """
    Prints a FASTA file in colour
    :param type: Type of sites to display.
    :param file: Path to FASTA file to display. 
    """
    text = file_helper.read_all_text(file)
    MCMD.information( cli_view_utils.colour_fasta_ansi( text, type ) )
