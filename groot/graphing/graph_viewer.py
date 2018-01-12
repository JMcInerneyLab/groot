from typing import List, Optional, Set

from groot.graphing.graphing import DNodeToText, MGraph, MNode
from mhelper import SvgWriter, array_helper, svg_helper


class SNode:
    def __init__( self, node: MNode, layer_index, layers: List[List["SNode"]], parent: Optional["SNode"], index ):
        self.node: MNode = node
        self.layer_index = layer_index
        self.layers = layers
        self.parent: SNode = parent
        self.children: List[SNode] = []
        self.slot = None
        self.index = index
    
    
    @property
    def layer( self ):
        return self.layers[self.layer_index]
    
    
    @property
    def has_slot( self ):
        return self.slot is not None
    
    
    def calculate_slot( self ) -> bool:
        if self.slot is not None:
            return True
        
        # I have children?
        if self.children:
            if not all( x.has_slot for x in self.children ):
                return False
            
            slot_sum = 0
            
            for child in self.children:
                if child.slot is not None:
                    slot_sum += child.slot
            
            self.slot = slot_sum / len( self.children )
            return True
        
        # I have parents?
        if self.parent and self.parent.has_slot:
            self.slot = self.parent.slot
            return True
        
        # If I have neither, distribute myself
        sorted_ = sorted( self.layer, key = lambda x: x.parent.index * 1000 + self.index )
        self.slot = (sorted_.index( self ) / len( sorted_ )) * 1024
        return True


def to_svg( self: MGraph, get_text: DNodeToText, roots = None, html: bool = False ):
    #
    # CONSTANTS
    #
    BOX_WIDTH = 48
    BOX_HEIGHT = 32
    SPACE_WIDTH = 16
    SPACE_HEIGHT = 16
    DIST_WIDTH = BOX_WIDTH + SPACE_WIDTH
    DIST_HEIGHT = BOX_HEIGHT + SPACE_HEIGHT
    
    node_style = {
        "fill"        : "#E0FFE0",
        "rx"          : 4,
        "ry"          : 4,
        "stroke_width": 2,
        "stroke"      : "#00FFC0",
    }
    
    text_style = {
        "font_size"         : 8,
        "alignment_baseline": svg_helper.EAlignmentBaseline.middle,
        "text_anchor"       : svg_helper.ETextAnchor.middle
    }
    
    line_style = {
        "stroke_width": 2
    }
    
    #
    # ORDERING
    #
    layers = __get_layers( roots, self )
    all_snodes = []
    map_snodes = { }
    
    for layer in layers:
        for snode in layer:
            map_snodes[snode.node] = snode
            all_snodes.append( snode )
    
    _position_below_parents( layers )
    _position_above_children( layers )
    
    svg = SvgWriter()
    svg.enable_html = html
    
    #
    # POSITIONS
    #
    for snode in all_snodes:
        snode.x = snode.slot * DIST_WIDTH
        snode.y = SPACE_HEIGHT + snode.layer_index * DIST_HEIGHT
    
    #
    # DRAWING
    #
    for snode in all_snodes:
        # Box
        svg.add_rect( snode.x, snode.y, BOX_WIDTH, BOX_HEIGHT, **node_style )
        
        # Text
        text = get_text( snode.node )
        svg.add_text( snode.x + BOX_WIDTH / 2, snode.y + BOX_HEIGHT / 2, text, **text_style )
        
        # Lines
        for friend in snode.node.iter_relations():
            sfriend = map_snodes[friend]
            
            if sfriend is snode.parent or sfriend.parent is snode:
                stroke = "black"
            else:
                stroke = "red"
            
            svg.add_connector( snode.x, snode.y, BOX_WIDTH, BOX_HEIGHT, sfriend.x, sfriend.y, BOX_WIDTH, BOX_HEIGHT, stroke = stroke, **line_style )
    
    return svg.to_string()


def _position_above_children( layers ):
    for layer in reversed( layers ):
        for snode in layer:
            if snode.children:
                snode.slot = sum( x.slot for x in snode.children ) // len( snode.children ) + 1


def _position_below_parents( layers ):
    for i, layer in enumerate( layers ):
        slots = set()
        
        if i == 0:
            ordered_layer = layer
        else:
            ordered_layer = sorted( layer, key = lambda x: x.parent.slot )
        
        for snode in ordered_layer:
            if snode.layer_index == 0:
                if snode.slot is None:
                    snode.slot = __next_free_slot( 0, slots )
            else:
                snode.slot = __next_free_slot( snode.parent.slot, slots )


def __next_free_slot( i, slots ):
    while i in slots:
        i += 1
    
    slots.add( i )
    return i


def __get_layers( roots, self ) -> List[List[SNode]]:
    layers: List[List[SNode]] = []
    
    if not roots:
        roots = [array_helper.first_or_error( self.nodes )]
    
    visited: Set[MNode] = set()
    nodes = []
    
    for node in roots:
        parent_snode = SNode( node, 0, layers, None, len( nodes ) )
        nodes.append( parent_snode )
    
    while nodes:
        layers.append( nodes )
        next_nodes = []
        
        for parent_snode in nodes:
            for edge in parent_snode.node.list_edges():
                opposite = edge.opposite( parent_snode.node )
                if opposite not in visited:
                    visited.add( parent_snode.node )
                    child_snode = SNode( opposite, len( layers ), layers, parent_snode, len( next_nodes ) )
                    parent_snode.children.append( child_snode )
                    next_nodes.append( child_snode )
        
        nodes = next_nodes
    
    return layers
