import warnings
from typing import Any, Optional

import groot
import intermake
import intermake_qt
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QFileDialog, QToolTip
from groot_gui.utilities import gui_workflow
from groot_gui.utilities.gui_workflow import EIntent, IntentHandler, handlers
from mhelper import ArgsKwargs, SwitchError, get_basic_documentation
from mhelper_qt import FrmGenericText, menu_helper, qt_gui_helper


class GuiActions:
    def __init__( self, frm_main, window ):
        from groot_gui.forms.frm_main import FrmMain
        from groot_gui.forms.frm_base import FrmBase
        assert isinstance( frm_main, FrmMain )
        self.frm_main: FrmMain = frm_main
        self.window: FrmBase = window
    
    
    
    
    def launch( self, visualiser: IntentHandler ):
        """
        Exacts the action denoted by a particular `IntentHandler`.
        """
        warnings.warn("Deprecated - use `IntentHandler`.launch", DeprecationWarning)
        visualiser.execute( self.window, EIntent.DIRECT, None )
        
    
    
    def menu( self, stage: groot.Stage ):
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
            handlers().VIEW_SAVE_FILE.execute( self, EIntent.DIRECT, None )
    
    
    def save_model_to( self, file_name: str ) -> None:
        self.run( groot.file_save, file_name )
    
    
    def request( self, plugin: intermake.AbstractCommand, *args, **kwargs ) -> Optional[intermake.AsyncResult]:
        """
        Runs an Intermake command after showing the user the arguments request form.
        """
        warnings.warn("Deprecated, use `Intent`.", DeprecationWarning)
        if args is None:
            args = ()
        
        return intermake_qt.FrmArguments.request( self.window, plugin, defaults = ArgsKwargs( *args, **kwargs ) )  # --> self.plugin_completed
    
    
    def show_status_message( self, text: str ) -> None:
        QToolTip.showText( QCursor.pos(), text )
    
    
    def get_visualiser( self, name ) -> IntentHandler:
        return getattr( gui_workflow.handlers(), name.upper() )
    
    
    def get_stage( self, name ) -> groot.Stage:
        return getattr( groot.STAGES, name.upper() ) if name else None
    
    
    def by_url( self, link: str, validate = False ) -> bool:
        if ":" in link:
            key, value = link.split( ":", 1 )
        else:
            key = link
            value = None
        
        if key == "action":
            try:
                visualiser = gui_workflow.handlers().find_by_key( value )
            except KeyError:
                if validate:
                    return False
                else:
                    raise
            
            if validate:
                return True
            
            visualiser.execute( self.window, EIntent.DIRECT, None )
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
        from groot_gui.forms.frm_base import FrmBaseWithSelection
        form: FrmBaseWithSelection = self.window
        assert isinstance( form, FrmBaseWithSelection )
        return form
    
    
    def get_selection( self ) -> object:
        return self.__get_selection_form().get_selection()
    
    
    
    
    
    
    
    
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
    
    
    def show_my_help( self ):
        FrmGenericText.request( self.window, text = get_basic_documentation( self.window ) )
    
    
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
