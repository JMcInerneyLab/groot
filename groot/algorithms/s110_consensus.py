from typing import Set
from mhelper import LogicError, ansi_helper, string_helper, Logger

from groot.constants import STAGES
from groot.data import LegoModel, LegoSplit



__LOG_EVIDENCE = Logger( "nrfg.evidence", False )

def drop_consensus( model: LegoModel ):
    model.get_status( STAGES.CONSENSUS_9 ).assert_drop()
    
    model.consensus = frozenset()


def create_consensus( model: LegoModel, cutoff: float ) -> None:
    """
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
    :param model:               The model 
    :return:                    The set of splits not rejected by the consensus.
    """
    __LOG_EVIDENCE.pause( "▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ EVIDENCE ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒" )
    
    model.get_status( STAGES.CONSENSUS_9 ).assert_create()
    
    __LOG_EVIDENCE( "BEGIN EVIDENCE ({} splits)".format( len( model.splits ) ) )
    viable_splits: Set[LegoSplit] = set()
    
    for split in model.splits:
        assert isinstance( split, LegoSplit ), split
        
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