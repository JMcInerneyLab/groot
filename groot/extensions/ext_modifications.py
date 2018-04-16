from typing import List, Optional
from intermake import command, MCMD

from groot import constants, algorithms
from groot.data import global_view, LegoEdge, LegoSequence, LegoComponent, EPosition, LegoSubsequence
from groot.frontends.gui.gui_view_utils import EChanges


__mcmd_folder_name__ = "Modifications"


@command()
def set_outgroups( accessions: List[str] ) -> EChanges:
    """
    Sets the outgroups for the genes with the specified accessions.
    All other genes will have their outgroup/root status removed.
    
    :param accessions:  The accessions
    """
    to_do = set( accessions )
    model = global_view.current_model()
    
    for accession in to_do:
        if not any( x.accession == accession for x in model.sequences ):
            raise ValueError( "Cannot set the outgroups because there is no gene with the accession «{}».".format( accession ) )
    
    for sequence in model.sequences:
        if sequence.accession in to_do:
            sequence.position = EPosition.OUTGROUP
            
            to_do.remove( sequence.accession )
        else:
            sequence.position = EPosition.NONE
    
    if algorithms.s080_tree.reposition_all( global_view.current_model() ):
        r = EChanges.COMP_DATA
    else:
        r = EChanges.NONE
    
    return r


@command()
def set_position( gene: Optional[LegoSequence] = None, position: Optional[EPosition] = None ) -> EChanges:
    """
    Defines or displays the position of a gene in the graph.
    If trees have been generated already they will be re-rooted.
    
    :param gene:        Gene, or `None` to display all genes.
    :param position:    New status (if not specified displays the current position of the gene).
                        If `gene` is `None` then this parameter instead filters the display. 
    """
    if gene is None:
        for gene in global_view.current_model().sequences:
            if (position is None and gene.position != EPosition.NONE) or (position is not None and gene.position == position):
                MCMD.information( "{} : {}".format( gene, gene.position ) )
        
        return EChanges.NONE
    
    if position is not None:
        if gene.model.get_status( constants.STAGES.TREES_6 ).is_partial:
            raise ValueError( "Cannot reposition genes because the trees have already been created." )
        
        gene.position = position
        return EChanges.NONE
    else:
        MCMD.information( "{} : {}".format( gene, gene.position ) )
    
    return EChanges.NONE


@command()
def set_tree( component: LegoComponent, newick: str ) -> EChanges:
    """
    Sets a component tree manually.
    Note that if you have roots/outgroups set your tree may be automatically re-rooted to remain consistent with these settings.
    
    :param component:   Component 
    :param newick:      Tree to set. In Newick format. 
                        _Gene accessions_ and/or _gene internal IDs_ may be provided.
    """
    if component.tree:
        raise ValueError( "This component already has an tree. Did you mean to drop the existing tree first?" )
    
    component.tree_unrooted = algorithms.s020_importation.import_newick( newick, component.model )
    component.tree = component.tree_unrooted.copy()
    component.tree_newick = newick
    algorithms.s080_tree.reposition_all( global_view.current_model(), component )
    
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
    algorithms.s999_editor.add_new_edge( left, right, no_fresh = False )
    return EChanges.MODEL_ENTITIES


@command()
def new_sequence( accessions: List[str] ) -> EChanges:
    """
    Adds a new sequence to the model
    
    :param accessions: Sequence accession(s)
    """
    model = global_view.current_model()
    for accession in accessions:
        sequence = algorithms.s999_editor.add_new_sequence( model, accession, no_fresh = False )
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
    
    component = algorithms.s999_editor.add_new_component( index, model, sequences, subsequences )
    MCMD.progress( "Added: {}".format( component ) )
    
    return EChanges.MODEL_ENTITIES


def remove_edges( subsequences: List[LegoSubsequence], edges: List[LegoEdge] ) -> EChanges:
    """
    Detaches the specified edges from the specified subsequences.
    
    :param subsequences:    Subsequences to unlink
    :param edges:           Edges to affect
    """
    algorithms.s999_editor.remove_edges( subsequences, edges, no_fresh = False )
    return EChanges.MODEL_ENTITIES
