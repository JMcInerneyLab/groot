import os
import shutil
from collections import defaultdict

from Bio.Phylo import BaseTree
from Bio.Phylo.BaseTree import Clade

from LegoModels import LegoModel, LegoComponent
from MHelper import FileHelper, ExceptionHelper


def process_create_tree( model, component: LegoComponent ):
    """
    Creates a tree from the component.
    """
    try:
        # noinspection PyUnresolvedReferences
        from MHelper import BioHelper
        # noinspection PyUnresolvedReferences
        from Bio import Phylo
    except ImportError:
        raise ImportError( "Install BioPython if you want to generate NRFGs." )
    
    fasta = component.to_fasta( simplify = True )
    
    temp_folder_name = "legoalign-temporary-folder"
    
    if os.path.exists( temp_folder_name ):
        shutil.rmtree( temp_folder_name )
    
    FileHelper.create_directory( temp_folder_name )
    
    os.chdir( temp_folder_name )
    
    uid = component.index
    in_file_name = "temp_{}_in.fasta".format( uid )
    out_file_name = "temp_{}_out.fasta".format( uid )
    phy_file_name = "temp_{}_out.phy".format( uid )
    raxml_file_extension = "t{}".format( uid )
    RAXML_BEST_FILE_NAME = "RAxML_bestTree." + raxml_file_extension  # NOT MODIFYABLE
    
    alignment_command = "muscle -in " + in_file_name + " -out " + out_file_name
    
    FileHelper.write_all_text( in_file_name, fasta )
    ExceptionHelper.run_subprocess( alignment_command )
    
    BioHelper.convert_file( out_file_name, phy_file_name, "fasta", "phylip" )
    
    tree_command = "raxml -m PROTGAMMAWAG -p 12345 -s " + phy_file_name + " -# 20 -n " + raxml_file_extension
    ExceptionHelper.run_subprocess( tree_command )
    
    component.tree = FileHelper.read_all_text( RAXML_BEST_FILE_NAME )
    
    for sequence in component.all_sequences():
        if "?" not in sequence.array:
            component.tree = component.tree.replace( "S{}:".format( sequence.id ), sequence.accession + ":" )
    
    # clean up
    os.chdir( ".." )
    shutil.rmtree( temp_folder_name )


class MyNode:
    def __init__( self, name, is_clade = False ):
        self.name = name
        self.is_clade = is_clade
    
    
    def __str__( self ):
        return str( self.name )
    
    
    def colour( self ):
        if self.is_clade:
            return "#FF00FF"
        else:
            return "#FFFF00"
    
    
    def label( self ):
        if self.is_clade:
            return ""
        else:
            return str( self )


def process_trees( model: LegoModel ):
    import networkx
    from Bio import Phylo
    import matplotlib.pyplot as plt
    
    graph = networkx.DiGraph()
    
    nodes = { }
    
    for component in model.components:
        temp_file_name = "temporary.new"
        FileHelper.write_all_text( temp_file_name, component.tree )
        tree = Phylo.read( temp_file_name, "newick" )  # type: BaseTree.Tree
        os.remove( temp_file_name )
        
        
        # Phylo.to_networkx seems broken (it treats all clades as one), hence use our own
        
        def recurse( clade ):
            if clade.name is None:
                the_node = MyNode( "({})".format( len( nodes ) ), True )
            else:
                the_node = nodes.get( clade.name )
                
                if the_node is None:
                    the_node = MyNode( clade.name )
                    nodes[ clade.name ] = the_node
            
            graph.add_node( the_node )
            
            for x in clade.clades:  # type: Clade
                edge_node = recurse( x )
                graph.add_edge( the_node, edge_node, length = x.branch_length )
            
            return the_node
        
        
        recurse( tree.root )
        
        print( "***********" + str( component ) )
        Phylo.draw_ascii( tree )
    
    from networkx.drawing.nx_pydot import pydot_layout
    positions = pydot_layout( graph, prog = 'neato' )
    networkx.draw_networkx( G = graph,
                            pos = positions,
                            with_labels = True,
                            node_color = [ x.colour() for x in graph ],
                            labels = dict( (x, x.label()) for x in graph ),
                            font_size = 8,
                            font_family = "Courier",
                            font_color = (0, 0, 1),
                            node_shape = "s",
                            edge_color = "#00FF00" )
    
    edge_labels = networkx.get_edge_attributes( graph, "length" )
    smallest = min(edge_labels.values())
    edge_labels = dict( (k, "{0}".format(int( v/smallest ))) for k, v in edge_labels.items() )
    
    networkx.draw_networkx_edge_labels( G = graph,
                                        pos = positions,
                                        edge_labels = edge_labels,
                                        font_family = "Courier",
                                        font_size = 8,
                                        font_color = "#008000")
    
    plt.show()
