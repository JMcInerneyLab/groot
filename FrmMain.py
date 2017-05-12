from typing import Any, Optional

from Designer.FrmMain_designer import Ui_MainWindow
from PyQt5.QtCore import QCoreApplication, QRectF, Qt, pyqtSlot
from PyQt5.QtGui import QColor
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from PyQt5.QtWidgets import QColorDialog, QFileDialog, QGraphicsScene, QInputDialog, QMainWindow, QMessageBox, QSizePolicy

import LegoFunctions
from LegoModels import LegoEdge, LegoModel, LegoSequence, LegoSubsequence
from LegoViews import EMode, ESelect, ESequenceColour, LegoViewModel, LegoViewSubsequence, PROT_COLOURS
from MHelper import IoHelper, QtColourHelper, QtGuiHelper
from MHelper.ExceptionHelper import SwitchError
from MHelper.QtColourHelper import Colours
from MyView import MyView


class FrmMain( QMainWindow ):
    """
    Main window
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self.no_update_options = False
        
        QCoreApplication.setAttribute( Qt.AA_DontUseNativeMenuBar )
        
        # QT stuff
        QMainWindow.__init__( self )
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )
        self.setWindowTitle( "Lego Model Creator" )
        self.ui.DOCK_COLOURS.setVisible(False)
        
        # Graphics view
        self.ui.graphicsView = MyView( self.ui.centralwidget )
        sizePolicy = QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        sizePolicy.setHeightForWidth( self.ui.graphicsView.sizePolicy().hasHeightForWidth() )
        self.ui.graphicsView.setSizePolicy( sizePolicy )
        self.ui.graphicsView.setObjectName( "graphicsView" )
        self.ui.gridLayout.addWidget( self.ui.graphicsView, 0, 0, 1, 1 )
        
        # Open GL rendering
        self.ui.graphicsView.setViewport( QGLWidget( QGLFormat( QGL.SampleBuffers ) ) )
        
        # Default (empty) scene
        scene = QGraphicsScene()
        scene.addRect( QRectF( -10, -10, 20, 20 ) )
        self.ui.graphicsView.setInteractive( True )
        self.ui.graphicsView.setScene( scene )
        
        
        # Load our sample model
        self._model = LegoModel()
        # try:
        #     #self._model.read_blast("./SampleData/blast.blast")
        #     # self._model.import_composites( "/Users/martinrusilowicz/work/data/sera/composites/c855817.composites_fixed" )
        #     # self._model.import_fasta( "/Users/martinrusilowicz/work/data/sera/data.faa" )
        #     # self._model.remove_all_edges()
        #     # self._model.import_blast( "/Users/martinrusilowicz/work/data/sera/bbcfta3878.blastp.fixed" )
        # except Exception as ex:
        #     PrintHelper.print_exception( ex )
        #     exit( 1 )
        
        self._view = None  # type:LegoViewModel
        self.refresh_model()
        
        self.statusBar().showMessage( "Press F1 to view keys." )
    
    def on_scene_selectionChanged( self ):
        if len(self._view.scene.selectedItems())==0:
            self.scene_selectionChanged()
    
    def scene_selectionChanged( self ):
        sel = self._view.selected_entity()
        
        if sel:
            type_name = type( sel ).__name__[ 4: ].upper()
            self.statusBar().showMessage( "SELECTED: <<{}>> {}".format( type_name, sel ) )
            
            self.ui.LBL_VIEW_LEFT.setText( str( sel ) )
            self.ui.LBL_VIEW_RIGHT.setText( type_name )
            
            if isinstance( sel, LegoSequence ):
                self.ui.TXT_VIEW.setText( self.colour_fasta( sel.array ) )
            elif isinstance( sel, LegoSubsequence ):
                self.ui.TXT_VIEW.setText( self.colour_fasta( sel.array ) )
            else:
                self.ui.TXT_VIEW.setText( "" )
            return
        
        tsel = self._view.selected_subsequence_views()
        nsel = len( tsel )
        
        if nsel == 0:
            self.statusBar().showMessage( "SELECTED: <<NOTHING>>" )
            self.ui.LBL_VIEW_LEFT.setText( "No selection" )
            self.ui.LBL_VIEW_RIGHT.setText( "" )
        else:
            self.statusBar().showMessage( "SELECTED: <<MULTIPLE ITEMS>> ({} subsequences)".format( nsel ) )
            self.ui.LBL_VIEW_LEFT.setText( "x {}".format( nsel ) )
            self.ui.LBL_VIEW_RIGHT.setText( "Subsequences" )
        
        self.ui.TXT_VIEW.setText( "* "+"\n* ".join( str( x.subsequence ) for x in tsel ) )
    
    
    def colour_fasta( self, array ):
        if not array:
            return "<b>Missing array data!</b><br/>Have you loaded the FASTA?"
        
        res = [ ]
        
        for x in array:
            colour = PROT_COLOURS.get( x )
            
            if colour is None:
                colour = QtColourHelper.Pens.BLACK
            
            res.append( '<span style="color:' + colour.color().name() + ';">' + x + '</span>' )
        
        return "".join( res )
    
    
    def subsequence_view_focus( self, subsequence_view: LegoViewSubsequence ):
        """
        CALLBACK
        When subsequence view changes
        :return: 
        """
        pass
    
    
    def refresh_model( self ):
        self.no_update_options = True
        # noinspection PyUnresolvedReferences
        self._view = LegoViewModel( self.scene_selectionChanged, self.ui.graphicsView, self.subsequence_view_focus, self._model )
        # noinspection PyUnresolvedReferences
        self.ui.graphicsView.setScene( self._view.scene )
        
        self._view.scene.selectionChanged.connect( self.on_scene_selectionChanged )  # TODO: Does this need cleanup like in C#?
        
        o = self._view.options
        self.ui.CHK_MOVE_XSNAP.setChecked( o.x_snap )
        self.ui.CHK_MOVE_YSNAP.setChecked( o.y_snap )
        self.ui.SLI_BLEND.setValue( o.colour_blend * 100 )
        self.ui.CHK_VIEW_EDGES.setCheckState( QtGuiHelper.to_check_state( o.view_edges ) )
        self.ui.CHK_VIEW_NAMES.setCheckState( QtGuiHelper.to_check_state( o.view_names ) )
        self.ui.CHK_VIEW_PIANO_ROLLS.setCheckState( QtGuiHelper.to_check_state( o.view_piano_roll ) )
        self.ui.CHK_VIEW_POSITIONS.setCheckState( QtGuiHelper.to_check_state( o.view_positions ) )
        self.ui.CHK_VIEW_COMPONENTS.setChecked( o.view_component )
        self.update_sel_btns()
        
        self.no_update_options = False
    
    def update_sel_btns(self):
        
        o = self._view.options
        print("UPDATE TO {}".format(o.mode))
        
        self.ui.BTN_SEL_SEQUENCE_.setChecked(o.mode == EMode.SEQUENCE)
        self.ui.ACT_SELECT_SEQUENCE.setChecked(o.mode == EMode.SEQUENCE)
        
        self.ui.BTN_SEL_COMPONENT_.setChecked(o.mode == EMode.COMPONENT)
        self.ui.ACT_SELECT_COMPONENT.setChecked(o.mode == EMode.COMPONENT)
        
        self.ui.BTN_SEL_SUBSEQUENCE_.setChecked(o.mode == EMode.SUBSEQUENCE)
        self.ui.ACT_SELECT_SUBSEQUENCE.setChecked(o.mode == EMode.SUBSEQUENCE)
        
        self.ui.BTN_SEL_EDGE_.setChecked(o.mode == EMode.EDGE)
        self.ui.ACT_SELECT_EDGE.setChecked(o.mode == EMode.EDGE)
        
        
        
    
    def closeEvent( self, *args, **kwargs ):
        """
        OVERRIDE
        Fixes crash on exit on Windows
        """
        exit()
    
    
    def update_options( self ):
        if self.no_update_options:
            return
        
        o = self._view.options
        o.x_snap = self.ui.CHK_MOVE_XSNAP.isChecked()
        o.y_snap = self.ui.CHK_MOVE_YSNAP.isChecked()
        o.colour_blend = self.ui.SLI_BLEND.value() / 100
        o.view_edges = QtGuiHelper.from_check_state( self.ui.CHK_VIEW_EDGES.checkState() )
        o.view_names = QtGuiHelper.from_check_state( self.ui.CHK_VIEW_NAMES.checkState() )
        o.view_piano_roll = QtGuiHelper.from_check_state( self.ui.CHK_VIEW_PIANO_ROLLS.checkState() )
        o.view_positions = QtGuiHelper.from_check_state( self.ui.CHK_VIEW_POSITIONS.checkState() )
        o.view_component = self.ui.CHK_VIEW_COMPONENTS.isChecked()
        #o.mode = EMode.SEQUENCE if self.ui.ACT_SELECT_SEQUENCE.isChecked() else EMode.SUBSEQUENCE if self.ui.ACT_SELECT_SUBSEQUENCE.isChecked() else EMode.EDGE if self.ui.ACT_SELECT_EDGE.isChecked() else EMode.COMPONENT
        self.update_sel_btns()
        
        self._view.scene.update()
        self.statusBar().showMessage("HIIII!")
        self.no_update_options = False
    
    
    @pyqtSlot( int )
    def on_CHK_VIEW_EDGES_stateChanged( self, _ ): #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        self.update_options()
    
    
    @pyqtSlot( int )
    def on_CHK_VIEW_COMPONENTS_stateChanged( self, _ ): #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        self.update_options()
    
    
    @pyqtSlot( int )
    def on_CHK_VIEW_NAMES_stateChanged( self, _ ): #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        self.update_options()
    
    
    @pyqtSlot( int )
    def on_CHK_VIEW_PIANO_ROLLS_stateChanged( self, _ ): #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        self.update_options()
    
    
    @pyqtSlot( int )
    def on_CHK_VIEW_POSITIONS_stateChanged( self, _ ): #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        self.update_options()
    
    
    @pyqtSlot( int )
    def on_CHK_MOVE_XSNAP_stateChanged( self, _ ): #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        self.update_options()
    
    
    @pyqtSlot( int )
    def on_CHK_MOVE_YSNAP_stateChanged( self, _ ): #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        self.update_options()
    
    
    @pyqtSlot( int )
    def on_CHK_COL_BLEND_stateChanged( self, _ ): #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        self.update_options()
    
    
    @pyqtSlot( bool )
    def on_RAD_COL_CONNECTED_toggled( self, _ ): #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        self.update_options()
    
    
    @pyqtSlot( bool )
    def on_RAD_COL_SELECTION_toggled( self, _ ): #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        self.update_options()
    
    
    @pyqtSlot( bool )
    def on_RAD_COL_ALL_toggled( self, _ ): #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        self.update_options()
    
    
    @pyqtSlot( int )
    def on_SLI_BLEND_valueChanged( self, _ ): #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        self.update_options()
    
    
    def apply_colour( self, new_colour, darken = True ):
        if darken and self.ui.BTNCHK_DARKER.isChecked():
            new_colour = QColor( new_colour.red() // 2, new_colour.green() // 2, new_colour.blue() // 2 )
        
        self._view.change_colours( new_colour )
    
    
    @pyqtSlot()
    def on_BTNCHK_DARKER_clicked( self ) -> None:
        """
        Signal handler: Darker check-button clicked
        """
        self.ui.ACTCHK_DARKER.setChecked( self.ui.BTNCHK_DARKER.isChecked() )
    
    
    @pyqtSlot()
    def on_BTN_BLANK_clicked( self ) -> None: #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER #TODO: BAD_HANDLER
        """
        Signal handler: Blanking plate clicked
        """
        pass  # nothing to do
    
    
    @pyqtSlot()
    def on_ACT_MODEL_NEW_triggered( self ) -> None:
        """
        Signal handler: New model
        """
        self._model = LegoModel()
        self.refresh_model()
    
    
    @pyqtSlot()
    def on_ACT_MODEL_IMPORT_triggered( self ) -> None:
        """
        Signal handler: Import data
        """
        filters = "FASTA files (*.fasta *.fa *.faa)", "BLAST output (*.blast *.tsv)", "Composite finder output (*.composites)"
        
        file_name, filter = QFileDialog.getOpenFileName( self, "Select file", None, ";;".join( filters ) )
        
        if not file_name:
            return
        
        filter_index = filters.index( filter )
        
        if filter_index == 0:
            r = self._model.import_fasta( file_name )
        elif filter_index == 1:
            r = self._model.import_blast( file_name )
        elif filter_index == 2:
            r = self._model.import_composites( file_name )
        else:
            raise SwitchError( "filter_index", filter_index )
        
        if r:
            self.statusBar().showMessage( str( r ) )
        
        self.refresh_model()
    
    
    @pyqtSlot()
    def on_ACT_APP_EXIT_triggered( self ) -> None:
        """
        Signal handler: Exit application
        """
        self.close()
    
    
    @pyqtSlot()
    def on_ACT_MODEL_SAVE_triggered( self ) -> None:
        """
        Signal handler: Save model
        """
        file_name = QtGuiHelper.browse_save( self, "Genetic lego (*.glego)" )
        
        if file_name:
            IoHelper.save_binary( file_name, self._model )
    
    
    @pyqtSlot()
    def on_ACT_MODEL_OPEN_triggered( self ) -> None:
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
    def on_ACT_MODEL_QUANTISE_triggered( self ) -> None:
        """
        Signal handler:
        """
        level, ok = QInputDialog.getInt( self, self.windowTitle(), "This option will quantise subsequence positions to the nearest 'n', where 'n' is:", 10, 2, 1000 )
        
        if not ok:
            return
        
        self._model.quantise( level )
        self.refresh_model()
    
    
    @pyqtSlot()
    def on_ACT_NEW_SEQUENCE_triggered( self ) -> None:
        """
        Signal handler:
        """
        sequence = self._model.add_new_sequence()
        self._view.add_new_sequence( sequence )
    
    
    @pyqtSlot()
    def on_ACT_NEW_EDGE_triggered( self ) -> None:
        """
        Signal handler:
        """
        subsequences = self.selected_subsequences()
        
        try:
            self._model.add_new_edge( subsequences )
            self._view.recreate_edges()
        
        except Exception as ex:
            QtGuiHelper.show_exception( self, ex )
    
    
    @pyqtSlot()
    def on_ACT_NEW_SPLIT_triggered( self ) -> None:
        """
        Signal handler:
        """
        subsequences = self.selected_subsequences()
        sequence = self.selected_sequence()
        
        if not sequence:
            return
        
        # noinspection PyUnresolvedReferences
        default_split = (min( x.start for x in subsequences ) + max( x.end for x in subsequences )) // 2
        split_point, ok = QInputDialog.getInt( self, self.windowTitle(), "Split the sequence '{0}' into [1:x] and [x+1:n] where x = ", default_split, 1, sequence.length )
        
        if not ok:
            return
        
        try:
            self._model.add_new_subsequence( sequence, split_point )
            self._view.recreate_sequences( [sequence] )
        
        except Exception as ex:
            QtGuiHelper.show_exception( self, ex )
    
    
    @pyqtSlot()
    def on_ACT_REMOVE_SELECTION_triggered( self ) -> None:
        """
        Signal handler: Remove selection
        """
        pass
    
    
    @pyqtSlot()
    def on_ACT_REMOVE_SEQUENCE_triggered( self ) -> None:
        """
        Signal handler:
        """
        sequences = self.selected_sequences()
        
        if sequences:
            message = "This will remove {} sequences.".format(len(sequences))
            details = "* "+ "\n* ".join(str(x) for x in sequences)
            msgbox = QMessageBox()
            msgbox.setText(message)
            msgbox.setDetailedText(details)
            msgbox.setStandardButtons(QMessageBox.Yes | QMessageBox.No)
            
            if msgbox.exec_() != QMessageBox.Yes:
                return
            
            self._model.remove_sequences( sequences )
            self._view.remove_sequences( sequences )
        else:
            QMessageBox.information(self, self.windowTitle(), "Please select a sequence first.")
    
    
    @pyqtSlot()
    def on_ACT_REMOVE_EDGE_triggered( self ) -> None:
        """
        Signal handler:
        """
        edge = self.__ask_for_one( self._view.selected_edges() )
        
        if edge:
            if QMessageBox.question( self, self.windowTitle(), "This will remove the edge '{0}'.".format( edge ), QMessageBox.Yes | QMessageBox.No ) != QMessageBox.Yes:
                return
            
            self._model.remove_edge( edge )
            self._view.recreate_edges()
    
    
    @pyqtSlot()
    def on_ACT_REMOVE_SPLIT_triggered( self ) -> None:
        """
        Signal handler:
        """
        subsequences = self._view.selected_subsequences()
        
        if subsequences:
            if QMessageBox.question( self, self.windowTitle(), "This will remove merge the following subsequences:\n* "+("\n* ".join(str(x) for x in subsequences )), QMessageBox.Yes | QMessageBox.No ) != QMessageBox.Yes:
                return
            
            results = self._model.merge_subsequences(subsequences)
            self._view.recreate_sequences(x.sequence for x in results)
    
    
    @pyqtSlot()
    def on_ACT_COL_RED_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour( Colours.RED )
    
    
    @pyqtSlot()
    def on_ACT_COL_GREEN_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour( Colours.GREEN )
    
    
    @pyqtSlot()
    def on_ACT_COL_BLUE_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour( Colours.BLUE )
    
    
    @pyqtSlot()
    def on_ACT_COL_CYAN_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour( Colours.CYAN )
    
    
    @pyqtSlot()
    def on_ACT_COL_MAGENTA_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour( Colours.MAGENTA )
    
    
    @pyqtSlot()
    def on_ACT_COL_YELLOW_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour( Colours.YELLOW )
    
    
    @pyqtSlot()
    def on_ACT_COL_BLACK_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour( Colours.BLACK )
    
    
    @pyqtSlot()
    def on_ACT_COL_GRAY_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour( Colours.GRAY )
    
    
    @pyqtSlot()
    def on_ACT_COL_WHITE_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour( Colours.WHITE )
    
    
    @pyqtSlot()
    def on_ACT_WINDOW_COLOURS_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.ui.DOCK_COLOURS.setVisible( self.ui.ACT_WINDOW_COLOURS.isChecked() )
    
    
    @pyqtSlot( bool )
    def on_DOCK_COLOURS_visibilityChanged( self, visible ):
        self.ui.ACT_WINDOW_COLOURS.setChecked( visible )
    
    
    @pyqtSlot()
    def on_ACT_COL_RESET_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.apply_colour( ESequenceColour.RESET, False )
    
    
    @pyqtSlot()
    def on_ACT_COL_CUSTOM_triggered( self ) -> None:
        """
        Signal handler:
        """
        new_colour = QColorDialog.getColor( Qt.white, self )
        
        if new_colour is not None:
            self.apply_colour( new_colour, False )
    
    
    @pyqtSlot()
    def on_ACT_DETAILS_SEQUENCE_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.__view_sequence_details( self.__ask_for_one( self._view.selected_sequences() ) )
    
    
    def __view_sequence_details( self, s: Optional[ LegoSequence ] ):
        if not s:
            return
        
        S = "<h2>"
        E = "</h2>"
        L = "<br/>"
        
        details = [ ]
        details.append( S + "ACCESSION" + E )
        details.append( s.accession )
        details.append( L )
        details.append( S + "SUBSEQUENCES" + E )
        details.append( s.subsequences )
        details.append( L )
        details.append( S + "LENGTH" + E )
        details.append( s.length )
        details.append( L )
        details.append( S + "ARRAY" + E )
        details.append( s.array )
        details.append( L )
        details.append( S + "META" + E )
        details.append( "<br/>".join( str( x ) for x in s.source_info ) )
        
        b = QMessageBox()
        b.setText( "SEQUENCE '{}'".format( s ) )
        b.setInformativeText( "".join( str( x ) for x in details ) )
        b.exec_()
    
    
    def __view_edge_details( self, s: Optional[ LegoEdge ] ):
        if not s:
            return
        
        S = "<h2>"
        E = "</h2>"
        L = "<br/>"
        
        details = [ ]
        details.append( S + "SOURCE" + E )
        details.append( "{}[{}:{}" + E.format( s.source_sequence, s.source_start, s.source_end ) )
        details.append( L )
        details.append( S + "DESTINATION" + E )
        details.append( "{}[{}:{}" + E.format( s.destination_sequence, s.destination_start, s.destination_end ) )
        details.append( L )
        details.append( S + "SOURCES" + E )
        details.append( s.source )
        details.append( L )
        details.append( S + "DESTINATIONS" + E )
        details.append( s.destination )
        details.append( L )
        details.append( S + "META" + E )
        details.append( "\n".join( str( x ) for x in s.source_info ) )
        details.append( L )
        
        b = QMessageBox()
        b.setText( "EDGE '{}'".format( s ) )
        b.setInformativeText( "\n".join( str( x ) for x in details ) )
        b.exec_()
    
    
    def __view_subsequence_details( self, s: Optional[ LegoSubsequence ] ):
        if not s:
            return
        
        S = "<h2>"
        E = "</h2>"
        L = "<br/>"
        
        details = [ ]
        details.append( S + "SEQUENCE" + E )
        details.append( s.sequence.accession )
        details.append( L )
        details.append( S + "START" + E )
        details.append( s.start )
        details.append( L )
        details.append( S + "END" + E )
        details.append( s.end )
        details.append( L )
        details.append( S + "EDGES" + E )
        details.append( s.edges )
        details.append( L )
        details.append( S + "UI POSITION" + E )
        details.append( s.ui_position )
        details.append( L )
        details.append( S + "UI COLOUR" + E )
        details.append( s.ui_colour )
        details.append( L )
        details.append( S + "ARRAY" + E )
        details.append( s.array )
        details.append( L )
        details.append( S + "META" + E )
        details.append( s.source_info )
        details.append( L )
        
        b = QMessageBox()
        b.setText( "SUBSEQUENCE '{}'".format( s ) )
        b.setInformativeText( "\n".join( str( x ) for x in details ) )
        b.exec_()
    
    
    @pyqtSlot()
    def on_ACT_DETAILS_EDGE_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.__view_edge_details( self.__ask_for_one( self._view.selected_edges() ) )
    
    
    @pyqtSlot()
    def on_ACT_DETAILS_SPLIT_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.__view_subsequence_details( self.__ask_for_one( self._view.selected_subsequences() ) )
    
    
    @pyqtSlot()
    def on_ACTCHK_DARKER_triggered( self ) -> None:
        """
        Signal handler: "Darker" check-button
        """
        self.ui.BTNCHK_DARKER.setChecked( self.ui.ACTCHK_DARKER.isChecked() )
    
    
    @pyqtSlot()
    def on_ACT_COL_DARK_GRAY_triggered( self ) -> None:
        """
        Signal handler: Colour dark gray
        """
        self.apply_colour( Colours.DARK_GRAY, False )
    
    
    def __ask_for_one( self, array ) -> Optional[ Any ]:
        if not array:
            QMessageBox.information(self, self.windowTitle(), "Make a valid selection first.")
            return None
        
        if len( array ) == 1:
            return next( iter( array ) )
        
        item, ok = QInputDialog.getItem( self, self.windowTitle(), "Select", [ str( x ) for x in array ] )
        
        if not ok:
            return None
        
        for x in array:
            if str( x ) == item:
                return x
        
        return None
    
    
    @pyqtSlot()
    def on_ACT_DETAILS_SELECTION_triggered( self ) -> None:
        """
        Signal handler:
        """
        selected = self._view.selected_entity()
        
        if isinstance( selected, LegoSubsequence ):
            self.__view_subsequence_details( selected )
        elif isinstance( selected, LegoSequence ):
            self.__view_sequence_details( selected )
        elif isinstance( selected, LegoEdge ):
            self.__view_edge_details( selected )
    
    
    @pyqtSlot()
    def on_ACT_COL_RANDOM_triggered( self ) -> None:
        """
        Signal handler: Random colour
        """
        self.apply_colour( ESequenceColour.RANDOM, False )
    
    
    @pyqtSlot()
    def on_ACT_HELP_KEYS_triggered( self ) -> None:
        """
        Signal handler:
        """
        keys = "Left click = Select subsequence|Double click = Select sequence|Double click + Alt = Select edge|Left click + Control = Add to selection|Left drag = Move selection|Left drag + Control = Move selection (toggle X-snap)|Left drag + Alt = Move selection (toggle Y-snap)"
        
        QMessageBox.information( self, "Keys", keys.replace( "|", "\n" ) )
    
    
    @pyqtSlot()
    def on_ACT_REMOVE_ALL_EDGES_triggered( self ) -> None:
        """
        Signal handler: Remove all edges
        """
        self._model.remove_all_edges()
        self.refresh_model()
    
    
    @pyqtSlot()
    def on_ACT_COMPONENT_COMPARTMENTALISE_triggered( self ) -> None:
        """
        Signal handler:
        """
        self._model.compartmentalise()
        self.refresh_model()
    
    
    @pyqtSlot()
    def on_ACT_ARRAY_TREE_triggered( self ) -> None:
        """
        Signal handler:
        """
        component_name, ok = QInputDialog.getItem(self, self.windowTitle(), "Select component", [str(x) for x in self._model.components])
        
        if not ok:
            return 
        
        component =  next(iter((x for x in self._model.components if str(x) == component_name)))
        
        assert component
        
        try:
            LegoFunctions.process_create_tree( self._model, component )
        except Exception as ex:
            QtGuiHelper.show_exception(self, "Failed to process NRFG.", ex)
    
    
    @pyqtSlot()
    def on_ACT_ARRAY_FUSE_triggered( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    @pyqtSlot()
    def on_ACT_SELECT_ALL_triggered(self) -> None:
        """
        Signal handler:
        """
        self._view.select_all(ESelect.APPEND)
            
    @pyqtSlot()
    def on_ACT_SELECT_NONE_triggered(self) -> None:
        """
        Signal handler:
        """
        self._view.select_all(ESelect.REMOVE)
            
    @pyqtSlot()
    def on_ACT_SELECT_EMPTY_triggered(self) -> None:
        """
        Signal handler:
        """
        self._view.select_empty()
            
    @pyqtSlot()
    def on_ACT_SELECTION_INVERT_triggered(self) -> None:
        """
        Signal handler:
        """
        self._view.select_all(ESelect.TOGGLE)
        
    @pyqtSlot()
    def on_ACT_SELECT_SEQUENCE_triggered(self) -> None:
        """
        Signal handler: Sequence selection mode
        """
        if self.no_update_options:
            return 
        
        self._view.options.mode =EMode.SEQUENCE
        self.update_options()
            
    @pyqtSlot()
    def on_ACT_SELECT_SUBSEQUENCE_triggered(self) -> None:
        """
        Signal handler: Subsequence selection mode
        """
        if self.no_update_options:
            return
        
        self._view.options.mode =EMode.SUBSEQUENCE
        self.update_options()
            
    @pyqtSlot()
    def on_ACT_SELECT_EDGE_triggered(self) -> None:
        """
        Signal handler: Edge selection mode
        """
        if self.no_update_options:
            return
        
        self._view.options.mode =EMode.EDGE
        self.update_options()
            
    @pyqtSlot()
    def on_ACT_SELECT_COMPONENT_triggered(self) -> None:
        """
        Signal handler: Component selection mode
        """
        if self.no_update_options:
            return
        
        self._view.options.mode =EMode.COMPONENT
        self.update_options()
            
    @pyqtSlot()
    def on_ACT_NEW_ENTITY_triggered(self) -> None: #TODO
        """
        Signal handler: 
        """
        pass
            
    @pyqtSlot()
    def on_ACT_DELETE_ENTITY_triggered(self) -> None:
        """
        Signal handler:
        """
        pass
            
    
            
    @pyqtSlot()
    def on_ACT_COMPONENT_COMPARTMENTALISE_triggered( self ) -> None:
        """
        Signal handler: Compartmentalise model
        """
        self._model.compartmentalise()
        self.refresh_model()
    
    
