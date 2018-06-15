from groot import supertree_algorithms, Subset, Gene
from mgraph import importing, MGraph
from mhelper import file_helper, Logger, LogicError, exception_helper
from intermake import subprocess_helper


__LOG_CREATE = Logger( "supertree" )


@supertree_algorithms.register( "clann" )
def supertree_clann( inputs: str ) -> str:
    """
    Uses CLANN to generate a supertree.
    
    :param inputs:      Input trees in Newick format.
    :return:            The consensus supertree in Newick format.
    """
    file_helper.write_all_text( "in_file.nwk", inputs )
    
    script = """
    execute in_file.nwk;
    hs savetrees=out_file.nwk;
    quit
    """
    
    subprocess_helper.run_subprocess( ["clann"], stdin = script )
    
    result = file_helper.read_all_text( "out_file.nwk" )
    
    return result.split( ";" )[0]


@supertree_algorithms.register( "groot" )
def supertree_groot( subset_src: Subset ) -> MGraph:
    """
    Uses GROOT to grow a supertree from the splits.
    
    This is a fast, ad-hoc algorithm and should not substitute a well defined, peer reviewed tool.
    """
    
    __LOG_CREATE.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ CREATE GRAPHS FOR POINTS ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    
    exception_helper.assert_type( "subset_src", subset_src, Subset )
    
    subset = subset_src.contents
    __LOG_CREATE.pause( "***** LEAF SET {} *****", subset )
    
    relevant_splits = set()
    
    __LOG_CREATE.pause( "LEAF SET {}", subset )
    model = subset_src.model
    
    for split in model.consensus:
        subset_sequences = frozenset( x for x in subset if isinstance( x, Gene ) )
        
        if split.split.all.issuperset( subset_sequences ):  # S c G
            intersection = split.split.intersection( subset )
            if intersection.is_redundant():
                __LOG_CREATE( "  BAD: {} “{}”", split, intersection )
            elif intersection not in relevant_splits:
                __LOG_CREATE( "  OK : {} “{}”", split, intersection )
                relevant_splits.add( intersection )
            else:
                __LOG_CREATE( "  REP: {} “{}”", split, intersection )
        else:
            missing = subset - split.split.all
            if not missing:
                __LOG_CREATE( "ERROR" )
            
            __LOG_CREATE( "  NSU: {}", split )
            __LOG_CREATE( "    -: {}", missing )
    
    if not relevant_splits:
        msg = "I cannot reconstruct this graph because all splits for the gene set «{}» were rejected. " \
              "The reasons for rejections have not been retained in memory. " \
              "Please turn on logging and investigate history to see details."
        raise LogicError( msg.format( subset ) )
    
    minigraph = importing.import_splits( relevant_splits )
    
    __LOG_CREATE( minigraph.to_ascii() )
    __LOG_CREATE( "END OF GENE SET {}", subset, key = "nrfg.289" )
    
    return minigraph
