from os import path

from Designer.FrmMain_designer import Ui_MainWindow
from PyQt5.QtCore import QRectF, pyqtSlot
from PyQt5.QtOpenGL import QGLWidget, QGLFormat, QGL
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QMainWindow
from PyQt5.QtWidgets import QWhatsThis

from LegoModels import LegoModel
from LegoViews import LegoViewModel


class FrmMain( QMainWindow ):
    """
    Main window
    """

    def closeEvent( self, *args, **kwargs ):
        exit() # fixes crash on exit on Windows

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



        self._model = LegoModel(  )
        self._model.read_blast("C:\\MJR\\Apps\\legodiagram\\sample-data.blast")
        self._view = LegoViewModel( self._model )
        self.ui.graphicsView.setScene( self._view.scene )


        self.setWindowTitle( "Lego Model Creator" )


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


    @pyqtSlot()
    def on_action_New_triggered(self) -> None:
        """
        Signal handler:
        """
        pass

    @pyqtSlot()
    def on_action_Import_triggered(self) -> None:
        """
        Signal handler:
        """
        pass

    @pyqtSlot()
    def on_action_Exit_triggered(self) -> None:
        """
        Signal handler:
        """
        self.close()

    @pyqtSlot()
    def on_action_Preferences_triggered(self) -> None:
        """
        Signal handler:
        """
        pass

    @pyqtSlot()
    def on_action_Simplify_layout_triggered(self) -> None:
        """
        Signal handler:
        """
        pass
    