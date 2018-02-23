from typing import Callable, Optional

import re
from PyQt5.QtGui import QCursor
from PyQt5.QtWidgets import QAction, QFileDialog, QLabel, QMainWindow, QMenu, QMenuBar, QPushButton, QToolTip
from groot.data.global_view import RecentFile

from intermake import intermake_gui
from groot import constants, extensions
from groot.data import global_view
from groot.frontends.gui import gui_view_utils
from groot.frontends.gui.gui_view_utils import ESelMenu, LegoSelection
from intermake.engine.plugin import Plugin
from intermake.engine.plugin_arguments import ArgsKwargs
from intermake.hosts.frontends.gui_qt.frm_arguments import FrmArguments
from mhelper import SwitchError, file_helper
from mhelper_qt import exceptToGui, qt_gui_helper


class GuiMenu:
    def __init__( self, frm_main: QMainWindow ):
        from groot.frontends.gui.forms.frm_main import FrmMain
        self.frm_main: FrmMain = frm_main
        self.menu_bar: QMenuBar = self.frm_main.menuBar()
        self.menus = { }
        self.actions = []
        self.gui_actions: GuiActions = GuiActions( self.frm_main, self.frm_main )
        
        a = self.gui_actions
        
        self.mnu_file = self.add_menu( ["File"] )
        self.add_action( "File", "&New", fn = a.new_model )
        self.add_action( "File", "&Open", fn = a.show_load_model, checked = a.is_load_file_visible )
        self.add_action( "File", "&Save", fn = a.save_model )
        self.add_action( "File", "Save &as", fn = a.show_save_model, checked = a.is_save_file_visible )
        self.add_action( "File", "Recent", "r" )
        self.add_action( "File", "-" )
        self.add_action( "File", "&Show options", fn = a.show_options, checked = a.is_options_visible )
        self.add_action( "File", "-" )
        self.add_action( "File", "E&xit", fn = a.close_application )
        
        self.mnu_data = self.add_menu( ["Data"] )
        self.add_action( "Data", "&Show workflow", fn = a.show_workflow, checked = a.is_workflow_visible )
        self.add_action( "Data", "&Show wizard", fn = a.show_wizard, checked = a.is_wizard_visible )
        self.add_action( "Data", "-" )
        self.add_action( "Data", "&Import", fn = a.import_file )
        self.add_action( "Data", "&Show model entities", fn = a.show_entities, checked = a.is_entities_visible )
        self.add_action( "Data", "&View text", fn = a.show_text_data, checked = a.is_text_visible )
        
        self.mnu_components = self.add_menu( ["Components"] )
        self.add_action( "Components", "&Create", fn = a.create_components )
        self.add_action( "Components", "&Drop", fn = a.drop_components )
        self.add_action( "Components", "&View lego", fn = a.show_lego, checked = a.is_lego_visible )
        
        self.mnu_domains = self.add_menu( ["Domains"] )
        self.add_action( "Domains", "&Modify", fn = a.show_domains, checked = a.is_domain_visible )
        self.add_action( "Domains", "&View lego", fn = a.show_lego, checked = a.is_lego_visible )
        
        self.mnu_alignments = self.add_menu( ["Alignments"] )
        self.add_action( "Alignments", "&Create alignment...", fn = a.show_create_alignment, checked = a.is_create_alignment_visible )
        self.add_action( "Alignments", "&Drop", fn = a.drop_alignments )
        self.add_action( "Alignments", "&View alignments", fn = a.show_alignments, checked = a.is_alignments_visible )
        
        self.mnu_trees = self.add_menu( ["Trees"] )
        self.add_action( "Trees", "&Create trees...", fn = a.show_create_trees, checked = a.is_create_tree_visible )
        self.add_action( "Trees", "&Drop", fn = a.drop_trees )
        self.add_action( "Trees", "&View trees", fn = a.show_trees, checked = a.is_tree_visible )
        
        self.mnu_fusions = self.add_menu( ["Fusions"] )
        self.add_action( "Fusions", "&Create", fn = a.create_fusions )
        self.add_action( "Fusions", "&Drop", fn = a.drop_fusions )
        self.add_action( "Fusions", "&Show fusions", fn = a.show_fusions, checked = a.is_fusion_visible )
        
        self.mnu_nrfg = self.add_menu( ["Nrfg"] )
        self.add_action( "Nrfg", "&Create", fn = a.create_nrfg )
        self.add_action( "Nrfg", "&Drop", fn = a.drop_nrfg )
        self.add_action( "Nrfg", "&Show tree visualiser", fn = a.show_trees, checked = a.is_tree_visible )
        
        self.mnu_windows = self.add_menu( ["Windows"] )
        self.add_action( "Windows", "&Show options", fn = a.show_options, checked = a.is_workflow_visible )
        self.add_action( "Windows", "&Show workflow", fn = a.show_workflow, checked = a.is_workflow_visible )
        self.add_action( "Windows", "&Show wizard", fn = a.show_wizard, checked = a.is_wizard_visible )
        self.add_action( "Windows", "&Show samples", fn = a.show_load_model, checked = a.is_load_file_visible )
        self.add_action( "Windows", "&Show samples", fn = a.show_save_model, checked = a.is_save_file_visible )
        self.add_action( "Windows", "&Show lego diagram", fn = a.show_lego, checked = a.is_lego_visible )
        self.add_action( "Windows", "&Show alignment viewer", fn = a.show_alignments, checked = a.is_alignments_visible )
        self.add_action( "Windows", "&Show text data", fn = a.show_text_data, checked = a.is_text_visible )
        self.add_action( "Windows", "&Show model entities", fn = a.show_entities, checked = a.is_entities_visible )
        self.add_action( "Windows", "&Show fusion", fn = a.show_fusions, checked = a.is_fusion_visible )
        self.add_action( "Windows", "&Show intermake", fn = a.show_intermake, checked = a.is_intermake_visible )
        self.add_action( "Windows", "&Show domain", fn = a.show_domains, checked = a.is_domain_visible )
        self.add_action( "Windows", "&Show debug", fn = a.show_debug_form, checked = a.is_debug_visible )
        self.add_action( "Windows", "&Show startup", fn = a.show_startup, checked = a.is_startup_visible )
        self.add_action( "Windows", "&Show version", fn = a.show_version, checked = a.is_version_visible )
        self.add_action( "Windows", "&Show create trees", fn = a.show_trees, checked = a.is_tree_visible )
        self.add_action( "Windows", "&Show create trees", fn = a.show_create_trees, checked = a.is_create_tree_visible )
        self.add_action( "Windows", "&Show create alignment", fn = a.show_create_alignment, checked = a.is_create_alignment_visible )
        self.add_action( "Windows", "&Show wizard progress", fn = a.show_wizard_progress, checked = a.is_wizard_progress_visible )
        
        self.mnu_help = self.add_menu( ["Help"] )
        self.add_action( "Help", "&Show readme", fn = a.show_help )
        self.add_action( "Help", "&Show version", fn = a.show_version, checked = a.is_version_visible )
    
    
    def add_action( self, *texts: str, fn: Callable[[], None] = None, checked = None ):
        menu = self.add_menu( texts[:-1] )
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
        action.TAG_checked = checked
        
        if checked is not None:
            action.setCheckable( True )
        
        self.actions.append( action )
        menu.addAction( action )
    
    
    def add_recent( self, menu: QMenu ):
        if not global_view.options().recent_files:
            menu.setEnabled( False )
        
        for item in reversed( global_view.options().recent_files ):
            if not isinstance( item, RecentFile ):
                # Legacy data, discard
                continue
            
            action = QAction()
            action.setText( file_helper.get_filename_without_extension( item.file_name ) )
            action.TAG_file = item
            action.triggered[bool].connect( self.__on_action )
            self.actions.append( action )
            menu.addAction( action )
    
    
    def add_menu( self, texts ):
        menu_path = ""
        menu = self.menu_bar
        
        for text in texts:
            menu_path += "." + text
            new_menu: QMenu = self.menus.get( menu_path )
            
            if not new_menu:
                new_menu = QMenu()
                new_menu.setStyleSheet( intermake_gui.default_style_sheet() )
                new_menu.setTitle( text )
                self.menus[menu_path] = new_menu
                new_menu.aboutToShow.connect( self.__on_menu_about_to_show )
                menu.addMenu( new_menu )
            
            menu = new_menu
        
        return menu
    
    
    def __on_menu_about_to_show( self ):
        menu: QMenu = self.frm_main.sender()
        for action in menu.actions():
            assert isinstance( action, QAction )
            
            if hasattr( action, "TAG_checked" ) and action.TAG_checked:
                action.setChecked( action.TAG_checked() )
    
    
    def __on_action( self, _: bool ):
        sender = self.frm_main.sender()
        
        if hasattr( sender, "TAG_file" ):
            file_name = sender.TAG_file
            self.gui_actions.load_file( file_name )
            return
        else:
            fn = sender.TAG_function
            fn()


class GuiActions:
    def __init__( self, frm_main, window ):
        from groot.frontends.gui.forms.frm_main import FrmMain
        assert isinstance( frm_main, FrmMain )
        self.frm_main = frm_main
        self.window = window
        self.select_button: QPushButton = None
        self.select_choice: ESelMenu = ESelMenu.ALL
    
    
    @exceptToGui()
    def close_window( self ):
        self.window.close()
    
    
    @exceptToGui()
    def wizard_next( self ):
        # TODO
        raise NotImplementedError( "TODO" )  # TODO
    
    
    @exceptToGui()
    def close_application( self ):
        self.frm_main.close()
    
    
    @exceptToGui()
    def get_model( self ):
        return global_view.current_model()
    
    
    @exceptToGui()
    def new_model( self ):
        extensions.ext_files.file_new.run()
    
    
    @exceptToGui()
    def save_model( self ):
        if self.get_model().file_name:
            extensions.ext_files.file_save( self.get_model().file_name )
        else:
            self.show_save_model()
    
    
    @exceptToGui()
    def save_model_using( self, file_name: str ):
        extensions.ext_files.file_save( file_name )
    
    
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
    def show_workflow( self ) -> None:
        """
        Shows FrmWorkflow
        """
        from groot.frontends.gui.forms.frm_workflow import FrmWorkflow
        self.frm_main.show_form( FrmWorkflow )
    
    
    @exceptToGui()
    def show_wizard( self ) -> None:
        """
        Shows FrmWizard
        """
        from groot.frontends.gui.forms.frm_wizard import FrmWizard
        self.frm_main.show_form( FrmWizard )
    
    
    @exceptToGui()
    def show_options( self ) -> None:
        """
        Shows FrmViewOptions
        """
        from groot.frontends.gui.forms.frm_view_options import FrmViewOptions
        self.frm_main.show_form( FrmViewOptions )
    
    
    @exceptToGui()
    def show_lego( self ) -> None:
        """
        Shows FrmLego
        """
        from groot.frontends.gui.forms.frm_lego import FrmLego
        self.frm_main.show_form( FrmLego )
    
    
    @exceptToGui()
    def show_trees( self ) -> None:
        """
        Shows FrmWebtree
        """
        from groot.frontends.gui.forms.frm_webtree import FrmWebtree
        self.frm_main.show_form( FrmWebtree )
    
    
    @exceptToGui()
    def show_text_data( self ) -> None:
        """
        Shows FrmBigText
        """
        from groot.frontends.gui.forms.frm_big_text import FrmBigText
        self.frm_main.show_form( FrmBigText )
    
    
    @exceptToGui()
    def show_create_trees( self ) -> None:
        """
        Shows FrmCreateTrees
        """
        from groot.frontends.gui.forms.frm_run_algorithm import FrmCreateTrees
        self.frm_main.show_form( FrmCreateTrees )
    
    
    @exceptToGui()
    def show_create_alignment( self ) -> None:
        """
        Shows FrmCreateAlignment
        """
        from groot.frontends.gui.forms.frm_run_algorithm import FrmCreateAlignment
        self.frm_main.show_form( FrmCreateAlignment )
    
    
    @exceptToGui()
    def show_entities( self ) -> None:
        """
        Shows FrmSelectionList
        """
        from groot.frontends.gui.forms.frm_selection_list import FrmSelectionList
        self.frm_main.show_form( FrmSelectionList )
    
    
    @exceptToGui()
    def show_alignments( self ) -> None:
        """
        Shows FrmAlignment
        """
        from groot.frontends.gui.forms.frm_alignment import FrmAlignment
        self.frm_main.show_form( FrmAlignment )
    
    
    @exceptToGui()
    def show_fusions( self ) -> None:
        """
        Shows FrmFusions
        """
        from groot.frontends.gui.forms.frm_fusions import FrmFusions
        self.frm_main.show_form( FrmFusions )
    
    
    @exceptToGui()
    def show_load_model( self ) -> None:
        """
        Shows FrmLoadFile
        """
        from groot.frontends.gui.forms.frm_samples import FrmLoadFile
        self.frm_main.show_form( FrmLoadFile )
    
    
    @exceptToGui()
    def show_save_model( self ) -> None:
        """
        Shows FrmSaveFile
        """
        from groot.frontends.gui.forms.frm_samples import FrmSaveFile
        self.frm_main.show_form( FrmSaveFile )
    
    
    @exceptToGui()
    def show_wizard_progress( self ) -> None:
        """
        Shows FrmWizardActive
        """
        from groot.frontends.gui.forms.frm_wizard_active import FrmWizardActive
        self.frm_main.show_form( FrmWizardActive )
    
    
    @exceptToGui()
    def show_intermake( self ) -> None:
        """
        Shows the intermake window (FrmIntermakeMain)
        """
        from intermake.hosts.frontends.gui_qt.frm_intermake_main import FrmIntermakeMain
        self.frm_main.show_form( FrmIntermakeMain )
    
    
    @exceptToGui()
    def show_domains( self ) -> None:
        """
        Shows FrmDomain
        """
        from groot.frontends.gui.forms.frm_domain import FrmDomain
        self.frm_main.show_form( FrmDomain )
    
    
    @exceptToGui()
    def show_startup( self ) -> None:
        """
        Shows FrmStartup
        """
        from groot.frontends.gui.forms.frm_startup import FrmStartup
        self.frm_main.show_form( FrmStartup )
    
    
    @exceptToGui()
    def show_debug_form( self ) -> None:
        """
        Shows FrmDebug
        """
        from groot.frontends.gui.forms.frm_debug import FrmDebug
        self.frm_main.show_form( FrmDebug )
    
    
    @exceptToGui()
    def is_workflow_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_workflow import FrmWorkflow
        return FrmWorkflow in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_options_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_view_options import FrmViewOptions
        return FrmViewOptions in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_wizard_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_wizard import FrmWizard
        return FrmWizard in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_lego_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_lego import FrmLego
        return FrmLego in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_tree_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_webtree import FrmWebtree
        return FrmWebtree in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_create_tree_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_run_algorithm import FrmCreateTrees
        return FrmCreateTrees in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_create_alignment_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_run_algorithm import FrmCreateAlignment
        return FrmCreateAlignment in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_text_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_big_text import FrmBigText
        return FrmBigText in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_entities_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_selection_list import FrmSelectionList
        return FrmSelectionList in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_wizard_progress_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_wizard_active import FrmWizardActive
        return FrmWizardActive in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_alignments_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_alignment import FrmAlignment
        return FrmAlignment in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_fusion_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_fusions import FrmFusions
        return FrmFusions in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_load_file_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_samples import FrmLoadFile
        return FrmLoadFile in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_save_file_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_samples import FrmSaveFile
        return FrmSaveFile in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_intermake_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from intermake.hosts.frontends.gui_qt.frm_intermake_main import FrmIntermakeMain
        return FrmIntermakeMain in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_domain_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_domain import FrmDomain
        return FrmDomain in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_debug_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_debug import FrmDebug
        return FrmDebug in self.frm_main.mdi
    
    
    @exceptToGui()
    def is_startup_visible( self ) -> bool:
        """
        Returns if the form is visible
        """
        from groot.frontends.gui.forms.frm_startup import FrmStartup
        return FrmStartup in self.frm_main.mdi
    
    
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
        from groot.frontends.gui.forms.frm_about import FrmAbout
        self.frm_main.show_form( FrmAbout )
    
    
    def is_version_visible( self ):
        from groot.frontends.gui.forms.frm_about import FrmAbout
        return FrmAbout in self.frm_main.mdi
    
    
    def dismiss_startup_screen( self ):
        from groot.frontends.gui.forms.frm_startup import FrmStartup
        self.frm_main.close_form( FrmStartup )
    
    
    def bind_to_label( self, label: QLabel ):
        label.linkActivated[str].connect( self.by_url )
        label.linkHovered[str].connect( self.show_status_message )
        
        for x in re.findall( 'href="([^"]+)"', label.text() ):
            if not self.by_url( x, validate = True ):
                raise ValueError( "«{}» is not a valid Groot URL.".format( x ) )
    
    
    def bind_to_select( self, button: QPushButton, choice: ESelMenu = ESelMenu.ALL ):
        self.select_button = button
        self.select_choice = choice
        
        self.select_button.setProperty( "style", "dropdown" )
        self.select_button.setText( str( self.get_selection() ) )
        self.select_button.clicked.connect( self.show_selection )
    
    
    def on_selection_changed( self ):
        if self.select_button is not None:
            self.select_button.setText( str( self.get_selection() ) )
    
    
    def get_selection( self ):
        return global_view.current_selection()
    
    
    def show_status_message( self, text: str ):
        self.frm_main.statusBar().showMessage( text )
        QToolTip.showText( QCursor.pos(), text )
    
    
    def by_url( self, link: str, validate = False ):
        key, value = link.split( ":", 1 )
        
        if key == "action":
            if validate:
                return hasattr( self, value )
            
            fn = getattr( self, value )
            fn()
        elif key == "save_file":
            if validate:
                return True
            
            self.save_model_using( value )
        elif key == "load_file":
            if validate:
                return True
            
            self.load_file( value )
        elif key == "load_sample":
            if validate:
                return True
            
            self.load_sample( value )
        else:
            if validate:
                return False
            
            raise SwitchError( "link", link )
    
    
    def show_selection( self ):
        gui_view_utils.show_selection_menu( self.select_button, self, self.select_choice )
    
    
    def browse_open( self ):
        file_name = qt_gui_helper.browse_open( self.window, constants.DIALOGUE_FILTER )
        
        if file_name:
            extensions.ext_files.file_load( file_name )
    
    
    def set_selection( self, value: LegoSelection ):
        global_view.set_selection( value )
    
    
    def enable_inbuilt_browser( self ):
        from groot.frontends.gui.forms.frm_webtree import FrmWebtree
        form = self.frm_main.mdi.get( FrmWebtree )
        
        if form is None:
            return
        
        form.enable_inbuilt_browser()
