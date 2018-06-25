from mhelper import ignore


def setup():
    import editorium
    editorium.register( __mk )


def __mk():
    from editorium import EditorInfo, AbstractBrowserEditor
    from groot.data import INamedGraph, global_view
    from typing import Optional
    from groot_gui.utilities.selection import show_selection_menu
    
    class Editor_Graph( AbstractBrowserEditor):
        def on_convert_from_text( self, text: str ) -> object:
            model = global_view.current_model()
            
            for graph in model.iter_graphs():
                if graph.name == text:
                    return graph
            
            return None
        
        
        def on_convert_to_text( self, value: object ) -> str:
            assert isinstance( value, INamedGraph )
            return value.name
        
        
        @classmethod
        def can_handle( cls, info: EditorInfo ) -> bool:
            return info.annotation.is_direct_subclass_of( INamedGraph )
        
        
        def on_browse( self, value: Optional[object] ) -> Optional[str]:
            ignore( value )
            r = show_selection_menu( self.edit_btn, None, INamedGraph )
            
            if r is not None:
                assert isinstance( r.single, INamedGraph )
                return r.single.name
    
    
    return Editor_Graph
