import re
import warnings
from typing import Union

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QAction, QDialog, QFrame, QLabel, QMessageBox, QToolButton, QWidget
from groot_gui.forms.resources import resources

import mhelper
import mhelper as mh
import mhelper_qt as qt
from groot.data import global_view
from groot_gui.utilities.gui_menu import GuiActions
from groot_gui.utilities.gui_workflow import EIntent, Intent, IntentHandler, handlers
from groot_gui.utilities.selection import show_selection_menu


class FrmBase( QDialog ):
    """
    This is the base class for Groot dialogues.
    
    Its main functions are to construct `self.actions` and define `on_apply_request` and `on_command_completed`. 
    """
    handler_info: IntentHandler = None
    
    
    @qt.exceptToGui()
    def __init__( self, parent: QWidget ):
        from groot_gui.forms.frm_main import FrmMain
        assert isinstance( parent, FrmMain )
        self.frm_main: FrmMain = parent
        super().__init__( parent )
        
        self.actions: GuiActions = GuiActions( self.frm_main, self )
        
        handles = self.handler_info.handles[EIntent.INSPECT]
        
        if handles:
            self.selecting_mode = Union[handles]
        else:
            self.selecting_mode = None
    
    
    @mh.virtual
    def on_apply_request( self, request: Intent ):
        """
        Groot forms display _non-modally_, therefore requests to display certain
        data are handled through this function, rather than `__init__`.
          
        The derived class should implement this function to fulfill the request.
        """
        if request.is_inspect:
            self.on_inspect( request.target )
    
    
    @mh.virtual
    def on_inspect( self, item: object ):
        pass
    
    
    def on_command_completed( self ):
        """
        The Groot main form calls this on all dialogues when a command completes.
        
        The derived class should implement this function to respond to the command.
        
        ¡¡¡Overriding this is now obsolete!!!
        Intermake now allows the callback to be hooked via `AsyncResult.listen`
        """
        self.refresh_data()
    
    
    def refresh_data( self ):
        """
        Updates the displayed data.
        """
        self.on_refresh_data()
    
    
    def on_refresh_data( self ):
        """
        This is called whenever the model changes.
        
        The derived class should update its display accordingly.
        """
        pass
    
    
    def bind_to_label( self, label: QLabel ):
        label.linkActivated[str].connect( self.actions.by_url )
        label.linkHovered[str].connect( self.actions.show_status_message )
        
        for x in re.findall( 'href="([^"]+)"', label.text() ):
            if not self.actions.by_url( x, validate = True ):
                warnings.warn( "«{}» in the text «{}» in the label «{}».«{}» is not a valid Groot URL.".format( x, label.text(), type( label.window() ), label.objectName() ), UserWarning )
    
    
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
        return qt.menu_helper.show_menu( self, *args )
    
    
    def inspect_elsewhere( self, tgt ):
        if tgt is None:
            return
        
        if mh.array_helper.is_simple_iterable( tgt ):
            if len( tgt ) == 1:
                tgt = mhelper.array_helper.single( tgt )
            else:
                tgt = self.show_menu( *tgt )
                
                if tgt is None:
                    return
        
        handlers_ = handlers().list_avail( EIntent.INSPECT, type( tgt ) )
        menu = qt.QMenu()
        acm = { }
        
        qt.menu_helper.add_section( menu, "{}: {}".format( type( tgt ).__name__, str( tgt ) ) )
        
        for handler in handlers_:
            act = QAction()
            menu.addAction( act )
            acm[act] = handler
            act.setText( handler.name )
            if handler.icon:
                act.setIcon( handler.icon.icon() )
        
        act = self.show_menu( menu )
        
        if act is None:
            return
        
        acm[act].execute( self, EIntent.INSPECT, tgt )
    
    
    def add_select_button( self, frame: QFrame ):
        # Create the select button
        c = QToolButton()
        c.setIconSize( QSize( 32, 32 ) )
        c.setText( "Find" )
        self.on_style_select_button( c )
        c.clicked.connect( self.on_show_selection_menu )
        frame.layout().insertWidget( 0, c )
    
    
    def on_style_select_button( self, c ):
        c.setFixedSize( QSize( 64, 64 ) )
        c.setToolButtonStyle( Qt.ToolButtonTextUnderIcon )
        c.setIcon( resources.find.icon() )
    
    
    def on_show_selection_menu( self ):
        choice = show_selection_menu( self.sender(), None, self.selecting_mode )
        
        if choice is not None:
            self.on_apply_request( Intent( self, EIntent.INSPECT, choice ) )


class FrmBaseWithSelection( FrmBase ):
    """
    Extends `FrmBase` by maintaining a persistent selection.
    
        * Access the selection through the `selection` property
        * A unique style is applied to the "select button" created by `add_select_button`
        * When the selection property changes, so does the text on the "select button"
        * When an INSPECT intent arrives the selection is changed 
    """
    
    
    def __init__( self, parent: QWidget ):
        super().__init__( parent )
        
        if not self.handler_info.handles[EIntent.INSPECT]:
            raise mh.LogicError( "This dialogue, {}, has a selection toolbar, but no EIntent.INSPECT has been registered designating what exactly this dialogue is able to handle.".format( type( self ) ) )
        
        self.__selection: object = None
        self.__select_button: qt.QAbstractButton = None
    
    
    def on_style_select_button( self, c ):
        """
        OVERRIDES base to provide unique style
        """
        c.setFixedSize( QSize( 192, 64 ) )
        c.setToolButtonStyle( Qt.ToolButtonTextBesideIcon )
        c.setIcon( resources.black_check.icon() )
        c.setStyleSheet( SELECT_STYLE )
        self.__select_button = c
    
    
    def on_show_selection_menu( self ):
        """
        OVERRIDES base to provide unique style
        """
        self.sender().setStyleSheet( MENU_SHOWN_STYLE )
        
        choice = show_selection_menu( self.sender(), self.selection, self.selecting_mode )
        
        if choice is not None:
            self.on_apply_request( Intent( self, EIntent.INSPECT, choice ) )
        
        self.sender().setStyleSheet( SELECT_STYLE )
    
    
    def inspect_elsewhere( self, target = None ):
        """
        OVERRIDES base to allow `target` to default to the current selection
        """
        if target is None:
            target = self.selection
        
        super().inspect_elsewhere( target )
    
    
    def on_inspect( self, item: object ):
        """
        OVERRIDES base to set the new selection
        """
        self.__selection = item
        self.__select_button.setText( str( self.__selection ) )
    
    
    def get_selection( self ) -> object:
        warnings.warn( "Deprecated - use selection", DeprecationWarning )
        return self.__selection
    
    
    @property
    def selection( self ):
        """
        Retrieves the selection.
        Note this cannot be set directly - raise an INSPECT intent to do this. 
        """
        return self.__selection


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
