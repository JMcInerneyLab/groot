import warnings
from typing import Optional

from mgraph import MGraph
from mhelper import MEnum


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
    
    Note that `RNA` is obsolete and is no longer supported.
    Please convert RNA to DNA first.
    
    :cvar UNKNOWN:  Unknown site type.
                    Placeholder only until the correct value is identified.
                    Not usually a valid option. 
    :cvar PROTEIN:  For peptide sequences "IVLFCMAGTSWYPHEQDNKR"
    :cvar DNA:      For DNA nucleotide sequences "ATCG"
    """
    UNKNOWN = 0
    PROTEIN = 1
    DNA = 2


class INamedGraph:
    @property
    def graph( self ) -> Optional[MGraph]:
        return self.on_get_graph()
    
    
    def on_get_graph( self ) -> Optional[MGraph]:
        raise NotImplementedError( "abstract" )
    
    
    @property
    def name( self ) -> str:
        warnings.warn( "Deprecated - ambiguous between `str` and `get_accid`.", DeprecationWarning )
        return self.get_accid()
    
    
    def get_accid( self ) -> str:
        raise NotImplementedError( "abstract" )
