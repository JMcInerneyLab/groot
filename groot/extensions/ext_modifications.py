import re
from typing import List, Optional

from groot.algorithms import deconvolution, editor, importation
from groot.data import global_view
from groot.data.lego_model import LegoComponent, LegoEdge, LegoSequence, LegoSubsequence
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import command
from intermake.engine.environment import MCMD



__mcmd_folder_name__ = "Modifications"


@command()
def clean( edges: bool = True, subsequences: bool = True ) -> EChanges:
    """
    Removes redundancies (duplicates) from the model.
    
    :param subsequences: When `True`, redundant subsequences are removed. 
    :param edges:        When `True`, redundant edges are removed.
    :return: 
    """
    model = global_view.current_model()
    
    if not edges and not subsequences:
        raise ValueError( "You must specify at least one item to clean." )
    
    if edges:
        with MCMD.action( "Removing redundant edges" ):
            deconvolution.remove_redundant_edges( model )
    
    if subsequences:
        with MCMD.action( "Removing redundant subsequences" ):
            deconvolution.remove_redundant_subsequences( model )
    
    return EChanges.MODEL_ENTITIES




@command()
def set_tree( component: LegoComponent, tree: str ) -> EChanges:
    """
    Sets a component tree manually.
    
    :param component:   Component 
    :param tree:        Tree to set. In newick format. 
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





def new_edge( left: LegoSubsequence, right : LegoSubsequence ) -> EChanges:
    """
    Adds a new edge to the model.
    :param left:     Subsequence to create the edge from 
    :param right:    Subsequence to create the edge to
    """
    editor.add_new_edge( left, right, no_fresh = False )
    return EChanges.MODEL_ENTITIES


@command()
def new_sequence() -> EChanges:
    """
    Adds a new sequence to the model
    """
    model = global_view.current_model()
    editor.add_new_sequence( model, no_fresh = False )
    return EChanges.MODEL_ENTITIES


def merge_subsequences( subsequences: List[LegoSubsequence] ) -> EChanges:
    """
    Merges the specified subsequences, combining them into one, bigger, subsequence.
    :param subsequences:    Subsequences to merge
    """
    model = global_view.current_model()
    editor.merge_subsequences( model, subsequences, no_fresh = False )
    return EChanges.MODEL_ENTITIES


@command()
def find_sequences( find: str ) -> EChanges:
    """
    Lists the sequences whose accession matches the specified regular expression.
    
    :param find:    Regular expression
    """
    __find_sequences( find )
    return EChanges.NONE


@command()
def remove_sequences( sequences: Optional[List[LegoSequence]] = None, find: Optional[str] = None ) -> EChanges:
    """
    Removes one or more sequences from the model.
    :param find:      Optional regular expression specifying the sequence(s) to remove, by accession.
    :param sequences: The sequences to remove
    """
    if sequences is None:
        sequences = []
    
    if find:
        sequences.extend( __find_sequences( find ) )
    
    editor.remove_sequences( sequences, no_fresh = False )
    
    MCMD.print( "Dropped {} sequences.".format( len( sequences ) ) )
    
    return EChanges.MODEL_ENTITIES


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
