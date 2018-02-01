from typing import Optional

from PyQt5.QtWidgets import QMessageBox

from groot.data.lego_model import LegoSequence, LegoEdge, LegoSubsequence


"""
Main form
"""
import sip
from typing import Any, List, Optional, Sequence, Set, cast

from PyQt5.QtCore import QCoreApplication, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from PyQt5.QtWidgets import QAction, QFileDialog, QFrame, QGraphicsScene, QGridLayout, QInputDialog, QMainWindow, QMessageBox, QPushButton, QSizePolicy, QTextEdit, QVBoxLayout, QWidget
from groot.frontends.gui.forms.designer.frm_main_designer import Ui_MainWindow

import groot.extensions as COMMANDS
from groot import constants
from groot.algorithms import fastaiser, layout
from groot.data import global_view, user_options
from groot.data.lego_model import ILegoVisualisable, LegoComponent
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.forms.frm_view_options import FrmViewOptions
from groot.frontends.gui.gui_view import EMode, ESelect, ILegoViewModelObserver, LegoView_Model
from groot.frontends.gui.gui_view_utils import EChanges, MyView
from intermake import AsyncResult, MENV, Plugin, intermake_gui
from intermake.engine.plugin_arguments import ArgsKwargs
from intermake.hosts.frontends.gui_qt.frm_arguments import FrmArguments
from intermake.hosts.gui import IGuiPluginHostWindow
from mhelper import SwitchError, ansi, array_helper, file_helper, string_helper, NOT_PROVIDED
from mhelper_qt import qt_gui_helper, menu_helper
from mhelper_qt.qt_gui_helper import exceptToGui, exqtSlot


class FrmMain( QMainWindow, ILegoViewModelObserver, IGuiPluginHostWindow ):
    """
    Main window
    """
    
    
    
    
    
    
    
    class __on__check_box:
        def __init__( self, form: "FrmMain", entity: ILegoVisualisable ):
            self.form = form
            self.entity = entity
        
        
        def call( self, _: bool ):
            self.form.model_view.select_entity( self.entity )
    
    
    def ILegoViewModelObserver_options_changed( self ):
        self.update_ui_from_options()
    
    
    def closeEvent( self, *args, **kwargs ):
        """
        OVERRIDE
        Fixes crash on exit on Windows
        """
        exit()
    
    
    def __ask_for_one( self, array ) -> Optional[object]:
        if not array:
            QMessageBox.information( self, self.windowTitle(), "Make a valid selection first." )
            return None
        
        if len( array ) == 1:
            return next( iter( array ) )
        
        item, ok = QInputDialog.getItem( self, self.windowTitle(), "Select", [str( x ) for x in array] )
        
        if not ok:
            return None
        
        for x in array:
            if str( x ) == item:
                return x
        
        return None
    
    
    @staticmethod
    def __query_remove( items: Set[object] ) -> bool:
        first = array_helper.first_or_none( items )
        
        if first is None:
            return False
        
        type_name = type( first ).__name__[4:] + "s"
        message = "This will remove {} {}.".format( len( items ), type_name )
        details = "* " + "\n* ".join( str( x ) for x in items )
        message_box = QMessageBox()
        message_box.setText( message )
        message_box.setDetailedText( details )
        message_box.setStandardButtons( QMessageBox.Yes | QMessageBox.No )
        x = message_box.exec_()
        return x == QMessageBox.Yes
    
    
    
    
    
    
    
    
    
    
    
    


# endregion
