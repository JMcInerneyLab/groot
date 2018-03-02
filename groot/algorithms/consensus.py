from typing import Iterable, Optional

import groot.algorithms.external_runner
from groot.algorithms import graph_viewing, importation
from groot.data.lego_model import LegoModel, LegoSequence
from mgraph import MGraph, MNode, exporting
from mhelper import ByRef, array_helper


def tree_consensus( algorithm: Optional[str], model: LegoModel, graphs: Iterable[MGraph] ) -> (MGraph, MNode):
    """
    Generates a consensus tree.
    :param algorithm:   Algorithm to use. See `algorithm_help`.
    :param model:       Model 
    :param graphs:      Graphs to generate consensus from 
    :return:            Tuple of consensus tree and its root 
    """
    newick = []
    
    for a, b in array_helper.lagged_iterate( graphs ):
        aa = set( x.data for x in a.nodes if isinstance( x.data, LegoSequence ) )
        bb = set( x.data for x in b.nodes if isinstance( x.data, LegoSequence ) )
        
        if aa != bb:
            raise ValueError( "Refusing to generate a consensus because the sets of at least two of the graphs are dissimilar. First set = «{}», second set = «{}», difference = «{}».".format( aa, bb, aa.difference( bb ) ) )
    
    for graph in graphs:
        aa = set( x for x in graph.nodes if isinstance( x.data, LegoSequence ) )
        
        if not aa:
            raise ValueError( "Refusing to generate a consensus because at least one graph has no sequence data: {}".format( graph ) )
        
        newick.append( exporting.export_newick( graph, fnode = graph_viewing.FORMATTER.prefixed_sequence_internal_id ) )
    
    fn = groot.algorithms.external_runner.get_tool( "consensus", algorithm )
    
    consensus_newick = groot.algorithms.external_runner.run_in_temporary( fn, model, "\n".join( newick ) + "\n" )
    
    root_ref = ByRef[MNode]( None )
    result = importation.import_newick( consensus_newick, model, root_ref )
    return result, root_ref.value
