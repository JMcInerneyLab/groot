from groot.data.lego_model import LegoViewOptions
from groot.frontends.gui.gui_view import LegoView_Model
from intermake import intermake_gui
from mhelper_qt import exqtSlot
from PyQt5.QtWidgets import QDialog, QWidget
from groot.frontends.gui.gui_view_support import EMode, EDomainFunction
from groot.frontends.gui.forms.designer.frm_view_options_designer import Ui_Dialog


class FrmViewOptions( QDialog ):
    def __init__( self,
                  parent: QWidget,
                  options: LegoViewOptions ):
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        
        main = intermake_gui.default_style_sheet()
        self.setStyleSheet( main )
        
        self.options: LegoViewOptions = options
        
        self.map( False )
    
    
    def map( self, reverse ):
        if reverse:
            self.options.domain_function_parameter = self.ui.SPN_DOMAIN_PARAMETER.value()
        else:
            self.ui.SPN_DOMAIN_PARAMETER.setValue( self.options.domain_function_parameter )
        
        self.__map( reverse, self.options, "mode", { EMode.COMPONENT  : self.ui.RAD_MODE_COMPONENT,
                                                     EMode.EDGE       : self.ui.RAD_MODE_EDGE,
                                                     EMode.SEQUENCE   : self.ui.RAD_MODE_GENE,
                                                     EMode.SUBSEQUENCE: self.ui.RAD_MODE_DOMAIN } )
        
        self.__map( reverse, self.options, "domain_function", { EDomainFunction.COMPONENT  : self.ui.RAD_DOMAIN_COMPONENT,
                                                                EDomainFunction.FIXED_COUNT: self.ui.RAD_DOMAIN_FIXEDNUMBER,
                                                                EDomainFunction.FIXED_WIDTH: self.ui.RAD_DOMAIN_FIXEDWIDTH } )
        
        self.__map( reverse, self.options, "move_enabled", { True : self.ui.RAD_MOVE_YES,
                                                             None : self.ui.RAD_MOVE_IND,
                                                             False: self.ui.RAD_MOVE_NO } )
        
        self.__map( reverse, self.options, "view_names", { True : self.ui.RAD_NAME_YES,
                                                           None : self.ui.RAD_NAME_IND,
                                                           False: self.ui.RAD_NAME_NO } )
        
        self.__map( reverse, self.options, "view_piano_roll", { True : self.ui.RAD_PIANO_YES,
                                                                None : self.ui.RAD_PIANO_IND,
                                                                False: self.ui.RAD_PIANO_NO } )
        
        self.__map( reverse, self.options, "view_positions", { True : self.ui.RAD_POS_YES,
                                                               None : self.ui.RAD_POS_IND,
                                                               False: self.ui.RAD_POS_NO } )
        
        self.__map( reverse, self.options, "x_snap", { True : self.ui.RAD_XSNAP_YES,
                                                       None : self.ui.RAD_XSNAP_IND,
                                                       False: self.ui.RAD_XSNAP_NO } )
        
        self.__map( reverse, self.options, "y_snap", { True : self.ui.RAD_YSNAP_YES,
                                                       None : self.ui.RAD_YSNAP_IND,
                                                       False: self.ui.RAD_YSNAP_NO } )
        
        self.__map( reverse, self.options, "view_components", { True : self.ui.RAD_COMPONENTS_YES,
                                                                None : self.ui.RAD_COMPONENTS_IND,
                                                                False: self.ui.RAD_COMPONENTS_NO } )
    
    
    def __map( self, reverse, object_, field, mapping ):
        if reverse:
            for k, v in mapping.items():
                if v.isChecked():
                    setattr( object_, field, k )
                    return
        else:
            value = getattr( object_, field )
            
            for k, v in mapping.items():
                v.setChecked( value == k )
    
    
    @classmethod
    def request( cls, owner_window: QWidget, view: LegoView_Model ):
        form = FrmViewOptions( owner_window, view.options )
        
        if form.exec_():
            return True
        else:
            return False
    
    
    @exqtSlot()
    def on_buttonBox_accepted( self ) -> None:
        """
        Signal handler:
        """
        self.map( True )
    
    
    @exqtSlot()
    def on_buttonBox_rejected( self ) -> None:
        """
        Signal handler:
        """
        pass
