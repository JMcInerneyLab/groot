"""
Dealing with extendable algorithms
"""
import inspect
from typing import Callable, Type, TypeVar

import mhelper
from mhelper import ArgsKwargs, NotFoundError


TDelegate = TypeVar( "TDelegate" )


class AbstractAlgorithm:
    """
    The concrete varieties of this class serve as function annotations denoting which type of algorithm a command accepts.
    Other than that, such annotations may be considered synonymous with `Callable`.
    These concrete versions are defined in `AlgorithmCollection.__init__`.
    
    Instances of this class simply wrap a function.
    """
    
    
    @classmethod
    def get_owner( cls ):
        raise NotImplementedError( "abstract" )
    
    
    def __init__( self,
                  function: Callable,
                  argskwargs: ArgsKwargs = ArgsKwargs.EMPTY,
                  name: str = None,
                  ):
        """
        :param function:        Function to call. 
        :param argskwargs:      Any __additional__ parameters this function takes should be specified here.  
        """
        assert inspect.isfunction( function ), repr( function )
        self.function = function
        self.argskwargs = argskwargs
        self.name = name
    
    
    def __call__( self, *args, **kwargs ) -> object:
        """
        Calls the algorithm.
        """
        try:
            return self.function( *args, *self.argskwargs.args, **kwargs, **self.argskwargs.kwargs )
        except Exception as ex:
            raise ValueError( "The algorithm «{}» failed to execute correctly, see causing exception for details.".format( repr( self ) ) ) from ex
    
    
    def __str__( self ):
        name = self.name or self.function
        args = "({})".format( self.argskwargs ) if self.argskwargs else ""
        return "{}{}".format( name, args )
    
    
    def __repr__( self ):
        return "{}(function = {}, argskwargs = {})".format( type( self ).__name__, repr( self.function ), repr( self.argskwargs ) )


class AlgorithmCollection:
    """
    Holds a collection of algorithms suited for a particular task.
    
    This class isn't strictly necessary, but it lets the UI quickly know the set of functions are suited to a
    particular task.
    
    Functions taking an algorithm as an argument should annotate that argument using `x.Algorithm`, where `x` is
    the `AlgorithmCollection` describing the purpose of the algorithm.
    
    :cvar ALL:          Holds a reference to all created algorithm collections
    
    :ivar delegate:     A `Callable` describing the prototype function accepted by this `AlgorithmCollection`.
                        Functions may also take user-provided arguments in addition to the arguments specified
                        by this delegate.
                        
                        Note that the UI cannot understand arguments that are kw-only or positional-only,
                        so such arguments should be avoided.
                         
    :ivar name:         Name of the algorithm collection
    :ivar default:      The of the default algorithm to fall back to using if no name is provided.
    :ivar algorithms:   Maps the algorithm names to their functions
    """
    ALL = []
    
    
    def __init__( self, delegate: Type[TDelegate], name: str ):
        AlgorithmCollection.ALL.append( self )
        
        
        class _AlgorithmType( AbstractAlgorithm ):
            @classmethod
            def get_owner( cls ):
                return self
        
        
        self.Algorithm = _AlgorithmType
        self.delegate = delegate
        self.name = name
        self.default = None
        self.algorithms = { }
    
    
    @property
    def num_expected_args( self ):
        """
        Gets the number of arguments functions in this collection are expected to take, based on the `delegate`. 
        Any additional arguments should be considered optional and their support is dependent on the caller. 
        """
        return len( self.delegate.__args__ ) - 1
    
    
    def register( self, name: str = "", default: bool = False ):
        """
        A decorator generator used to register an algorithm.
        The decorated function should conform to the `delegate`.
        Any _additional_ parameters may be specified by the user along with the algorithm name.
        
        :param default: Sets the function as the default.
                        An algorithm will also be the default if there is no alternative. 
        :param name:    Name. If missing the function's `__name__` is used. 
        :return:        A decorator that registers the algorithm with the specified name. 
        """
        assert isinstance( name, str )
        
        name = name.lower().replace( " ", "_" ).replace( ".", "_" )
        
        
        def decorator( fn: TDelegate ) -> TDelegate:
            fn_name: str = name or fn.__name__
            
            if default or self.default is None:
                self.default = fn_name
            
            self.algorithms[fn_name] = fn
            
            return fn
        
        
        return decorator
    
    
    def keys( self ):
        return self.algorithms.keys()
    
    
    def get_function( self, name: str ) -> TDelegate:
        """
        Gets the function associated with a particular name.
        
        :except NotFoundError:
        """
        if not name:
            name = self.default
        
        if not name in self.algorithms:
            raise NotFoundError( "There is no algorithm called «{}» in the collection of «{}» algorithms. Your options appear to be as follows: «{}»".format( name, self.name, list( self.algorithms.keys() ) ) )
        
        return self.algorithms[name]
    
    
    def get_algorithm( self, name, *args, **kwargs ) -> AbstractAlgorithm:
        """
        Gets the `AbstractAlgorithm` which combines a function with any function-specific parameters.
        """
        return self.Algorithm( self.get_function( name ), ArgsKwargs( *args, **kwargs ), name )
    
    
    def items( self ):
        return self.algorithms.items()
    
    
    def __iter__( self ):
        return iter( self.algorithms.items() )
    
    
    def __repr__( self ):
        return 'AlgorithmCollection(name = "{}", count = {})'.format( self.name, len( self.algorithms ) )
