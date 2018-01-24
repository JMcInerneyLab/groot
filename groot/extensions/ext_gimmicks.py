from typing import Optional, List

from groot.data import global_view
from groot.data.lego_model import ESiteType
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import MCMD, command, visibilities, common_commands
from intermake.engine.environment import MENV
from intermake.engine.theme import Theme
from mhelper import EFileMode, Filename, file_helper, string_helper
from groot.extensions import ext_files, ext_generating, ext_viewing, ext_gui


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


def __review( review, msg, fns, *, retry = True ):
    if not review:
        return
    
    MCMD.question( msg + ". Continue to show the results.", ["continue"] )
    
    for fn in fns:
        fn()
    
    while True:
        if retry:
            msg = "Please review the results.\n* continue = continue the walkthrough\n* retry = retry this step\n* pause = Pause the walkthrough to inspect your data."
            opts = ["continue", "retry", "pause", "abort"]
        else:
            msg = "Please review the results.\n* continue = continue the walkthrough\n* pause = Pause the walkthrough to inspect your data."
            opts = ["continue", "pause", "abort"]
        
        switch = MCMD.question( msg, opts, default = "continue" )
        
        if switch == "continue":
            if global_view.current_model().file_name:
                ext_files.file_save()
            return True
        elif switch == "retry":
            return False
        elif switch == "pause":
            common_commands.cli()
        elif switch == "abort":
            raise ValueError( "User cancelled." )


def __line( title ):
    common_commands.cls()
    MCMD.print( Theme.C.SHADE * MENV.host.console_width )
    MCMD.print( string_helper.centre_align( " " + title + " ", MENV.host.console_width, Theme.C.SHADE ) )
    MCMD.print( Theme.C.SHADE * MENV.host.console_width )


@command()
def walkthrough( new: Optional[bool] = None,
                 name: Optional[str] = None,
                 imports: Optional[List[str]] = None,
                 review: bool = True,
                 tolerance: Optional[int] = None,
                 alignment: Optional[str] = None,
                 tree: Optional[str] = None,
                 fusion: bool = False,
                 nrfg: bool = False,
                 view: Optional[bool] = None ) -> None:
    """
    Guides you through.
    
    :param new:          When set, won't ask if you want to start a new model and will use this option. 
    :param name:         When set, won't ask you for the model name and will use this option.
    :param imports:      When set, won't ask you for the files to import and will use this option. 
    :param review:       When set, won't ask you to review the results. 
    :param tolerance:    When set, won't ask you for the component identification tolerance and will use this option. 
    :param alignment:    When set, won't ask you for the alignment algorithm and will use this option. 
    :param tree:         When set, won't ask you for the tree generation algorithm and will use this option.
    :param fusion:       When set, won't ask you to confirm the fusion generation.
    :param nrfg:         When set, won't ask you to confirm the NRFG generation.
    :param view:         When set, won't ask if you want to view the results and will use this option.
    """
    
    # Start a new model
    if global_view.current_model().sequences:
        __line( "Clean" )
        
        if new is None:
            new = (MCMD.question( "Are you starting a new model, or do you want to continue with your current data?", ["new", "continue"] ) == "new")
        
        if new:
            ext_files.file_new()
    elif new is not None:
        MCMD.warning( "`new` parameter specified but the model is already new." )
    
    # Save the model
    __line( "Save" )
    if not global_view.current_model().file_name:
        if name is None:
            name = MCMD.question( "Name your model.\nYou can specify a complete path or just a name.\nIf you don't enter a name, your file won't be saved.", ["*"] )
        
        if not name:
            MCMD.warning( "Your file will not be saved." )
        else:
            ext_files.file_save( name )
    elif name is not None:
        MCMD.warning( "`name` parameter specified but the model is already named." )
    
    # Import data
    __line( "Import" )
    if imports is not None:
        for import_ in imports:
            ext_files.import_file( import_ )
    else:
        while True:
            ex = "\nJust enter a blank line when you don't want to add any more files." if global_view.current_model().sequences else ""
            file_name = MCMD.question( "Enter the file path to import a BLAST or FASTA file." + ex, ["*"] )
            
            if file_name:
                ext_files.import_file( file_name )
            else:
                break
    
    __review( review, "Data imported", (ext_viewing.print_sequences,), retry = False )
    
    # Make components
    __line( "Components" )
    while True:
        if tolerance is None:
            tolerance = int( MCMD.question( "Component identification will commence. What tolerance do you want to use?", ["*"] ) )
        
        ext_generating.make_components( tolerance )
        
        if __review( review, "Components generated", (ext_viewing.print_sequences, ext_viewing.print_components) ):
            break
        
        tolerance = None
    
    # Make alignments
    __line( "Alignments" )
    while True:
        if alignment is None:
            alignment = MCMD.question( "Sequence alignment will commence. Specify the algorithm?", ["*"] )
        
        ext_generating.make_alignments( alignment )
        
        if __review( review, "Domains aligned", (ext_viewing.print_alignments,) ):
            break
        
        alignment = None
    
    # Make trees
    __line( "Trees" )
    while True:
        if tree is None:
            tree = MCMD.question( "Tree generation will commence. Specify the algorithm?", ["*"] )
        
        ext_generating.make_trees( tree )
        
        if __review( review, "Trees generated", (ext_viewing.print_trees,) ):
            break
        
        tree = None
    
    # Make fusions
    __line( "Fusions" )
    if fusion:
        MCMD.question( "Fusion identification will commence.", ["continue"] )
    
    ext_generating.make_fusions()
    
    __review( review, "Fusions identified", (ext_viewing.print_trees, ext_viewing.print_fusions), retry = False )
    
    # Make NRFG
    __line( "NRFG" )
    if nrfg:
        MCMD.question( "NRFG generation will commence.", ["continue"] )
    
    ext_generating.make_nrfg()
    
    __review( review, "NRFG generated", (ext_viewing.print_trees,), retry = False )
    
    # Open for viewing
    __line( "View" )
    if view is None:
        view = MCMD.question( "Do you wish to open the NRFG?" )
    
    if view:
        ext_gui.view_nrfg_gui()
