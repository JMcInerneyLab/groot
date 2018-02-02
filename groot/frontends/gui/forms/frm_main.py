from typing import Dict, Type

from PyQt5.QtCore import QCoreApplication, Qt
from PyQt5.QtGui import QCloseEvent, QColor
from PyQt5.QtWidgets import QMainWindow, QMdiSubWindow
from groot.frontends.gui.forms.designer import frm_main_designer

from groot.data import global_view
from groot.frontends.gui.forms.frm_base import FrmBase
from groot.frontends.gui.gui_view_utils import EChanges
from intermake import AsyncResult, IGuiPluginHostWindow, intermake_gui
from intermake.engine.environment import MENV
from mhelper import file_helper, SwitchError
from mhelper_qt import exceptToGui, qt_gui_helper


class FrmMain( QMainWindow, IGuiPluginHostWindow ):
    """
    Main window
    """
    
    
    @exceptToGui()
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        # QT stuff
        QCoreApplication.setAttribute( Qt.AA_DontUseNativeMenuBar )
        QMainWindow.__init__( self )
        self.ui = frm_main_designer.Ui_MainWindow()
        self.ui.setupUi( self )
        self.setWindowTitle( "Lego Model Creator" )
        self.setStyleSheet( intermake_gui.default_style_sheet() )
        
        self._mdi: Dict[Type[FrmBase], FrmBase] = { }
        
        self.COLOUR_EMPTY = QColor( intermake_gui.parse_style_sheet().get( 'QMdiArea[style="empty"].background', "#C0C0C0" ) )
        self.COLOUR_NOT_EMPTY = QColor( intermake_gui.parse_style_sheet().get( 'QMdiArea.background', "#C0C0C0" ) )
        
        self.ui.MDI_AREA.setBackground( self.COLOUR_EMPTY )
        self.ui.MDI_AREA.setVisible( False )
        
        self.showMaximized()
        
        self.mdi_mode = False
        
        global_view.subscribe_to_selection_changed( self.on_selection_changed )
        
        from groot.frontends.gui.gui_menu import GuiMenu
        self.actions = GuiMenu( self )
        
        txt = self.ui.LBL_FIRST_MESSAGE.text()
        
        txt = txt.replace( "$(VERSION)", MENV.version )
        r = []
        
        r.append( "<h3>Recent files</h3><ul>" )
        
        for file in reversed( global_view.options().recent_files ):
            r.append( '<li><a href="load_file:{}">{}</a></li>'.format( file, file_helper.get_filename_without_extension( file ) ) )
        
        r.append( '<li><a href="action:browse_open"><i>browse...</i></a></li>' )
        r.append( "</ul>" )
        
        r.append( "<h3>Sample data</h3><ul>" )
        
        for file in global_view.get_samples():
            r.append( '<li><a href="load_sample:{}">{}</a><li/>'.format( file, file_helper.get_filename_without_extension( file ) ) )
        
        r.append( '<li><a href="action:show_samples_form"><i>browse...</i></a></li>' )
        r.append( "</ul>" )
        
        txt = txt.replace( "$(RECENT_FILES)", "\n".join( r ) )
        
        self.ui.LBL_FIRST_MESSAGE.setText( txt )
        self.actions.gui_actions.bind_to_label( self.ui.LBL_FIRST_MESSAGE )
    
    
    def closeEvent( self, e: QCloseEvent ):
        global_view.unsubscribe_from_selection_changed( self.on_selection_changed )
    
    
    def on_selection_changed( self ):
        for form in self.iter_forms():
            form.on_selection_changed()
    
    
    def plugin_completed( self, result: AsyncResult ) -> None:
        self.actions.gui_actions.dismiss_startup_screen()
        self.statusBar().showMessage( str( result ) )
        
        if result.is_error:
            qt_gui_helper.show_exception( self, "The operation did not complete.", result.exception )
        elif result.is_success and isinstance( result.result, EChanges ):
            for form in self.iter_forms():
                print( form )
                form.on_plugin_completed( result.result )
    
    
    def iter_forms( self ):
        return [x for x in self._mdi.values() if isinstance( x, FrmBase )]
    
    
    def remove_form( self, form ):
        del self._mdi[type( form )]
        
        if not self._mdi:
            self.ui.MDI_AREA.setBackground( self.COLOUR_EMPTY )
    
    
    def close_form( self, form: FrmBase ):
        if self.mdi_mode:
            form.parentWidget().close()
        else:
            form.close()
    
    
    def show_form( self, form_class ):
        self.actions.gui_actions.dismiss_startup_screen()
        
        if form_class in self._mdi:
            form = self._mdi[form_class]
            form.setFocus()
            return
        
        form: FrmBase = form_class( self )
        
        if self.mdi_mode:
            mdi: QMdiSubWindow = self.ui.MDI_AREA.addSubWindow( form )
            mdi.setSizePolicy( form.sizePolicy() )
        
        form.setWindowFlag( Qt.Tool, True )
        form.show()
        self._mdi[form_class] = form
        self.ui.MDI_AREA.setBackground( self.COLOUR_NOT_EMPTY )
