

class NotReadyError(Exception):
    def __init__(self, current, requires):
        super().__init__( "Cannot proceed with the «{}» stage because the prerequisite stage «{}» has not yet been performed. Perhaps you meant to perform that stage first?".format(current,requires))
        

class AlreadyError(Exception):
    def __init__(self, current):
        super().__init__( "Cannot proceed with the «{}» stage because it has already been performed. Perhaps you meant to revert this stage first?".format(current))
    
class InUseError(Exception):
    def __init__(self, current, requires):
        super().__init__( "Cannot proceed with the «{}» stage because the following stage «{}» is relying on that data. Perhaps you meant to drop that stage first?".format(current,requires))