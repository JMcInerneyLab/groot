from typing import Iterator, Sequence

from PyQt5.QtCore import Qt, QSize
from PyQt5.QtGui import QResizeEvent, QKeySequence
from PyQt5.QtWidgets import QAction, QApplication, QLabel, QMainWindow, QMenu, QMenuBar, QSizePolicy, QWidgetAction, QGroupBox, QHBoxLayout, QFrame, QToolButton, QAbstractButton

from groot import constants
from groot.constants import STAGES, Stage
from mhelper import file_helper, ResourceIcon
from groot_gui.utilities import gui_workflow
from groot.data import global_view
from groot.data.global_view import RecentFile
from groot_gui.utilities.gui_workflow import EIntent, IntentHandler, handlers
from groot_gui.utilities.gui_actions import GuiActions
from groot_gui.forms.resources import resources


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
    """
    Combines a `IntentHandler` and its `GuiActions` owner, allowing it to be executed asynchronously from the owner.
    """
    
    
    def __init__( self, owner: GuiActions, handler: IntentHandler ):
        self.owner = owner
        self.handler = handler
    
    
    def execute( self, _: bool ) -> None:
        self.handler.execute( self.owner.window, EIntent.DIRECT, None )


class _RecentFileSlot:
    def __init__( self, owner: GuiActions, file_name: str ):
        self.owner = owner
        self.file_name = file_name
    
    
    def execute( self, _: bool ) -> None:
        self.owner.load_file_from( self.file_name )


class StageWrap:
    def __init__( self, owner: GuiActions, stage: Stage ):
        self.owner = owner
        self.stage = stage
    
    
    def execute( self, _: bool ) -> None:
        self.owner.menu( self.stage )


class GuiMenu:
    def __init__( self, frm_main: QMainWindow ):
        from groot_gui.forms.frm_main import FrmMain
        assert isinstance( frm_main, FrmMain )
        ui = frm_main.ui
        vis = gui_workflow.handlers()
        
        self.frm_main: FrmMain = frm_main
        self.menu_bar: QMenuBar = self.frm_main.menuBar()
        self.menus = { }
        self.keep_alive = []
        self.headlines = []
        self.stages = { }
        self.workflow_buttons = []
        self.gui_actions: GuiActions = GuiActions( self.frm_main, self.frm_main )
        
        self.mnu_file = self.add_menu( ["File"], headline = lambda m: constants.STAGES._FILE_0.headline( m ) )
        self.add_action( ["File", "New"], handler = vis.ACT_FILE_NEW, toolbar = ui.FRA_FILE )
        self.add_action( ["File", "Open..."], handler = vis.VIEW_OPEN_FILE, toolbar = ui.FRA_FILE )
        self.add_action( ["File", "Recent", "r"] )
        self.add_action( ["File", "-"] )
        self.add_action( ["File", "Save"], handler = vis.ACT_FILE_SAVE, toolbar = ui.FRA_FILE )
        self.add_action( ["File", "Save &as..."], handler = vis.VIEW_SAVE_FILE )
        self.add_action( ["File", "-"] )
        self.add_action( ["File", "E&xit"], handler = vis.ACT_EXIT )
        
        for stage in STAGES:
            self.add_workflow( stage )
        
        self.mnu_windows = self.add_menu( ["Windows"] )
        self.add_action( ["Windows", "&Workflow..."], handler = vis.VIEW_WORKFLOW, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "&Wizard..."], handler = vis.VIEW_WIZARD, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "&Preferences..."], handler = vis.VIEW_PREFERENCES, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "-"], toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Visualisers", "Reports..."], handler = vis.VIEW_TEXT, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Visualisers", "Lego..."], handler = vis.VIEW_LEGO, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Visualisers", "Alignments..."], handler = vis.VIEW_ALIGNMENT, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Visualisers", "Fusions..."], handler = vis.VIEW_FUSIONS, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Visualisers", "Splits..."], handler = vis.VIEW_SPLITS, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Visualisers", "Genes..."], handler = vis.VIEW_GENES, toolbar = ui.FRA_VISUALISERS )
        self.add_action( ["Windows", "Editors", "Trees..."], handler = vis.CREATE_TREES )
        self.add_action( ["Windows", "Editors", "Alignment..."], handler = vis.CREATE_ALIGNMENTS )
        self.add_action( ["Windows", "Editors", "Domains..."], handler = vis.CREATE_DOMAINS )
        self.add_action( ["Windows", "Editors", "Subgraphs..."], handler = vis.CREATE_SUBGRAPHS )
        self.add_action( ["Windows", "Others", "File open..."], handler = vis.VIEW_OPEN_FILE )
        self.add_action( ["Windows", "Others", "File save..."], handler = vis.VIEW_SAVE_FILE )
        self.add_action( ["Windows", "Others", "Startup..."], handler = vis.VIEW_STARTUP )
        self.add_action( ["Windows", "Others", "Version..."], handler = vis.VIEW_ABOUT )
        self.add_action( ["Windows", "Others", "Intermake..."], handler = vis.VIEW_INTERMAKE, shortcut = Qt.Key_F12 )
        
        self.mnu_help = self.add_menu( ["Help"] )
        self.add_action( ["Help", "&Usage..."], handler = vis.VIEW_MY_HELP )
        self.add_action( ["Help", "&Readme (online)..."], handler = vis.VIEW_HELP )
        self.add_action( ["Help", "&About..."], handler = vis.VIEW_ABOUT )
    
    
    def add_workflow( self, stage: Stage ):
        assert isinstance( stage, Stage ), stage
        
        path = ["Workflow", stage.name]
        mnu = self.add_menu( path, headline = stage.headline )
        
        self.add_workflow_menu( path + ["Create"], handlers().list_avail( EIntent.CREATE, stage ), icon = resources.create )
        self.add_workflow_menu( path + ["Drop"], handlers().list_avail( EIntent.DROP, stage ), icon = resources.remove )
        self.add_workflow_menu( path + ["View"], handlers().list_avail( EIntent.VIEW, stage ), icon = resources.view )
        
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
            assert isinstance( stage, Stage ), stage
            assert isinstance( button, QAbstractButton )
            
            if model.get_status( stage ).is_complete:
                button.setIcon( ResourceIcon( path.replace( "black", "green" ) ).icon() )
            elif model.get_status( stage ).requisite_complete:
                button.setIcon( ResourceIcon( path.replace( "black", "red" ) ).icon() )
            else:
                button.setIcon( ResourceIcon( path ).icon() )
    
    
    def add_workflow_menu( self, path, visualisers: Iterator[IntentHandler], icon: ResourceIcon ):
        visualisers = list( visualisers )
        
        if len( visualisers ) == 0:
            return
        if len( visualisers ) == 1:
            self.add_action( path, handler = visualisers[0], icon = icon )
        else:
            self.add_menu( path, icon = icon )
            
            for visualiser in visualisers:
                self.add_action( path + [visualiser.name], handler = visualiser )
    
    
    def add_action( self, texts: Sequence[str], handler: IntentHandler = None, icon: ResourceIcon = None, shortcut: int = None, toolbar: QGroupBox = None ):
        """
        Adds an action to the menu.
        
        :param texts:           Path to menu item 
        :param handler:      Action to perform 
        :param icon:            Menu icon
        :param shortcut:        Shortcut key
        :param toolbar:         Toolbar to a shortcut button to
        """
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
        
        if handler is not None:
            if icon is None and handler.icon is not None:
                action.setIcon( handler.icon.icon() )
            
            exec_ = VisWrap( self.gui_actions, handler )
            action.triggered[bool].connect( exec_.execute )
            self.keep_alive.append( exec_ )
            action.TAG_visualiser = handler
        
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
            exec_ = _RecentFileSlot( self.gui_actions, item.file_name )
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
                visualiser: IntentHandler = action.TAG_visualiser
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
