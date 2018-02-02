from PyQt5.QtWidgets import QDialog, QWidget
from groot.frontends.gui.forms.designer.frm_view_options_designer import Ui_Dialog

from groot.data.lego_model import LegoViewOptions
from groot.frontends.gui.forms.frm_base import FrmBase
from intermake import intermake_gui


class FrmViewOptions( FrmBase ):
    def __init__( self, parent: QWidget ):
        """
        CONSTRUCTOR
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        
        main = intermake_gui.default_style_sheet()
        self.setStyleSheet( main )
        
        self.options: LegoViewOptions = self.get_model().ui_options
        
        self.map( False )
        
        radios = (self.ui.RAD_COMPONENTS_IND,
                  self.ui.RAD_COMPONENTS_NO,
                  self.ui.RAD_COMPONENTS_YES,
                  self.ui.RAD_MOVE_IND,
                  self.ui.RAD_MOVE_NO,
                  self.ui.RAD_MOVE_YES,
                  self.ui.RAD_NAME_IND,
                  self.ui.RAD_NAME_NO,
                  self.ui.RAD_NAME_YES,
                  self.ui.RAD_PIANO_IND,
                  self.ui.RAD_PIANO_NO,
                  self.ui.RAD_PIANO_YES,
                  self.ui.RAD_POS_IND,
                  self.ui.RAD_POS_NO,
                  self.ui.RAD_POS_YES,
                  self.ui.RAD_XSNAP_IND,
                  self.ui.RAD_XSNAP_NO,
                  self.ui.RAD_XSNAP_YES,
                  self.ui.RAD_YSNAP_IND,
                  self.ui.RAD_YSNAP_NO,
                  self.ui.RAD_YSNAP_YES)
        
        for rad in radios:
            rad.toggled[bool].connect( self.__on_radio_changed )
    
    
    def __on_radio_changed( self, _: bool ):
        self.map( True )
    
    
    def map( self, reverse ):
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
@exqtSlot()
            def on_BTN_CLEAR_RECENT_clicked(self) -> None:
                """
                Signal handler:
                """
                pass
            
@exqtSlot()
            def on_BTN_VISJS_clicked(self) -> None:
                """
                Signal handler:
                """
                pass
            
@exqtSlot()
            def on_BTN_INTERMAKE_ADVANCED_clicked(self) -> None:
                """
                Signal handler:
                """
                pass
            