def setup():
    from typing import Optional
    
    import re
    
    from os import path
    
    import stringcoercion
    from groot import constants
    from groot.data import global_view, LegoComponent, INamedGraph, UserGraph, LegoSubsequence, LegoSequence
    from mgraph import MGraph, importing
    from mhelper import string_helper, file_helper
    from stringcoercion import CoercionError
    
    
    class MGraphCoercer( stringcoercion.Coercer ):
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
        
        
        def can_handle( self, info: stringcoercion.CoercionInfo ):
            return self.PRIORITY.HIGH if (info.annotation.is_directly_below( INamedGraph ) or info.annotation.is_directly_below( MGraph )) else False
        
        
        def coerce( self, info: stringcoercion.CoercionInfo ) -> Optional[object]:
            txt = info.source
            prefixes = "newick", "compact", "csv", "tsv", "file", "file-newick", "file-compact", "file-csv", "file-tsv"
            prefix = None
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
            
            name_graph = info.annotation.is_directly_below( INamedGraph )
            
            if is_file is True or (is_file is None and path.isfile( txt )):
                if prefix is None:
                    ext = file_helper.get_extension( txt )
                    if ext in (".nwk", ".new", ".newick"):
                        prefix = "newick"
                    elif ext == ".tsv":
                        prefix = "tsv"
                    elif ext == ".edg":
                        prefix = "compact"
                    elif ext == ".csv":
                        prefix = "csv"
                
                txt = file_helper.read_all_text( txt )
            
            model = global_view.current_model()
            
            for named_graph in model.iter_graphs():
                if named_graph.name == txt:
                    return named_graph if name_graph else named_graph.graph
            
            if prefix == "compact" or (prefix is None and "|" in txt):
                r = importing.import_compact( txt )
            elif prefix in ("csv", "tsv") or (prefix is None and "\n" in txt):
                if prefix == "tsv" or (prefix is None and "\t" in txt):
                    r = importing.import_edgelist( txt, delimiter = "\t" )
                else:
                    assert prefix is None or prefix == "csv"
                    r = importing.import_edgelist( txt )
            else:
                assert prefix is None or prefix == "newick"
                r = importing.import_newick( txt )
            
            return UserGraph( r ) if name_graph else r
    
    
    class MSequenceCoercer( stringcoercion.Coercer ):
        """
        **Sequences** are referenced by their _accession_ or _internal ID_.
        """
        
        
        def can_handle( self, info: stringcoercion.CoercionInfo ):
            return info.annotation.is_directly_below( LegoSequence )
        
        
        def coerce( self, info: stringcoercion.CoercionInfo ) -> Optional[object]:
            model = global_view.current_model()
            
            try:
                sequence = model.find_sequence_by_accession( info.source )
            except LookupError:
                try:
                    sequence = model.find_sequence_by_legacy_accession( info.source )
                except ValueError:
                    sequence = None
                except LookupError:
                    sequence = None
            
            if sequence is None:
                raise stringcoercion.CoercionError( "«{}» is neither a valid sequence accession nor internal ID.".format( info.source ) )
            
            return sequence
    
    
    class MSubsequenceCoercer( stringcoercion.Coercer ):
        """
        **Domains** are referenced _in the form_: `X[Y:Z]` where `X` is the sequence, and `Y` and `Z` are the range of the domain (inclusive and 1 based).
        """
        
        RX1 = re.compile( r"^(.+)\[([0-9]+):([0-9]+)\]$" )
        
        
        def can_handle( self, info: stringcoercion.CoercionInfo ):
            return info.annotation.is_directly_below( LegoSubsequence )
        
        
        def coerce( self, info: stringcoercion.CoercionInfo ) -> Optional[object]:
            m = self.RX1.match( info.source )
            
            if m is None:
                raise stringcoercion.CoercionError( "«{}» is not a valid subsequence of the form `X[Y:Z]`.".format( info.source ) )
            
            str_sequence, str_start, str_end = m.groups()
            
            try:
                sequence = info.collection.coerce( LegoSequence, str_sequence )
            except CoercionError as ex:
                raise stringcoercion.CoercionError( "«{}» is not a valid subsequence of the form `X[Y:Z]` because X («{}») is not a sequence.".format( info.source, str_start ) ) from ex
            
            try:
                start = int( str_start )
            except ValueError as ex:
                raise stringcoercion.CoercionError( "«{}» is not a valid subsequence of the form `X[Y:Z]` because Y («{}») is not a integer.".format( info.source, str_start ) ) from ex
            
            try:
                end = int( str_end )
            except ValueError as ex:
                raise stringcoercion.CoercionError( "«{}» is not a valid subsequence of the form `X[Y:Z]` because Z («{}») is not a integer.".format( info.source, str_start ) ) from ex
            
            return LegoSubsequence( sequence, start, end )
    
    
    class MComponentCoercer( stringcoercion.Coercer ):
        """
        **Components** are referenced by:
            * `xxx` where `xxx` is the _name_ of the component
            * `c:xxx` where `xxx` is the _index_ of the component
        """
        
        
        def can_handle( self, info: stringcoercion.CoercionInfo ):
            return info.annotation.is_directly_below( LegoComponent )
        
        
        def coerce( self, info: stringcoercion.CoercionInfo ) -> Optional[object]:
            model = global_view.current_model()
            
            if info.source.lower().startswith( constants.COMPONENT_PREFIX ):
                try:
                    return model.components[string_helper.to_int( info.source[2:] )]
                except:
                    pass
            
            try:
                model.components.find_component_by_name( info.source )
            except:
                pass
            
            raise stringcoercion.CoercionError( "«{}» is neither a valid component index nor name.".format( info.source ) )
    
    
    stringcoercion.register( MSequenceCoercer() )
    stringcoercion.register( MGraphCoercer() )
    stringcoercion.register( MComponentCoercer() )
    stringcoercion.register( MSubsequenceCoercer() )
