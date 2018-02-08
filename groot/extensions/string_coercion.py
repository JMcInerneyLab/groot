# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
# ░░░░░░░░░░░░░░░░░░░░░░░░░░ String coercion    ░░░░░░░░░░░░░░░░░░░░░░░░░░
# ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
from typing import Optional

import stringcoercion
from groot.data import global_view
from groot.data.lego_model import LegoComponent, LegoSequence
from intermake.helpers.coercion_extensions import VISUALISABLE_COERCION
from mgraph import MGraph

def setup():
    class MGraphCoercer( stringcoercion.Coercer ):
        def can_handle( self, info: stringcoercion.CoercionInfo ):
            return info.annotation.is_directly_below( MGraph )
        
        
        def coerce( self, info: stringcoercion.CoercionInfo ) -> Optional[object]:
            txt = info.source.lower()
            model = global_view.current_model()
            
            if txt == "nrfg":
                return model.nrfg
            
            for i, component in enumerate( model.components ):
                assert isinstance( component, LegoComponent )
                if txt == str( i + 1 ) or txt == str( component ):
                    return component.tree
            
            raise stringcoercion.CoercionError( "«{}» is not a valid graph name.".format( info.source ) )
    
    
    class MSequenceCoercer( stringcoercion.Coercer ):
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
                raise stringcoercion.CoercionError( "«{}» is not a valid sequence accession or ID.".format( info.source ) )
            
            return sequence
    
    
    stringcoercion.register( MSequenceCoercer() )
    stringcoercion.register( MGraphCoercer() )
    VISUALISABLE_COERCION.register_as_visualisable( MGraph )