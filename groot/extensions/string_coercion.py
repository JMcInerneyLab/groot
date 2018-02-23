# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ░░░░░░░░░░░░░░░░░░░░░░░░░░ String coercion    ░░░░░░░░░░░░░░░░░░░░░░░░░░
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
from typing import Optional

import re
import stringcoercion
from groot.data import global_view
from groot.data.lego_model import LegoComponent, LegoSequence, LegoSubsequence
from mgraph import MGraph
from mhelper import string_helper
from stringcoercion import CoercionError


def setup():
    class MGraphCoercer( stringcoercion.Coercer ):
        """
        **Graphs and trees** are referenced by the _index_ of their component, or the _text_ "nrfg", for the NRFG.
        """
        
        
        def can_handle( self, info: stringcoercion.CoercionInfo ):
            return self.PRIORITY.HIGH if info.annotation.is_directly_below( MGraph ) else False
        
        
        def coerce( self, info: stringcoercion.CoercionInfo ) -> Optional[object]:
            txt = info.source.lower()
            model = global_view.current_model()
            
            if txt == "nrfg":
                if model.nrfg is None:
                    raise stringcoercion.CoercionError( "The model does not have an NRFG." )
                
                return model.nrfg.graph
            
            try:
                component = info.collection.coerce( LegoComponent, info.source )
                return component.tree
            except CoercionError as ex:
                raise stringcoercion.CoercionError( "«{}» is not a valid graph name.".format( info.source ) ) from ex
    
    
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
                    id = int( info.source )
                    sequence = model.find_sequence_by_id( id )
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
        **Components** are referenced by their _index_ or _name_.
        """
        
        
        def can_handle( self, info: stringcoercion.CoercionInfo ):
            return info.annotation.is_directly_below( LegoComponent )
        
        
        def coerce( self, info: stringcoercion.CoercionInfo ) -> Optional[object]:
            model = global_view.current_model()
            
            try:
                return model.components[string_helper.to_int( info.source )]
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
