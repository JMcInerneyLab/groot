import re
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QDialog, QMessageBox, QWidget, QPushButton, QLabel, QToolButton, QGroupBox, QMenu, QAction
from typing import Tuple

from groot.frontends.gui.gui_menu import GuiActions
from groot.constants import EWorkflow
from groot.data import global_view
from groot.frontends.gui.gui_view_utils import LegoSelection
from groot.frontends.gui.gui_workflow import LegoVisualiser, LegoStage, EIntent
from groot.frontends.gui.forms.resources import resources
from intermake.engine.environment import MCMD
from mhelper import virtual
from mhelper_qt import menu_helper, exceptToGui


class FrmBase( QDialog ):
    @exceptToGui()
    def __init__( self, parent: QWidget ):
        from groot.frontends.gui.forms.frm_main import FrmMain
        assert isinstance( parent, FrmMain )
        self.frm_main: FrmMain = parent
        super().__init__( parent )
        
        self.actions: GuiActions = GuiActions( self.frm_main, self )
        self.__select_button: QPushButton = None
        self.__workflow_frame: QGroupBox = None
        self.__workflow_workflow: QToolButton = None
        self.__workflow_create: QToolButton = None
        self.__workflow_remove: QToolButton = None
        self.__workflow_view: QToolButton = None
        self.__workflow_options: Tuple[EWorkflow, ...] = None
        self.__workflow_selected: LegoStage = None
    
    
    @property
    def select_button( self ):
        return self.__select_button
    
    
    @property
    def workflow( self ) -> LegoStage:
        return self.__workflow_selected
    
    
    def set_parameters( self, *parameters ):
        if len( parameters ) > 0 and isinstance( parameters[0], LegoStage ):
            if self.__workflow_options and parameters[0] in self.__workflow_options:
                assert isinstance( parameters[0], LegoStage )
                self.__workflow_selected = parameters[0]
                self.update_workflow_selected()
    
    
    def on_plugin_completed( self ):
        self.on_refresh_data()
    
    
    def on_selection_changed( self ):
        pass
    
    
    def selection_changed( self ):
        if self.__select_button is not None:
            self.__select_button.setText( str( self.actions.get_selection() ) )
        
        self.on_selection_changed()
        self.on_refresh_data()
    
    
    def on_refresh_data( self ):
        pass
    
    
    def bind_to_workflow_box( self,
                              frame: QGroupBox,
                              workflow: QToolButton,
                              create: QToolButton,
                              remove: QToolButton,
                              view: QToolButton,
                              visualiser: LegoVisualiser,
                              selected: LegoStage ):
        assert isinstance( selected, LegoStage )
        self.__workflow_frame = frame
        self.__workflow_workflow = workflow
        self.__workflow_create = create
        self.__workflow_remove = remove
        self.__workflow_view = view
        self.__workflow_options = visualiser.intents[EIntent.VIEW]
        self.__workflow_selected = selected
        
        frame.setTitle( "Workflow" )
        workflow.setIcon( resources.workflow.icon() )
        workflow.clicked.connect( self.__on_workflow_workflow_clicked )
        create.clicked.connect( self.__on_workflow_create_clicked )
        remove.clicked.connect( self.__on_workflow_remove_clicked )
        view.clicked.connect( self.__on_workflow_view_clicked )
        workflow.setProperty( "style", "combo" )
        view.setVisible( False )
        self.update_workflow_selected()
    
    
    def update_workflow_selected( self ):
        self.__workflow_workflow.setText( self.get_workflow_name( self.__workflow_selected ) )
        
        if self.__select_button:
            self.__select_button.setIcon( self.workflow.icon.icon() )
        
        self.actions.set_selection( LegoSelection() )
        self.on_refresh_data()
    
    
    @virtual
    def on_workflow_changed( self ):
        pass
    
    
    def __on_workflow_workflow_clicked( self ):
        menu = QMenu()
        actions = []
        
        for stage in self.__workflow_options:
            assert isinstance( stage, LegoStage )
            
            action = QAction()
            actions.append( action )
            action.setText( stage.name )
            action.setIcon( stage.icon.icon() )
            action.TAG_item = stage
            
            if stage == self.__workflow_selected:
                action.setCheckable( True )
                action.setChecked( True )
            
            menu.addAction( action )
        
        ot = self.__workflow_workflow.text()
        self.__workflow_workflow.setText( "Workflow" )
        selected = menu_helper.show_menu( self, menu )
        self.__workflow_workflow.setText( ot )
        
        if selected is None:
            return
        
        assert isinstance( selected, QAction )
        assert hasattr( selected, "TAG_item" )
        
        self.__workflow_selected = selected.TAG_item
        self.update_workflow_selected()
    
    
    def get_workflow_name( self, item ):
        return MCMD.host.translate_name( item.name.split( "_" )[0].lower() )
    
    
    def __on_workflow_create_clicked( self ):
        self.actions.launch_intent( self.__workflow_selected, EIntent.CREATE )
    
    
    def __on_workflow_remove_clicked( self ):
        self.actions.launch_intent( self.__workflow_selected, EIntent.DROP )
    
    
    def __on_workflow_view_clicked( self ):
        pass
    
    
    def bind_to_label( self, label: QLabel ):
        label.linkActivated[str].connect( self.actions.by_url )
        label.linkHovered[str].connect( self.actions.show_status_message )
        
        for x in re.findall( 'href="([^"]+)"', label.text() ):
            if not self.actions.by_url( x, validate = True ):
                raise ValueError( "«{}» in the text «{}» in the label «{}».«{}» is not a valid Groot URL.".format( x, label.text(), type( label.window() ), label.objectName() ) )
    
    
    def bind_to_select( self, button: QPushButton ):
        self.__select_button = button
        button.setText( str( self.actions.get_selection() ) )
        button.clicked.connect( self.actions.show_selection )
        button.setProperty( "style", "combo" )
        self.actions.select_button = button
    
    
    def alert( self, message: str ):
        msg = QMessageBox()
        msg.setText( message )
        msg.setWindowTitle( self.windowTitle() )
        msg.setIcon( QMessageBox.Warning )
        msg.exec_()
    
    
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
        return global_view.current_selection()
    
    
    def get_model( self ):
        return global_view.current_model()
    
    
    def closeEvent( self, event: QCloseEvent ):
        self.frm_main.remove_form( self )
    
    
    def show_menu( self, *args ):
        return menu_helper.show( self.sender(), *args )
    
    
    def show_form( self, form_class ):
        self.frm_main.show_form( form_class )
