import os
import shutil
from collections import defaultdict

import networkx

from MHelper import FileHelper, ExceptionHelper


def process_create_tree( model, component ):
    """
    Creates a tree from the component.
    """
    try:
        # noinspection PyUnresolvedReferences
        from MHelper import BioHelper
        # noinspection PyUnresolvedReferences
        from Bio import Phylo
    except ImportError:
        raise ImportError("Install BioPython if you want to generate NRFGs.")
        
    
    fasta = [ ]
        
    sequence_components = defaultdict(list)
    
    for component in model.components:
        for sequence in component.all_sequences():
            sequence_components[sequence].append(component)
    
    composite_sequence = None
    
    for sequence in component.all_sequences():
        if len(sequence_components[sequence]) !=1:
            if composite_sequence:
                raise ValueError("There are more than one composites in this component: At least '{}' and '{}'. Consider removing extraenuous sequences.".format(composite_sequence, sequence))
                                 
            composite_sequence = sequence
            continue
            
        if sequence.array:
            fasta.append( ">S" + str( sequence.id ) )
            fasta.append( sequence.array )
            fasta.append( "" )
        else:
            raise ValueError("Sequence '{}' has no array data. Have you loaded the FASTA? Have you loaded the correct FASTA?".format(sequence))
    
    temp_folder_name = "legoalign-temporary-folder"
    
    FileHelper.create_directory( temp_folder_name )
    
    os.chdir( temp_folder_name )
    
    uid = component.index
    in_file_name = "temp_{}_in.fasta".format(uid)
    out_file_name = "temp_{}_out.fasta".format(uid)
    phy_file_name = "temp_{}_out.phy".format(uid)
    raxml_file_extension = "t{}".format(uid)
    RAXML_BEST_FILE_NAME = "RAxML_bestTree." + raxml_file_extension # NOT MODIFYABLE
    best_tree_file_name = "best_tree_{}.new".format(uid)
    
    input_text = "\n".join( fasta )
    alignment_command = "muscle -in "+in_file_name+" -out "+out_file_name
    
    FileHelper.write_all_text( in_file_name, input_text )
    ExceptionHelper.run_subprocess( alignment_command )
    
    
    
    BioHelper.convert_file( out_file_name, phy_file_name, "fasta", "phylip" )
    
    tree_command = "raxml -m PROTGAMMAWAG -p 12345 -s "+phy_file_name+" -# 20 -n "+raxml_file_extension
    ExceptionHelper.run_subprocess( tree_command )
    
    component.tree = FileHelper.read_all_text( RAXML_BEST_FILE_NAME )
    
    for sequence in component.all_sequences():
        if "?" not in sequence.array:
            component.tree = component.tree.replace( "S{}:".format( sequence.id ), sequence.accession )
        
    FileHelper.write_all_text( best_tree_file_name, component.tree )
    
    tree = Phylo.read( best_tree_file_name, "newick" )
    #tree.ladderize()  # Flip branches so deeper clades are displayed at top
    #Phylo.draw( tree )
    
    network = Phylo.to_networkx(tree)
    #networkx.draw(network)
    
    # clean up
    os.chdir( ".." )
    shutil.rmtree( temp_folder_name )