from legoalign.data.lego_model import LegoSequence, LegoSubsequence, LegoEdge, LegoComponent
from mhelper import SwitchError


def to_fasta( item ):
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


def component_to_fasta( component: LegoComponent, simplify : bool = False ):
    fasta = [ ]
    
    if not simplify:
        fasta.append( ";" )
        fasta.append( "; COMPONENT: {}".format( component ) )
        fasta.append( ";" )
    
    for element in component.elements():
        if simplify:
            fasta.append( ">S{}".format( element.sequence.id ) )
        else:
            fasta.append( ">{}".format( element ) )
            
        fasta.append( element.sites() )
        fasta.append( "" )
    
    return "\n".join( fasta )


def edge_to_fasta( edge: LegoEdge ):
    fasta = [ ]
    
    fasta.append( ";" )
    fasta.append( "; EDGE: {}".format( edge ) )
    fasta.append( ";" )
    fasta.append( ">{} [ {} : {} ]".format( edge.left.sequence, edge.left.start, edge.left.end ) )
    fasta.append( edge.left.sites or ";MISSING" )
    fasta.append( "" )
    fasta.append( ">{} [ {} : {} ]".format( edge.right.sequence, edge.right.start, edge.right.end ) )
    fasta.append( edge.right.sites or ";MISSING" )
    fasta.append( "" )
    
    return "\n".join( fasta )


def subsequence_to_fasta( subsequence: LegoSubsequence ):
    fasta = [ ]
    
    
    fasta.append( ">" + str( subsequence ) )
    
    if subsequence.site_array is not None:
        fasta.append( subsequence.site_array )
    else:
        fasta.append( "; MISSING" )
    
    return "\n".join( fasta )


def sequence_to_fasta( sequence: LegoSequence ):
    fasta = [ ]
    
    fasta.append( ">" + sequence.accession )
    
    if sequence.site_array:
        fasta.append( sequence.site_array )
    else:
        fasta.append( "; MISSING" )
    
    return "\n".join( fasta )


