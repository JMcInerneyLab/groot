from os import path
from typing import List

from PyQt5.QtWidgets import QWhatsThis

from LegoModels import LegoModel, LegoModelOptions, LegoBlast
from LegoViews import LegoModelView
from PyQt5.QtCore import QRectF, pyqtSlot
from PyQt5.QtOpenGL import QGLWidget, QGLFormat, QGL
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QMainWindow

from FrmMain_designer import Ui_MainWindow


class FrmMain( QMainWindow ):
    """
    Main window
    """


    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """

        # ...QT stuff
        QMainWindow.__init__( self )
        self.ui = Ui_MainWindow( )
        self.ui.setupUi( self )

        # Open GL rendering
        self.ui.graphicsView.setViewport( QGLWidget( QGLFormat( QGL.SampleBuffers ) ) )
        # self.ui.graphicsView.scale( 2, 2 )

        scene = QGraphicsScene( )

        scene.addRect( QRectF( -10, -10, 20, 20 ) )

        self.ui.graphicsView.setScene( scene )


        self._options = LegoModelOptions( )
        self._model = LegoModel( self._options )
        self._view = None

        self.ui.NUM_MERGE.setValue( 10 )
        self.ui.CHK_TRANSITION.setChecked( True )
        self.ui.TXT_FILENAME.setText( path.join( path.split( path.abspath( __file__ ) )[ 0 ], "sample-data.blast" ) )
        self.ui.RAD_OPT_NONE.setChecked( True )

        self.read_file( )


    @pyqtSlot( )
    def on_action_Open_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.on_BTN_FILENAME_clicked( )
        self.read( )
        self.read_file( )


    @pyqtSlot( )
    def on_actionE_xit_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.close( )


    @pyqtSlot( )
    def on_BTN_WHATS_THIS_clicked( self ) -> None:
        """
        Signal handler:
        """
        QWhatsThis.enterWhatsThisMode( )


    @pyqtSlot( )
    def on_BTN_FILENAME_clicked( self ) -> None:
        """
        Signal handler:
        """
        file_name = QFileDialog.getOpenFileName( self, "Open BLAST", None, "*.blast" )

        if not file_name:
            return

        self.ui.TXT_FILENAME.setText( file_name )


    @pyqtSlot( )
    def on_pushButton_clicked( self ) -> None:
        """
        Signal handler: Update
        """
        self.read_file( )


    def read_file( self ):

        self._options.file_name = self.ui.TXT_FILENAME.text( )
        self._options.ignore_transitions = self.ui.CHK_TRANSITION.isChecked( )
        self._options.combine_cuts = self.ui.NUM_MERGE.value( )

        if self.ui.RAD_OPT_ALL.isChecked( ):
            self._options.pack = "all"

        if self.ui.RAD_OPT_MC.isChecked( ):
            self._options.pack = "montecarlo"

        if self.ui.RAD_OPT_NONE.isChecked( ):
            self._options.pack = "none"

        self._model = LegoModel( self._options )
        view = LegoModelView( self._model, None )  # self._view
        self.ui.graphicsView.setScene( view.scene )
        self._view = view

        self.setWindowTitle( "Lego - " + path.split( self._options.file_name )[ 1 ] )
