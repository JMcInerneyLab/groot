"""
Dealing with extendable algorithms
"""
from typing import TypeVar, Generic


T = TypeVar( "T" )


class AlgorithmCollection( Generic[T] ):
    """
    Holds a collection of algorithms.
    
    :generic T: Type of argument (delegate)
    :data ALL:  All algorithm collections
    """
    ALL = []
    
    
    def __init__( self, name: str ):
        self.name = name
        self.default = None
        self.algorithms = { }
        self.ALL.append( self )
    
    
    def register( self, name: str = "", default: bool = False ):
        """
        Used to register an algorithm
        
        :param default: Sets the function as the default. An algorithm will also be the default if there is no alternative. 
        :param name:    Name. If missing the function's `__name__` is used. 
        :return:        A decorator that registers the algorithm with the specified name. 
        """
        assert isinstance( name, str )
        
        name = name.lower().replace( " ", "_" ).replace( ".", "_" )
        
        
        def decorator( fn: T ) -> T:
            fn_name: str = name or fn.__name__
            
            if default or self.default is None:
                self.default = fn_name
            
            self.algorithms[fn_name] = fn
            
            return fn
        
        
        return decorator
    
    
    @property
    def keys( self ):
        return self.algorithms.keys()
    
    
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
