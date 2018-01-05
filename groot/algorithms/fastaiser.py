from groot.data.lego_model import LegoSequence, LegoSubsequence, LegoEdge, LegoComponent, ILegoVisualisable
from mhelper import SwitchError


def to_fasta( item: ILegoVisualisable ):
    """
    Converts the component to FASTA
    :param item: 
    :return: 
    """
    if isinstance( item, LegoEdge ):
        return edge_to_fasta( item )
    elif isinstance( item, LegoSubsequence ):
        return subsequence_to_fasta( item )
    elif isinstance( item, LegoSequence ):
        return sequence_to_fasta( item )
    elif isinstance( item, LegoComponent ):
        return component_to_fasta( item )
    else:
        raise SwitchError( "item", item, instance = True )


def component_to_fasta( component: LegoComponent, simplify_ids: bool = False ):
    fasta = []
    
    for subsequence in component.minor_subsequences:
        assert isinstance(subsequence, LegoSubsequence)
        
        if simplify_ids:
            fasta.append( ">S{}".format( subsequence.sequence.id ) )
        else:
            fasta.append( ">{}".format( subsequence ) )
        
        fasta.append( subsequence.site_array )
        fasta.append( "" )
    
    return "\n".join( fasta )


def edge_to_fasta( edge: LegoEdge ):
    fasta = []
    
    fasta.append( ";" )
    fasta.append( "; EDGE: {}".format( edge ) )
    fasta.append( ";" )
    fasta.append( ">{} [ {} : {} ]".format( edge.left.sequence, edge.left.start, edge.left.end ) )
    fasta.append( edge.left.site_array or ";MISSING" )
    fasta.append( "" )
    fasta.append( ">{} [ {} : {} ]".format( edge.right.sequence, edge.right.start, edge.right.end ) )
    fasta.append( edge.right.site_array or ";MISSING" )
    fasta.append( "" )
    
    return "\n".join( fasta )


def subsequence_to_fasta( subsequence: LegoSubsequence ):
    fasta = []
    
    fasta.append( ">" + str( subsequence ) )
    
    if subsequence.site_array is not None:
        fasta.append( subsequence.site_array )
    else:
        fasta.append( "; MISSING" )
    
    return "\n".join( fasta )


def sequence_to_fasta( sequence: LegoSequence ):
    fasta = []
    
    fasta.append( ">" + sequence.accession )
    
    if sequence.site_array:
        fasta.append( sequence.site_array )
    else:
        fasta.append( "; MISSING" )
    
    return "\n".join( fasta )
