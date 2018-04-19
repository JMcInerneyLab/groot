def setup():
    import editorium
    editorium.register( __mk )


def __mk():
    from editorium.editorium_qt import EditorInfo, Editor_TextBrowsableBase
    from groot.data import INamedGraph, global_view
    from typing import Optional
    from groot_gui.utilities import gui_view_utils
    from groot_gui.utilities.gui_view_utils import ESelect
    
    class Editor_Graph( Editor_TextBrowsableBase ):
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
            return info.inspector.is_directly_below( INamedGraph )
        
        
        def on_browse( self, value: Optional[object] ) -> Optional[str]:
            r = gui_view_utils.show_selection_menu( self.edit_btn, None, ESelect.HAS_GRAPH )
            
            if r is not None:
                assert isinstance( r.single, INamedGraph )
                return r.single.name
            
    return Editor_Graph
