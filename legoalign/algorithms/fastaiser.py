from legoalign.LegoModels import LegoEdge, LegoSubsequence, LegoSequence, LegoModel
from mhelper.ExceptionHelper import SwitchError


def to_fasta( item, header ):
    if isinstance( item, LegoEdge ):
        return edge_to_fasta( item, header )
    elif isinstance( item, LegoSubsequence ):
        return subsequence_to_fasta( item, header )
    elif isinstance( item, LegoSequence ):
        return sequence_to_fasta( item, header )
    else:
        raise SwitchError( "item", item, instance = True )


def edge_to_fasta( edge: LegoEdge, header ):
    fasta = [ ]
    fasta.append( ";" )
    fasta.append( "; EDGE: {}".format( edge ) )
    fasta.append( ";" )
    
    if header:
        fasta.append( ">{} [ {} : {} ]".format( edge.source.sequence, edge.source.start, edge.source.end ) )
    
    fasta.append( edge.source.sites or ";MISSING" )
    fasta.append( "" )
    
    if header:
        fasta.append( ">{} [ {} : {} ]".format( edge.destination.sequence, edge.destination.start, edge.destination.end ) )
    
    fasta.append( edge.destination.sites or ";MISSING" )
    fasta.append( "" )
    return "\n".join( fasta )


def subsequence_to_fasta( subsequence: LegoSubsequence, header ):
    fasta = [ ]
    
    if header:
        fasta.append( ">" + str( subsequence ) )
    
    if subsequence.site_array is not None:
        fasta.append( subsequence.site_array )
    else:
        fasta.append( "; MISSING" )
    
    return "\n".join( fasta )


def sequence_to_fasta( sequence: LegoSequence, header ):
    fasta = [ ]
    
    if header:
        fasta.append( ">" + sequence.accession )
    
    if sequence.site_array is not None:
        fasta.append( sequence.site_array )
    else:
        fasta.append( "; MISSING" )
    
    return "\n".join( fasta )


def model_to_fasta( model: LegoModel, header: bool = True, simplify: bool = False ) -> str:
    """
    Converts the component to FASTA
    :param header:   Include header (as FASTA comments)
    :param simplify: Turns on simplified mode to produce output for limited parsers:
                            * Names are replaced with short "S*" numbers
                            * Comments are removed
                            * Errors are raised on failure instead of appending comments to the file 
    :return:         FASTA, as a string 
    """
    fasta = [ ]
    
    if header and not simplify:
        fasta.append( ";" )
        fasta.append( "; COMPONENT: " + str( model ) )
        fasta.append( ";" )
    
    for sequence in model.sequences:
        if sequence.component is model:
            start = 1
            end = sequence.length
            entirety = True
        else:
            relevant = [ x for x in sequence.subsequences if model in x.components ]
            
            if not relevant:
                continue
            
            start = min( x.start for x in relevant )
            end = max( x.end for x in relevant )
            entirety = False
        
        array = sequence.sub_sites( start, end )
        
        if simplify:
            fasta.append( ">S" + str( sequence.id ) )
        elif entirety:
            fasta.append( ">{}".format( sequence ) )
        else:
            fasta.append( ">{}[{}:{}]".format( sequence, start, end ) )
        
        if array is not None:
            fasta.append( array )
            fasta.append( "" )
        elif simplify:
            raise ValueError( "Sequence '{}' has no array data. Have you loaded the FASTA? Have you loaded the correct FASTA?".format( sequence ) )
        else:
            fasta.append( ";MISSING" )
            fasta.append( "" )
    
    return "\n".join( fasta )
