from typing import Any, Optional, Callable, List, Iterable

from PyQt5.QtCore import pyqtSlot, Qt
from PyQt5.QtWidgets import QDialog, QTreeWidgetItem, QDialogButtonBox

from mhelper import qt_gui_helper as QtGuiHelper

from groot.frontends.gui.forms.designer.frm_list_selector_designer import Ui_Dialog


class FrmListSelector( QDialog ):
    def __init__( self, parent, message: Any, options: Iterable[ Any ], constraint: Optional[ Callable[ [ List[ Any ] ], bool ] ] ):
        """
        CONSTRUCTOR
        :param parent:          Parent form 
        :param options:         Options to show
        :param constraint:      Optional constraint on selection (callable on list of selected items)
        """
        QDialog.__init__( self, parent )
        self.ui = Ui_Dialog( self )
        
        self.ui.LBL_MESSAGE.setText( str( message ) )
        
        self.constraint = constraint
        
        for x in options:
            item = QTreeWidgetItem()
            item.setText( 0, str( x ) )
            item.setData( 0, Qt.UserRole, x )
            self.ui.TVW_LEFT.addTopLevelItem( item )
    
    
    @staticmethod
    def request( parent, message: Any, options: Iterable[ Any ], constraint: Optional[ Callable[ [ List[ Any ] ], bool ] ] ):
        """
        Shows the form with the specified options.
        See `__init__` for parameter details.
        :return: Returns the selected options, or `None` if cancelled.
        """
        form = FrmListSelector( parent, message, options, constraint )
        
        if form.exec():
            return form.__selected_items()
        else:
            return None
    
    
    @pyqtSlot()
    def on_BTN_REMOVE_ONE_clicked( self ) -> None:
        """
        Signal handler:
        """
        QtGuiHelper.move_treeview_items( self.ui.TVW_RIGHT, self.ui.TVW_LEFT, True )
        self.__items_changed()
    
    
    @pyqtSlot()
    def on_BTN_REMOVE_ALL_clicked( self ) -> None:
        """
        Signal handler:
        """
        QtGuiHelper.move_treeview_items( self.ui.TVW_RIGHT, self.ui.TVW_LEFT, False )
        self.__items_changed()
    
    
    @pyqtSlot()
    def on_BTN_ADD_clicked( self ) -> None:
        """
        Signal handler:
        """
        QtGuiHelper.move_treeview_items( self.ui.TVW_LEFT, self.ui.TVW_RIGHT, True )
        self.__items_changed()
    
    
    @pyqtSlot()
    def on_BTN_ADD_ALL_clicked( self ) -> None:
        """
        Signal handler:
        """
        QtGuiHelper.move_treeview_items( self.ui.TVW_LEFT, self.ui.TVW_RIGHT, False )
        self.__items_changed()
    
    
    def __selected_items( self ):
        result = [ ]
        
        for index in range( self.ui.TVW_RIGHT.topLevelItemCount() ):
            item = self.ui.TVW_RIGHT.topLevelItem( index )  # type:QTreeWidgetItem
            data = item.data( 0, Qt.UserRole )
            result.append( data )
        
        return result
    
    
    def __items_changed( self ):
        if self.constraint is None:
            return
        
        enabled = self.constraint( self.__selected_items() )
        
        self.ui.BTNBOX_MAIN.button( QDialogButtonBox.Ok ).setEnabled( enabled )
    
    
    @pyqtSlot()
    def on_BTNBOX_MAIN_accepted( self ) -> None:
        """
        Signal handler:
        """
        self.accept()
    
    
    @pyqtSlot()
    def on_BTNBOX_MAIN_rejected( self ) -> None:
        """
        Signal handler:
        """
        self.reject()
