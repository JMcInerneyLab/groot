from groot.algorithms import fastaiser, external_tools
from groot.data.lego_model import LegoComponent


def clear(component : LegoComponent):
    component.alignment = None

def align(component : LegoComponent):
    fasta = fastaiser.component_to_fasta(component, simplify = True)
    
    component.alignment = external_tools.run_in_temporary( external_tools.align, fasta )