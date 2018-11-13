from mhelper import NotFoundError, ArgsKwargs, FunctionInspector, exception_helper
from typing import Union, Iterable, cast, Type

import re
import stringcoercion
import mgraph

from groot.data import global_view, Component, INamedGraph, UserGraph, Domain, Gene
from groot.utilities import AbstractAlgorithm, AlgorithmCollection


class AlgorithmCoercer( stringcoercion.AbstractCoercer ):
    """
    Algorithms are referenced by their names, with parameters specified using semicolons.
    
    e.g. `dbscan`
    e.g. `kmeans;3`
    """
    
    
    def on_get_archetype( self ) -> type:
        return AbstractAlgorithm
    
    
    def on_coerce( self, info: stringcoercion.CoercionInfo ) -> AbstractAlgorithm:
        type_ = cast( Type[AbstractAlgorithm], info.annotation.value )
        col: AlgorithmCollection = type_.get_owner()
        
        elements = info.source.split( ";" )
        
        algo_name = elements.pop( 0 )
        
        try:
            function = col.get_function( algo_name )
        except NotFoundError as ex:
            raise stringcoercion.CoercionError( str( ex ) ) from ex
        
        args = FunctionInspector( function ).args
        arg_values = { }
        
        for index in range( len( args ) ):
            if index < col.num_expected_args:
                pass
            else:
                arg = args.by_index( index )
                arg_values[arg.name] = info.collection.coerce( elements.pop( 0 ), arg.annotation.value )
        
        return type_( function = function, name = algo_name, argskwargs = ArgsKwargs( **arg_values ) )


class MGraphCoercer( stringcoercion.AbstractEnumCoercer ):
    """
    **Graphs and trees** can be referenced as the name of the object containing the graph, or as
    a format suitable for passing into `mgraph.importing.import_string` (newick, edge list, etc.)
    """
    
    
    def on_get_priority( self ):
        return self.PRIORITY.HIGH
    
    
    def on_get_archetype( self ) -> type:
        return Union[mgraph.MGraph, INamedGraph]
    
    
    def on_get_options( self, info: stringcoercion.CoercionInfo ) -> Iterable[object]:
        return global_view.current_model().iter_graphs()
    
    
    def on_get_option_names( self, value: object ):
        if isinstance( value, INamedGraph ):
            return value, value.get_accid()
        elif isinstance( value, str ):
            return value
        else:
            raise exception_helper.type_error( "value", value, (INamedGraph, str) )
    
    
    def on_get_accepts_user_options( self ) -> bool:
        return True
    
    
    def on_convert_option( self, info: stringcoercion.CoercionInfo, option: object ) -> object:
        if not isinstance( option, INamedGraph ):
            raise ValueError( "Return should be `INamedGraph` but I've got a `{}`".format( repr( option ) ) )
        
        if info.annotation.is_direct_subclass_of( INamedGraph ):
            return option
        else:
            return option.graph
    
    
    def on_convert_user_option( self, info: stringcoercion.CoercionInfo ) -> object:
        g = mgraph.importing.import_string( info.source )
        return self.on_convert_option( info, UserGraph( g ) )


class GeneCoercer( stringcoercion.AbstractEnumCoercer ):
    """
    **Sequences** are referenced by their _accession_ or _internal ID_.
    """
    
    
    def on_get_archetype( self ) -> type:
        return Gene
    
    
    def on_get_options( self, info: stringcoercion.CoercionInfo ) -> Iterable[object]:
        return global_view.current_model().genes
    
    
    def on_get_option_names( self, value: Gene ) -> Iterable[str]:
        return value.display_name, value.accession, value.legacy_accession, value.index


class DomainCoercer( stringcoercion.AbstractEnumCoercer ):
    """
    **Domains** are referenced _in the form_: `X[Y:Z]` where `X` is the sequence, and `Y` and `Z` are the range of the domain (inclusive and 1 based).
    """
    
    RX1 = re.compile( r"^(.+)\[([0-9]+):([0-9]+)\]$" )
    
    
    def on_get_options( self, info: stringcoercion.CoercionInfo ) -> Iterable[object]:
        return global_view.current_model().user_domains
    
    
    def on_get_archetype( self ) -> type:
        return Domain
    
    
    def on_convert_user_option( self, info: stringcoercion.CoercionInfo ) -> object:
        m = self.RX1.match( info.source )
        
        if m is None:
            raise stringcoercion.CoercionError( "«{}» is not a valid subsequence of the form `X[Y:Z]`.".format( info.source ) )
        
        str_sequence, str_start, str_end = m.groups()
        
        try:
            sequence = info.collection.coerce( Gene, str_sequence )
        except stringcoercion.CoercionError as ex:
            raise stringcoercion.CoercionError( "«{}» is not a valid subsequence of the form `X[Y:Z]` because X («{}») is not a sequence.".format( info.source, str_start ) ) from ex
        
        try:
            start = int( str_start )
        except ValueError as ex:
            raise stringcoercion.CoercionError( "«{}» is not a valid subsequence of the form `X[Y:Z]` because Y («{}») is not a integer.".format( info.source, str_start ) ) from ex
        
        try:
            end = int( str_end )
        except ValueError as ex:
            raise stringcoercion.CoercionError( "«{}» is not a valid subsequence of the form `X[Y:Z]` because Z («{}») is not a integer.".format( info.source, str_start ) ) from ex
        
        return Domain( sequence, start, end )


class ComponentCoercer( stringcoercion.AbstractEnumCoercer ):
    """
    **Components** are referenced by:
        * `xxx` where `xxx` is the _name_ of the component
        * `c:xxx` where `xxx` is the _index_ of the component
    """
    
    
    def on_get_options( self, info: stringcoercion.CoercionInfo ) -> Iterable[object]:
        return global_view.current_model().components
    
    
    def on_get_archetype( self ) -> type:
        return Component
    
    
    def on_get_option_names( self, value: Component ) -> Iterable[object]:
        return value, value.index


def setup( collection: stringcoercion.CoercerCollection ):
    collection.register( GeneCoercer() )
    collection.register( MGraphCoercer() )
    collection.register( ComponentCoercer() )
    collection.register( DomainCoercer() )
    collection.register( AlgorithmCoercer() )
