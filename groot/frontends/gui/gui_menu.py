from PyQt5.QtWidgets import QMainWindow, QMenuBar, QMenu, QAction, QFileDialog, QMessageBox, QLabel, QPushButton
from typing import Callable, Optional

from groot import extensions, constants
from groot.frontends.gui.gui_view_utils import LegoSelection, ESelMenu
from groot.frontends.gui import gui_view_utils
from intermake.engine.environment import MENV
from intermake.engine.plugin import Plugin
from intermake.engine.plugin_arguments import ArgsKwargs
from intermake.hosts.frontends.gui_qt.frm_arguments import FrmArguments
from mhelper import SwitchError, file_helper
from mhelper_qt import exceptToGui, qt_gui_helper
from groot.data import global_view


class GuiMenu:
    def __init__( self, form: QMainWindow ):
        self.form = form
        self.menu_bar: QMenuBar = self.form.menuBar()
        self.menus = { }
        self.actions = []
        self.gui_actions: GuiActions = GuiActions( self.form, self.form )
        self.select_button: QPushButton = None
        self.select_choice: ESelMenu = ESelMenu.ALL
        
        a = self.gui_actions
        
        self.add_action( "File", "&New" )
        self.add_action( "File", "&Open" )
        self.add_action( "File", "&Save" )
        self.add_action( "File", "Save &as" )
        self.add_action( "File", "Recent", "r" )
        self.add_action( "File", "-" )
        self.add_action( "File", "&Show samples", fn = a.show_samples_form )
        self.add_action( "File", "&Show workflow", fn = a.show_workflow_form )
        self.add_action( "File", "&Show wizard", fn = a.show_wizard_form )
        self.add_action( "File", "-" )
        self.add_action( "File", "E&xit", fn = a.close_application )
        
        self.add_action( "Data", "&Import" )
        self.add_action( "Data", "&Show model entities", fn = a.show_entities_form )
        self.add_action( "Data", "&Show text data", fn = a.show_text_form )
        
        self.add_action( "Components", "&Create", fn = a.create_components )
        self.add_action( "Components", "&Drop", fn = a.drop_components )
        self.add_action( "Components", "&Show lego diagram", fn = a.show_lego_form )
        
        self.add_action( "Domains", "&Create", fn = a.show_domain_form )
        self.add_action( "Domains", "&Drop", fn = a.show_domain_form )
        self.add_action( "Domains", "&Show lego diagram", fn = a.show_lego_form )
        
        self.add_action( "Alignments", "&Create", fn = a.create_alignments )
        self.add_action( "Alignments", "&Drop", fn = a.drop_alignments )
        self.add_action( "Alignments", "&Show alignments", fn = a.show_alignments_form )
        
        self.add_action( "Trees", "&Create", fn = a.create_trees )
        self.add_action( "Trees", "&Drop", fn = a.drop_trees )
        self.add_action( "Trees", "&Show tree visualiser", fn = a.show_tree_form )
        
        self.add_action( "Fusions", "&Create", fn = a.create_fusions )
        self.add_action( "Fusions", "&Drop", fn = a.drop_fusions )
        self.add_action( "Fusions", "&Show fusions", fn = a.show_fusion_form )
        
        self.add_action( "NRFG", "&Create", fn = a.create_nrfg )
        self.add_action( "NRFG", "&Drop", fn = a.drop_nrfg )
        self.add_action( "NRFG", "&Show tree visualiser", fn = a.show_tree_form )
        
        self.add_action( "Windows", "&Show workflow", fn = a.show_workflow_form )
        self.add_action( "Windows", "&Show wizard", fn = a.show_wizard_form )
        self.add_action( "Windows", "&Show samples", fn = a.show_samples_form )
        self.add_action( "Windows", "&Show lego diagram", fn = a.show_lego_form )
        self.add_action( "Windows", "&Show alignment viewer", fn = a.show_alignments_form )
        self.add_action( "Windows", "&Show text data", fn = a.show_text_form )
        self.add_action( "Windows", "&Show model entities", fn = a.show_entities_form )
        self.add_action( "Windows", "&Show fusion", fn = a.show_fusion_form )
        self.add_action( "Windows", "&Show intermake", fn = a.show_intermake_form )
        self.add_action( "Windows", "&Show domain", fn = a.show_domain_form )
        self.add_action( "Windows", "&Show debug", fn = a.show_debug_form )
        
        self.add_action( "Help", "&Show readme", fn = a.show_help )
        self.add_action( "Help", "&Show version", fn = a.show_version )
    
    
    def add_action( self, *texts: str, fn: Callable[[], None] = None ):
        menu = self.get_menu( texts[:-1] )
        final = texts[-1]
        
        if final == "-":
            menu.addSeparator()
            return
        elif final == "r":
            self.add_recent( menu )
            return
        
        action = QAction()
        action.setText( texts[-1] )
        if fn:
            action.TAG_function = fn
            action.triggered[bool].connect( self.__on_action )
        self.actions.append( action )
        menu.addAction( action )
    
    
    def add_recent( self, menu: QMenu ):
        if not global_view.options().recent_files:
            menu.setEnabled( False )
        
        for item in reversed( global_view.options().recent_files ):
            action = QAction()
            action.setText( file_helper.get_filename_without_extension( item ) )
            action.TAG_file = item
            action.triggered[bool].connect( self.__on_action )
            self.actions.append( action )
            menu.addAction( action )
    
    
    def get_menu( self, texts ):
        menu_path = ""
        menu = self.menu_bar
        
        for text in texts:
            menu_path += "." + text
            new_menu: QMenu = self.menus.get( menu_path )
            
            if not new_menu:
                new_menu = QMenu()
                new_menu.setTitle( text )
                self.menus[menu_path] = new_menu
                menu.addMenu( new_menu )
            
            menu = new_menu
        
        return menu
    
    
    def __on_action( self, _: bool ):
        sender = self.form.sender()
        
        if hasattr( sender, "TAG_file" ):
            file_name = sender.TAG_file
            self.gui_actions.load_file( file_name )
            return
        else:
            fn = sender.TAG_function
            fn()


class GuiActions:
    def __init__( self, form, window ):
        self.form = form
        self.window = window
    
    
    @exceptToGui()
    def close_application( self ):
        self.form.close()
    
    
    @exceptToGui()
    def get_model( self ):
        global_view.current_model()
    
    
    @exceptToGui()
    def new_model( self ):
        extensions.ext_files.file_new.run()
    
    
    @exceptToGui()
    def save_model( self ):
        extensions.ext_files.file_save( self.get_model().file_name )
    
    
    @exceptToGui()
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
    
    
    @exceptToGui()
    def save_model_as( self ):
        file_name = qt_gui_helper.browse_save( self.window, constants.DIALOGUE_FILTER )
        
        if file_name:
            extensions.ext_files.file_save( file_name )
    
    
    @exceptToGui()
    def show_workflow_form( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_workflow import FrmWorkflow
        self.form.show_form( FrmWorkflow )
    
    
    @exceptToGui()
    def show_wizard_form( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_wizard import FrmWizard
        self.form.show_form( FrmWizard )
    
    
    @exceptToGui()
    def show_lego_form( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_lego import FrmLego
        self.form.show_form( FrmLego )
    
    
    @exceptToGui()
    def show_tree_form( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_webtree import FrmWebtree
        self.form.show_form( FrmWebtree )
    
    
    @exceptToGui()
    def show_text_form( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_big_text import FrmBigText
        self.form.show_form( FrmBigText )
    
    
    @exceptToGui()
    def show_entities_form( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_selection_list import FrmSelectionList
        self.form.show_form( FrmSelectionList )
    
    
    @exceptToGui()
    def show_alignments_form( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_alignment import FrmAlignment
        self.form.show_form( FrmAlignment )
    
    
    @exceptToGui()
    def show_fusion_form( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_fusions import FrmFusions
        self.form.show_form( FrmFusions )
    
    
    @exceptToGui()
    def show_samples_form( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_samples import FrmSamples
        self.form.show_form( FrmSamples )
    
    
    @exceptToGui()
    def show_intermake_form( self ) -> None:
        """
        Signal handler:
        """
        from intermake.hosts.frontends.gui_qt.frm_intermake_main import FrmIntermakeMain
        self.form.show_form( FrmIntermakeMain )
    
    
    @exceptToGui()
    def show_domain_form( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_domain import FrmDomain
        self.form.show_form( FrmDomain )
    
    
    @exceptToGui()
    def show_debug_form( self ) -> None:
        """
        Signal handler:
        """
        from groot.frontends.gui.forms.frm_debug import FrmDebug
        self.form.show_form( FrmDebug )
    
    
    def create_nrfg( self ):
        self.request( extensions.ext_generating.make_nrfg )
    
    
    def request( self, plugin: Plugin, *args, **kwargs ):
        if args is None:
            args = ()
        
        arguments: Optional[ArgsKwargs] = FrmArguments.request( self.window, plugin, *args, **kwargs )
        
        if arguments is not None:
            plugin.run( *arguments.args, **arguments.kwargs )  # --> self.plugin_completed
    
    
    def drop_nrfg( self ):
        self.request( extensions.ext_dropping.drop_nrfg )
    
    
    def drop_fusions( self ):
        self.request( extensions.ext_dropping.drop_fusions )
    
    
    def create_fusions( self ):
        self.request( extensions.ext_generating.make_fusions )
    
    
    def drop_trees( self ):
        self.request( extensions.ext_dropping.drop_tree )
    
    
    def create_trees( self ):
        self.request( extensions.ext_generating.make_trees )
    
    
    def drop_alignments( self ):
        self.request( extensions.ext_dropping.drop_alignment )
    
    
    def create_alignments( self ):
        self.request( extensions.ext_generating.make_alignments )
    
    
    def drop_components( self ):
        self.request( extensions.ext_dropping.drop_components )
    
    
    def create_components( self ):
        self.request( extensions.ext_generating.make_components )
    
    
    def load_sample( self, param ):
        extensions.ext_files.file_sample( param )
    
    
    def load_file( self, param ):
        extensions.ext_files.file_load( param )
    
    
    def show_help( self ):
        import webbrowser
        webbrowser.open( "https://bitbucket.org/mjr129/groot" )
    
    
    def show_version( self ):
        QMessageBox.about( self.window, self.form.windowTitle(), MENV.name + " - " + str( MENV.version ) )
    
    
    def dismiss_startup_screen( self ):
        self.form.ui.FRA_HELP.setVisible( False )
        self.form.ui.MDI_AREA.setVisible( True )
    
    
    def bind_to_label( self, label: QLabel ):
        label.linkActivated[str].connect( self.by_url )
        label.linkHovered[str].connect( self.show_status_message )
    
    
    def bind_to_select( self, button: QPushButton, choice: ESelMenu = ESelMenu.ALL ):
        self.select_button = button
        self.select_choice = choice
        
        self.select_button.setProperty("style", "dropdown")
        self.select_button.setText( str( self.get_selection() ) )
        self.select_button.clicked.connect( self.show_selection )
    
    
    def get_selection( self ):
        return global_view.current_selection()
    
    
    def show_status_message( self, text: str ):
        self.form.statusBar().showMessage( text )
    
    
    def by_url( self, link: str ):
        if link == "action:show_workflow_form":
            self.show_workflow_form()
        elif link == "action:show_wizard_form":
            self.show_wizard_form()
        elif link == "action:dismiss_startup_screen":
            self.dismiss_startup_screen()
        elif link == "action:new_model":
            self.new_model()
        elif link == "action:save_model":
            self.save_model()
        elif link == "action:show_help":
            self.show_help()
        elif link == "action:show_domain_form":
            self.show_domain_form()
        elif link == "action:show_lego_form":
            self.show_lego_form()
        elif link == "action:create_alignments":
            self.create_alignments()
        elif link == "action:show_alignments_form":
            self.show_alignments_form()
        elif link == "action:create_trees":
            self.create_trees()
        elif link == "action:show_tree_form":
            self.show_tree_form()
        elif link == "action:create_fusions":
            self.create_fusions()
        elif link == "action:create_nrfg":
            self.create_nrfg()
        elif link == "action:create_nrfg":
            self.show_fusion_form()
        elif link == "action:show_samples_form":
            self.show_samples_form()
        elif link == "action:show_selection":
            self.show_selection()
        elif link == "action:show_entities_form":
            self.show_entities_form()
        elif link == "action:create_components":
            self.create_components()
        elif link == "action:browse_open":
            self.browse_open()
        elif link == "action:show_text_form":
            self.show_text_form()
        elif link == "action:create_components":
            self.create_components()
        elif link == "action:import_file":
            self.import_file()
        elif link.startswith( "load_file:" ):
            self.load_file( link.split( ":", 1 )[1] )
        elif link.startswith( "load_sample:" ):
            self.load_sample( link.split( ":", 1 )[1] )
        else:
            raise SwitchError( "link", link )
    
    
    def show_selection( self ):
        gui_view_utils.show_selection_menu( self.select_button, self, self.select_choice )
    
    
    def browse_open( self ):
        file_name = qt_gui_helper.browse_open( self.window, constants.DIALOGUE_FILTER )
        
        if file_name:
            extensions.ext_files.file_load( file_name )
    
    
    def set_selection( self, value: LegoSelection ):
        global_view.set_selection( value )
