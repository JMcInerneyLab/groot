from mhelper import NotFoundError, ArgsKwargs
from typing import Union


def setup():
    """
    Sets up the `stringcoercion` library for use with Groot.
    `stringcoercion` is used by `intermake` to convert text (e.g. `"123"`) entered in the CLI into Python values (e.g. `123`).
    """
    from typing import Iterable, cast, Type
    import re
    from os import path
    import stringcoercion as sc
    import mgraph
    import mhelper
    
    from groot.data import global_view, Component, INamedGraph, UserGraph, Domain, Gene
    from groot.utilities import AbstractAlgorithm, AlgorithmCollection
    
    
    class AlgorithmCoercer( sc.AbstractCoercer ):
        """
        Algorithms referenced by their names, with parameters specified using semicolons.
        
        e.g. `dbscan`
        e.g. `kmeans;3`
        """
        
        
        def on_get_archetype( self ) -> type:
            return AbstractAlgorithm
        
        
        def on_coerce( self, info: sc.CoercionInfo ) -> AbstractAlgorithm:
            type_ = cast( Type[AbstractAlgorithm], info.annotation.value )
            col: AlgorithmCollection = type_.get_owner()
            
            elements = info.source.split( ";" )
            
            algo_name = elements.pop( 0 )
            
            try:
                function = col.get_function( algo_name )
            except NotFoundError as ex:
                raise sc.CoercionError( str( ex ) ) from ex
            
            args = mhelper.FunctionInspector( function ).args
            arg_values = { }
            
            for index in range( len( args ) ):
                if index < col.num_expected_args:
                    pass
                else:
                    arg = args.by_index( index )
                    arg_values[arg.name] = info.collection.coerce( elements.pop( 0 ), arg.annotation.value )
            
            return type_( function = function, name = algo_name, argskwargs = ArgsKwargs( **arg_values ) )
    
    
    class MGraphCoercer( sc.AbstractEnumCoercer ):
        """
        **Graphs and trees** are referenced by one of the following:
        
            * Graph in model  : The name of a graph in the current model (you can get a list of graph names via `cd /graphs ; ls`)
            * Graph on disk   : The name of a file 
            * Compact edgelist: File extension is `.edg` OR argument is prefixed `compact:` or `file-compact:` OR argument/file contains `pipe`
            * TSV             : ''                `.tsv` OR ''                   `tsv:`     or `file-tsv:`     OR ''                     `newline` and `tab`
            * CSV             : ''                `.csv` OR ''                   `csv:`     or `file-csv:`     OR ''                     `newline` and not `tab` 
            * Newick          : ''                `.nwk` OR ''                   `newick:`  or `file-newick:`  OR ''                     none of the above
            
        * You can be explicit by prefixing your string with `newick:` `compact:` `csv:` `tsv:` `file:` `file-newick:` `file-compact:` `file-csv:` `file-tsv:`
        """
        
        
        def on_get_priority( self ):
            return self.PRIORITY.HIGH
        
        
        def on_get_archetype( self ) -> type:
            return Union[mgraph.MGraph, INamedGraph]
        
        
        def on_get_options( self, info: sc.CoercionInfo ) -> Iterable[object]:
            return global_view.current_model().iter_graphs()
        
        
        def on_get_option_name( self, value ):
            if isinstance( value, INamedGraph ):
                return value.name
            elif isinstance( value, str ):
                return value
            else:
                raise mhelper.exception_helper.type_error( "value", value, (INamedGraph, str) )
        
        
        def on_get_accepts_user_options( self ) -> bool:
            return True
        
        
        def on_convert_option( self, info: sc.CoercionInfo, option: object ) -> object:
            if not isinstance( option, INamedGraph ):
                raise ValueError( "Return should be `INamedGraph` but I've got a `{}`".format( repr( option ) ) )
            
            if info.annotation.is_direct_subclass_of( INamedGraph ):
                return option
            else:
                return option.graph
        
        
        def on_convert_user_option( self, info: sc.CoercionInfo ) -> object:
            txt = info.source
            prefixes = "newick", "compact", "csv", "tsv", "file", "file-newick", "file-compact", "file-csv", "file-tsv"
            prefix, filename = txt.split( ":", 1 )
            is_file = None
            
            for prefix_ in prefixes:
                if txt.startswith( prefix_ + ":" ):
                    prefix = prefix_
                    txt = txt[len( prefix_ ) + 1:]
                    
                    if prefix == "file":
                        is_file = True
                        prefix = None
                    elif prefix.startswith( "file-" ):
                        is_file = True
                        prefix = prefix[5:]
                    
                    break
            
            if is_file is True or (is_file is None and path.isfile( txt )):
                if prefix is None:
                    ext = mhelper.file_helper.get_extension( txt )
                    if ext in (".nwk", ".new", ".newick"):
                        prefix = "newick"
                    elif ext == ".tsv":
                        prefix = "tsv"
                    elif ext == ".edg":
                        prefix = "compact"
                    elif ext == ".csv":
                        prefix = "csv"
                
                txt = mhelper.file_helper.read_all_text( txt )
            
            if prefix == "compact" or (prefix is None and "|" in txt):
                r = mgraph.importing.import_compact( txt )
            elif prefix in ("csv", "tsv") or (prefix is None and "\n" in txt):
                if prefix == "tsv" or (prefix is None and "\t" in txt):
                    r = mgraph.importing.import_edgelist( txt, delimiter = "\t" )
                else:
                    assert prefix is None or prefix == "csv"
                    r = mgraph.importing.import_edgelist( txt )
            else:
                assert prefix is None or prefix == "newick"
                r = mgraph.importing.import_newick( txt )
            
            return self.on_convert_option( info, UserGraph( r ) )
    
    
    class GeneCoercer( sc.AbstractEnumCoercer ):
        """
        **Sequences** are referenced by their _accession_ or _internal ID_.
        """
        
        
        def on_get_archetype( self ) -> type:
            return Gene
        
        
        def on_get_options( self, info: sc.CoercionInfo ) -> Iterable[object]:
            return global_view.current_model().genes
        
        
        def on_get_option_names( self, value: Gene ) -> Iterable[str]:
            return value.name, value.display_name, value.index
    
    
    class DomainCoercer( sc.AbstractEnumCoercer ):
        """
        **Domains** are referenced _in the form_: `X[Y:Z]` where `X` is the sequence, and `Y` and `Z` are the range of the domain (inclusive and 1 based).
        """
        
        RX1 = re.compile( r"^(.+)\[([0-9]+):([0-9]+)\]$" )
        
        
        def on_get_options( self, info: sc.CoercionInfo ) -> Iterable[object]:
            return global_view.current_model().user_domains
        
        
        def on_get_archetype( self ) -> type:
            return Domain
        
        
        def on_convert_user_option( self, info: sc.CoercionInfo ) -> object:
            m = self.RX1.match( info.source )
            
            if m is None:
                raise sc.CoercionError( "«{}» is not a valid subsequence of the form `X[Y:Z]`.".format( info.source ) )
            
            str_sequence, str_start, str_end = m.groups()
            
            try:
                sequence = info.collection.coerce( Gene, str_sequence )
            except sc.CoercionError as ex:
                raise sc.CoercionError( "«{}» is not a valid subsequence of the form `X[Y:Z]` because X («{}») is not a sequence.".format( info.source, str_start ) ) from ex
            
            try:
                start = int( str_start )
            except ValueError as ex:
                raise sc.CoercionError( "«{}» is not a valid subsequence of the form `X[Y:Z]` because Y («{}») is not a integer.".format( info.source, str_start ) ) from ex
            
            try:
                end = int( str_end )
            except ValueError as ex:
                raise sc.CoercionError( "«{}» is not a valid subsequence of the form `X[Y:Z]` because Z («{}») is not a integer.".format( info.source, str_start ) ) from ex
            
            return Domain( sequence, start, end )
    
    
    class ComponentCoercer( sc.AbstractEnumCoercer ):
        """
        **Components** are referenced by:
            * `xxx` where `xxx` is the _name_ of the component
            * `c:xxx` where `xxx` is the _index_ of the component
        """
        
        
        def on_get_options( self, info: sc.CoercionInfo ) -> Iterable[object]:
            return global_view.current_model().components
        
        
        def on_get_archetype( self ) -> type:
            return Component
        
        
        def on_get_option_names( self, value: Component ) -> Iterable[str]:
            return value, value.name, value.index
    
    
    sc.register( GeneCoercer() )
    sc.register( MGraphCoercer() )
    sc.register( ComponentCoercer() )
    sc.register( DomainCoercer() )
    sc.register( AlgorithmCoercer() )
