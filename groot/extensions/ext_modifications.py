from typing import List, Optional

import re

from groot.algorithms import deconvolution, quantisation, verification, editor
from groot.data import global_view
from groot.data.graphing import MGraph
from groot.data.lego_model import LegoComponent, LegoSequence
from groot.frontends.gui.gui_view_utils import Changes
from intermake import command
from intermake.engine.environment import MCMD
from mhelper import ignore


__mcmd_folder_name__ = "Modifications"


@command()
def clean( edges: bool = True, subsequences: bool = True ) -> Changes:
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
    
    return Changes( Changes.MODEL_ENTITIES )


@command()
def verify() -> Changes:
    """
    Verifies the integrity of the model.
    """
    verification.verify( global_view.current_model() )
    MCMD.print( "Verified OK." )
    
    return Changes( Changes.NONE )


@command()
def set_tree( component: LegoComponent, tree: str ) -> Changes:
    """
    Sets a component tree manually.
    
    :param component:   Component 
    :param tree:        Tree to set. In newick format. 
    """
    g = MGraph()
    g.import_newick( tree, component.model )
    component.tree = g
    
    return Changes( Changes.COMP_DATA )


@command()
def set_alignment( component: LegoComponent, alignment: str ) -> Changes:
    """
    Sets a component tree manually.
    
    :param component:        Component. 
    :param alignment:        Alignment to set. 
    """
    component.alignment = alignment
    
    return Changes( Changes.COMP_DATA )


@command()
def quantise( level: int ) -> Changes:
    """
    Quantises the model.
    
    :param level:   Quantisation level, in sites 
    :return: 
    """
    
    before, after = quantisation.quantise( global_view.current_model(), level )
    
    MCMD.print( "Quantised applied. Reduced the model from {} to {} subsequences.".format( before, after ) )
    
    return Changes( Changes.MODEL_ENTITIES )


def new_subsequence( sequence, split_point ) -> Changes:
    ignore( sequence, split_point )
    return Changes( Changes.NONE )  # TODO


def new_edge( subsequences ) -> Changes:
    ignore( subsequences )
    return Changes( Changes.NONE )  # TODO


def new_sequence() -> Changes:
    return Changes( Changes.NONE )  # TODO


def merge_subsequences( subsequences ) -> Changes:
    ignore( subsequences )
    return Changes( Changes.NONE )  # TODO


@command()
def find_sequences( find: str ) -> Changes:
    """
    Lists the sequences whose accession matches the specified regular expression.
    :param find:    Regular expression
    """
    for sequence in __find_sequences( find ):
        MCMD.print( sequence )
    
    return Changes( Changes.NONE )


@command()
def remove_sequences( sequences: Optional[List[LegoSequence]] = None, find: Optional[str] = None ) -> Changes:
    """
    Removes one or more sequences from the model.
    :param find:      Optional regular expression specifying the sequence(s) to remove, by accession.
    :param sequences: The sequences to remove
    """
    if sequences is None:
        sequences = []
    
    model = global_view.current_model()
    
    if find:
        sequences.extend( __find_sequences( find ) )
        
    
    for sequence in sequences:
        MCMD.print( "READY TO DROP {}".format(sequence ))
        
    editor.remove_sequences( model, sequences )
    
    return Changes( Changes.MODEL_ENTITIES )


def __find_sequences( find ):
    model = global_view.current_model()
    
    sequences = []
    rx = re.compile( find, re.IGNORECASE )
    for s in model.sequences:
        if rx.search( s.accession ):
            sequences.append( s )
    
    return sequences


def remove_edges( subsequences, edges ) -> Changes:
    ignore( subsequences, edges )
    return Changes( Changes.NONE )  # TODO
