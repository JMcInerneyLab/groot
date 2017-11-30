from mhelper import SwitchError

from groot.algorithms.classes import FusionPoint
from groot.data.graphing import MNode, DNodeToText
from groot.data.lego_model import LegoSequence
from intermake.engine.theme import Theme


NEXT_SPECIAL = "["
END_SPECIAL = "]"
END_SKIP = "|"


class __Formatter:
    def pipe( self, _: MNode ) -> str:
        """
        Pipe symbol (`|`)
        """
        return END_SKIP
    
    
    def lbr( self, _: MNode ) -> str:
        """
        Left bracket (`[`)
        """
        return NEXT_SPECIAL
    
    
    def rbr( self, _: MNode ) -> str:
        """
        Right bracket (`]`)
        """
        return END_SPECIAL
    
    
    def name( self, node: MNode ) -> str:
        """
        Name of the sequence, fusion, or clade, prefixed with `seq:`, `fus:` or `cla:` respectively
        """
        if isinstance( node.data, LegoSequence ):
            return "seq:{}".format( node.data.accession )
        elif isinstance( node.data, FusionPoint ):
            return "fus:{}:{}".format( node.data.opposite_component, node.data.count )
        else:
            return "cla:{}".format( node.uid )
    
    
    def uid( self, node: MNode ) -> str:
        return str( node.uid )
    
    
    def short( self, node: MNode ) -> str:
        """
        Name of the sequence or fusion, or clade, prefixed with `⊕ `, `⊛ ` respectively.
        Clades are denoted by `⊙` and the name is not shown.
        """
        if isinstance( node.data, LegoSequence ):
            return "⊕ {}".format( node.data.accession )
        elif isinstance( node.data, FusionPoint ):
            return "⊛ {}:{}".format( node.data.opposite_component, node.data.count )
        else:
            return "⊙"
    
    
    def fusion_name( self, node: MNode ) -> str:
        """
        Name of the fusion, or empty if not a fusion.
        """
        if isinstance( node.data, FusionPoint ):
            return Theme.BOLD + str( node.data ) + Theme.RESET
    
    
    def component_name( self, node: MNode ) -> str:
        """
        Name of the component of the sequence, or empty if not a sequence or the sequence has no component.
        """
        if isinstance( node.data, LegoSequence ) and node.data.component:
            return str( node.data.component )
    
    
    def minor_component_names( self, node: MNode ) -> str:
        """
        Name of the minor components of the sequence, or empty if not a sequence or the sequence has no component.
        """
        if isinstance( node.data, LegoSequence ):
            minor_components = node.data.minor_components()
            
            if minor_components:
                for minor_component in sorted( minor_components, key = str ):
                    return str( minor_component )
    
    
    def sequence_accession( self, node: MNode ) -> str:
        """
        Accession of the sequence, or empty if not a sequence.
        """
        if isinstance( node.data, LegoSequence ):
            return node.data.accession
    
    
    def sequence_length( self, node: MNode ) -> str:
        """
        Length of the sequence, or empty if not a sequence.
        """
        if isinstance( node.data, LegoSequence ):
            return str( node.data.length )
    
    
    def sequence_internal_id( self, node: MNode ) -> str:
        """
        Internal ID of the sequence, or empty if not a sequence.
        """
        if isinstance( node.data, LegoSequence ):
            return node.data.id
    
    
    def is_sequence( self, node: MNode ) -> bool:
        """
        Skips the text until the next `|` if this node is a sequence.
        """
        return isinstance( node.data, LegoSequence )
    
    
    def is_not_sequence( self, node: MNode ) -> bool:
        """
        Skips the text until the next `|` if this node is not a sequence.
        """
        return not isinstance( node.data, LegoSequence )
    
    
    def is_fusion( self, node: MNode ) -> bool:
        """
        Skips the text until the next `|` if this node is a fusion.
        """
        return isinstance( node.data, FusionPoint )
    
    
    def is_not_fusion( self, node: MNode ) -> bool:
        """
        Skips the text until the next `|` if this node is not a fusion.
        """
        return not isinstance( node.data, FusionPoint )
    
    
    def is_clade( self, node: MNode ) -> bool:
        """
        Skips the text until the next `|` if this node is a clade.
        """
        return not isinstance( node.data, LegoSequence ) and not isinstance( node.data, FusionPoint )
    
    
    def is_not_clade( self, node: MNode ) -> bool:
        """
        Skips the text until the next `|` if this node is not a clade.
        """
        return isinstance( node.data, LegoSequence ) or isinstance( node.data, FusionPoint )


FORMATTER = __Formatter()


def create_user_formatter( format_str: str = None ) -> DNodeToText:
    """
    Creates a formatter function based on the specified format string.
    """
    if format_str is None:
        return FORMATTER.short
    
    return (lambda x: lambda n: __format_node( n, x ))( format_str )


def __format_node( node: MNode, format_str: str ) -> str:
    """
    Describes the nodes.
    
    :param node: Node to format
    :param format_str: Format to use:
                            `[xxx]`         - use special entry xxx (taken from __Formatter's methods)
                            `|`             - stop skipping a section (after __Formatter's methods that return a bool)
                                              if not in a section this character is ignored
                            anything else   - verbatim 
    """
    ss = []
    skip = False
    special = False
    special_ss = []
    
    for x in format_str:
        if x == END_SKIP:
            skip = False
        elif skip:
            pass
        elif not special:
            if x == NEXT_SPECIAL:
                special_ss.clear()
                special = True
            else:
                ss.append( x )
        else:
            if x == END_SPECIAL:
                special_str = "".join( special_ss )
                method = getattr( FORMATTER, special_str )
                result = method( node )
                
                if isinstance( result, str ):
                    ss.append( result )
                elif result is False:
                    skip = True
                elif result is True:
                    skip = False
                else:
                    raise SwitchError( "result", result )
            else:
                special_ss.append( x )
    
    return "".join( str( x ) for x in ss ).strip()
