from typing import Optional

from mgraph import MGraph
from mhelper import MEnum, abstract


class EPosition( MEnum ):
    """
    Node positions.
    
    :data NONE:     No specific position
    :data ROOT:     Node is a root.
                    Many software and algorithms only allow named taxa on leaves so this isn't recommended and may be removed.
    :data OUTGROUP: Node is an outgroup.
    """
    NONE = 0
    ROOT = 1
    OUTGROUP = 2


class ILegoNode:
    """
    Things that can be data on graph nodes.
    """
    pass


class INamed:
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
    
    :data UNKNOWN:  Unknown site type.
                    Placeholder only until the correct value is identified.
                    Not usually a valid option. 
    :data PROTEIN:  For peptide sequences "IVLFCMAGTSWYPHEQDNKR"
    :data DNA:      For DNA nucleotide sequences "ATCG"
    :data RNA:      For RNA nucleotide sequences "AUCG".
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