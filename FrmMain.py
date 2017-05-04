from random import randint

from PyQt5.QtCore import QRectF, pyqtSlot, QCoreApplication, Qt
from PyQt5.QtGui import QColor
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from PyQt5.QtWidgets import QFileDialog, QGraphicsScene, QMainWindow, QWhatsThis, QColorDialog

from Designer.FrmMain_designer import Ui_MainWindow
from LegoModels import LegoModel
from LegoViews import LegoViewModel, LegoViewSubsequence, EApply, ESequenceColour
from MHelper import QtGuiHelper, IoHelper
from MHelper.QtColourHelper import Colours


class FrmMain( QMainWindow ):
    """
    Main window
    """
    
    
    def closeEvent( self, *args, **kwargs ):
        exit()  # fixes crash on exit on Windows
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self.no_update_options=False
        
        QCoreApplication.setAttribute( Qt.AA_DontUseNativeMenuBar )
        
        # QT stuff
        QMainWindow.__init__( self )
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )
        self.setWindowTitle( "Lego Model Creator" )
        
        # Open GL rendering
        self.ui.graphicsView.setViewport( QGLWidget( QGLFormat( QGL.SampleBuffers ) ) )
        
        # Default (empty) scene
        scene = QGraphicsScene()
        scene.addRect( QRectF( -10, -10, 20, 20 ) )
        self.ui.graphicsView.setInteractive( True )
        self.ui.graphicsView.setScene( scene )
        
        # Load our sample model
        self._model = LegoModel()
        # self._model.read_blast("./SampleData/blast.blast")
        self._model.read_composites( "/Users/martinrusilowicz/HiddenDesktop/COMPOSITES/A0A024WP05.composites" )
        
        self._view = None  # type:LegoViewModel
        self.refresh_model()
        
        self.statusBar().showMessage( "LMB = Select | LMB+Drag = Move sequence; Shift = Move subsequence; Ctrl = No X-snap; Alt = No Y-snap | 0-9 RGB CYMK W = Change colour; Shift = Bright colour; Ctrl = Recursive | X = Restore all colours", 0 )
        
    
    
    def refresh_model( self ):
        self.no_update_options=True
        
        self._model.deoverlap()
        self._view = LegoViewModel( self._model )
        self.ui.graphicsView.setScene( self._view.scene )
        
        self.ui.LST_SEQUENCES.clear()
        self.ui.LST_SEQUENCES.addItems( x.accession for x in self._model.sequences )
        
        o = self._view.options
        self.ui.CHK_MOVE_XSNAP.setChecked( o.x_snap )
        self.ui.CHK_MOVE_YSNAP.setChecked( o.y_snap )
        self.ui.RAD_COL_CONNECTED.setChecked( o.colour_apply == EApply.EDGES )
        self.ui.RAD_COL_ALL.setChecked( o.colour_apply == EApply.ALL )
        self.ui.RAD_COL_SELECTION.setChecked( o.colour_apply == EApply.ONE )
        self.ui.CHK_COL_BLEND.setChecked( o.colour_blend != 1 )
        self.ui.SLI_BLEND.setValue( o.colour_blend * 100 )
        self.ui.CHK_VIEW_EDGES.setCheckState( QtGuiHelper.to_check_state( o.view_edges ) )
        self.ui.CHK_VIEW_NAMES.setCheckState( QtGuiHelper.to_check_state( o.view_names ) )
        self.ui.CHK_VIEW_PIANO_ROLLS.setCheckState( QtGuiHelper.to_check_state( o.view_piano_roll ) )
        self.ui.CHK_VIEW_POSITIONS.setCheckState( QtGuiHelper.to_check_state( o.view_positions ) )
        
        self.no_update_options=False
    
    
    def update_options( self ):
        if self.no_update_options:
            return 
        
        o = self._view.options
        o.x_snap = self.ui.CHK_MOVE_XSNAP.isChecked()
        o.y_snap = self.ui.CHK_MOVE_YSNAP.isChecked()
        o.colour_apply = EApply.EDGES if self.ui.RAD_COL_CONNECTED.isChecked() \
            else EApply.ALL if self.ui.RAD_COL_ALL.isChecked() \
            else EApply.ONE if self.ui.RAD_COL_SELECTION.isChecked() else None
        o.colour_blend = self.ui.SLI_BLEND.value() / 100 if self.ui.CHK_COL_BLEND.isChecked() else 1
        o.view_edges = QtGuiHelper.from_check_state(self.ui.CHK_VIEW_EDGES.checkState())
        o.view_names = QtGuiHelper.from_check_state(self.ui.CHK_VIEW_NAMES.checkState())
        o.view_piano_roll = QtGuiHelper.from_check_state(self.ui.CHK_VIEW_PIANO_ROLLS.checkState())
        o.view_positions = QtGuiHelper.from_check_state(self.ui.CHK_VIEW_POSITIONS.checkState())
        
        self._view.scene.update()
        
        self.statusBar().showMessage(str(randint(0,1000)),0)
    
    
    @pyqtSlot()
    def on_action_New_triggered( self ) -> None:
        """
        Signal handler:
        """
        self._model = LegoModel()
        self.refresh_model()
    
    
    @pyqtSlot()
    def on_action_Import_triggered( self ) -> None:
        """
        Signal handler:
        """
        filters = "FASTA files (*.fasta *.fa)", "BLAST output (*.blast *.tsv)", "Composite finder output (*.composites)"
        
        file_name, filter = QFileDialog.getOpenFileName( self, "Select file", None, ";;".join( filters ) )
        
        if not file_name:
            return
        
        filter_index = filters.index( filter )
        
        if filter_index == 0:
            self._model.read_fasta( file_name )
        elif filter_index == 1:
            self._model.read_blast( file_name )
        elif filter_index == 2:
            self._model.read_composites( file_name )
        
        self.refresh_model()
    
    @pyqtSlot(int)
    def on_CHK_VIEW_EDGES_stateChanged(self, state):
        self.update_options()
        
        
    @pyqtSlot(int)
    def on_CHK_VIEW_NAMES_stateChanged(self, state):
        self.update_options()
    
    @pyqtSlot(int)
    def on_CHK_VIEW_PIANO_ROLLS_stateChanged(self, state):
        self.update_options()
        
    @pyqtSlot(int)
    def on_CHK_VIEW_POSITIONS_stateChanged(self, state):
        self.update_options()
        
    @pyqtSlot(int)
    def on_CHK_MOVE_XSNAP_stateChanged(self, state):
        self.update_options()
    
    @pyqtSlot(int)
    def on_CHK_MOVE_YSNAP_stateChanged(self, state):
        self.update_options()
        
    @pyqtSlot(int)
    def on_CHK_COL_BLEND_stateChanged(self, state):
        self.update_options()
        
    @pyqtSlot(bool)
    def on_RAD_COL_CONNECTED_toggled(self, is_checked):
        self.update_options()
        
    @pyqtSlot(bool)
    def on_RAD_COL_SELECTION_toggled(self, is_checked):
        self.update_options()
        
    @pyqtSlot(bool)
    def on_RAD_COL_ALL_toggled(self, is_checked):
        self.update_options()
        
    @pyqtSlot(int)
    def on_SLI_BLEND_valueChanged(self, value:int):
        self.update_options()
    
    @pyqtSlot()
    def on_action_Exit_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.close()
    
    
    @pyqtSlot()
    def on_action_Preferences_triggered( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @pyqtSlot()
    def on_action_Simplify_layout_triggered( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @pyqtSlot()
    def on_BTN_COL_WHITE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour(Colours.WHITE)
    
    
    @pyqtSlot()
    def on_BTN_COL_YELLOW_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour(Colours.YELLOW)
    
    
    @pyqtSlot()
    def on_BTN_COL_RED_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour(Colours.RED)
    
    
    @pyqtSlot()
    def on_BTN_COL_MANENTA_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour(Colours.MAGENTA)
    
    
    @pyqtSlot()
    def on_BTN_COL_BLACK_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour(Colours.BLACK)
    
    
    @pyqtSlot()
    def on_BTN_COL_GREEN_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour(Colours.GREEN)
    
    
    @pyqtSlot()
    def on_BTN_COL_BLUE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour(Colours.BLUE)
    
    
    @pyqtSlot()
    def on_BTN_COL_CYAN_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour(Colours.CYAN)
    
    
    @pyqtSlot()
    def on_BTN_COL_RESET_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour(ESequenceColour.RESET, False)
    
    
    @pyqtSlot()
    def on_BTN_COL_CUSTOM_clicked( self ) -> None:
        """
        Signal handler:
        """
        new_colour = QColorDialog.getColor(Qt.white, self)
        
        if new_colour is not None:
            self.apply_colour(new_colour, False)
            
    def apply_colour(self, new_colour, darken = True):
        if darken and self.ui.CHK_COL_DARKER.isChecked():
            new_colour = QColor(new_colour.red() //2,new_colour.green()//2, new_colour.blue()//2)
        
        self._view.change_colours(new_colour)
    
    
    @pyqtSlot()
    def on_BTN_FILE_NEW_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @pyqtSlot()
    def on_BTN_FILE_IMPORT_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @pyqtSlot()
    def on_action_Save_triggered( self ) -> None:
        """
        Signal handler:
        """
        file_name = QtGuiHelper.browse_save( self, "Genetic lego (*.glego)" )
        
        if file_name:
            IoHelper.save_binary( file_name, self._model )
    
    
    @pyqtSlot()
    def on_action_Open_triggered( self ) -> None:
        """
        Signal handler:
        """
        file_name = QtGuiHelper.browse_open( self, "Genetic lego (*.glego)" )
        
        if file_name:
            try:
                self._model = IoHelper.load_binary( file_name )
                self.refresh_model()
            except Exception as ex:
                QtGuiHelper.show_exception( self, "Could not load the file. Perhaps it is from a different version?", ex )
    
    
    @pyqtSlot()
    def on_BTN_SEQUENCE_DETAILS_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @pyqtSlot( int )
    def on_LST_SEQUENCES_currentIndexChanged( self, index: int ):
        self.ui.LST_SUBSEQUENCES.clear()
        
        seq = self.selected_sequence()
        
        if seq:
            self.ui.LST_SUBSEQUENCES.addItems( "{0} - {1}".format( x.start, x.end ) for x in seq.subsequences )
    
    
    def selected_sequence( self ):
        text = self.ui.LST_SEQUENCES.currentText()
        return self._model.find( text )
    
    
    def selected_subsequence( self ):
        seq = self.selected_sequence()
        
        if not seq:
            return
        
        text = self.ui.LST_SUBSEQUENCES.currentText()
        
        if not text:
            return None
        
        s, e = text.split( "-" )
        sss = int( s )
        sse = int( e )
        return seq.find( sss, sse )
    
    
    @pyqtSlot( int )
    def on_LST_SUBSEQUENCES_currentIndexChanged( self, index: int ):
        self.ui.LST_EDGES.clear()
        
        sseq = self.selected_subsequence()
        
        if sseq:
            for edge in sseq.edges:
                self.ui.LST_EDGES.addItems( "--> {0} ({1} - {2})".format( x.sequence.accession, x.start, x.end ) for x in edge.source )
                self.ui.LST_EDGES.addItems( "<-- {0} ({1} - {2})".format( x.sequence.accession, x.start, x.end ) for x in edge.destination )
    
    
    @pyqtSlot()
    def on_BTN_SUBSEQUENCE_DETAILS_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @pyqtSlot()
    def on_BTN_EDGE_DETAILS_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
