import re

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QAbstractButton, QDialog, QFrame, QGroupBox, QHBoxLayout, QLabel, QMessageBox, QToolButton, QWidget, QSpacerItem, QSizePolicy
from groot.frontends.gui.forms.resources import resources

from groot.data import global_view
from groot.frontends.gui.gui_menu import GuiActions
from groot.frontends.gui.gui_view_utils import ESelect, LegoSelection
from mhelper import virtual
from mhelper_qt import exceptToGui, menu_helper


class FrmBase( QDialog ):
    @exceptToGui()
    def __init__( self, parent: QWidget ):
        from groot.frontends.gui.forms.frm_main import FrmMain
        assert isinstance( parent, FrmMain )
        self.frm_main: FrmMain = parent
        super().__init__( parent )
        
        self.actions: GuiActions = GuiActions( self.frm_main, self )
    
    
    
    
    def on_plugin_completed( self ):
        self.on_refresh_data()
    
    
    def on_refresh_data( self ):
        pass
    
    
    def bind_to_label( self, label: QLabel ):
        label.linkActivated[str].connect( self.actions.by_url )
        label.linkHovered[str].connect( self.actions.show_status_message )
        
        for x in re.findall( 'href="([^"]+)"', label.text() ):
            if not self.actions.by_url( x, validate = True ):
                raise ValueError( "«{}» in the text «{}» in the label «{}».«{}» is not a valid Groot URL.".format( x, label.text(), type( label.window() ), label.objectName() ) )
    
    
    def alert( self, message: str ):
        msg = QMessageBox()
        msg.setText( message )
        msg.setWindowTitle( self.windowTitle() )
        msg.setIcon( QMessageBox.Warning )
        msg.exec_()
    
    
    def get_model( self ):
        return global_view.current_model()
    
    
    def closeEvent( self, event: QCloseEvent ):
        self.frm_main.remove_form( self )
    
    
    def show_menu( self, *args ):
        return menu_helper.show( self.sender(), *args )
    
    
    def show_form( self, form_class ):
        self.frm_main.show_form( form_class )


class FrmSelectingToolbar( FrmBase ):
    def __init__( self, parent: QWidget ):
        super().__init__( parent )
        
        self.selecting_frame: QGroupBox = None
        self.selecting_mode: ESelect = None
        
        self.__selection: LegoSelection = LegoSelection()
        
        self.select_button: QAbstractButton = None
        self.__clear_button: QAbstractButton = None
    
    
    def bind_to_workflow_box( self, frame: QFrame, mode: ESelect ):
        self.selecting_frame = frame
        self.selecting_mode = mode
        frame.setContentsMargins( 0, 0, 0, 8 )
        frame.setProperty( "style", "custom" )
        frame.setStyleSheet( 'QFrame[style="custom"] { border-top: none; border-left: none; border-right: none; border-bottom: 1px dotted gray; }' )
        layout: QHBoxLayout = frame.layout()
        layout.setContentsMargins( 0, 0, 0, 0 )
        
        # Create the select button
        c = QToolButton()
        c.setFixedSize( QSize( 192, 64 ) )
        c.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
        c.setIcon( resources.black_check.icon() )
        c.setIconSize( QSize( 32, 32 ) )
        c.setText( str( self.actions.get_selection() ) )
        c.clicked.connect( self.actions.show_selection )
        # c.setProperty( "style", "combo" )
        c.setStyleSheet( SELECT_STYLE )
        layout.insertWidget( 0, c )
        self.actions.select_button = c
        self.select_button = c
        
        # Create the divider
        c = QFrame()
        c.setFixedWidth( 16 )
        c.setFrameShape( QFrame.VLine )
        c.setFrameShadow( QFrame.Sunken )
        layout.insertWidget( 1, c )
        
        # Create the spacer
        c = QSpacerItem( 1, 1, QSizePolicy.Expanding, QSizePolicy.Minimum )
        layout.addItem( c )
    
    
    def set_selection( self, selection: LegoSelection ):
        self.__selection = selection
        self.handle_selection_changed()
    
    
    def handle_selection_changed( self ):
        self.select_button.setText( str( self.actions.get_selection() ) )
        self.on_selection_changed()
        self.on_refresh_data()
    
    
    @virtual
    def on_selection_changed( self ):
        pass
    
    
    def set_selected( self, item, selected ):
        selection: LegoSelection = self.get_selection()
        existing = item in selection
        
        if selected == existing:
            return
        
        if selected:
            if selection.is_empty() or selection.selection_type() != type( item ):
                self.actions.set_selection( LegoSelection( frozenset( { item } ) ) )
            else:
                self.actions.set_selection( LegoSelection( selection.items.union( { item } ) ) )
        else:
            self.actions.set_selection( LegoSelection( selection.items - { item } ) )
    
    
    def get_selection( self ) -> LegoSelection:
        return self.__selection
    
    
    def show_selection_menu( self ):
        self.select_button.setStyleSheet( MENU_SHOWN_STYLE )
        from groot.frontends.gui import gui_view_utils
        gui_view_utils.show_selection_menu( self.select_button, self.actions, self.selecting_mode )
        self.select_button.setStyleSheet( SELECT_STYLE )


SELECT_STYLE = """
                QToolButton
                {
                color: black;
                background: #FFFFFF;
                border: 1px outset #808080;
                border-radius: 8px;
                }
                
                QToolButton:pressed
                {
                background: #EEEEEE;
                border: 1px inset #808080;
                }
                """

MENU_SHOWN_STYLE = """
                    QToolButton
                    {
                    color: blue;
                    background: #EEEEFF;
                    border: 1px solid black;
                    border-radius: 8px;
                    }
                    """
