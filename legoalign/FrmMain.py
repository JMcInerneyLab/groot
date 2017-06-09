from os import path
from typing import Optional, List, Set

import sys

import sip
from PyQt5.QtCore import QCoreApplication, QRectF, Qt, pyqtSlot, QPoint
from PyQt5.QtGui import QColor, QBrush
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from PyQt5.QtWidgets import QAction, QColorDialog, QFileDialog, QGraphicsScene, QInputDialog, QMainWindow, QMessageBox, QSizePolicy, QTextEdit, QGroupBox, QVBoxLayout, QWidget, QCheckBox, QPushButton, QGraphicsView

from MHelper import FileHelper, IoHelper, QtColourHelper, QtGuiHelper, ArrayHelper
from MHelper.ExceptionHelper import SwitchError
from MHelper.QtColourHelper import Colours
from MHelper.QtGuiHelper import exceptToGui, exqtSlot

from legoalign import LegoFunctions
from legoalign.FrmTreeSelector import FrmTreeSelector
from legoalign.Designer.FrmMain_designer import Ui_MainWindow
from legoalign.GlobalOptions import GlobalOptions
from legoalign.LegoViews import EMode, ESelect, ESequenceColour, ILegoViewModelObserver, LegoViewModel, LegoViewSubsequence
from legoalign.LegoModels import LegoComponent, LegoEdge, LegoModel, LegoSequence, LegoSubsequence
from legoalign.MyView import MyView


class FrmMain( QMainWindow, ILegoViewModelObserver ):
    """
    Main window
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self.no_update_options = False
        self.__group_boxes = []
        
        
        QCoreApplication.setAttribute( Qt.AA_DontUseNativeMenuBar )
        
        # QT stuff
        QMainWindow.__init__( self )
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )
        self.setWindowTitle( "Lego Model Creator" )
        
        self.ui.DOCK_COLOURS.setVisible( False )
        self.ui.DOCK_VIEW.setVisible( False )
        self.ui.DOCK_MOVEMENT.setVisible( False )
        
        self.ui.ACT_WIN_EDIT.setChecked( True )
        self.ui.ACT_WIN_SELECTION.setChecked( True )
        
        self.global_options = IoHelper.default_values( IoHelper.load_binary( self.global_options_file_name(), default = None ), GlobalOptions() )  # type: GlobalOptions
        self.refresh_recent_files()
        
        # Graphics view
        self.ui.graphicsView = MyView( self.ui.centralwidget )
        sizePolicy = QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        sizePolicy.setHeightForWidth( self.ui.graphicsView.sizePolicy().hasHeightForWidth() )
        self.ui.graphicsView.setSizePolicy( sizePolicy )
        self.ui.graphicsView.setObjectName( "graphicsView" )
        self.ui.graphicsView.setBackgroundBrush(QBrush(QColor(255,255,255)))
        self.ui.gridLayout.addWidget( self.ui.graphicsView, 0, 0, 1, 1 )
        
        # Open GL rendering
        self.ui.graphicsView.setViewport( QGLWidget( QGLFormat( QGL.SampleBuffers ) ) )
        
        # Default (empty) scene
        scene = QGraphicsScene()
        scene.addRect( QRectF( -10, -10, 20, 20 ) )
        self.ui.graphicsView.setInteractive( True )
        self.ui.graphicsView.setScene( scene )
        
        # Load our default model
        self._model = LegoModel()
        self._model_file_name = None
        
            
        sample_data_folder = path.join( FileHelper.get_directory( __file__), "sampledata")
        
        for x in FileHelper.sub_dirs(sample_data_folder):  
            action = QAction( FileHelper.get_filename(x), self )
            action.setStatusTip( x )
            # noinspection PyUnresolvedReferences
            action.triggered[bool].connect( self.__select_sample_data )
            self.ui.MNU_EXAMPLES.addAction( action )
        
        if self.global_options.recent_files:
            try:
                self.load_file( self.global_options.recent_files[ -1 ], errors = False )
                self._view = None  # type:LegoViewModel
                self.refresh_model()
            except:
                self.statusBar().showMessage("Could not load the file '{}'.".format(self.global_options.recent_files[ -1 ]))
            
            
        
    @exceptToGui()
    def __select_sample_data(self, _ : bool):
        directory = self.sender().statusTip()
        contents = FileHelper.list_dir(directory)
        
        self._model = LegoModel()
        self._model_file_name = None
        
        for x in contents:
            if x.endswith(".composites"):
                self._model.import_composites( x )
        
        for x in contents:
            if x.endswith(".blast"):
                self._model.import_blast( x )
    
        for x in contents:
            if x.endswith(".fasta"):
                self._model.import_fasta( x )
                
        self.refresh_model()
        
        QMessageBox.information(self, self.windowTitle(), "\n".join(self._model.comments))
    
    def refresh_recent_files( self ):
        self.ui.MNU_RECENT.clear()
        
        for x in self.global_options.recent_files:
            action = QAction( x, self )
            action.setStatusTip( x )
            # noinspection PyUnresolvedReferences
            action.triggered.connect( self.recent_file_triggered )
            self.ui.MNU_RECENT.addAction( action )
    
    
    def recent_file_triggered( self ):
        file_name = self.sender().statusTip()
        self.load_file( file_name )
    
    
    def on_scene_selectionChanged( self ):
        if len( self._view.scene.selectedItems() ) == 0:
            self.ILegoViewModelObserver_selection_changed()
    
    
    def ILegoViewModelObserver_selection_changed( self ):
        #
        # What have we selected?
        #
        entities = self._view.selected_entities()
        first = ArrayHelper.first_or_nothing(entities)
        type_name = (type( first ).__name__[ 4: ].upper() + ("s" if len( entities ) > 1 else "")) if entities else None
        self._view.clear_selection_mask()
        
        self.ui.BTN_SELMASK_ALL.setText(str(len(entities)))
        
        #
        # Delete existing controls
        #
        for group_box in self.__group_boxes: #type: List[QWidget]
            for widget in group_box: #type: QWidget
                widget.parentWidget().layout().removeWidget(widget)
                sip.delete(widget)
            
        self.__group_boxes.clear()
        
        # Status bar
        #
        if len( entities ) == 0:
            self.statusBar().showMessage( "SELECTED: <<NOTHING>>" )
            return
        elif len( entities ) == 1:
            self.statusBar().showMessage( "SELECTED: <<{}>> {}".format( type_name, first ) )
        else:
            self.statusBar().showMessage( "SELECTED: <<MULTIPLE ITEMS>> ({} {})".format( len( entities ), type_name ) )
            
        
        
        for entity in entities:
            assert entity is not None
            
            #
            # Controls
            #
            group_box = QGroupBox()
            group_box.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Minimum)
            group_box.setTitle(type(entity).__name__[4:]+" : "+  str(entity))
            self.ui.SCR_AREA.layout().addWidget(group_box)
            
            layout = QVBoxLayout()
            group_box.setLayout(layout)
            
            def __check_box(state : bool):
                check_box = self.sender() #type: QPushButton
                
                if not isinstance(check_box, QPushButton):
                    return

                self.__update_for_checkbox( check_box )
                self._view.scene.update()


            


            check_box = QPushButton()
            check_box.setText("Selected")
            check_box.setCheckable(True)
            check_box.setChecked(True)
            check_box.toggled[bool].connect(__check_box)
            check_box.setProperty("entity", entity)
            layout.addWidget(check_box)
            
            multiline = len(entities) > 1 or not self.ui.CHKBTN_DATA_FASTA.isChecked()
            
            text_edit = QTextEdit()
            text_edit.setLineWrapMode(QTextEdit.NoWrap if multiline else QTextEdit.WidgetWidth)
            text_edit.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Expanding if multiline else QSizePolicy.Minimum)
            text_edit.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            text_edit.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOn)
            text_edit.setStyleSheet("background: black; color: white;")
            layout.addWidget(text_edit)
            
            self.__group_boxes.append((check_box, text_edit, group_box))
            
            content = []
            
            if self.ui.CHKBTN_DATA_NEWICK.isChecked():
                #content.append(">"+str(entity))
                
                if isinstance(entity, LegoComponent):
                    if entity.tree:
                        content.append(entity.tree)
                    else:
                        content.append("; MISSING - Generate a tree first!")
                else:
                    
                    content.append("; NOT AVAILABLE - Only available for components")
            elif self.ui.CHKBTN_DATA_FASTA.isChecked():
                if hasattr( entity, "to_fasta" ):
                    fasta = entity.to_fasta(header=False)
                    content.append(fasta)
                else:
                    #content.append(">"+str(entity))
                    content.append("; NOT AVAILABLE")
            elif self.ui.CHKBTN_DATA_BLAST.isChecked():
                if hasattr( entity, "extra_data" ):
                    content.append("\n".join(entity.extra_data))
                else:
                    content.append("; NOT AVAILABLE")
                    
            content = "\n\n".join(content)
            
            if self.ui.CHKBTN_DATA_FASTA.isChecked():
                content = self.colour_fasta( content)
            
            text_edit.setText(content)
            
    def __update_for_checkbox( self, check_box : QPushButton):
        assert isinstance(check_box, QPushButton), check_box
        
        entity = check_box.property( "entity" )
        assert entity is not None
        
        state = check_box.isChecked()
        self._view.set_selection_mask( entity, state )

    
    
    def ILegoViewModelObserver_options_changed( self ):
        self.update_selection_buttons()
    
    
    def colour_fasta( self, array ):
        if not array:
            return "<b>Missing array data!</b><br/>Have you loaded the FASTA?"
        
        res = [ ]
        no_colours = False
        pending=""
        table=self._view.lookup_table.letter_colour_table
        
        for x in array:
            if x == ">":
                no_colours = True
                res.append('<b>')
                pending = "</b>"+pending
            elif x == "[":
                res.append('<span style="color:cyan;">[')
                continue
            elif x == "]":
                res.append(']</span>')
                continue
            elif x == ";":
                no_colours = True
                res.append('<span style="color:silver;">')
                pending = "</span>"+pending
            elif x=="\n":
                no_colours = False
                res.append(pending+"<br/>")
                pending=""
                
            if no_colours:
                res.append(x)
            else:
                colour = table.get( x )
                
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
        first_load=  self._view is None
        # noinspection PyUnresolvedReferences
        self._view = LegoViewModel( self, self.ui.graphicsView, self.subsequence_view_focus, self._model )
        # noinspection PyUnresolvedReferences
        self.ui.graphicsView.setScene( self._view.scene )
        
        self._view.scene.selectionChanged.connect( self.on_scene_selectionChanged ) # TODO: Does this need cleanup like in C#?
        
        if first_load:
            self.update_selection_buttons()
        else:
            self.no_update_options = False
            self.update_options()
            
        self.update_window_title()
    
    
    def update_selection_buttons( self ):
        self.no_update_options = True
        
        o = self._view.options
        
        self.ui.CHK_MOVE_XSNAP.setChecked( o.x_snap )
        self.ui.CHK_MOVE_YSNAP.setChecked( o.y_snap )
        self.ui.SLI_BLEND.setValue( o.colour_blend * 100 )
        self.ui.CHK_VIEW_EDGES.setCheckState( QtGuiHelper.to_check_state( o.view_edges ) )
        self.ui.CHK_VIEW_NAMES.setCheckState( QtGuiHelper.to_check_state( o.view_names ) )
        self.ui.CHK_VIEW_PIANO_ROLLS.setCheckState( QtGuiHelper.to_check_state( o.view_piano_roll ) )
        self.ui.CHK_VIEW_POSITIONS.setCheckState( QtGuiHelper.to_check_state( o.view_positions ) )
        self.ui.CHK_VIEW_COMPONENTS.setChecked( o.view_component )
        self.ui.CHK_MOVE.setChecked( o.move_enabled )
        
        self.ui.BTN_SEL_SEQUENCE_.setChecked( o.mode == EMode.SEQUENCE )
        self.ui.ACT_SELECT_SEQUENCE.setChecked( o.mode == EMode.SEQUENCE )
        
        self.ui.BTN_SEL_COMPONENT_.setChecked( o.mode == EMode.COMPONENT )
        self.ui.ACT_SELECT_COMPONENT.setChecked( o.mode == EMode.COMPONENT )
        
        self.ui.BTN_SEL_SUBSEQUENCE_.setChecked( o.mode == EMode.SUBSEQUENCE )
        self.ui.ACT_SELECT_SUBSEQUENCE.setChecked( o.mode == EMode.SUBSEQUENCE )
        
        self.ui.BTN_SEL_EDGE_.setChecked( o.mode == EMode.EDGE )
        self.ui.ACT_SELECT_EDGE.setChecked( o.mode == EMode.EDGE )
        
        self.no_update_options = False
    
    
    def closeEvent( self, *args, **kwargs ):
        """
        OVERRIDE
        Fixes crash on exit on Windows
        """
        exit()
    
    
    def update_options( self ):
        if self.no_update_options:
            return
        
        o                 = self._view.options
        o.x_snap          = self.ui.CHK_MOVE_XSNAP.isChecked()
        o.y_snap          = self.ui.CHK_MOVE_YSNAP.isChecked()
        o.colour_blend    = self.ui.SLI_BLEND.value() / 100
        o.view_edges      = QtGuiHelper.from_check_state( self.ui.CHK_VIEW_EDGES.checkState() )
        o.view_names      = QtGuiHelper.from_check_state( self.ui.CHK_VIEW_NAMES.checkState() )
        o.view_piano_roll = QtGuiHelper.from_check_state( self.ui.CHK_VIEW_PIANO_ROLLS.checkState() )
        o.view_positions  = QtGuiHelper.from_check_state( self.ui.CHK_VIEW_POSITIONS.checkState() )
        o.view_component  = self.ui.CHK_VIEW_COMPONENTS.isChecked()
        o.move_enabled    = self.ui.CHK_MOVE.isChecked()
        self.update_selection_buttons()
        
        self._view.scene.update()
        self.no_update_options = False
    
    
    def apply_colour( self, new_colour, darken = True ):
        if darken and self.ui.BTNCHK_DARKER.isChecked():
            new_colour = QColor( new_colour.red() // 2, new_colour.green() // 2, new_colour.blue() // 2 )
        
        self._view.change_colours( new_colour )
    
    
    @exqtSlot(bool)
    def on_BTNCHK_DARKER_clicked( self, _:bool) -> None:
        """
        Signal handler: Darker check-button clicked
        """
        self.ui.ACTCHK_DARKER.setChecked( self.ui.BTNCHK_DARKER.isChecked() )
    
    
    @exqtSlot(bool)
    def on_ACT_MODEL_NEW_triggered( self, _ : bool ) -> None:
        """
        Signal handler: New model
        """
        self.__new_model()
        
    def __new_model(self):
        self._model = LegoModel()
        self._model_file_name = None
        self.update_window_title()
        self.refresh_model()
        
    def update_window_title(self):
        if self._model_file_name:
            file_name = FileHelper.get_filename(self._model_file_name)
            self.setWindowTitle("GeneticLego Diagram Editor - "+ file_name)
        else:
            self.setWindowTitle("GeneticLego Diagram Editor - (Untitled)")
    
    
    @exqtSlot(bool)
    def on_ACT_MODEL_IMPORT_triggered( self,_:bool ) -> None:
        """
        Signal handler: Import data
        """
        filters = "FASTA files (*.fasta *.fa *.faa)", "BLAST output (*.blast *.tsv)", "Composite finder output (*.composites)"
        
        file_name, filter = QFileDialog.getOpenFileName( self, "Select file", None, ";;".join( filters ), options = QFileDialog.DontUseNativeDialog )
        
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
    
    
    @exqtSlot(bool)
    def on_ACT_APP_EXIT_triggered( self,_:bool ) -> None:
        """
        Signal handler: Exit application
        """
        self.close()
    
    
    @exqtSlot(bool)
    def on_ACT_MODEL_SAVE_triggered( self,_:bool ) -> None:
        """
        Signal handler: Save model
        """
        if self._model_file_name:
            file_name = self._model_file_name
        else:
            file_name = QtGuiHelper.browse_save( self, "Genetic lego (*.glego)" )
        
        self.save_file(file_name)
    
    
    @exqtSlot(bool)
    def on_ACT_MODEL_OPEN_triggered( self,_:bool ) -> None:
        """
        Signal handler:
        """
        file_name = QtGuiHelper.browse_open( self, "Genetic lego (*.glego)" )
        
        if file_name:
            self._model_file_name = file_name
            self.load_file( file_name )
    
    
    def load_file( self, file_name, errors = True ):
        if file_name:
            try:
                self._model = IoHelper.load_binary( file_name )
                self._model_file_name = file_name
                self.remember_file( file_name )
                self.refresh_model()
                self.update_window_title()
            except Exception as ex:
                if errors:
                    QtGuiHelper.show_exception( self, "Could not load the file '{}'. Perhaps it is from a different version?".format(file_name), ex )
                else:
                    self.statusBar().showMessage("Could not load the file '{}'.".format(file_name))
                
    def save_file(self, file_name):
        if file_name:
            try:
                self._model_file_name = file_name
                self.remember_file(file_name)
                sys.setrecursionlimit(10000)
                IoHelper.save_binary( file_name, self._model )
                self.update_window_title()
            except Exception as ex:
                QtGuiHelper.show_exception( self, "Could not save the file '{}. Check the filename and permissions.".format(file_name), ex )
    
    
    def remember_file( self, file_name ):
        if file_name in self.global_options.recent_files:
            self.global_options.recent_files.remove( file_name )
        
        self.global_options.recent_files.append( file_name )
        
        while len( self.global_options.recent_files ) > 10:
            del self.global_options.recent_files[ 0 ]
        
        self.save_global_options()
        self.refresh_recent_files()
    
    
    def global_options_file_name( self ):
        dir = path.expanduser( "~/legoalign" )
        FileHelper.create_directory( dir )
        
        return path.join( dir, "options.p" )
    
    
    def save_global_options( self ):
        IoHelper.save_binary( self.global_options_file_name(), self.global_options )
    
    
    @exqtSlot(bool)
    def on_ACT_MODEL_QUANTISE_triggered( self,_:bool ) -> None:
        """
        Signal handler:
        """
        level, ok = QInputDialog.getInt( self, self.windowTitle(), "This option will quantise subsequence positions to the nearest 'n', where 'n' is:", 10, 2, 1000 )
        
        if not ok:
            return
        
        self._model.quantise( level )
        self.refresh_model()
        
    
    
    
    
    
    
    
    
    
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
    
    
    def __ask_for_one( self, array ) -> Optional[ object ]:
        if not array:
            QMessageBox.information( self, self.windowTitle(), "Make a valid selection first." )
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
        ALL = "(ALL)"
        component_name, ok = QInputDialog.getItem( self, self.windowTitle(), "Select component", [ALL]+[ str( x ) for x in self._model.components ] )
        
        if not ok:
            return
        
        
        
        if component_name == ALL:
            components = list(self._model.components)
        else:
            component = next( iter( (x for x in self._model.components if str( x ) == component_name) ) )
            assert component
            components = [component]
        
        with_trees = []
        
        for x in components:
            if x.tree is not None:
                with_trees.append(x)
                
        if with_trees:
            if len(components) == len(with_trees):
                tt = "This tree has" if len(components)==0 else "These {} trees have".format(len(components))
                r = QMessageBox.question(self, self.windowTitle(), "{} already been generated. Do you wish to continue?".format(tt), QMessageBox.Ok | QMessageBox.Cancel)
            else:
                r = QMessageBox.question(self, self.windowTitle(), "Trees have already been generated for {} out of {} selected components. Do you want to exclude these trees from the process?".format(len(with_trees), len(components)), QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)
            
            if r == QMessageBox.Yes:
                for x in with_trees:
                    components.remove(x)
            elif r== QMessageBox.Cancel:
                return
                
        
        component = None
        
        try:
            for component in components:
                LegoFunctions.process_create_tree( self._model, component )
        except Exception as ex:
            QtGuiHelper.show_exception( self, "Failed to process NRFG for component '{}'.".format(component), ex )
    
    
    @exqtSlot(bool)
    def on_ACT_ARRAY_FUSE_triggered( self, _ : bool ) -> None:
        """
        Signal handler:
        """
        FrmTreeSelector.request(self, self._model)
    
    
    @pyqtSlot()
    def on_ACT_SELECT_ALL_triggered( self ) -> None:
        """
        Signal handler:
        """
        self._view.select_all( ESelect.APPEND )
    
    
    @pyqtSlot()
    def on_ACT_SELECT_NONE_triggered( self ) -> None:
        """
        Signal handler:
        """
        self._view.select_all( ESelect.REMOVE )
    
    
    @pyqtSlot()
    def on_ACT_SELECT_EMPTY_triggered( self ) -> None:
        """
        Signal handler:
        """
        self._view.select_empty()
    
    
    @pyqtSlot()
    def on_ACT_SELECTION_INVERT_triggered( self ) -> None:
        """
        Signal handler:
        """
        self._view.select_all( ESelect.TOGGLE )
    
    
    @pyqtSlot()
    def on_ACT_SELECT_SEQUENCE_triggered( self ) -> None:
        """
        Signal handler: Sequence selection mode
        """
        if self.no_update_options:
            return
        
        self._view.options.mode = EMode.SEQUENCE
        self.update_options()
    
    
    @pyqtSlot()
    def on_ACT_SELECT_SUBSEQUENCE_triggered( self ) -> None:
        """
        Signal handler: Subsequence selection mode
        """
        if self.no_update_options:
            return
        
        self._view.options.mode = EMode.SUBSEQUENCE
        self.update_options()
    
    
    @pyqtSlot()
    def on_ACT_SELECT_EDGE_triggered( self ) -> None:
        """
        Signal handler: Edge selection mode
        """
        if self.no_update_options:
            return
        
        self._view.options.mode = EMode.EDGE
        self.update_options()
    
    
    @pyqtSlot()
    def on_ACT_SELECT_COMPONENT_triggered( self ) -> None:
        """
        Signal handler: Component selection mode
        """
        if self.no_update_options:
            return
        
        self._view.options.mode = EMode.COMPONENT
        self.update_options()
    
    
    @pyqtSlot()
    def on_ACT_NEW_ENTITY_triggered( self ) -> None:
        """
        Signal handler: 
        """
        m = self._view.options.mode
        
        if m == EMode.SEQUENCE:
            sequence = self._model.add_new_sequence()
            self._view.add_new_sequence( sequence )
        elif m == EMode.SUBSEQUENCE:
            subsequences = self._view.selected_subsequences()
            
            if not subsequences:
                QMessageBox.information( self, self.windowTitle(), "Select a subsequence to split first." )
                return
            
            sequence = ArrayHelper.first(subsequences).sequence
            
            if not all(x.sequence is sequence for x in subsequences):
                QMessageBox.information( self, self.windowTitle(), "All of the the selected subsequences must be in the same sequence." )
                return
            
            # noinspection PyUnresolvedReferences
            default_split = (min( x.start for x in subsequences ) + max( x.end for x in subsequences )) // 2
            split_point, ok = QInputDialog.getInt( self, self.windowTitle(), "Split the sequence '{0}' into [1:x] and [x+1:n] where x = ".format(sequence), default_split, 1, sequence.length )
            
            if not ok:
                return
            
            try:
                self._model.add_new_subsequence( sequence, split_point )
                self._view.recreate_sequences( [ sequence ] )
            except Exception as ex:
                QtGuiHelper.show_exception( self, ex )
        elif m == EMode.EDGE:
            subsequences = self.selected_subsequences()
        
            try:
                self._model.add_new_edge( subsequences )
                self._view.recreate_edges()
            
            except Exception as ex:
                QtGuiHelper.show_exception( self, ex )
        elif m == EMode.COMPONENT:
            QMessageBox.information( self, self.windowTitle(), "Components are automatically generated, you cannot create new ones manually." )
            
    
    
    @pyqtSlot()
    def on_ACT_DELETE_ENTITY_triggered( self ) -> None:
        """
        Signal handler:
        """
        m = self._view.options.mode
        
        if m == EMode.SEQUENCE:
            sequences = self._view.selected_sequences()
            
            if sequences:
                if not self.__query_remove( sequences ):
                    return
                
                self._model.remove_sequences( sequences )
                self._view.remove_sequences( sequences )
            else:
                QMessageBox.information( self, self.windowTitle(), "Please select a sequence first." )
        elif m==EMode.SUBSEQUENCE:
            subsequences = self._view.selected_subsequences()
        
            if len(subsequences)>=2:
                if not self.__query_remove( subsequences ):
                    return
                
                results = self._model.merge_subsequences( subsequences )
                self._view.recreate_sequences( x.sequence for x in results )
            else:
                QMessageBox.information( self, self.windowTitle(), "Please select at least two adjacent subsequences first." )
        elif m==EMode.EDGE:
            subsequences = self._view.selected_subsequences()
            edges = self._view.selected_edges()
            
            if not edges:
                QMessageBox.information( self, self.windowTitle(), "Please select a subsequence with edges first." )
                return
            
            edge_name, ok = QInputDialog.getItem(self, self.windowTitle(), "Select an edge to delink from the selected subsequence(s)", (str(x) for x in edges))
            
            if not ok:
                return
            
            self._model.remove_edges( subsequences, edges )
            self._view.recreate_edges()
            
        elif m==EMode.COMPONENT:
            QMessageBox.information( self, self.windowTitle(), "Components are automatically generated, you cannot delete them." )


    def __query_remove( self, items : Set[object] )->bool:
        first = ArrayHelper.first(items)
        
        if first is None:
            return False
        
        type_name = type(first).__name__[ 4: ] + "s"
        message = "This will remove {} {}.".format( len( items ), type_name )
        details = "* " + "\n* ".join( str( x ) for x in items )
        message_box = QMessageBox()
        message_box.setText( message )
        message_box.setDetailedText( details )
        message_box.setStandardButtons( QMessageBox.Yes | QMessageBox.No )
        x = message_box.exec_()
        return x  == QMessageBox.Yes
    
    
    @pyqtSlot()
    def on_ACT_SAVE_AS_triggered( self ) -> None:
        """
        Signal handler:
        """
        file_name = QtGuiHelper.browse_save( self, "Genetic lego (*.glego)" )
        self.save_file(file_name)
    
    
    @pyqtSlot()
    def on_ACT_EXPORT_triggered( self ) -> None:
        """
        Signal handler:
        """
        filter = "FASTA (*.fasta)" if self.ui.CHKBTN_DATA_FASTA.isChecked() else "Newick tree (*.newick)"
        file_name = QtGuiHelper.browse_save( self, filter )
        
        if file_name:
            c = []
            
            for a in self.__group_boxes:
                b = a[0] #type: QPushButton
                t = a[1] #type: QTextEdit
                
                if b.isChecked():
                    c.append(t.toPlainText())
                
            FileHelper.write_all_text(file_name, "\n".join(c))
    
    
    @pyqtSlot()
    def on_ACT_SELECT_BY_NAME_triggered( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @pyqtSlot()
    def on_ACT_WIN_REFERENCE_triggered( self ) -> None: #TODO: BAD_HANDLER - The widget 'ACT_WIN_REFERENCE' does not appear in the designer file.
        """
        Signal handler:
        """
        self.ui.DOCK_REFERENCE.setVisible( self.ui.ACT_WIN_REFERENCE.isChecked() )
    
    
    @pyqtSlot()
    def on_ACT_WIN_REFERENCE_visibilityChanged( self, visible ) -> None: #TODO: BAD_HANDLER - The widget 'ACT_WIN_REFERENCE' does not appear in the designer file.
        self.ui.ACT_WIN_REFERENCE.setChecked( visible )
    
    
    @pyqtSlot()
    def on_ACT_WIN_MOVE_visibilityChanged( self, visible ) -> None:
        self.ui.ACT_WIN_MOVE.setChecked( visible )
    
    
    @pyqtSlot()
    def on_ACT_WIN_VIEW_visibilityChanged( self, visible ) -> None:
        self.ui.ACT_WIN_VIEW.setChecked( visible )
    
    
    @pyqtSlot()
    def on_ACT_WIN_EDIT_visibilityChanged( self, visible ) -> None:
        self.ui.ACT_WIN_EDIT.setChecked( visible )
    
    
    @pyqtSlot()
    def on_ACT_WIN_SELECTION_visibilityChanged( self, visible ) -> None:
        self.ui.ACT_WIN_SELECTION.setChecked( visible )
    
    
    @pyqtSlot()
    def on_ACT_WIN_MOVE_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.ui.DOCK_MOVEMENT.setVisible( self.ui.ACT_WIN_MOVE.isChecked() )
    
    
    @pyqtSlot()
    def on_ACT_WIN_VIEW_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.ui.DOCK_VIEW.setVisible( self.ui.ACT_WIN_VIEW.isChecked() )
    
    
    @pyqtSlot()
    def on_ACT_WIN_EDIT_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.ui.DOCK_EDIT.setVisible( self.ui.ACT_WIN_EDIT.isChecked() )
    
    
    @pyqtSlot()
    def on_ACT_WIN_SELECTION_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.ui.DOCK_SELECTION.setVisible( self.ui.ACT_WIN_SELECTION.isChecked() )
        
    @pyqtSlot()
    def on_ACT_DECONVOLUTE_triggered(self) -> None:
        """
        Signal handler:
        """
        self._model.deconvolute()
        self.refresh_model()
        
    @pyqtSlot()
    def on_ACT_ALIGN_triggered(self) -> None:
        """
        Signal handler: Align others to sequence
        """
        sel_sequence = self._view.selected_sequence()
        
        if not sel_sequence:
            QMessageBox.information(self, self.windowTitle(), "Select a single sequence first.")
            return 
        
        self._view.align_to_sequence(sel_sequence)
                
        QMessageBox.information(self, self.windowTitle(), "Aligned data about '{}'.".format(sel_sequence))
                
    @exqtSlot(bool)
    def on_ACT_REMOVE_REDUNDANT_EDGES_triggered(self, _:bool) -> None:
        """
        Signal handler: Remove redundant edges
        """
        self._model.remove_redundant_edges()
        self.refresh_model()
    
    @exqtSlot(bool)
    def on_ACT_SELECT_LEFT_triggered(self, _:bool) -> None:
        """
        Signal handler: Select subsequences to left
        """
        self._view.select_left()
    
    @exqtSlot(bool)
    def on_ACT_SELECT_RIGHT_triggered(self, _:bool) -> None:
        """
        Signal handler: Select subsequences to right
        """
        self._view.select_right()
    
    @exqtSlot(bool)
    def on_ACT_SELECT_DIRECT_CONNECTIONS_triggered(self, _:bool) -> None:
        """
        Signal handler: Select direct connections
        """
        self._view.select_direct_connections()
    
    @exqtSlot(bool)
    def on_ACT_REMOVE_REDUNDANT_SUBSEQUENCES_triggered(self, _:bool) -> None:
        """
        Signal handler: Remove redundant subsequences
        """
        self._model.remove_redundant_subsequences()
        self.refresh_model()
        
    @exqtSlot(bool)
    def on_ACT_ALIGN_SUBSEQUENCES_triggered(self, _ : bool) -> None:
        """
        Signal handler: Align subsequences to precursors
        """
        the_list = self._view.selected_subsequence_views() or self._view.subsequence_views
        
        for x in sorted(the_list, key = lambda x: x.index):
            if x.index != 0:
                x.restore_default_position()
            
    @exqtSlot(bool)
    def on_ACT_CONNECT_COMPONENTS_triggered(self, _:bool) -> None:
        """
        Signal handler:
        """
        self._model.deconvolute()
        self.refresh_model()
    
    @exqtSlot(bool)
    def on_ACT_ALIGN_FIRST_SUBSEQUENCES_triggered(self, _:bool) -> None:
        """
        Signal handler: Align first subsequences
        """
        the_list = self._view.selected_subsequence_views() or self._view.subsequence_views
        
        x = min(x.pos().x() for x in the_list)
        
        for subsequence_view in self._view.selected_subsequence_views():
            if subsequence_view.index == 0:
                subsequence_view.setPos(QPoint(x, subsequence_view.pos().y()))
                subsequence_view.update_model()
                
    @exqtSlot(bool)
    def on_ACT_MARK_AS_COMPOSITE_triggered(self, _:bool) -> None:
        """
        Signal handler:
        """
        for x in self._view.selected_sequences():
            x.is_composite = not x.is_composite
        
    @pyqtSlot()
    def on_ACT_MARK_AS_ROOT_triggered(self) -> None:
        """
        Signal handler:
        """
        for x in self._view.selected_sequences():
            x.is_root = not x.is_root
            
    @pyqtSlot()
    def on_ACT_DEBUG_FIX_triggered(self) -> None:
        """
        Signal handler:
        """
        for sequence in self._model.sequences:
            sequence.is_root = False
            
    @pyqtSlot()
    def on_BTN_SELMASK_PREV_clicked(self) -> None:
        """
        Signal handler: Pass. Handled in action.
        """
        pass
            
    @pyqtSlot()
    def on_BTN_SELMASK_NONE_clicked(self) -> None: #TODO: BAD_HANDLER - The widget 'BTN_SELMASK_NONE' does not appear in the designer file.
        """
        Signal handler: Pass. Handled in action.
        """
        pass
    
    @pyqtSlot()
    def on_BTN_SELMASK_ALL_clicked(self) -> None:
        """
        Signal handler: Pass. Handled in action.
        """
        pass
    
    @pyqtSlot()
    def on_BTN_SELMASK_NEXT_clicked(self) -> None:
        """
        Signal handler: Pass. Handled in action.
        """
        pass
    
    @pyqtSlot()
    def on_ACT_SELMASK_ALL_triggered(self) -> None:
        """
        Signal handler: Select all in mask
        """
        state = not self.__group_boxes[0][0].isChecked()
        
        for x in self.__group_boxes:
            c = x[0] #type: QCheckBox
            c.setChecked(state)
            self.__update_for_checkbox( c )
            
        self._view.scene.update()
    
    @pyqtSlot()
    def on_ACT_SELMASK_NEXT_triggered(self) -> None:
        """
        Signal handler:
        """
        self.__select_next([x[0] for x in self.__group_boxes])


    def __select_next( self, check_boxes : List[QPushButton]):
        first = None
        multiple = False
        
        for check_box in check_boxes:
            if check_box.isChecked():
                if first is None:
                    first = check_box
                else:
                    multiple = True
                    
        if first is None:
            first = ArrayHelper.first(check_boxes)
            multiple = True
        
        defer = False
        
        for check_box in check_boxes:
            if check_box is first:
                if multiple:
                    check_box.setChecked(True)
                else:
                    defer = True
                    check_box.setChecked(False)
            elif defer:
                check_box.setChecked(True)
                defer = False
            else:
                check_box.setChecked(False)
                
            self.__update_for_checkbox( check_box )
                
        if defer:
            check_box = ArrayHelper.first(check_boxes)
            
            if check_box is not None:
                check_box.setChecked(True)
                self.__update_for_checkbox( check_box )
            
        self._view.scene.update()


    @pyqtSlot()
    def on_ACT_SELMASK_PREV_triggered(self) -> None:
        """
        Signal handler:
        """
        self.__select_next(list(reversed([x[0] for x in self.__group_boxes])))
        
    @pyqtSlot()
    def on_CHKBTN_DATA_BLAST_clicked(self) -> None:
        """
        Signal handler:
        """
        pass
            
    @exqtSlot(bool)
    def on_CHKBTN_DATA_FASTA_clicked(self, _:bool) -> None:
        """
        Signal handler: No action
        """
        pass
        
    @exqtSlot(bool)
    def on_CHKBTN_DATA_NEWICK_clicked(self, _:bool) -> None:
        """
        Signal handler: No action
        """
        pass
            
    @exqtSlot()
    def on_BTN_DATA_SAVE_clicked(self, _:bool) -> None:
        """
        Signal handler: Save FASTA / Tree
        """
        pass #TODO
        
    @exqtSlot(bool)
    def on_CHKBTN_DATA_FASTA_toggled(self, _:bool) -> None:
        """
        Signal handler:
        """
        self.ILegoViewModelObserver_selection_changed()
        
    @exqtSlot(bool)
    def on_CHKBTN_DATA_NEWICK_toggled(self, _:bool) -> None:
        """
        Signal handler: View data
        """
        self.ILegoViewModelObserver_selection_changed()
            
    @exqtSlot()
    def on_ACT_COMPONENT_COMPARTMENTALISE_triggered( self:bool ) -> None:
        """
        Signal handler: Compartmentalise model
        """
        self._model.compartmentalise()
        self.refresh_model()

    @exqtSlot( int )
    def on_CHK_VIEW_EDGES_stateChanged( self, _ :int):   
        self.update_options()
    
    
    @exqtSlot( int )
    def on_CHK_VIEW_COMPONENTS_stateChanged( self, _:int ):   
        self.update_options()
    
    
    @exqtSlot( int )
    def on_CHK_VIEW_NAMES_stateChanged( self, _:int ):   
        self.update_options()
    
    
    @exqtSlot( int )
    def on_CHK_VIEW_PIANO_ROLLS_stateChanged( self, _ :int):   
        self.update_options()
    
    
    @exqtSlot( int )
    def on_CHK_VIEW_POSITIONS_stateChanged( self, _:int ):   
        self.update_options()
    
    
    @exqtSlot( int )
    def on_CHK_MOVE_XSNAP_stateChanged( self, _:int ):   
        self.update_options()
    
    
    @exqtSlot( int )
    def on_CHK_MOVE_YSNAP_stateChanged( self, _:int ):   
        self.update_options()
    
    
    @exqtSlot( int )
    def on_SLI_BLEND_valueChanged( self, _ :int): 
        self.update_options()