from legoalign.scripts import external_tools
from legoalign import external_runner
from legoalign.LegoModels import LegoComponent
from legoalign.algorithms import fastaiser

def clear(component : LegoComponent):
    component.alignment = None

def align(component : LegoComponent):
    fasta = fastaiser.component_to_fasta(component, simplify = True)
    
    component.alignment = external_runner.run_in_temporary( external_tools.align, fasta )