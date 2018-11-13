import itertools
from typing import Iterable, List, Set, cast, Callable

from groot import constants
from groot.application import app
from groot.constants import EChanges
from groot.data import INamedGraph, Report, global_view
from groot.utilities import lego_graph
from intermake import pr
from mgraph import AbstractQuartet, QuartetCollection, QuartetComparison, analysing
from mhelper import SwitchError, TIniData, TIniSection, array_helper, string_helper


@app.command( folder = constants.F_CREATE )
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
    
    :param calc_graph_: The model graph. Data is `ILeaf` or `None`. 
    :param orig_graph_: The source graph. Data is `str`.
    :return:  A `Report` object with an `TIniData` as its `raw_data`. 
    """
    differences = []
    differences.append( "<html><body>" )
    differences.append( "<h1>Results for comparison of graphs {} and {}</h1>".format( calc_graph_, orig_graph_ ) )
    
    calc_graph = calc_graph_.graph
    orig_graph = orig_graph_.graph
    ccs = analysing.find_connected_components( calc_graph )
    if len( ccs ) != 1:
        raise ValueError( "The graph has more than 1 connected component ({}).".format( len( ccs ) ) )
    
    calc_genes: Set[object] = set( x.data for x in analysing.realise_node_predicate_as_set( calc_graph, lego_graph.is_sequence_node ) )
    orig_genes: Set[object] = set( x.data for x in analysing.realise_node_predicate_as_set( orig_graph, lego_graph.is_sequence_node ) )
    
    if not calc_genes:
        raise ValueError( "The calculated graph contains no genes." )
    
    if not orig_genes:
        raise ValueError( "The original graph contains no genes." )
    
    if calc_genes != orig_genes:
        raise ValueError( "The calculated graph has a different gene set to the original. Missing: {}; additional: {}.".format(
                string_helper.format_array( orig_genes - calc_genes, sort = True, format = lambda x: "{}:{}".format( type( x ).__name__, x ) ),
                string_helper.format_array( calc_genes - orig_genes, sort = True, format = lambda x: "{}:{}".format( type( x ).__name__, x ) ) ) )
    
    calc_quartets = __get_quartets_with_progress( calc_graph, "calculated" )
    orig_quartets = __get_quartets_with_progress( orig_graph, "original" )
    comparison: QuartetComparison = calc_quartets.compare( orig_quartets )
    
    html = []
    ini_data: TIniData = { }
    
    # QUARTETS
    html.append( '<table border=1 style="border-collapse: collapse;">' )
    html.append( "<tr><td colspan=2><b>QUARTETS</b></td></tr>" )
    ini_data["quartets"] = q = { }
    __add_row( html, q, "total_quartets", len( comparison ) )
    __add_row( html, q, "match_quartets", string_helper.percent( len( comparison.match ), len( comparison.all ) ) )
    __add_row( html, q, "mismatch_quartets", string_helper.percent( len( comparison.mismatch ), len( comparison.all ) ) )
    __add_row( html, q, "new_quartets", string_helper.percent( len( comparison.missing_in_left ), len( comparison.all ) ) )
    __add_row( html, q, "missing_quartets", string_helper.percent( len( comparison.missing_in_right ), len( comparison.all ) ) )
    
    # GENE COMBINATIONS
    __enumerate_2genes( calc_genes, comparison, html, 1, ini_data )
    __enumerate_2genes( calc_genes, comparison, html, 2, ini_data )
    __enumerate_2genes( calc_genes, comparison, html, 3, ini_data )
    
    c = calc_quartets.get_unsorted_lookup()
    o = orig_quartets.get_unsorted_lookup()
    __list_comp( comparison.match, "MATCHING", html, c, o, ini_data )
    __list_comp( comparison.mismatch, "MISMATCH", html, c, o, ini_data )
    if comparison.missing_in_left:
        __list_comp( comparison.missing_in_left, "MISSING IN LEFT", html, c, o, ini_data )
    if comparison.missing_in_right:
        __list_comp( comparison.missing_in_right, "MISSING IN RIGHT", html, c, o, ini_data )
    
    differences.append( "</body></html>" )
    
    report = Report( "{} -vs- {}".format( orig_graph_, calc_graph_ ), "\n".join( html ) )
    report.raw_data = ini_data
    return report


def __add_row( html, ini, name, value ):
    assert name not in ini
    html.append( "<tr><td>{}</td><td>{}</td></tr>".format( name, value ) )
    ini[name] = value


def __list_comp( comparison, name, html, calculated, original, ini: TIniData ):
    html.append( '<table border=1 style="border-collapse: collapse;">' )
    html.append( "<tr><td colspan=6><b>{} QUARTETS</b></td></tr>".format( name ) )
    ini_sect: TIniSection = { }
    ini[name.lower()] = ini_sect
    
    for quartet in comparison:
        calc = calculated[quartet.get_unsorted_key()]
        orig = original[quartet.get_unsorted_key()]
        html.append( "<tr><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td><td>{}</td></tr>".format( *quartet.get_unsorted_key(), calc, orig ) )
        ini_sect["{}_calculated".format( string_helper.format_array( quartet.get_unsorted_key() ) )] = str( calc )
        ini_sect["{}_original".format( string_helper.format_array( quartet.get_unsorted_key() ) )] = str( orig )
    
    html.append( "</table><br/>" )


def __enumerate_2genes( calc_seq: Set[object],
                        comparison: QuartetComparison,
                        html: List[str],
                        n: int,
                        ini_data: TIniData
                        ) -> None:
    if array_helper.get_num_combinations( calc_seq, n ) > 100:
        return
    
    html.append( '<table border=1 style="border-collapse: collapse;">' )
    html.append( "<tr><td colspan=5><b>BREAKDOWN FOR COMBINATIONS OF {}</b></td></tr>".format( n ) )
    html.append( "<tr><td>total</td><td>hit</td><td>miss</td><td>missing in left</td><td>missing in right</td></tr>" )
    ini_sect: TIniSection = { }
    ini_data["n_quartets_{}".format( n )] = ini_sect
    
    for comb in sorted( itertools.combinations( calc_seq, n ), key = cast( Callable, str ) ):  # type: Iterable[object]
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
        
        html.append( "<tr>" )
        i = []
        
        # COMBINATION NAME
        name = string_helper.format_array( comb )
        html.append( "<td>{}</td>".format( name ) )
        # HIT
        txt = string_helper.percent( len( n_hit ), len( n_tot ) ) if n_hit else ""
        html.append( "<td>{}</td>".format( txt ) )
        i.append( txt )
        # MISS
        txt = string_helper.percent( len( n_mis ), len( n_tot ) ) if n_mis else ""
        html.append( "<td>{}</td>".format( txt ) )
        i.append( txt )
        # MISSING IN LEFT
        txt = string_helper.percent( len( n_mil ), len( n_tot ) ) if n_mil else ""
        html.append( "<td>{}</td>".format( txt ) )
        i.append( txt )
        # MISSING IN RIGHT
        txt = string_helper.percent( len( n_mir ), len( n_tot ) ) if n_mil else ""
        html.append( "<td>{}</td>".format( txt ) )
        i.append( txt )
        
        html.append( "</tr>" )
        ini_sect[name] = "; ".join( str( x ) for x in i )
        
        # Write out full quartets (if < 10)
        i = []
        
        if len( n_hit ) < len( n_mis ) < 10:
            for quartet in n_mis:
                html.append( "<tr>" )
                html.append( "<td></td>" )
                html.append( "<td colspan=4>{}</td>".format( quartet ) )
                html.append( "</tr>" )
                i.append( quartet )
        
        ini_sect[name + "_list"] = "; ".join( str( x ) for x in i )
    
    html.append( "</table><br/>" )


def __get_quartets_with_progress( graph, title ) -> QuartetCollection:
    r = []
    
    for q in pr.pr_iterate( analysing.iter_quartets( graph, lego_graph.is_sequence_node ), "Reducing '{}' to quartets".format( title ), count = analysing.get_num_quartets( graph, lego_graph.is_sequence_node ) ):
        r.append( q )
    
    return QuartetCollection( r )


def __append_ev( out_list: List[str],
                 the_set,
                 title: str
                 ) -> None:
    for index, b_split in enumerate( the_set ):
        out_list.append( title + "_({}/{}) = {}".format( index + 1, len( the_set ), b_split.to_string() ) )
