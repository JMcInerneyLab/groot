from typing import Optional, List

from os import path

from groot.constants import EFormat
from groot.data import global_view
from groot.data.lego_model import ESiteType
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import MCMD, command, visibilities, common_commands
from mgraph import MGraph, importing
from mhelper import EFileMode, Filename, file_helper, io_helper
from groot.extensions import ext_files
from groot.algorithms import alignment as alignment_, tree as tree_, graph_viewing
from groot.algorithms.walkthrough import Walkthrough


__mcmd_folder_name__ = "Gimmicks"
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
def view_graph( text: str, title: Optional[str] = None ):
    """
    Views a graph in Vis-Js.
    
    :param text:    Text representing the graph, created with `MGraph.to_compact` OR a filename, created with `MGRAPH.to_csv`.
    :param title:   Title of graph (optional)
    """
    if path.isfile( text ):
        try:
            g = importing.import_edgelist( file_helper.read_all_text( text ), delimiter = "\t" )
        except Exception as ex:
            raise ValueError( "Invalid file: " + text ) from ex
    else:
        g = importing.import_compact( text )
    
    visjs = graph_viewing.create_vis_js( graph = [("custom-graph", g)],
                                         title = title,
                                         inline_title = title is not None )
    
    MCMD.print( str( g ) )
    
    with io_helper.open_write( "open", extension = ".html" ) as file_out:
        file_out.write( visjs )


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
            msg = "Please review the results.\n* continue = continue the wizard\n* retry = retry this step\n* pause = Pause the wizard to inspect your data."
            opts = ["continue", "retry", "pause", "abort"]
        else:
            msg = "Please review the results.\n* continue = continue the wizard\n* pause = Pause the wizard to inspect your data."
            opts = ["continue", "pause", "abort"]
        
        switch = MCMD.question( msg, opts, default = "continue" )
        
        if switch == "continue":
            if global_view.current_model().file_name:
                ext_files.file_save()
            return True
        elif switch == "retry":
            return False
        elif switch == "pause":
            common_commands.start_cli()
        elif switch == "abort":
            raise ValueError( "User cancelled." )


@command( names = ["continue"] )
def continue_wizard() -> EChanges:
    """
    Continues the wizard after it was paused.
    """
    if Walkthrough.get_active() is None:
        raise ValueError( "There is no active wizard to continue." )
    
    return Walkthrough.get_active().step()

@command( names = ["stop"] )
def stop_wizard() -> EChanges:
    """
    Stops a wizard.
    """
    if Walkthrough.get_active() is None:
        raise ValueError( "There is no active wizard to stop." )
    
    return Walkthrough.get_active().stop()


@command()
def wizard( new: Optional[bool] = None,
            name: Optional[str] = None,
            imports: Optional[List[str]] = None,
            outgroups: Optional[List[str]] = None,
            pause_import: Optional[bool] = None,
            pause_components: Optional[bool] = None,
            pause_align: Optional[bool] = None,
            pause_tree: Optional[bool] = None,
            pause_fusion: Optional[bool] = None,
            pause_nrfg: Optional[bool] = None,
            tolerance: Optional[int] = None,
            alignment: Optional[str] = None,
            tree: Optional[str] = None,
            view: Optional[bool] = None ) -> None:
    """
    Sets up a workflow that you can activate in one go.
    
    If you don't fill out the parameters then whatever UI you are using will prompt you for them.
    
    If you have a set of default parameters that you'd like to preserve, take a look at the `alias` command.
    
    This method is represented in the GUI by the wizard window.
    
    :param new:                 Create a new model? 
    :param name:                Name the model?
    :param outgroups:           Outgroup accessions?
    :param imports:             Import files into the model? 
    :param pause_components:    Pause after component generation? 
    :param pause_import:        Pause after data import? 
    :param pause_align:         Pause after sequence alignment? 
    :param pause_tree:          Pause after tree generation? 
    :param pause_fusion:        Pause after fusion finding? 
    :param pause_nrfg:          Pause after NRFG generation? 
    :param tolerance:           Component identification tolerance? 
    :param alignment:           Alignment method? 
    :param tree:                Tree generation method?
    :param view:                View the final NRFG in Vis.js?
    """
    if new is None:
        new = (MCMD.question( "1/14. Are you starting a new model, or do you want to continue with your current data?", ["new", "continue"] ) == "new")
    
    if name is None:
        name = MCMD.question( "2/14. Name your model.\nYou can specify a complete path or just a name.\nIf you don't enter a name, your file won't be saved.", ["*"] )
        
        if not name:
            MCMD.warning( "Your file will not be saved." )
    
    if imports is None:
        imports = []
        
        while True:
            ex = "\nEnter a blank line when you don't want to add any more files." if imports else ""
            file_name = MCMD.question( "3/14. Enter file paths to import BLAST or FASTA files, one per line." + ex, ["*"] )
            
            if file_name:
                imports.append( file_name )
            else:
                break
    
    if outgroups is None:
        outgroups = []
        
        while True:
            ex = "\nEnter a blank line when you don't want to add any more outgroups."
            outgroup = MCMD.question( "4/14. Enter outgroup accessions, one per line." + ex, ["*"] )
            
            if outgroup:
                outgroups.append( outgroup )
            else:
                break
    
    if tolerance is None:
        success = False
        
        while not success:
            tolerance_str = MCMD.question( "5/14. What tolerance do you want to use for the component identification?", ["*"] )
            
            try:
                tolerance = int( tolerance_str )
                success = True
            except:
                MCMD.print( "Something went wrong. Let's try that question again." )
                success = False
    
    if alignment is None:
        alignment = MCMD.question( "6/14. Which function do you want to use for the sequence alignment? Enter a blank line for the default.", list( alignment_.algorithms ) + [""] )
    
    if tree is None:
        tree = MCMD.question( "7/14. Which function do you want to use for the tree generation? Enter a blank line for the default.", list( tree_.algorithms ) + [""] )
    
    if pause_import is None:
        pause_import = MCMD.question( "8/14. Do you wish the wizard to pause for you to review the imported data?" )
    
    if pause_components is None:
        pause_components = MCMD.question( "9/14. Do you wish the wizard to pause for you to review the components?" )
    
    if pause_align is None:
        pause_align = MCMD.question( "10/14. Do you wish the wizard to pause for you to review the alignments?" )
    
    if pause_tree is None:
        pause_tree = MCMD.question( "11/14. Do you wish the wizard to pause for you to review the trees?" )
    
    if pause_fusion is None:
        pause_fusion = MCMD.question( "12/14. Do you wish the wizard to pause for you to review the fusion?" )
    
    if pause_nrfg is None:
        pause_nrfg = MCMD.question( "13/14. Do you wish the wizard to pause for you to review the NRFG?" )
    
    if view is None:
        view = MCMD.question( "14/14. Do you wish the wizard to show you the final NRFG in Vis.js?" )
    
    walkthrough = Walkthrough( new,
                               name,
                               imports,
                               pause_import,
                               pause_components,
                               pause_align,
                               pause_tree,
                               pause_fusion,
                               pause_nrfg,
                               tolerance,
                               alignment,
                               tree,
                               view,
                               outgroups )
    
    walkthrough.make_active()
