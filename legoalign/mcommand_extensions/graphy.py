from ete3.evol import model

from legoalign.data.graphing import MGraph
from legoalign.data.lego_model import LegoComponent
from mcommand import command, MCMD 
from legoalign.algorithms import fuse

@command()
def graph_split( component: LegoComponent ):
    """
    Testing
    :param component: Testing 
    :return: 
    """
    graph = MGraph()
    graph.import_newick( component.tree, component.model )
    fuse.find_fusion_events()
    MCMD.print(graph.to_string())