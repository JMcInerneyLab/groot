from typing import Optional

from mgraph import MGraph
from mhelper import MEnum, abstract


class EPosition( MEnum ):
    """
    Node positions.
    
    :cvar NONE:     No specific position
    :cvar OUTGROUP: Node is an outgroup.
    """
    NONE = 0
    OUTGROUP = 2


class INode:
    """
    Things that can be data on graph nodes.
    """
    pass


class INamed:   # TODO: This is unused, add it into the derived classes and remove it
    @property
    def name( self ):
        return self.on_get_name()
    
    
    @abstract
    def on_get_name( self ):
        raise NotImplementedError( "abstract" )


class IHasFasta:
    """
    Class which has FASTA data.
    This is used by the UI to display such data.
    """
    
    
    def to_fasta( self ) -> str:
        """
        The derived class should return FASTA data commensurate with the request.
        :except FastaError: Request cannot be completed.
        """
        raise NotImplementedError( "abstract" )


class ESiteType( MEnum ):
    """
    Type of sites.
    
    :cvar UNKNOWN:  Unknown site type.
                    Placeholder only until the correct value is identified.
                    Not usually a valid option. 
    :cvar PROTEIN:  For peptide sequences "IVLFCMAGTSWYPHEQDNKR"
    :cvar DNA:      For DNA nucleotide sequences "ATCG"
    :cvar RNA:      For RNA nucleotide sequences "AUCG".
                    For completeness only.
                    Custom/extension algorithms are not expected to support this.
                    Please convert to DNA first!
    """
    UNKNOWN = 0
    PROTEIN = 1
    DNA = 2
    RNA = 3


class INamedGraph( INamed ):
    @property
    def graph( self ) -> Optional[MGraph]:
        return self.on_get_graph()
    
    
    def on_get_graph( self ) -> Optional[MGraph]:
        raise NotImplementedError( "abstract" )
    
    
    @property
    def name( self ) -> str:
        return self.on_get_name()
    
    
    def on_get_name( self ) -> str:
        return str( self )