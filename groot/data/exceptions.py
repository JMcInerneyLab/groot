



class NotReadyError(Exception):
    pass
        

class AlreadyError(Exception):
    def __init__(self, op,current):
        super().__init__( "Cannot proceed with the «{}.{}» stage because it has already been performed. Perhaps you meant to revert this stage first?".format(op,current))
    
class InUseError(Exception):
    pass


class FastaError( Exception ):
    """
    Returned by `IHasFasta.to_fasta` when the request cannot be completed.
    """
    pass