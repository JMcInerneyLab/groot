"""
Dealing with extendable algorithms
"""
from typing import TypeVar, Generic


T = TypeVar( "T" )


class AlgorithmCollection( Generic[T] ):
    ALL = []
    
    
    def __init__( self, name: str ):
        self.name = name
        self.default = None
        self.algorithms = { }
        self.ALL.append( self )
    
    
    def register( self, name: str = "" ):
        """
        Used to register an algorithm
        
        :param name:    Name. If missing the function's `__name__` is used. 
        :return:        A decorator that registers the algorithm with the specified name. 
        """
        assert isinstance(name, str)
        
        def decorator( fn: T ) -> T:
            fn_name: str = name or fn.__name__
            
            if self.default is None:
                self.default = fn_name
            
            self.algorithms[fn_name] = fn
            
            return fn
        
        return decorator
    
    
    def __getitem__( self, item ):
        if not item:
            item = self.default
        
        if not item in self.algorithms:
            raise ValueError( "There is no such {} algorithm as «{}».".format( self.name, item ) )
        
        return self.algorithms[item]
    
    
    def __iter__( self ):
        return iter( self.algorithms.items() )
    
    
    def __repr__( self ):
        return 'AlgorithmCollection(name = "{}", count = {})'.format( self.name, len( self.algorithms ) )
