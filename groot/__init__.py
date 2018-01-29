"""
Groot entry point.
"""

# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ META DATA          ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
__author__ = "Martin Rusilowicz"
__version__ = "0.0.0.32"


# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ ENVIRONMENT SETUP  ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
def __setup():
    from intermake import MENV, create_simple_host_provider_from_class, ConsoleHost, VISUALISABLE_COERCION
    import stringcoercion
    from typing import Optional
    from mgraph import MGraph
    from groot.data import global_view
    from groot.data.lego_model import LegoComponent
    
    # ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    # ░░░░░░░░░░░░░░░░░░░░░░░░░░ String coercion    ░░░░░░░░░░░░░░░░░░░░░░░░░░
    # ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    
    class MGraphCoercer( stringcoercion.Coercer ):
        def can_handle( self, info: stringcoercion.CoercionInfo ):
            return self.PRIORITY.HIGH if info.annotation.is_directly_below( MGraph ) else None
        
        
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
    
    
    stringcoercion.register( MGraphCoercer() )
    VISUALISABLE_COERCION.register_as_visualisable( MGraph )
    
    
    # ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    # ░░░░░░░░░░░░░░░░░░░░░░░░░░ Intermake GUI host ░░░░░░░░░░░░░░░░░░░░░░░░░░
    # ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    
    
    def __gui_host():
        from groot.frontends.gui.gui_host import LegoGuiHost
        return LegoGuiHost()
    
    
    MENV.host_provider = create_simple_host_provider_from_class( ConsoleHost, __gui_host )
    
    # ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    # ░░░░░░░░░░░░░░░░░░░░░░░░░░ Intermake setup    ░░░░░░░░░░░░░░░░░░░░░░░░░░
    # ░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░░
    
    MENV.name = "GROOT"
    MENV.abv_name = "groot"
    MENV.version = __version__


__setup()

# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒ MAIN EXPORTS       ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
# ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒
from groot.extensions import ext_viewing, ext_files, ext_generating, ext_gimmicks, ext_modifications, ext_dropping, ext_gui
from intermake import run_jupyter


run_jupyter = run_jupyter
