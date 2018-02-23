import re
from typing import List, Optional

from groot.algorithms import editor, importation
from groot.data import global_view
from groot.data.lego_model import LegoComponent, LegoEdge, LegoSubsequence, LegoSequence
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import command
from intermake.engine.environment import MCMD


__mcmd_folder_name__ = "Modifications"


@command()
def set_tree( component: LegoComponent, tree: str ) -> EChanges:
    """
    Sets a component tree manually.
    
    :param component:   Component 
    :param tree:        Tree to set. In Newick format. 
                        Either gene accessions OR gene internal IDs may be provided.
    """
    if component.tree:
        raise ValueError( "This component already has an tree. Did you mean to drop the existing tree first?" )
    
    component.tree = importation.import_newick( tree, component.model )
    
    return EChanges.COMP_DATA


@command()
def set_alignment( component: LegoComponent, alignment: str ) -> EChanges:
    """
    Sets a component tree manually.
    
    :param component:        Component. 
    :param alignment:        Alignment to set. 
    """
    if component.alignment:
        raise ValueError( "This component already has an alignment. Did you mean to drop the existing alignment first?" )
    
    component.alignment = alignment
    
    return EChanges.COMP_DATA


def new_edge( left: LegoSubsequence, right: LegoSubsequence ) -> EChanges:
    """
    Adds a new edge to the model.
    :param left:     Subsequence to create the edge from 
    :param right:    Subsequence to create the edge to
    """
    editor.add_new_edge( left, right, no_fresh = False )
    return EChanges.MODEL_ENTITIES


@command()
def new_sequence( accessions: List[str] ) -> EChanges:
    """
    Adds a new sequence to the model
    
    :param accessions: Sequence accession(s)
    """
    model = global_view.current_model()
    for accession in accessions:
        sequence = editor.add_new_sequence( model, accession, no_fresh = False )
        MCMD.progress( "Added: {}".format( sequence ) )
    return EChanges.MODEL_ENTITIES


@command()
def new_component( index: int, sequences: List[LegoSequence], minor_sequences: Optional[List[LegoSequence]] = None, subsequences: Optional[List[LegoSubsequence]] = None ) -> EChanges:
    """
    Adds a new component to the model
    
    :param index:               Component index. This is a check value and must match the next assigned component. If this is `-1` then no check is performed (not recommended).
    :param sequences:           Sequences (major) of the component. 
    :param minor_sequences:     Subsequences (minor) of the component, as an alternative to the `subsequences` parameter.
                                Component will be invalid for tree generation if this option is used.
    :param subsequences:        Domains (minor) of the component, as an alternative to the `minor_sequences` parameter.
                                This allows the component to be used for tree generation, but requires that the domains of the components are known. 
    """
    model = global_view.current_model()
    
    if subsequences is None:
        subsequences = []
    
    if minor_sequences is not None:
        subsequences.extend( [x.get_totality() for x in minor_sequences] )
    
    component = editor.add_new_component( index, model, sequences, subsequences )
    MCMD.progress( "Added: {}".format( component ) )
    
    return EChanges.MODEL_ENTITIES


@command()
def find_sequences( find: str ) -> EChanges:
    """
    Lists the sequences whose accession matches the specified regular expression.
    
    :param find:    Regular expression
    """
    __find_sequences( find )
    return EChanges.NONE


def __find_sequences( find ):
    model = global_view.current_model()
    
    sequences = []
    rx = re.compile( find, re.IGNORECASE )
    for s in model.sequences:
        if rx.search( s.accession ):
            sequences.append( s )
    
    if not sequences:
        MCMD.print( "No matching sequences." )
    else:
        for sequence in sequences:
            MCMD.print( sequence )
        
        MCMD.print( "Found {} sequences.".format( len( sequences ) ) )
    
    return sequences


def remove_edges( subsequences: List[LegoSubsequence], edges: List[LegoEdge] ) -> EChanges:
    """
    Detaches the specified edges from the specified subsequences.
    
    :param subsequences:    Subsequences to unlink
    :param edges:           Edges to affect
    """
    editor.remove_edges( subsequences, edges, no_fresh = False )
    return EChanges.MODEL_ENTITIES
