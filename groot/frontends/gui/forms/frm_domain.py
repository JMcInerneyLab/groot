from groot.frontends.gui.forms.designer import frm_domain_designer

from groot.frontends.gui.forms.frm_base import FrmBase

from groot import extensions

from groot.frontends.gui.gui_view_support import EDomainFunction
from mhelper import SwitchError
from mhelper_qt import exceptToGui, exqtSlot


class FrmDomain( FrmBase ):
    @exceptToGui()
    def __init__( self, parent ):
        """
        CONSTRUCTOR
        """
        super().__init__( parent )
        self.ui = frm_domain_designer.Ui_Dialog( self )
        self.setWindowTitle( "Domain Editor" )
        
        self.__suspend_updates=False
        
        self.ui.RAD_AUTO.toggled[bool].connect( self.__on_radio_changed )
        self.ui.RAD_EXISTING.toggled[bool].connect( self.__on_radio_changed )
        self.ui.RAD_NO.toggled[bool].connect( self.__on_radio_changed )
        self.ui.RAD_NUM.toggled[bool].connect( self.__on_radio_changed )
        self.ui.RAD_SIZE.toggled[bool].connect( self.__on_radio_changed )
        
        self.update_options()
        
        self.bind_to_label( self.ui.LBL_DATA_WARNING )
        self.bind_to_label( self.ui.LBL_COMPONENT_WARNING )  
        self.bind_to_label( self.ui.LBL_HELP )
        
    
    
    def on_plugin_completed( self ):
        self.__suspend_updates=True
        self.ui.RAD_EXISTING.setChecked(True)
        self.__suspend_updates=False
        self.update_options()
    
    
    def __on_radio_changed( self, _: bool ):
        self.update_options()
    
    
    def update_options( self ):
        if self.__suspend_updates:
            return
        
        self.__suspend_updates=True
        model = self.get_model()
        
        if model.user_domains:
            self.ui.LBL_MAIN.setText( "You currently have {} domains defined.".format( len( model.user_domains ) ) )
            self.ui.RAD_EXISTING.setEnabled( True )
        else:
            self.ui.LBL_MAIN.setText( "You currently have no domains defined." )
            self.ui.RAD_EXISTING.setEnabled( False )
        
        self.ui.LBL_COMPONENT_WARNING.setVisible( self.ui.RAD_AUTO.isChecked() and not model.components )
        self.ui.LBL_DATA_WARNING.setVisible( not model.sequences )
        
        self.ui.RAD_AUTO.setEnabled( bool( model.sequences ) )
        self.ui.RAD_NO.setEnabled( bool( model.sequences ) )
        self.ui.RAD_NUM.setEnabled( bool( model.sequences ) )
        self.ui.RAD_SIZE.setEnabled( bool( model.sequences ) )
        
        self.ui.WID_NUM.setVisible( self.ui.RAD_NUM.isEnabled() and self.ui.RAD_NUM.isChecked() )
        self.ui.WID_SIZE.setVisible( self.ui.RAD_SIZE.isEnabled() and self.ui.RAD_SIZE.isChecked() )
        
        if self.ui.RAD_AUTO.isChecked() and model.sequences and model.components:
            self.ui.BTN_OK.setEnabled( True )
        elif self.ui.RAD_NUM.isChecked() and model.sequences:
            self.ui.BTN_OK.setEnabled( True )
        elif self.ui.RAD_SIZE.isChecked() and model.sequences:
            self.ui.BTN_OK.setEnabled( True )
        elif self.ui.RAD_NO.isChecked() and model.sequences:
            self.ui.BTN_OK.setEnabled( True )
        else:
            self.ui.BTN_OK.setEnabled( False )
            
        self.__suspend_updates=False
    
    
    @exqtSlot()
    def on_BTN_OK_clicked( self ) -> None:
        """
        Signal handler:
        """
        if self.ui.RAD_AUTO.isChecked():
            extensions.ext_generating.create_domains( EDomainFunction.COMPONENT )
        elif self.ui.RAD_NO.isChecked():
            extensions.ext_generating.create_domains( EDomainFunction.NONE )
        elif self.ui.RAD_SIZE.isChecked():
            extensions.ext_generating.create_domains( EDomainFunction.FIXED_WIDTH, self.ui.SPN_SIZE.value() )
        elif self.ui.RAD_NUM.isChecked():
            extensions.ext_generating.create_domains( EDomainFunction.FIXED_COUNT, self.ui.SPN_NUM.value() )
        else:
            raise SwitchError( "radio-selection", None )
