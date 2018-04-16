from typing import List, Optional

from groot import algorithms
from groot.data import global_view
from groot.data.model_interfaces import ESiteType, INamedGraph
from groot.extensions import ext_files
from groot.utilities import cli_view_utils
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import MCMD, command, common_commands, visibilities
from intermake.engine.environment import MENV
from mgraph import Quartet, analysing
from mhelper import EFileMode, Filename, bio_helper, file_helper, io_helper


__mcmd_folder_name__ = "Gimmicks"
__EXT_FASTA = ".fasta"


@command( visibility = visibilities.ADVANCED )
def query_quartet( graph: INamedGraph, a: str, b: str, c: str, d: str ):
    """
    Displays what a particular quartet looks like for a particular graph.
    
    :param graph:   Graph to query. 
    :param a:       Name of node in quartet. 
    :param b:       Name of node in quartet.
    :param c:       Name of node in quartet. 
    :param d:       Name of node in quartet. 
    """
    g = graph.graph
    an = g.nodes.by_predicate( lambda x: str( x ) == a )
    bn = g.nodes.by_predicate( lambda x: str( x ) == b )
    cn = g.nodes.by_predicate( lambda x: str( x ) == c )
    dn = g.nodes.by_predicate( lambda x: str( x ) == d )
    
    q = analysing.get_quartet( g, (an, bn, cn, dn) )
    
    if isinstance( q, Quartet ):
        l1, l2 = q.left_nodes
        r1, r2 = q.right_nodes
        
        l1t = "{}".format( l1 ).rjust( 10 )
        l2t = "{}".format( l2 ).rjust( 10 )
        r1t = "{}".format( r1 ).ljust( 10 )
        r2t = "{}".format( r2 ).ljust( 10 )
        
        MCMD.print( str( q ) + ":" )
        MCMD.print( r"    {XXXXXXXX}          {YYYYYYYY}".format( XXXXXXXX = l1t, YYYYYYYY = r1t ) )
        MCMD.print( r"              \        /          " )
        MCMD.print( r"               --------           " )
        MCMD.print( r"              /        \          " )
        MCMD.print( r"    {XXXXXXXX}          {YYYYYYYY}".format( XXXXXXXX = l2t, YYYYYYYY = r2t ) )
    else:
        MCMD.print( str( q ) )
        MCMD.print( r"    (unresolved)" )


# noinspection SpellCheckingInspection
@command( visibility = visibilities.ADVANCED )
def composite_search_fix( blast: Filename[EFileMode.READ], fasta: Filename[EFileMode.READ], output: Filename[EFileMode.OUTPUT] ):
    """
    Converts standard BLAST format 6 TSV to `Composite search` formatted BLAST. 
    
    Composite search [1] uses a custom input format.
    If you already have standard BLAST this converts to that format, so you don't need to BLAST again.
    
    [1] JS Pathmanathan, P Lopez, F-J Lapointe and E Bapteste
    
    :param blast:   BLAST file 
    :param fasta:   FASTA file 
    :param output:  Output
    :return:        BLAST file, suitable for use with composite searcher 
    """
    # 
    # CS: qseqid sseqid evalue pident    bitscore qstart     qend     qlen*  sstart send   slen*
    # ST: qseqid sseqid pident alignment length   mismatches gapopens qstart qend   sstart send evalue bitscore
    
    lengths = { }
    
    with MCMD.action( "Reading FASTA" ) as action:
        for accession, sequence in bio_helper.parse_fasta( file = fasta ):
            if " " in accession:
                accession = accession.split( " ", 1 )[0]
            
            lengths[accession] = len( sequence )
            action.increment()
    
    MCMD.progress( "{} accessions".format( len( lengths ) ) )
    count = 0
    
    with io_helper.open_write( output ) as file_out:
        with MCMD.action( "Processing" ) as action:
            with open( blast, "r" ) as file_in:
                for row in file_in:
                    count += 1
                    action.increment()
                    elements = row.strip().split( "\t" )
                    
                    qseqid = elements[0]
                    sseqid = elements[1]
                    pident = elements[2]
                    # length = elements[3]
                    # mismatches = elements[4]
                    # gapopens = elements[5]
                    qstart = elements[6]
                    qend = elements[7]
                    sstart = elements[8]
                    send = elements[9]
                    evalue = elements[10]
                    bitscore = elements[11]
                    
                    try:
                        qlen = str( lengths[qseqid] )
                        slen = str( lengths[sseqid] )
                    except KeyError as ex:
                        raise ValueError( "Accession found in BLAST file but not in FASTA file. See internal error for details." ) from ex
                    
                    file_out.write( "\t".join( [qseqid, sseqid, evalue, pident, bitscore, qstart, qend, qlen, sstart, send, slen] ) )
                    file_out.write( "\n" )
    
    MCMD.progress( "{} BLASTs".format( count ) )


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


@command( visibility = visibilities.ADVANCED, names = ["continue"] )
def continue_wizard() -> EChanges:
    """
    Continues the wizard after it was paused.
    """
    if algorithms.s999_wizard.Wizard.get_active() is None:
        raise ValueError( "There is no active wizard to continue." )
    
    return algorithms.s999_wizard.Wizard.get_active().step()


@command( visibility = visibilities.ADVANCED, names = ["stop"] )
def stop_wizard() -> EChanges:
    """
    Stops a wizard.
    """
    if algorithms.s999_wizard.Wizard.get_active() is None:
        raise ValueError( "There is no active wizard to stop." )
    
    return algorithms.s999_wizard.Wizard.get_active().stop()


@command()
def wizard( new: Optional[bool] = None,
            name: Optional[str] = None,
            imports: Optional[List[str]] = None,
            outgroups: Optional[List[str]] = None,
            tolerance: Optional[int] = None,
            alignment: Optional[str] = None,
            supertree: Optional[str] = None,
            tree: Optional[str] = None,
            view: Optional[bool] = None,
            save: Optional[bool] = None,
            pause_import: Optional[bool] = None,
            pause_components: Optional[bool] = None,
            pause_align: Optional[bool] = None,
            pause_tree: Optional[bool] = None,
            pause_fusion: Optional[bool] = None,
            pause_splits: Optional[bool] = None,
            pause_consensus: Optional[bool] = None,
            pause_subset: Optional[bool] = None,
            pause_pregraphs: Optional[bool] = None,
            pause_minigraph: Optional[bool] = None,
            pause_sew: Optional[bool] = None,
            pause_clean: Optional[bool] = None,
            pause_check: Optional[bool] = None ) -> None:
    """
    Sets up a workflow that you can activate in one go.
    
    If you don't fill out the parameters then whatever UI you are using will prompt you for them.
    
    If you have a set of default parameters that you'd like to preserve, take a look at the `alias` command.
    
    This method is represented in the GUI by the wizard window.
    
    :param pause_pregraphs:     Pause after stage. 
    :param new:                 Create a new model? 
    :param name:                Name the model?
    :param outgroups:           Outgroup accessions?
    :param imports:             Import files into the model? 
    :param tolerance:           Component identification tolerance? 
    :param alignment:           Alignment method?
    :param supertree:           Supertree method? 
    :param tree:                Tree generation method?
    :param view:                View the final NRFG in Vis.js?
    :param save:                Save file to disk? (requires `name`)
    :param pause_components:    Pause after stage. 
    :param pause_import:        Pause after stage. 
    :param pause_align:         Pause after stage. 
    :param pause_tree:          Pause after stage. 
    :param pause_fusion:        Pause after stage. 
    :param pause_splits:        Pause after stage.
    :param pause_consensus:     Pause after stage.
    :param pause_subset:        Pause after stage.
    :param pause_minigraph:     Pause after stage.
    :param pause_sew:           Pause after stage.
    :param pause_clean:         Pause after stage.
    :param pause_check:         Pause after stage.
    """
    if new is None:
        new = (MCMD.question( "1/14. Are you starting a new model, or do you want to continue with your current data?", ["new", "continue"] ) == "new")
    
    if name is None:
        name = MCMD.question( "Name your model.\nYou can specify a complete path or just a name.\nIf you don't enter a name, your won't have the option to save your file using the wizard, though you can still do so manually.", ["*"] )
        
        if not name:
            MCMD.warning( "Your file will not be saved by the wizard." )
    
    if imports is None:
        imports = []
        
        while True:
            ex = "\nEnter a blank line when you don't want to add any more files." if imports else ""
            file_name = MCMD.question( "Enter file paths to import BLAST or FASTA files, one per line." + ex, ["*"] )
            
            if file_name:
                imports.append( file_name )
            else:
                break
    
    if outgroups is None:
        outgroups = []
        
        while True:
            ex = "\nEnter a blank line when you don't want to add any more outgroups."
            outgroup = MCMD.question( "Enter outgroup accessions, one per line." + ex, ["*"] )
            
            if outgroup:
                outgroups.append( outgroup )
            else:
                break
    
    if tolerance is None:
        success = False
        
        while not success:
            tolerance_str = MCMD.question( "What tolerance do you want to use for the component identification?", ["*"] )
            
            try:
                tolerance = int( tolerance_str )
                success = True
            except:
                MCMD.print( "Something went wrong. Let's try that question again." )
                success = False
    
    if alignment is None:
        alignment = question( "Which function do you want to use for the sequence alignment? Enter a blank line for the default.", list( algorithms.s070_alignment.alignment_algorithms.keys ) + [""] )
    
    if tree is None:
        tree = question( "Which function do you want to use for the tree generation? Enter a blank line for the default.", list( algorithms.s080_tree.tree_algorithms.keys ) + [""] )
    
    if supertree is None:
        supertree = question( "Which function do you want to use for the supertree generation? Enter a blank line for the default.", list( algorithms.s140_supertrees.supertree_algorithms.keys ) + [""] )
    
    if pause_import is None:
        pause_import = question( "Do you wish the wizard to pause for you to review the imported data?" )
    
    if pause_components is None:
        pause_components = question( "Do you wish the wizard to pause for you to review the components?" )
    
    if pause_align is None:
        pause_align = question( "Do you wish the wizard to pause for you to review the alignments?" )
    
    if pause_tree is None:
        pause_tree = question( "Do you wish the wizard to pause for you to review the trees?" )
    
    if pause_fusion is None:
        pause_fusion = question( "Do you wish the wizard to pause for you to review the fusions?" )
    
    if pause_splits is None:
        pause_splits = question( "Do you wish the wizard to pause for you to review the candidate splits?" )
    
    if pause_consensus is None:
        pause_consensus = question( "Do you wish the wizard to pause for you to review the consensus splits?" )
    
    if pause_subset is None:
        pause_subset = question( "Do you wish the wizard to pause for you to review the subsets?" )
    
    if pause_pregraphs is None:
        pause_pregraphs = question( "Do you wish the wizard to pause for you to review the pregraphs?" )
    
    if pause_minigraph is None:
        pause_minigraph = question( "Do you wish the wizard to pause for you to review the subgraphs?" )
    
    if pause_sew is None:
        pause_sew = question( "Do you wish the wizard to pause for you to review the uncleaned NRFG?" )
    
    if pause_clean is None:
        pause_clean = question( "Do you wish the wizard to pause for you to review the cleaned NRFG?" )
    
    if pause_check is None:
        pause_check = question( "Do you wish the wizard to pause for you to review the checks?" )
    
    if view is None:
        view = question( "Do you wish the wizard to show you the final NRFG in Vis.js?" )
    
    if save is None:
        if not name:
            save = False
        else:
            save = question( "Save your model after each stage completes?" )
    
    walkthrough = algorithms.s999_wizard.Wizard( new = new,
                                                 name = name,
                                                 imports = imports,
                                                 pause_import = pause_import,
                                                 pause_components = pause_components,
                                                 pause_align = pause_align,
                                                 pause_tree = pause_tree,
                                                 pause_fusion = pause_fusion,
                                                 pause_splits = pause_splits,
                                                 pause_consensus = pause_consensus,
                                                 pause_subset = pause_subset,
                                                 pause_pregraphs = pause_pregraphs,
                                                 pause_minigraph = pause_minigraph,
                                                 pause_sew = pause_sew,
                                                 pause_clean = pause_clean,
                                                 pause_check = pause_check,
                                                 tolerance = tolerance,
                                                 alignment = alignment,
                                                 tree = tree,
                                                 view = view,
                                                 save = save,
                                                 outgroups = outgroups,
                                                 supertree = supertree )
    
    walkthrough.make_active()
    MCMD.progress( "The wizard has been created paused.\nYou can use the {} and {} commands to manage your wizard.".format( continue_wizard, stop_wizard ) )


def question( *args ):
    return MCMD.question( *args )


@command( names = ["groot"], visibility = visibilities.ADVANCED )
def cmd_groot():
    """
    Displays the application version.
    """
    MCMD.print( "I AM {}. VERSION {}.".format( MENV.name, MENV.version ) )
