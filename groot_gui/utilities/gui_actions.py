from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QAction, QFileDialog, QMenu, QToolTip, QMessageBox
from typing import Optional, Any

import intermake
import groot
import intermake_qt

from mhelper import SwitchError, ArgsKwargs
from mhelper_qt import qt_gui_helper, menu_helper
from groot_gui.utilities.selection import LegoSelection
from groot_gui.utilities.gui_workflow import EIntent, Stage, LegoVisualiser
from groot_gui.utilities import gui_workflow


class GuiActions:
    def __init__( self, frm_main, window ):
        from groot_gui.forms.frm_main import FrmMain
        from groot_gui.forms.frm_base import FrmBase
        assert isinstance( frm_main, FrmMain )
        self.frm_main: FrmMain = frm_main
        self.window: FrmBase = window
    
    
    def launch_intent( self, stage: Stage, intent: EIntent ):
        """
        Given a `stage` and `intent` this finds the corresponding `LegoVisualiser` and `launch`es its action.
        """
        visualisers = list( LegoVisualiser.iter_from_stage( stage, intent ) )
        
        if len( visualisers ) == 0:
            QMessageBox.info( self.window, "Intent", "No handlers for this intent: {}+{}".format( stage, intent ) )
        elif len( visualisers ) == 1:
            self.launch( visualisers[0] )
        else:
            menu = QMenu()
            map = { }
            
            for visualiser in visualisers:
                action = QAction()
                action.setText( visualiser.name )
                action.setIcon( visualiser.icon.icon() if visualiser.icon else None )
                map[action] = visualiser
                menu.addAction( action )
            
            selected = menu_helper.show_menu( self.window, menu )
            
            if selected is not None:
                self.launch( map[selected] )
    
    
    def launch( self, visualiser: LegoVisualiser, *args ):
        """
        Exacts the action denoted by a particular `LegoVisualiser`.
        """
        from groot_gui.forms.frm_base import FrmBase
        
        if isinstance( visualiser.action, type ) and issubclass( visualiser.action, FrmBase ):
            self.frm_main.show_form( visualiser.action, *args )
        elif isinstance( visualiser.action, intermake.AbstractCommand ) or intermake.BasicCommand.retrieve( visualiser.action, None ) is not None:
            self.request( visualiser.action, *args )
        else:
            visualiser.action( self )
    
    
    def menu( self, stage: Stage ):
        """
        Shows the menu associated with a particular `stage`.
        """
        menu_handler = self.frm_main.menu_handler
        menu = menu_handler.stages[stage]
        menu_handler.update_dynamic_menu( menu )
        menu_helper.show_menu( self.window, menu )
    
    
    def close_window( self ):
        """
        Closes the calling window.
        
        As well as providing a means to close the form via an action string,
        this should be called instead of `QDialog.close` since QDialog.close doesn't work
        properly if the form is hosted as an MDI window.
        """
        self.frm_main.close_form( type( self.window ) )
    
    
    def wizard_next( self ):
        self.run( groot.continue_wizard )
    
    
    def close_application( self ):
        self.frm_main.close()
    
    
    def run( self, command: intermake.AbstractCommand, *args, **kwargs ) -> intermake.AsyncResult:
        """
        Runs an Intermake command asynchronously.
        """
        return intermake.acquire( command, window = self.window ).run( *args, **kwargs )
    
    
    def get_model( self ) -> groot.Model:
        return groot.current_model()
    
    
    def save_model( self ) -> None:
        if self.get_model().file_name:
            self.run( groot.file_save, self.get_model().file_name )
        else:
            self.launch( gui_workflow.get_visualisers().VIEW_SAVE_FILE )
    
    
    def save_model_to( self, file_name: str ) -> None:
        self.run( groot.file_save, file_name )
    
    
    def request( self, plugin: intermake.AbstractCommand, *args, **kwargs ) -> Optional[intermake.AsyncResult]:
        """
        Runs an Intermake command after showing the user the arguments request form.
        """
        if args is None:
            args = ()
        
        return intermake_qt.FrmArguments.request( self.window, plugin, defaults = ArgsKwargs( *args, **kwargs ) )  # --> self.plugin_completed
    
    
    def show_status_message( self, text: str ) -> None:
        QToolTip.showText( QCursor.pos(), text )
    
    
    def get_visualiser( self, name ) -> LegoVisualiser:
        return getattr( gui_workflow.get_visualisers(), name.upper() )
    
    
    def get_stage( self, name ) -> Stage:
        return getattr( gui_workflow.STAGES, name.upper() ) if name else None
    
    
    def by_url( self, link: str, validate = False ) -> bool:
        if ":" in link:
            key, value = link.split( ":", 1 )
        else:
            key = link
            value = None
        
        if key == "action":
            try:
                visualiser = gui_workflow.get_visualisers().find_by_key( value )
            except KeyError:
                if validate:
                    return False
                else:
                    raise
            
            if validate:
                return True
            
            self.launch( visualiser )
        elif key == "file_save":
            if validate:
                return True
            
            self.run( groot.file_save, value )
        elif key == "file_load":
            if validate:
                return True
            
            self.run( groot.file_load, value )
        elif key == "file_sample":
            if validate:
                return True
            
            self.run( groot.file_sample, value )
        else:
            if validate:
                return False
            else:
                raise SwitchError( "link", link )
    
    
    def show_intermake( self ) -> None:
        from intermake_qt import FrmTreeView
        FrmTreeView.request( self.window, root = intermake.VisualisablePath.get_root(), flat = True )
    
    
    def __get_selection_form( self ) -> Any:
        from groot_gui.forms.frm_base import FrmSelectingToolbar
        form: FrmSelectingToolbar = self.window
        assert isinstance( form, FrmSelectingToolbar )
        return form
    
    
    def get_selection( self ) -> LegoSelection:
        return self.__get_selection_form().get_selection()
    
    
    def show_selection( self ):
        return self.__get_selection_form().show_selection_menu()
    
    
    def set_selection( self, value: LegoSelection ):
        return self.__get_selection_form().set_selection( value )
    
    
    def clear_selection( self ):
        self.set_selection( LegoSelection() )
    
    
    def browse_open( self ):
        file_name = qt_gui_helper.browse_open( self.window, groot.constants.DIALOGUE_FILTER )
        
        if file_name:
            self.run( groot.file_load, file_name )
    
    
    def enable_inbuilt_browser( self ):
        from groot_gui.forms.frm_webtree import FrmWebtree
        form = self.frm_main.mdi.get( FrmWebtree.__name__ )
        
        if form is None:
            return
        
        form.enable_inbuilt_browser()
    
    
    def adjust_window_size( self ):
        self.frm_main.adjust_window_size( self.window )
    
    
    def show_help( self ):
        import webbrowser
        webbrowser.open( "https://bitbucket.org/mjr129/groot" )
    
    
    def exit( self ):
        from groot_gui.forms.frm_main import FrmMain
        FrmMain.INSTANCE.close()
    
    
    def dismiss_startup_screen( self ):
        from groot_gui.forms.frm_main import FrmMain
        from groot_gui.forms.frm_startup import FrmStartup
        FrmMain.INSTANCE.close_form( FrmStartup )
    
    
    def load_sample_from( self, param ):
        self.run( groot.file_sample, param )
    
    
    def load_file_from( self, param ):
        self.run( groot.file_load, param )
    
    
    def stop_wizard( self ):
        self.run( groot.drop_wizard )
    
    
    def import_file( self ):
        filters = "Valid files (*.fasta *.fa *.faa *.blast *.tsv *.composites *.txt *.comp)", "FASTA files (*.fasta *.fa *.faa)", "BLAST output (*.blast *.tsv)"
        
        file_name, filter = QFileDialog.getOpenFileName( self.window, "Select file", None, ";;".join( filters ), options = QFileDialog.DontUseNativeDialog )
        
        if not file_name:
            return
        
        filter_index = filters.index( filter )
        
        if filter_index == 0:
            self.run( groot.import_file, file_name )
        elif filter_index == 0:
            self.run( groot.import_genes, file_name )
        elif filter_index == 1:
            self.run( groot.import_similarity, file_name )
        else:
            raise SwitchError( "filter_index", filter_index )
    
    
    def browse_save( self ):
        file_name = qt_gui_helper.browse_save( self.window, groot.constants.DIALOGUE_FILTER )
        
        if file_name:
            self.run( groot.file_save, file_name )
