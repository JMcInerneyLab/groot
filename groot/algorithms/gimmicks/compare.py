import itertools
from typing import Iterable, List, Set

from groot import constants
from intermake import MCMD, command
from mgraph import AbstractQuartet, MNode, QuartetCollection, QuartetComparison, analysing
from mhelper import SwitchError, ansi, array_helper, string_helper

from groot.data import INamedGraph, Model, Report, Gene, global_view
from groot.constants import EChanges
from groot.utilities import lego_graph

__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME_EXTRA

@command(folder=constants.F_CREATE)
def create_comparison( left: INamedGraph, right: INamedGraph ) -> EChanges:
    """
    Compares two graphs.
    The resulting report is added to the current model's user reports.
    :param left:        First graph. The calculated or "new" data. 
    :param right:       Second graph. The original or "existing" data.
    """
    model = global_view.current_model()
    
    model.user_reports.append( compare_graphs( left, right ) )
    
    return EChanges.INFORMATION


def compare_graphs( calc_graph_: INamedGraph,
                    orig_graph_: INamedGraph ) -> Report:
    """
    Compares graphs using quartets.
    
    :param calc_graph_: The model graph. Data is ILeaf or None. 
    :param orig_graph_: The source graph. Data is str.
    :return: 
    """
    differences = []
    differences.append( "<html><body>" )
    differences.append( "<h1>Results for comparison of graphs {} and {}</h1>".format( calc_graph_.name, orig_graph_.name ) )
    
    calc_graph = calc_graph_.graph
    orig_graph = orig_graph_.graph
    ccs = analysing.find_connected_components( calc_graph )
    if len( ccs ) != 1:
        raise ValueError( "The graph has more than 1 connected component ({}).".format( len( ccs ) ) )
    
    calc_seq: Set[object] = set( x.data for x in analysing.realise_node_predicate_as_set( calc_graph, lego_graph.is_sequence_node ) )
    orig_seq: Set[object] = set( x.data for x in analysing.realise_node_predicate_as_set( orig_graph, lego_graph.is_sequence_node ) )
    
    if not calc_seq:
        raise ValueError( "The calculated graph contains no sequences." )
    
    if not orig_seq:
        raise ValueError( "The original graph contains no sequences." )
    
    if calc_seq != orig_seq:
        raise ValueError( "The calculated graph has a different sequence set to the original. Missing: {}; additional: {}.".format(
                string_helper.format_array( orig_seq - calc_seq, sort = True, format = lambda x: "{}:{}".format( type( x ).__name__, x ) ),
                string_helper.format_array( calc_seq - orig_seq, sort = True, format = lambda x: "{}:{}".format( type( x ).__name__, x ) ) ) )
    
    calc_quartets = __get_quartets_with_progress( calc_graph, "calculated" )
    orig_quartets = __get_quartets_with_progress( orig_graph, "original" )
    comparison: QuartetComparison = calc_quartets.compare( orig_quartets )
    
    res = []
    
    res.append( '<table border=1 style="border-collapse: collapse;">' )
    res.append( "<tr><td colspan=2><b>QUARTETS</b></td></tr>" )
    res.append( "<tr><td>total_quartets</td><td>{}</td></tr>".format( len( comparison ) ) )
    res.append( "<tr><td>match_quartets</td><td>{}</td></tr>".format( string_helper.percent( len( comparison.match ), len( comparison.all ) ) ) )
    res.append( "<tr><td>mismatch_quartets</td><td>{}</td></tr>".format( string_helper.percent( len( comparison.mismatch ), len( comparison.all ) ) ) )
    if comparison.missing_in_left:
        res.append( "<tr><td>new_quartets</td><td>{}</td></tr>".format( string_helper.percent( len( comparison.missing_in_left ), len( comparison.all ) ) ) )
    if comparison.missing_in_right:
        res.append( "<tr><td>missing_quartets</td><td>{}</td></tr>".format( string_helper.percent( len( comparison.missing_in_right ), len( comparison.all ) ) ) )
    res.append( "</table><br/>" )
    
    __enumerate_2sequences( calc_seq, comparison, res, 1 )
    __enumerate_2sequences( calc_seq, comparison, res, 2 )
    __enumerate_2sequences( calc_seq, comparison, res, 3 )
    
    c = calc_quartets.get_unsorted_lookup()
    o = orig_quartets.get_unsorted_lookup()
    __list_comp( comparison.match, "MATCHING", res, c, o )
    __list_comp( comparison.mismatch, "MISMATCH", res, c, o )
    if comparison.missing_in_left:
        __list_comp( comparison.missing_in_left, "MISSING IN LEFT", res, c, o )
    if comparison.missing_in_right:
        __list_comp( comparison.missing_in_right, "MISSING IN RIGHT", res, c, o )
    
    differences.append( "</body></html>" )
    
    return Report( "{} -vs- {}".format( orig_graph_.name, calc_graph_.name ), "\n".join( res ) )


def __list_comp( comparison, t, res, c, o ):
    res.append( '<table border=1 style="border-collapse: collapse;">' )
    res.append( "<tr><td colspan=6><b>{} QUARTETS</b></td></tr>".format( t ) )
    for quartet in comparison:
        calc = c[quartet.get_unsorted_key()]
        orig = o[quartet.get_unsorted_key()]
        res.append( "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format( *quartet.get_unsorted_key(), calc, orig ) )
    res.append( "</table><br/>" )


def __enumerate_2sequences( calc_seq: Set[object],
                            comparison: QuartetComparison,
                            res: List[str],
                            r: int
                            ) -> None:
    if array_helper.get_num_combinations( calc_seq, r ) > 100:
        return
    
    res.append( '<table border=1 style="border-collapse: collapse;">' )
    res.append( "<tr><td colspan=5><b>BREAKDOWN FOR COMBINATIONS OF {}</b></td></tr>".format( r ) )
    res.append( "<tr><td>total</td><td>hit</td><td>miss</td><td>missing in left</td><td>missing in right</td></tr>" )
    
    for comb in sorted( itertools.combinations( calc_seq, r ), key = str ):  # type: Iterable[object]
        n_tot = []
        n_hit = []
        n_mis = []
        n_mil = []
        n_mir = []
        
        for quartet in comparison.all:
            assert isinstance( quartet, AbstractQuartet )
            
            if all( x in quartet.get_unsorted_key() for x in comb ):
                n_tot.append( quartet )
                
                if quartet in comparison.match:
                    n_hit.append( quartet )
                elif quartet in comparison.mismatch:
                    n_mis.append( quartet )
                elif quartet in comparison.missing_in_left:
                    n_mil.append( quartet )
                elif quartet in comparison.missing_in_right:
                    n_mir.append( quartet )
                else:
                    raise SwitchError( "quartet(in)", quartet )
        
        if not n_mis and not n_mil and not n_mir:
            continue
        
        res.append( "<tr>" )
        res.append( "<td>{}</td>".format( format( string_helper.format_array( comb ) ) ) )
        res.append( "<td>{}</td>".format( string_helper.percent( len( n_hit ), len( n_tot ) ) if n_hit else "" ) )
        res.append( "<td>{}</td>".format( string_helper.percent( len( n_mis ), len( n_tot ) ) if n_mis else "" ) )
        res.append( "<td>{}</td>".format( string_helper.percent( len( n_mil ), len( n_tot ) ) if n_mil else "" ) )
        res.append( "<td>{}</td>".format( string_helper.percent( len( n_mir ), len( n_tot ) ) if n_mil else "" ) )
        res.append( "</tr>" )
        
        if len( n_hit ) < len( n_mis ) < 10:
            for quartet in n_mis:
                res.append( "<tr>" )
                res.append( "<td></td>" )
                res.append( "<td colspan=4>{}</td>".format( quartet ) )
                res.append( "</tr>" )
    
    res.append( "</table><br/>" )


def __get_quartets_with_progress( graph, title ) -> QuartetCollection:
    r = []
    
    for q in MCMD.iterate( analysing.iter_quartets( graph, lego_graph.is_sequence_node ), "Reducing '{}' to quartets".format( title ), count = analysing.get_num_quartets( graph, lego_graph.is_sequence_node ) ):
        r.append( q )
    
    return QuartetCollection( r )


def __append_ev( out_list: List[str],
                 the_set,
                 title: str
                 ) -> None:
    for index, b_split in enumerate( the_set ):
        out_list.append( title + "_({}/{}) = {}".format( index + 1, len( the_set ), b_split.to_string() ) )


class __NodeFilter:
    def __init__( self, model: Model, accessions: Iterable[str] ):
        self.sequences = [model.genes[ accession ] for accession in accessions]
    
    
    def format( self, node: MNode ):
        d = node.data
        
        if d is None:
            t = "x"
        else:
            t = str( d )
        
        if d in self.sequences:
            assert isinstance( d, Gene )
            return ansi.FORE_GREEN + t + ansi.RESET
        
        for rel in node.relations:
            if rel.data in self.sequences:
                return ansi.FORE_YELLOW + t + ansi.RESET
        
        return ansi.FORE_RED + t + ansi.RESET
    
    
    def query( self, node: MNode ):
        if isinstance( node.data, Gene ):
            return node.data in self.sequences
        
        for rel in node.relations:
            if rel.data in self.sequences:
                return True
        
        for rel in node.relations:
            if isinstance( rel.data, Gene ) and rel.data not in self.sequences:
                return False
        
        return True
