from typing import Iterator, Optional, Sequence

from PyQt5.QtGui import QCursor, QResizeEvent
from PyQt5.QtWidgets import QAction, QApplication, QFileDialog, QLabel, QMainWindow, QMenu, QMenuBar, QSizePolicy, QToolTip, QWidgetAction, QMessageBox

from groot import constants, extensions
from groot.data import global_view
from groot.data.global_view import RecentFile
from groot.extensions import ext_gimmicks, ext_files
from groot.frontends.gui import gui_view_utils
from groot.frontends.gui.gui_view_utils import LegoSelection
from groot.frontends.gui.gui_workflow import EIntent, LegoStage, LegoVisualiser
from groot.frontends.gui import gui_workflow
from intermake.engine.plugin import Plugin
from intermake.engine.plugin_arguments import ArgsKwargs
from intermake.hosts.frontends.gui_qt.frm_arguments import FrmArguments
from mhelper import SwitchError, file_helper
from mhelper_qt import qt_gui_helper, menu_helper


class GuiActions:
    def __init__( self, frm_main, window ):
        from groot.frontends.gui.forms.frm_main import FrmMain
        from groot.frontends.gui.forms.frm_base import FrmBase
        assert isinstance( frm_main, FrmMain )
        self.frm_main: FrmMain = frm_main
        self.window: FrmBase = window
    
    
    def launch_intent( self, stage: LegoStage, intent: EIntent ):
        visualisers = list( stage.visualisers( intent ) )
        
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
                self.launch( map[selected], stage )
    
    
    def launch( self, visualiser: LegoVisualiser, stage: LegoStage = None ):
        from groot.frontends.gui.forms.frm_base import FrmBase
        
        if stage is None:
            args = ()
        else:
            args = (stage,)
        
        if isinstance( visualiser.action, type ) and issubclass( visualiser.action, FrmBase ):
            self.frm_main.show_form( visualiser.action, *args )
        elif isinstance( visualiser.action, Plugin ):
            self.request( visualiser.action )
        else:
            visualiser.action( self, *args )
    
    
    def menu( self, stage: LegoStage ):
        menu_handler = self.frm_main.menu_handler
        menu = menu_handler.stages[stage]
        menu_handler.update_dynamic_menu( menu )
        menu_helper.show_menu( self.window, menu )
    
    
    def close_window( self ):
        """
        Closes the calling window.
        
        As well as providing a means for help HTML to close the form,
        this should be called instead of `QDialog.close` since QDialog.close doesn't work
        properly if the form is hosted as an MDI window.
        """
        self.frm_main.close_form( type( self.window ) )
    
    
    def wizard_next( self ):
        ext_gimmicks.continue_wizard()
    
    
    def close_application( self ):
        self.frm_main.close()
    
    
    def get_model( self ):
        return global_view.current_model()
    
    
    def save_model( self ):
        if self.get_model().file_name:
            extensions.ext_files.file_save( self.get_model().file_name )
        else:
            self.launch( gui_workflow.VISUALISERS.VIEW_SAVE_FILE )
    
    
    def save_model_to( self, file_name: str ):
        extensions.ext_files.file_save( file_name )
    
    
    def request( self, plugin: Plugin, *args, **kwargs ):
        if args is None:
            args = ()
        
        arguments: Optional[ArgsKwargs] = FrmArguments.request( self.window, plugin, *args, **kwargs )
        
        if arguments is not None:
            plugin.run( *arguments.args, **arguments.kwargs )  # --> self.plugin_completed
    
    
    def get_selection( self ):
        return global_view.current_selection()
    
    
    def show_status_message( self, text: str ):
        self.frm_main.statusBar().showMessage( text )
        QToolTip.showText( QCursor.pos(), text )
    
    
    def get_visualiser( self, name ):
        return getattr( gui_workflow.VISUALISERS, name.upper() )
    
    
    def get_stage( self, name ):
        return getattr( gui_workflow.STAGES, name.upper() ) if name else None
    
    
    def by_url( self, link: str, validate = False ):
        if ":" in link:
            key, value = link.split( ":", 1 )
        else:
            key = link
            value = None
        
        if "/" in value:
            value, param = value.split( "/", 1 )
        else:
            param = None
        
        if key == "action":
            try:
                visualiser = gui_workflow.VISUALISERS.find_by_key( value )
            except KeyError:
                if validate:
                    return False
                else:
                    raise
            
            if validate:
                return True
            
            self.launch( visualiser, param if param else None )
        else:
            if validate:
                return False
            else:
                raise SwitchError( "link", link )
    
    
    def show_selection( self ):
        form = self.window
        
        from groot.frontends.gui.forms.frm_base import FrmBase
        assert isinstance( form, FrmBase )
        gui_view_utils.show_selection_menu( form.select_button, self, form.workflow )
    
    
    def browse_open( self ):
        file_name = qt_gui_helper.browse_open( self.window, constants.DIALOGUE_FILTER )
        
        if file_name:
            extensions.ext_files.file_load( file_name )
    
    
    def set_selection( self, value: LegoSelection ):
        global_view.set_selection( value )
    
    
    def enable_inbuilt_browser( self ):
        from groot.frontends.gui.forms.frm_webtree import FrmWebtree
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
        from groot.frontends.gui.forms.frm_main import FrmMain
        FrmMain.INSTANCE.close()
    
    
    def dismiss_startup_screen( self ):
        from groot.frontends.gui.forms.frm_main import FrmMain
        from groot.frontends.gui.forms.frm_startup import FrmStartup
        FrmMain.INSTANCE.close_form( FrmStartup )
    
    
    def load_sample_from( self, param ):
        ext_files.file_sample( param )
    
    
    def load_file_from( self, param ):
        ext_files.file_load( param )
    
    
    def stop_wizard( self ):
        ext_gimmicks.stop_wizard()
    
    
    def import_file( self ):
        filters = "Valid files (*.fasta *.fa *.faa *.blast *.tsv *.composites *.txt *.comp)", "FASTA files (*.fasta *.fa *.faa)", "BLAST output (*.blast *.tsv)", "Composite finder output (*.composites)"
        
        file_name, filter = QFileDialog.getOpenFileName( self.window, "Select file", None, ";;".join( filters ), options = QFileDialog.DontUseNativeDialog )
        
        if not file_name:
            return
        
        filter_index = filters.index( filter )
        
        if filter_index == 0:
            extensions.ext_files.import_file( self.get_model(), file_name )
        elif filter_index == 0:
            extensions.ext_files.import_fasta( self.get_model(), file_name )
        elif filter_index == 1:
            extensions.ext_files.import_blast( self.get_model(), file_name )
        elif filter_index == 2:
            extensions.ext_files.import_composites( self.get_model(), file_name )
        else:
            raise SwitchError( "filter_index", filter_index )
    
    
    def browse_save( self ):
        file_name = qt_gui_helper.browse_save( self.window, constants.DIALOGUE_FILTER )
        
        if file_name:
            extensions.ext_files.file_save( file_name )
