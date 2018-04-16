from typing import Iterator, Sequence

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QResizeEvent, QKeySequence
from PyQt5.QtWidgets import QAction, QApplication, QLabel, QMainWindow, QMenu, QMenuBar, QSizePolicy, QWidgetAction, QGroupBox, QHBoxLayout, QFrame, QToolButton, QAbstractButton

from groot import constants
from groot.constants import STAGES
from mhelper import file_helper, ResourceIcon
from groot.frontends.gui import gui_workflow
from groot.data import global_view
from groot.data.global_view import RecentFile
from groot.frontends.gui.gui_workflow import EIntent, LegoStage, LegoVisualiser
from groot.frontends.gui.gui_actions import GuiActions
from groot.frontends.gui.forms.resources import resources


_SUFFIX = """
QToolButton
{{
    border-left: 4px solid palette(button);
    border-top: 4px solid palette(button);
    border-right: 4px solid palette(button);
    border-bottom: 4px solid {};
}}
QToolButton:hover
{{
    border-top: 6px solid palette(button); 
}} 
QToolButton:pressed 
{{
    background: palette(dark); 
}}
"""


class VisWrap:
    def __init__( self, owner: GuiActions, visualiser: LegoVisualiser, *args ):
        self.owner = owner
        self.visualiser = visualiser
        self.args = args
    
    
    def execute( self, _: bool ) -> None:
        self.owner.launch( self.visualiser, *self.args )


class StageWrap:
    def __init__( self, owner: GuiActions, stage: LegoStage ):
        self.owner = owner
        self.stage = stage
    
    
    def execute( self, _: bool ) -> None:
        self.owner.menu( self.stage )


class GuiMenu:
    def __init__( self, frm_main: QMainWindow ):
        from groot.frontends.gui.forms.frm_main import FrmMain
        assert isinstance( frm_main, FrmMain )
        ui = frm_main.ui
        
        self.frm_main: FrmMain = frm_main
        self.menu_bar: QMenuBar = self.frm_main.menuBar()
        self.menus = { }
        self.keep_alive = []
        self.headlines = []
        self.stages = { }
        self.workflow_buttons = []
        self.gui_actions: GuiActions = GuiActions( self.frm_main, self.frm_main )
        
        self.mnu_file = self.add_menu( ["File"], headline = lambda m: constants.STAGES._FILE_0.headline( m ) )
        self.add_action( ["File", "New"], visualiser = gui_workflow.VISUALISERS.ACT_FILE_NEW, toolbar = ui.FRA_FILE )
        self.add_action( ["File", "Open..."], visualiser = gui_workflow.VISUALISERS.VIEW_OPEN_FILE, toolbar = ui.FRA_FILE )
        self.add_action( ["File", "Recent", "r"] )
        self.add_action( ["File", "-"] )
        self.add_action( ["File", "Save"], visualiser = gui_workflow.VISUALISERS.ACT_FILE_SAVE, toolbar = ui.FRA_FILE )
        self.add_action( ["File", "Save &as..."], visualiser = gui_workflow.VISUALISERS.VIEW_SAVE_FILE )
        self.add_action( ["File", "-"] )
        self.add_action( ["File", "E&xit"], visualiser = gui_workflow.VISUALISERS.ACT_EXIT )
        
        for stage in STAGES:
            self.add_workflow( stage )
        
        self.mnu_windows = self.add_menu( ["Windows"] )
        self.add_action( ["Windows", "&Workflow..."], visualiser = gui_workflow.VISUALISERS.VIEW_WORKFLOW, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "&Wizard..."], visualiser = gui_workflow.VISUALISERS.VIEW_WIZARD, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "&Preferences..."], visualiser = gui_workflow.VISUALISERS.VIEW_PREFERENCES, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "-"], toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Visualisers", "Text..."], visualiser = gui_workflow.VISUALISERS.VIEW_TEXT, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Visualisers", "Lego..."], visualiser = gui_workflow.VISUALISERS.VIEW_LEGO, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Visualisers", "Alignment..."], visualiser = gui_workflow.VISUALISERS.VIEW_ALIGNMENT, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Visualisers", "Fusion..."], visualiser = gui_workflow.VISUALISERS.VIEW_FUSIONS, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Visualisers", "Trees..."], visualiser = gui_workflow.VISUALISERS.VIEW_TREE, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Visualisers", "Splits..."], visualiser = gui_workflow.VISUALISERS.VIEW_SPLITS, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Editors", "Trees..."], visualiser = gui_workflow.VISUALISERS.CREATE_TREES )
        self.add_action( ["Windows", "Editors", "Alignment..."], visualiser = gui_workflow.VISUALISERS.CREATE_ALIGNMENTS )
        self.add_action( ["Windows", "Editors", "Domains..."], visualiser = gui_workflow.VISUALISERS.CREATE_DOMAINS )
        self.add_action( ["Windows", "Editors", "Subgraphs..."], visualiser = gui_workflow.VISUALISERS.CREATE_SUBGRAPHS )
        self.add_action( ["Windows", "Others", "File open..."], visualiser = gui_workflow.VISUALISERS.VIEW_OPEN_FILE )
        self.add_action( ["Windows", "Others", "File save..."], visualiser = gui_workflow.VISUALISERS.VIEW_SAVE_FILE )
        self.add_action( ["Windows", "Others", "Startup..."], visualiser = gui_workflow.VISUALISERS.VIEW_STARTUP )
        self.add_action( ["Windows", "Others", "Debug..."], visualiser = gui_workflow.VISUALISERS.VIEW_DEBUG )
        self.add_action( ["Windows", "Others", "Version..."], visualiser = gui_workflow.VISUALISERS.VIEW_ABOUT )
        self.add_action( ["Windows", "Others", "Intermake..."], visualiser = gui_workflow.VISUALISERS.VIEW_INTERMAKE, shortcut = Qt.Key_F12 )
        
        self.mnu_help = self.add_menu( ["Help"] )
        self.add_action( ["Help", "&Show readme..."], visualiser = gui_workflow.VISUALISERS.VIEW_HELP )
        self.add_action( ["Help", "&Show version..."], visualiser = gui_workflow.VISUALISERS.VIEW_ABOUT )
    
    
    def add_workflow( self, stage: LegoStage ):
        path = ["Workflow", stage.name]
        mnu = self.add_menu( path, headline = stage.headline )
        
        self.add_workflow_menu( path + ["Create"], stage.visualisers( EIntent.CREATE ), icon = resources.create )
        self.add_workflow_menu( path + ["Drop"], stage.visualisers( EIntent.DROP ), icon = resources.remove )
        self.add_workflow_menu( path + ["View"], stage.visualisers( EIntent.VIEW ), icon = resources.view )
        
        self.stages[stage] = mnu
        
        exe = StageWrap( self.gui_actions, stage )
        self.keep_alive.append( exe )
        
        lay: QHBoxLayout = self.frm_main.ui.FRA_WORKFLOW.layout()
        btn = self.__make_button()
        btn.setText( stage.name )
        btn.setIcon( stage.icon.icon() )
        btn.clicked[bool].connect( exe.execute )
        self.workflow_buttons.append( (stage, btn, stage.icon.path) )
        lay.addWidget( btn )
    
    
    def update_buttons( self ):
        model = self.gui_actions.get_model()
        
        for stage, button, path in self.workflow_buttons:
            assert isinstance( stage, LegoStage )
            assert isinstance( button, QAbstractButton )
            
            if model.get_status( stage ).is_complete:
                button.setIcon( ResourceIcon( path.replace( "black", "green" ) ).icon() )
            elif model.get_status( stage ).requisite_complete:
                button.setIcon( ResourceIcon( path.replace( "black", "red" ) ).icon() )
            else:
                button.setIcon( ResourceIcon( path ).icon() )
    
    
    def add_workflow_menu( self, path, visualisers: Iterator[LegoVisualiser], icon: ResourceIcon ):
        visualisers = list( visualisers )
        
        if len( visualisers ) == 0:
            return
        if len( visualisers ) == 1:
            self.add_action( path, visualiser = visualisers[0], icon = icon )
        else:
            self.add_menu( path, icon = icon )
            for visualiser in visualisers:
                self.add_action( path + [visualiser.name], visualiser = visualiser )
    
    
    def add_action( self, texts: Sequence[str], visualiser = None, icon: ResourceIcon = None, shortcut: int = None, toolbar: QGroupBox = None ):
        menu = self.add_menu( texts[:-1] )
        final = texts[-1]
        
        if final == "-":
            menu.addSeparator()
            
            if toolbar:
                lay: QHBoxLayout = toolbar.layout()
                fra = QFrame()
                fra.setMinimumWidth( 16 )
                fra.setFrameShape( QFrame.VLine )
                fra.setFrameShadow( QFrame.Sunken )
                lay.addWidget( fra )
            return
        elif final == "r":
            self.add_recent( menu )
            return
        
        action = QAction()
        text = texts[-1]
        if "&" not in text:
            text = "&" + text
        action.setText( text )
        
        if visualiser is not None:
            if icon is None and visualiser.icon is not None:
                action.setIcon( visualiser.icon.icon() )
            
            exec_ = VisWrap( self.gui_actions, visualiser )
            action.triggered[bool].connect( exec_.execute )
            self.keep_alive.append( exec_ )
            action.TAG_visualiser = visualiser
        
        if icon is not None:
            action.setIcon( icon.icon() )
        
        if shortcut is not None:
            action.setShortcut( QKeySequence( shortcut ) )
            self.frm_main.addAction( action )
        
        self.keep_alive.append( action )
        menu.addAction( action )
        
        if toolbar:
            lay: QHBoxLayout = toolbar.layout()
            btn = self.__make_button()
            btn.setDefaultAction( action )
            lay.addWidget( btn )
    
    
    def __make_button( self ):
        btn = QToolButton()
        btn.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )
        btn.setIconSize( QSize( 32, 32 ) )
        btn.setMinimumSize( QSize( 64, 64 ) )
        btn.setMaximumSize( QSize( 64, 64 ) )
        return btn
    
    
    def add_recent( self, menu: QMenu ):
        if not global_view.options().recent_files:
            menu.setEnabled( False )
        
        for item in reversed( global_view.options().recent_files ):
            if not isinstance( item, RecentFile ):
                # Legacy data, discard
                continue
            
            action = QAction()
            action.setText( file_helper.get_filename_without_extension( item.file_name ) )
            exec_ = VisWrap( self.gui_actions, gui_workflow.VISUALISERS.ACT_FILE_LOAD_FROM, item.file_name )
            self.keep_alive.append( exec_ )
            action.triggered[bool].connect( exec_.execute )
            self.keep_alive.append( action )
            
            menu.addAction( action )
    
    
    def add_menu( self, texts, headline = None, icon: ResourceIcon = None ):
        menu_path = ""
        menu = self.menu_bar
        
        for text in texts:
            if "&" not in text:
                text = "&" + text
            menu_path += "." + text
            new_menu: QMenu = self.menus.get( menu_path )
            
            if not new_menu:
                new_menu = QMenu()
                new_menu.setTitle( text )
                self.menus[menu_path] = new_menu
                new_menu.aboutToShow.connect( self.__on_menu_about_to_show )
                menu.addMenu( new_menu )
            
            menu = new_menu
        
        if icon is not None:
            menu.setIcon( icon.icon() )
        
        if headline is not None:
            a = QWidgetAction( menu )
            label = QLabel()
            label.setText( "..." )
            label.setSizePolicy( QSizePolicy.Minimum, QSizePolicy.Minimum )
            label.setWordWrap( True )
            label.setStyleSheet( "background:transparent;color:#4040C0;font-weight:bold;font-size:10px;border-bottom:2px groove #C0C0C0;padding-bottom: 4px;" )
            a.setDefaultWidget( label )
            a.TAG_headline = (label, headline, menu)
            menu.addAction( a )
            self.headlines.append( (label, headline, menu) )
        
        return menu
    
    
    def __on_menu_about_to_show( self ):
        menu: QMenu = self.frm_main.sender()
        self.update_dynamic_menu( menu )
    
    
    def update_dynamic_menu( self, menu ):
        self.__update_menu_headline( menu )
        self.__update_menu_checks( menu )
    
    
    def __update_menu_checks( self, menu ):
        for action in menu.actions():
            assert isinstance( action, QAction )
            
            if hasattr( action, "TAG_visualiser" ) and action.TAG_visualiser is not None:
                visualiser: LegoVisualiser = action.TAG_visualiser
                char = " ✔"
                
                if visualiser.is_visible is True:
                    if not action.text().endswith( char ):
                        action.setText( action.text() + char )
                elif visualiser.is_visible is False:
                    if action.text().endswith( char ):
                        action.setText( action.text()[:-len( char )] )
    
    
    def __update_menu_headline( self, menu ):
        for action in menu.actions():
            assert isinstance( action, QAction )
            
            if hasattr( action, "TAG_headline" ) and action.TAG_headline is not None:
                label, fheadline, menu = action.TAG_headline
                txt = str( fheadline( global_view.current_model() ) )
                label.setText( txt )
                label.setToolTip( txt )
                label.setStatusTip( txt )
                label.updateGeometry()
                
                re = QResizeEvent( menu.size(), menu.size() )
                
                QApplication.instance().sendEvent( menu, re )
        
        menu.updateGeometry()
