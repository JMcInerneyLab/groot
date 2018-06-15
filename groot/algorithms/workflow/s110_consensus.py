from groot import constants
from intermake import MCMD, command
from mhelper import Logger, LogicError, ansi_helper, string_helper
from typing import Set

from groot.constants import STAGES, EChanges
from groot.data import Split, global_view


__LOG_EVIDENCE = Logger( "nrfg.evidence", False )
__mcmd_folder_name__ = constants.MCMD_FOLDER_NAME

@command(folder = constants.F_CREATE)
def create_consensus( cutoff: float = 0.5 ) -> EChanges:
    """
    Filters the candidate splits.
    
    NRFG PHASE II.
    
    Collect consensus evidence.
    
    :remarks:
    ----------------------------------------------------------------------------------------------------
    | The second stage of the consensus.                                                               |
    | We collect evidence from the graphs to support or reject our splits.                             |
    | Unlike a normal majority rule consensus, there's no guarantee that our splits are in the graphs, |
    | so, in addition to support/reject evidence, we have a third category, whereby the graph neither  |
    | supports nor rejects a split.                                                                    |
    ----------------------------------------------------------------------------------------------------
                                                                                                       
    :param cutoff:              Cutoff to be used in the consensus 
    """
    model = global_view.current_model()
    __LOG_EVIDENCE.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ EVIDENCE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    
    model.get_status( STAGES.CONSENSUS_9 ).assert_create()
    
    __LOG_EVIDENCE( "BEGIN EVIDENCE ({} splits)".format( len( model.splits ) ) )
    viable_splits: Set[Split] = set()
    
    for split in model.splits:
        assert isinstance( split, Split ), split
        
        if split.split.is_empty:
            __LOG_EVIDENCE( "SPLIT IS EMPTY: {}".format( split ) )
            continue
        
        evidence_for = set()
        evidence_against = set()
        evidence_unused = set()
        
        for component in model.components:
            component_splits = component.splits
            has_evidence = None
            
            for component_split in component_splits:
                evidence = split.is_evidenced_by( component_split )
                
                if evidence is True:
                    has_evidence = True
                    break
                elif evidence is False:
                    has_evidence = False
            
            if has_evidence is True:
                evidence_for.add( component )
            elif has_evidence is False:
                evidence_against.add( component )
            else:
                evidence_unused.add( component )
        
        if not evidence_for:
            raise LogicError( "There is no evidence for (F{} A{} U{}) this split «{}», but the split must have come from somewhere.".format( len( evidence_for ), len( evidence_against ), len( evidence_unused ), split ) )
        
        total_evidence: int = len( evidence_for ) + len( evidence_against )
        frequency: float = len( evidence_for ) / total_evidence
        accept: bool = frequency > cutoff
        split.evidence_for = frozenset( evidence_for )
        split.evidence_against = frozenset( evidence_against )
        split.evidence_unused = frozenset( evidence_unused )
        
        __LOG_EVIDENCE( "{} {} = {}% -- FOR: ({}) {}, AGAINST: ({}) {}, UNUSED: ({}) {}",
                        "✔" if accept else "✘",
                        ansi_helper.ljust( str( split ), 80 ),
                        int( frequency * 100 ),
                        len( evidence_for ),
                        string_helper.format_array( evidence_for, sort = True ),
                        len( evidence_against ),
                        string_helper.format_array( evidence_against, sort = True ),
                        len( evidence_unused ),
                        string_helper.format_array( evidence_unused, sort = True ) )
        
        if accept:
            viable_splits.add( split )
    
    model.consensus = frozenset( viable_splits )
    
    return EChanges.MODEL_DATA


@command(folder = constants.F_DROP)
def drop_consensus():
    """
    Removes data from the model.
    """
    model = global_view.current_model()
    model.get_status( STAGES.CONSENSUS_9 ).assert_drop()
    
    model.consensus = frozenset()
    
    return EChanges.COMP_DATA


@command( names = ["print_consensus", "consensus"], folder=constants.F_PRINT )
def print_consensus() -> EChanges:
    """
    Prints NRFG viable splits.
    """
    
    model = global_view.current_model()
    
    for x in model.consensus:
        MCMD.information( str( x ) )
    
    return EChanges.INFORMATION
