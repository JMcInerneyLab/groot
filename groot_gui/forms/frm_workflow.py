from PyQt5.QtWidgets import QGridLayout, QLabel, QLineEdit, QMenu, QToolButton, QWidget
import groot
from groot_gui.utilities import gui_workflow
from groot_gui.forms.designer import frm_workflow_designer
from groot_gui.forms.frm_base import FrmBase
from groot_gui.utilities.gui_workflow import EIntent, handlers
from mhelper_qt import exceptToGui, exqtSlot, menu_helper


class FrmWorkflow( FrmBase ):
    """
    The workflow screen shows the Groot workflow: the set of stages required to generate
    an n-rooted fusion graph (and a few other stages that are interesting, if not particularly relevant).
    
    For each stage, its current status is displayed, and an option to manipulate or view more data on
    this stage is shown alongside.
    
    If the Wizard is running in interactive mode, the controls to continue or stop the wizard will
    also be shown on this screen. 
    """
    
    INDICATOR_SUFFIX = " margin-top: 2px; margin-bottom: 2px;"
    
    
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_workflow_designer.Ui_Dialog( self )
        self.setWindowTitle( "Workflow" )
        self.bind_to_label( self.ui.LBL_NEXT )
        self.bind_to_label( self.ui.LBL_CLOSE )
        
        self.map = []
        
        for row, stage in enumerate( groot.STAGES ):
            self.add( self.ui.LAY_MAIN, stage, row )
        
        self._refresh_labels()
    
    
    def on_command_completed( self ):
        self._refresh_labels()
    
    
    def _refresh_labels( self ):
        # Wizard
        wt = groot.Wizard.get_active()
        
        if wt is not None and wt.is_paused:
            self.ui.FRA_PAUSED.setVisible( True )
            self.ui.LBL_NEXT.setText( wt.get_stage_name() )
        else:
            self.ui.FRA_PAUSED.setVisible( False )
        
        # Others
        m = groot.current_model()
        
        for stage, indicator, label, box, btn in self.map:
            status = m.get_status( stage )
            
            if status.is_hot:
                indicator.setStyleSheet( "background:red;" + self.INDICATOR_SUFFIX )
            elif status.is_complete:
                indicator.setStyleSheet( "background:green;" + self.INDICATOR_SUFFIX )
            elif status.is_partial:
                indicator.setStyleSheet( "background:orange;" + self.INDICATOR_SUFFIX )
            else:
                indicator.setStyleSheet( "background:silver;" + self.INDICATOR_SUFFIX )
            
            box.setText( str( status ) )
    
    
    def add( self, layout: QGridLayout, stage: groot.Stage, row ):
        indicator = QWidget()
        indicator.setMinimumWidth( 4 )
        indicator.setMaximumWidth( 4 )
        indicator.setStyleSheet( "background:blue; " + self.INDICATOR_SUFFIX )
        layout.addWidget( indicator, row, 0 )
        
        label = QLabel()
        label.setText( stage.name )
        layout.addWidget( label, row, 1 )
        
        box = QLineEdit()
        box.setReadOnly( True )
        layout.addWidget( box, row, 2 )
        
        btn = QToolButton()
        btn.setText( "▼" )
        btn.clicked[bool].connect( self.__on_btn_clicked )
        layout.addWidget( btn, row, 3 )
        
        self.map.append( (stage, indicator, label, box, btn) )
    
    
    def __show_menu( self, menu: QMenu ):
        control: QToolButton = self.sender()
        ot = control.text()
        control.setText( menu.title() )
        control.parent().updateGeometry()
        menu_helper.show_menu( self, menu )
        control.setText( ot )
    
    
    @exceptToGui()
    def __on_btn_clicked( self, _ ) -> None:
        """
        Signal handler:
        """
        sender = self.sender()
        
        for stage, indicator, label, box, btn in self.map:
            if btn is sender:
                self.actions.menu( stage )
    
    
    @exqtSlot()
    def on_BTN_CONTINUE_clicked( self ) -> None:
        """
        Signal handler:
        """
        handlers().ACT_WIZARD_NEXT.execute( self, EIntent.DIRECT, None )
        
    @exqtSlot()
    def on_BTN_HELP_clicked(self) -> None:
        """
        Signal handler:
        """
        self.actions.show_my_help()
            