from groot.extensions import ext_viewing, ext_files, ext_generating, ext_gimmicks, ext_modifications, ext_dropping


__author__ = "Martin Rusilowicz"
__version__ = "0.0.0.18"


def __setup():
    from intermake import MENV, create_simple_host_provider_from_class, ConsoleHost
    
    
    def __gui_host():
        from groot.frontends.gui.gui_host import LegoGuiHost
        return LegoGuiHost()
    
    
    MENV.name = "GROOT"
    MENV.abv_name = "groot"
    MENV.version = __version__
    MENV.host_provider = create_simple_host_provider_from_class( ConsoleHost, __gui_host )


__setup()
