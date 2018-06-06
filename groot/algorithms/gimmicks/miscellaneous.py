from groot import constants
from groot.algorithms import workflow
from groot.constants import EChanges
from groot.data import global_view
from groot.data.model_interfaces import ESiteType, INamedGraph
from groot.utilities import cli_view_utils
from intermake import MCMD, command, common_commands, visibilities
from mgraph import Quartet, analysing
from mhelper import EFileMode, Filename, bio_helper, file_helper, io_helper


_VIS = visibilities.GUI & visibilities.ADVANCED

__EXT_FASTA = ".fasta"
__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME_EXTRA


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


@command( visibility = visibilities.ADVANCED, folder = constants.F_PRINT )
def print_file( type: ESiteType, file: Filename[EFileMode.READ, __EXT_FASTA] ) -> EChanges:
    """
    Prints a FASTA file in colour
    :param type: Type of sites to display.
    :param file: Path to FASTA file to display. 
    """
    text = file_helper.read_all_text( file )
    MCMD.information( cli_view_utils.colour_fasta_ansi( text, type ) )
    
    return EChanges.NONE



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
                workflow.s010_file.file_save()
            return True
        elif switch == "retry":
            return False
        elif switch == "pause":
            common_commands.cmd_start_cli()
        elif switch == "abort":
            raise ValueError( "User cancelled." )


