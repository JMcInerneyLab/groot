from random import randint
from typing import List

from PyQt5.QtCore import QLineF
from PyQt5.QtCore import QPointF
from PyQt5.QtCore import QRectF, pyqtSlot
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBrush
from PyQt5.QtGui import QColor
from PyQt5.QtGui import QPen
from PyQt5.QtGui import QPolygonF
from PyQt5.QtOpenGL import QGLWidget, QGLFormat, QGL
from PyQt5.QtWidgets import QFileDialog
from PyQt5.QtWidgets import QGraphicsTextItem
from os import path

from BlastResult import BlastResult, SequenceMananager
from BlastResult import Target

from PyQt5.QtWidgets import QGraphicsScene
from PyQt5.QtWidgets import QMainWindow

from FrmMain_designer import Ui_MainWindow
from Layouts import SeqLayoutManager


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

        self.ui.graphicsView.setViewport( QGLWidget( QGLFormat( QGL.SampleBuffers ) ) )
        # self.ui.graphicsView.scale( 2, 2 )

        scene = QGraphicsScene( )

        scene.addRect( QRectF( -10, -10, 20, 20 ) )

        self.ui.graphicsView.setScene( scene )

        # self.subset_file( "/Users/martinrusilowicz/work/data/plasmids/proteins.blast" )

        file_name = path.join( path.split( path.abspath( __file__ ) )[ 0 ], "sample-data.blast" )

        self.read_file( file_name )


    @pyqtSlot( )
    def on_action_Open_triggered( self ) -> None:
        """
        Signal handler:
        """
        file_name = QFileDialog.getOpenFileName( self, "Open BLAST", None, "*.blast" )

        if not file_name:
            return

        self.read_file( file_name )


    def subset_file( self, file_name ):
        MAX_BLASTS = 10
        interested = set( )
        blasts = [ ]

        with open( file_name, "r" ) as file:
            for line in file.readlines( ):
                result = BlastResult( line )

                if not result.query_accession in interested:
                    if len( interested ) == MAX_BLASTS:
                        continue

                    interested.add( result.query_accession )

                if not result.subject_accession in interested:
                    if len( interested ) == MAX_BLASTS:
                        continue

                    interested.add( result.subject_accession )

                blasts.append( line )

        with open( file_name + ".small_subset", "w" ) as file:
            for blast in blasts:
                file.writelines( blasts )


    def read_file( self, file_name ):
        blasts = [ ]

        with open( file_name, "r" ) as file:
            for line in file.readlines( ):
                result = BlastResult( line )
                blasts.append( result )

        scene = self.plot( blasts )
        self.ui.graphicsView.setScene( scene )


    @pyqtSlot( )
    def on_actionE_xit_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.close( )


    def plot( self, blasts: List[ BlastResult ] ) -> QGraphicsScene:
        scene = QGraphicsScene( )

        sequences = SequenceMananager( blasts )
        manager = SeqLayoutManager( sequences, scene )

        return scene
