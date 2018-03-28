from collections import defaultdict
from typing import Dict, FrozenSet, List, Set

from groot.constants import STAGES
from groot.data.lego_model import ILegoNode, LegoModel, LegoPoint, LegoSequence, LegoSubset
from mhelper import Logger


__LOG = Logger( "nrfg.find", False )

def drop_subsets( model: LegoModel ):
    model.get_status( STAGES.SUBSETS_10 ).assert_drop()
    
    model.nrfg.subsets = frozenset()


def create_subsets( model: LegoModel, no_super: bool ):
    """
    NRFG PHASE III.
    
    Find the gene sets
    
    :remarks:
    
    Now for the composite stuff. We need to separate all our graphs into mini-graphs.
    Each minigraph must contain...
          ...its genes (`LegoSequence`)
          ...the fusion points (`FusionPoint`)
              - showing where that graph fits into the big picture.
              
    In this stage we collect "gene_sets", representing the set of sequences in each minigraph.
    We also make a dictionary of "gene_set_to_fusion", representing which fusion points are matched to each "gene set".
    
    :param model:       Model to operate upon
    :param no_super:    Drop supersets from the trees. You want this.
                        Turn if off to see the supersets in the final graph (your NRFG will therefore be a disjoint union of multiple possibilities!).
    :return:            The set of gene sets
    """
    
    model.get_status( STAGES.SUBSETS_10 ).assert_create()
    
    
    __LOG.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ FIND POINTS WITH SAME GENES ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    
    # Define our output variables
    all_gene_sets: Set[FrozenSet[ILegoNode]] = set()
    gene_set_to_fusion: Dict[FrozenSet[ILegoNode], List[LegoPoint]] = defaultdict( list )
    
    # Iterate over the fusion points 
    for fusion_event in model.fusion_events:
        for fusion_point in fusion_event.points:
            # Each fusion point splits the graph into two halves ("inside" and "outside" that point)
            # Each half defines one of our minigraphs.
            pertinent_inner = frozenset( fusion_point.pertinent_inner )
            pertinent_outer = frozenset( fusion_point.pertinent_outer )
            all_gene_sets.add( pertinent_inner )
            all_gene_sets.add( pertinent_outer )
            
            # Note that multiple points may define the same graphs, hence here we specify which points define which graphs. 
            gene_set_to_fusion[pertinent_inner].append( fusion_point )
            gene_set_to_fusion[pertinent_outer].append( fusion_point )
    
    to_remove = set()
    
    # Some of our gene sets will ̶d̶e̶v̶o̶i̶d̶ ̶o̶f̶ ̶g̶e̶n̶e̶s shit
    
    # Drop these now 
    for gene_set in all_gene_sets:
        if not any( isinstance( x, LegoSequence ) for x in gene_set ):
            # No genes in this set
            __LOG( "DROP GENE SET (EMPTY): {}", gene_set )
            to_remove.add( gene_set )
            continue
        
        if no_super:
            remaining = set( gene_set )
            
            for gene_set_2 in all_gene_sets:
                if gene_set_2 is not gene_set:
                    if gene_set_2.issubset( gene_set ):
                        remaining -= gene_set_2
            
            if not remaining:
                # Gene set is a superset of other sets
                __LOG( "DROP GENE SET (SUPERSET): {}", gene_set )
                to_remove.add( gene_set )
                continue
        
        # Good gene set (keep)
        __LOG( "KEEP GENE SET: {}", gene_set )
        for fusion_point in gene_set_to_fusion[gene_set]:
            __LOG( "    POINT: {}", fusion_point )
    
    for gene_set in to_remove:
        all_gene_sets.remove( gene_set )
    
    # Finally, complement our gene sets with the fusion points they are adjacent to
    # We'll need these to know where our graph fits into the big picture
    results: Set[FrozenSet[ILegoNode]] = set()
    
    for gene_set in all_gene_sets:
        new_set = set( gene_set )
        new_set.update( gene_set_to_fusion[gene_set] )
        results.add( frozenset( new_set ) )
    
    model.nrfg.subsets = frozenset( LegoSubset( model, i, x ) for i, x in enumerate( results ) )