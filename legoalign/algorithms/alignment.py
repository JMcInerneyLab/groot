from typing import List

from os import path

from legoalign.LegoModels import LegoModel, LegoComponent
from legoalign.algorithms import fastaiser
from mcommand import current_environment, constants
from mhelper import FileHelper, ExceptionHelper

def clear(component : LegoComponent):
    component.alignment = None

def align(component : LegoComponent):
    fasta = fastaiser.component_to_fasta(component, simplify = True)
    
    working_dir = current_environment().local_data.local_folder( constants.FOLDER_TEMPORARY )
    in_file_name = path.join(working_dir, "temporary_fasta_file.fasta")
    out_file_name = path.join(working_dir, "temporary_aligned_file.fasta")
    alignment_command = "muscle -in " + in_file_name + " -out " + out_file_name
    
    FileHelper.write_all_text( in_file_name, fasta )
    ExceptionHelper.run_subprocess( alignment_command )
    
    alignment = FileHelper.read_all_text(out_file_name)
    
    component.alignment = alignment