"""
Main form
"""
import sip
from typing import Any, List, Optional, Set, Union, cast

from PyQt5.QtCore import QCoreApplication, QPoint, QRectF, Qt
from PyQt5.QtGui import QBrush, QColor
from PyQt5.QtOpenGL import QGL, QGLFormat, QGLWidget
from PyQt5.QtWidgets import QAction, QCheckBox, QFileDialog, QGraphicsScene, QGridLayout, QGroupBox, QInputDialog, QMainWindow, QMessageBox, QPushButton, QSizePolicy, QTextEdit, QVBoxLayout, QWidget

from groot import constants, extensions as COMMANDS
from groot.data import global_view, user_options
from groot.data.lego_model import LegoComponent
from groot.frontends.gui.forms.designer.frm_main_designer import Ui_MainWindow
from groot.frontends.gui.gui_view import EMode, ESelect, ILegoViewModelObserver, LegoViewModel, LegoViewSubsequence
from groot.frontends.gui.gui_view_utils import Changes, MyView
from groot.frontends.cli import cli_view_utils
from intermake.engine.async_result import AsyncResult
from intermake.engine.environment import MENV
from intermake.hosts.frontends.gui_qt.frm_arguments import FrmArguments
from mhelper import SwitchError, array_helper, file_helper, qt_gui_helper
from mhelper.qt_gui_helper import exceptToGui, exqtSlot


class FrmMain( QMainWindow, ILegoViewModelObserver ):
    """
    Main window
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        self.no_update_options = False
        self.__group_boxes = [ ]
        
        QCoreApplication.setAttribute( Qt.AA_DontUseNativeMenuBar )
        
        # QT stuff
        QMainWindow.__init__( self )
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )
        self.setWindowTitle( "Lego Model Creator" )
        
        
        self.ui.DOCK_VIEW.setVisible( False )
        
        
        # Graphics view
        self.ui.graphicsView = MyView()
        sizePolicy = QSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding )
        sizePolicy.setHeightForWidth( self.ui.graphicsView.sizePolicy().hasHeightForWidth() )
        self.ui.graphicsView.setSizePolicy( sizePolicy )
        self.ui.graphicsView.setObjectName( "graphicsView" )
        self.ui.graphicsView.setBackgroundBrush( QBrush( QColor( 255, 255, 255 ) ) )
        
        layout = QGridLayout()
        self.ui.FRA_MAIN.setLayout( layout )
        layout.addWidget( self.ui.graphicsView )
        
        # Open GL rendering
        self.ui.graphicsView.setViewport( QGLWidget( QGLFormat( QGL.SampleBuffers ) ) )
        # self.ui.graphicsView.resizeEvent()
        
        # Default (empty) scene
        scene = QGraphicsScene()
        scene.addRect( QRectF( -10, -10, 20, 20 ) )
        self.ui.graphicsView.setInteractive( True )
        self.ui.graphicsView.setScene( scene )
        
        for sample_dir in global_view.get_samples():
            action = QAction( file_helper.get_filename( sample_dir ), self )
            action.setStatusTip( sample_dir )
            # noinspection PyUnresolvedReferences
            action.triggered[ bool ].connect( self.__select_sample_data )
            self.ui.MNU_EXAMPLES.addAction( action )
        
        self._view = None  # type:LegoViewModel
        self.__update_as_required( (Changes.MODEL_OBJECT, Changes.FILE_NAME) )
        
        # if global_view:
        #     self.load_file( self.global_options.recent_files[ -1 ], errors = False )
    
    
    @property
    def _model( self ):
        return global_view.current_model()
    
    
    @exceptToGui()
    def __select_sample_data( self, _: bool ):
        sample_name = file_helper.get_file_name( self.sender().statusTip() )
        COMMANDS.ext_files.file_sample( sample_name )
    
    
    def recent_file_triggered( self ):
        file_name = self.sender().statusTip()
        COMMANDS.ext_files.file_load( file_name )
    
    
    def on_scene_selectionChanged( self ):
        if len( self._view.scene.selectedItems() ) == 0:
            self.ILegoViewModelObserver_selection_changed()
    
    
    def ILegoViewModelObserver_selection_changed( self ):
        #
        # What have we selected?
        #
        entities = self._view.selected_entities()
        first = array_helper.first( entities )
        type_name = (type( first ).__name__[ 4: ].upper() + ("s" if len( entities ) > 1 else "")) if entities else None
        self._view.clear_selection_mask()
        
        self.ui.BTN_SELMASK_ALL.setText( str( len( entities ) ) )
        
        #
        # Delete existing controls
        #
        for group_box in self.__group_boxes:  # type: List[QWidget]
            for widget in group_box:  # type: QWidget
                widget.parentWidget().layout().removeWidget( widget )
                # noinspection PyTypeChecker
                sip.delete( widget )
        
        self.__group_boxes.clear()
        
        # Status bar
        #
        if len( entities ) == 0:
            self.statusBar().showMessage( "SELECTED: <<NOTHING>>" )
            return
        elif len( entities ) == 1:
            self.statusBar().showMessage( "SELECTED: <«{}»> {}".format( type_name, first ) )
        else:
            self.statusBar().showMessage( "SELECTED: <<MULTIPLE ITEMS>> ({} {})".format( len( entities ), type_name ) )
        
        for entity in entities:
            assert entity is not None
            
            #
            # Controls
            #
            group_box = QGroupBox()
            group_box.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Minimum )
            group_box.setTitle( type( entity ).__name__[ 4: ] + " : " + str( entity ) )
            self.ui.SCR_AREA.layout().addWidget( group_box )
            
            layout = QVBoxLayout()
            group_box.setLayout( layout )
            
            
            def __check_box( _: bool ):
                check_box = self.sender()  # type: QPushButton
                
                if not isinstance( check_box, QPushButton ):
                    return
                
                self.__update_for_checkbox( check_box )
                self._view.scene.update()
            
            
            check_box = QPushButton()
            check_box.setText( "Selected" )
            check_box.setCheckable( True )
            check_box.setChecked( True )
            check_box.toggled[ bool ].connect( __check_box )
            check_box.setProperty( "entity", entity )
            layout.addWidget( check_box )
            
            multiline = len( entities ) > 1 or not self.ui.CHKBTN_DATA_FASTA.isChecked()
            
            text_edit = QTextEdit()
            text_edit.setLineWrapMode( QTextEdit.NoWrap if multiline else QTextEdit.WidgetWidth )
            text_edit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding if multiline else QSizePolicy.Minimum )
            text_edit.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOn )
            text_edit.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOn )
            text_edit.setStyleSheet( "background: black; color: white;" )
            layout.addWidget( text_edit )
            
            self.__group_boxes.append( (check_box, text_edit, group_box) )
            
            content = [ ]
            
            if self.ui.CHKBTN_DATA_NEWICK.isChecked():
                # content.append(">"+str(entity))
                
                if isinstance( entity, LegoComponent ):
                    if entity.tree:
                        content.append( entity.tree )
                    else:
                        content.append( "; MISSING - Generate a tree first!" )
                else:
                    content.append( "; NOT AVAILABLE - Only available for components" )
            elif self.ui.CHKBTN_DATA_FASTA.isChecked():
                if hasattr( entity, "to_fasta" ):
                    fasta = entity.to_fasta( header = False )
                    content.append( fasta )
                else:
                    # content.append(">"+str(entity))
                    content.append( "; NOT AVAILABLE" )
            elif self.ui.CHKBTN_DATA_BLAST.isChecked():
                if hasattr( entity, "comments" ):
                    content.append( "\n".join( entity.comments ) )
                else:
                    content.append( "; NOT AVAILABLE" )
            
            content = "\n\n".join( content )
            
            if self.ui.CHKBTN_DATA_FASTA.isChecked():
                content = qt_gui_helper.ansi_to_html( cli_view_utils.colour_fasta_ansi( content ), qt_gui_helper.ansi_scheme_light() )
            
            text_edit.setText( content )
    
    
    def __update_for_checkbox( self, check_box: Union[ QCheckBox, QPushButton ] ):
        assert isinstance( check_box, QPushButton ) or isinstance( check_box, QCheckBox ), check_box
        
        entity = check_box.property( "entity" )
        assert entity is not None
        
        state = check_box.isChecked()
        self._view.set_selection_mask( entity, state )
    
    
    def ILegoViewModelObserver_options_changed( self ):
        self.update_selection_buttons()
    
    
    def subsequence_view_focus( self, subsequence_view: LegoViewSubsequence ):
        """
        CALLBACK
        When subsequence view changes
        """
        pass
    
    
    def update_selection_buttons( self ):
        self.no_update_options = True
        
        o = self._view.options
        
        self.ui.CHK_MOVE_XSNAP.setChecked( o.x_snap )
        self.ui.CHK_MOVE_YSNAP.setChecked( o.y_snap )
        self.ui.CHK_VIEW_EDGES.setCheckState( qt_gui_helper.to_check_state( o.view_edges ) )
        self.ui.CHK_VIEW_NAMES.setCheckState( qt_gui_helper.to_check_state( o.view_names ) )
        self.ui.CHK_VIEW_PIANO_ROLLS.setCheckState( qt_gui_helper.to_check_state( o.view_piano_roll ) )
        self.ui.CHK_VIEW_POSITIONS.setCheckState( qt_gui_helper.to_check_state( o.view_positions ) )
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
        
        o = self._view.options
        o.x_snap = self.ui.CHK_MOVE_XSNAP.isChecked()
        o.y_snap = self.ui.CHK_MOVE_YSNAP.isChecked()
        o.view_edges = qt_gui_helper.from_check_state( self.ui.CHK_VIEW_EDGES.checkState() )
        o.view_names = qt_gui_helper.from_check_state( self.ui.CHK_VIEW_NAMES.checkState() )
        o.view_piano_roll = qt_gui_helper.from_check_state( self.ui.CHK_VIEW_PIANO_ROLLS.checkState() )
        o.view_positions = qt_gui_helper.from_check_state( self.ui.CHK_VIEW_POSITIONS.checkState() )
        o.move_enabled = self.ui.CHK_MOVE.isChecked()
        self.update_selection_buttons()
        
        self._view.scene.update()
        self.no_update_options = False
    
    
    def plugin_completed( self, result: AsyncResult ):
        result_value = result.result
        
        if isinstance( result_value, Changes ):
            changes = result_value.changes
            self.__update_as_required( changes )
            
            if Changes.INFORMATION in changes:
                html = qt_gui_helper.ansi_to_html( "\n".join( result.messages ), qt_gui_helper.ansi_scheme_light() )
                QMessageBox.information( self, self.windowTitle(), html )
    
    
    def __update_as_required( self, changes ):
        gv = cast( MyView, cast( Any, self.ui ).graphicsView )
        if Changes.MODEL_OBJECT in changes \
                or Changes.MODEL_ENTITIES in changes:
            self.no_update_options = True
            first_load = self._view is None
            self._view = LegoViewModel( self, gv, self.subsequence_view_focus, self._model )
            gv.setScene( self._view.scene )
            
            self._view.scene.selectionChanged.connect( self.on_scene_selectionChanged )
            
            if first_load:
                self.update_selection_buttons()
            else:
                self.no_update_options = False
                self.update_options()
        if Changes.COMPONENTS in changes:
            gv.update()
        if Changes.COMP_DATA in changes \
                or Changes.MODEL_DATA in changes:
            pass
        if Changes.FILE_NAME in changes:
            self.setWindowTitle( MENV.name + " - " + str( self._model ) )
            
            self.ui.MNU_RECENT.clear()
            
            for x in user_options.options().recent_files:
                action = QAction( x, self )
                action.setStatusTip( x )
                # noinspection PyUnresolvedReferences
                action.triggered.connect( self.recent_file_triggered )
                self.ui.MNU_RECENT.addAction( action )
    
    
    @exqtSlot( bool )
    def on_ACT_APP_EXIT_triggered( self, _: bool ) -> None:
        """
        Signal handler: Exit application
        """
        self.close()
    
    
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
    
    
    @exqtSlot()
    def on_ACT_HELP_KEYS_triggered( self ) -> None:
        """
        Signal handler:
        """
        keys = "Left click = Select subsequence|Double click = Select sequence|Double click + Alt = Select edge|Left click + Control = Add to selection|Left drag = Move selection|Left drag + Control = Move selection (toggle X-snap)|Left drag + Alt = Move selection (toggle Y-snap)"
        
        QMessageBox.information( self, "Keys", keys.replace( "|", "\n" ) )
    
    
    @exqtSlot()
    def on_ACT_SELECT_ALL_triggered( self ) -> None:
        """
        Signal handler:
        """
        self._view.select_all( ESelect.APPEND )
    
    
    @exqtSlot()
    def on_ACT_SELECT_NONE_triggered( self ) -> None:
        """
        Signal handler:
        """
        self._view.select_all( ESelect.REMOVE )
    
    
    @exqtSlot()
    def on_ACT_SELECT_EMPTY_triggered( self ) -> None:
        """
        Signal handler:
        """
        self._view.select_empty()
    
    
    @exqtSlot()
    def on_ACT_SELECTION_INVERT_triggered( self ) -> None:
        """
        Signal handler:
        """
        self._view.select_all( ESelect.TOGGLE )
    
    
    @exqtSlot()
    def on_ACT_SELECT_SEQUENCE_triggered( self ) -> None:
        """
        Signal handler: Sequence selection mode
        """
        if self.no_update_options:
            return
        
        self._view.options.mode = EMode.SEQUENCE
        self.update_options()
    
    
    @exqtSlot()
    def on_ACT_SELECT_SUBSEQUENCE_triggered( self ) -> None:
        """
        Signal handler: Subsequence selection mode
        """
        if self.no_update_options:
            return
        
        self._view.options.mode = EMode.SUBSEQUENCE
        self.update_options()
    
    
    @exqtSlot()
    def on_ACT_SELECT_EDGE_triggered( self ) -> None:
        """
        Signal handler: Edge selection mode
        """
        if self.no_update_options:
            return
        
        self._view.options.mode = EMode.EDGE
        self.update_options()
    
    
    @exqtSlot()
    def on_ACT_SELECT_COMPONENT_triggered( self ) -> None:
        """
        Signal handler: Component selection mode
        """
        if self.no_update_options:
            return
        
        self._view.options.mode = EMode.COMPONENT
        self.update_options()
    
    
    @staticmethod
    def __query_remove( items: Set[ object] ) -> bool:
        first = array_helper.first( items )
        
        if first is None:
            return False
        
        type_name = type( first ).__name__[ 4: ] + "s"
        message = "This will remove {} {}.".format( len( items ), type_name )
        details = "* " + "\n* ".join( str( x ) for x in items )
        message_box = QMessageBox()
        message_box.setText( message )
        message_box.setDetailedText( details )
        message_box.setStandardButtons( QMessageBox.Yes | QMessageBox.No )
        x = message_box.exec_()
        return x == QMessageBox.Yes
    
    
    @exqtSlot()
    def on_ACT_SELECT_BY_NAME_triggered( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot( bool )
    def on_ACT_SELECT_LEFT_triggered( self, _: bool ) -> None:
        """
        Signal handler: Select subsequences to left
        """
        self._view.select_left()
    
    
    @exqtSlot( bool )
    def on_ACT_SELECT_RIGHT_triggered( self, _: bool ) -> None:
        """
        Signal handler: Select subsequences to right
        """
        self._view.select_right()
    
    
    @exqtSlot( bool )
    def on_ACT_SELECT_DIRECT_CONNECTIONS_triggered( self, _: bool ) -> None:
        """
        Signal handler: Select direct connections
        """
        self._view.select_direct_connections()
    
    
    @exqtSlot()
    def on_ACT_FILE_NEW_triggered( self ) -> None:
        """
        Signal handler: New model
        """
        COMMANDS.ext_files.file_new.run()
    
    
    @exqtSlot()
    def on_ACT_FILE_IMPORT_triggered( self ) -> None:
        """
        Signal handler: Import data
        """
        filters = "Valid files (*.fasta *.fa *.faa *.blast *.tsv *.composites *.txt *.comp)", "FASTA files (*.fasta *.fa *.faa)", "BLAST output (*.blast *.tsv)", "Composite finder output (*.composites)"
        
        file_name, filter = QFileDialog.getOpenFileName( self, "Select file", None, ";;".join( filters ), options = QFileDialog.DontUseNativeDialog )
        
        if not file_name:
            return
        
        filter_index = filters.index( filter )
        
        if filter_index == 0:
            COMMANDS.ext_files.import_file( self._model, file_name )
        elif filter_index == 0:
            COMMANDS.ext_files.import_fasta( self._model, file_name )
        elif filter_index == 1:
            COMMANDS.ext_files.import_blast( self._model, file_name )
        elif filter_index == 2:
            COMMANDS.ext_files.import_composites( self._model, file_name )
        else:
            raise SwitchError( "filter_index", filter_index )
    
    
    @exqtSlot()
    def on_ACT_FILE_SAVE_triggered( self ) -> None:
        """
        Signal handler: File - save model
        """
        if self._model_file_name:
            file_name = self._model_file_name
        else:
            file_name = qt_gui_helper.browse_save( self, constants.DIALOGUE_FILTER )
        
        self.save_file( file_name )
    
    
    @exqtSlot()
    def on_ACT_FILE_OPEN_triggered( self ) -> None:
        """
        Signal handler: File - open model
        """
        file_name = qt_gui_helper.browse_open( self, constants.DIALOGUE_FILTER )
        
        if file_name:
            COMMANDS.ext_files.file_load( file_name )
    
    
    @exqtSlot()
    def on_ACT_FILE_SAVE_AS_triggered( self ) -> None:
        """
        Signal handler: File - save model as
        """
        file_name = qt_gui_helper.browse_save( self, constants.DIALOGUE_FILTER )
        self.save_file( file_name )
    
    
    @exqtSlot()
    def on_ACT_FILE_EXPORT_triggered( self ) -> None:
        """
        Signal handler: File - export
        """
        filter = constants.DIALOGUE_FILTER_FASTA if self.ui.CHKBTN_DATA_FASTA.isChecked() else constants.DIALOGUE_FILTER_NEWICK
        file_name = qt_gui_helper.browse_save( self, filter )
        
        if file_name:
            c = [ ]
            
            for a in self.__group_boxes:
                b = a[ 0 ]  # type: QPushButton
                t = a[ 1 ]  # type: QTextEdit
                
                if b.isChecked():
                    c.append( t.toPlainText() )
            
            file_helper.write_all_text( file_name, "\n".join( c ) )
    
    
    
    @exqtSlot()
    def on_ACT_WINDOW_EDIT_triggered( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_ACT_WINDOW_SELECTION_triggered( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_ACT_VIEW_ALIGN_triggered( self ) -> None:
        """
        Signal handler: Align selection
        """
        sel_sequence = self._view.selected_sequence()
        
        if not sel_sequence:
            QMessageBox.information( self, self.windowTitle(), "Select a single sequence first." )
            return
        
        self._view.align_to_sequence( sel_sequence )
        
        QMessageBox.information( self, self.windowTitle(), "Aligned data about '{}'.".format( sel_sequence ) )
    
    
    @exqtSlot()
    def on_ACT_VIEW_ALIGN_SUBSEQUENCES_triggered( self ) -> None:
        """
        Signal handler: View - align subsequences
        """
        the_list = self._view.selected_subsequence_views() or self._view.subsequence_views
        
        for x in sorted( the_list, key = lambda x: x.index ):
            if x.index != 0:
                x.restore_default_position()
    
    
    @exqtSlot()
    def on_ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES_triggered( self ) -> None:
        """
        Signal handler: View - align first subsequences in sequence
        """
        the_list = self._view.selected_subsequence_views() or self._view.subsequence_views
        
        x = min( x.pos().x() for x in the_list )
        
        for subsequence_view in self._view.selected_subsequence_views():
            if subsequence_view.index == 0:
                subsequence_view.setPos( QPoint( x, subsequence_view.pos().y() ) )
                subsequence_view.update_model()
    
    
    @exqtSlot()
    def on_ACT_EDIT_SUBSEL_ALL_triggered( self ) -> None:
        """
        Signal handler: Highlight all elements of the selection
        """
        state = not self.__group_boxes[ 0 ][ 0 ].isChecked()
        
        for x in self.__group_boxes:
            c = x[ 0 ]  # type: QCheckBox
            c.setChecked( state )
            self.__update_for_checkbox( c )
        
        self._view.scene.update()
    
    
    @exqtSlot()
    def on_ACT_EDIT_SUBSEL_NEXT_triggered( self ) -> None:
        """
        Signal handler: Highlight the next element of the selection
        """
        self.__select_next( [ x[ 0 ] for x in self.__group_boxes ] )
    
    
    @exqtSlot()
    def on_ACT_EDIT_SUBSEL_PREV_triggered( self ) -> None:
        """
        Signal handler: Highlight the previous element of the selection
        """
        self.__select_next( list( reversed( [ x[ 0 ] for x in self.__group_boxes ] ) ) )
    
    
    @exqtSlot()
    def on_ACT_MAKE_COMPONENTS_triggered( self ) -> None:
        """
        Signal handler: Make - components
        """
        FrmArguments.request( self, COMMANDS.ext_generating.make_components )
    
    
    @exqtSlot()
    def on_ACT_MAKE_ALIGNMENTS_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_generating.make_alignment, defaults = [ list( self._view.selected_components() ) ] )
    
    
    @exqtSlot()
    def on_ACT_MAKE_TREE_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_generating.make_tree, defaults = [ list( self._view.selected_components() ) ] )
    
    
    @exqtSlot()
    def on_ACT_MAKE_CONSENSUS_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_generating.make_consensus, defaults = [ list( self._view.selected_components() ) ] )
    
    
    @exqtSlot()
    def on_ACT_MAKE_NRFG_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_generating.make_nrfg )
    
    
    @exqtSlot()
    def on_ACT_MAKE_FUSIONS_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_generating.make_fusions )
    
    
    @exqtSlot()
    def on_ACT_MODIFY_CLEAN_triggered( self ) -> None:
        """
        Signal handler: Modify - Clean model
        """
        COMMANDS.ext_modifications.clean()
    
    
    @exqtSlot()
    def on_ACT_MODIFY_SET_TREE_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_modifications.set_tree )
    
    
    @exqtSlot()
    def on_ACT_MODIFY_SET_ALIGNMENT_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_modifications.set_alignment )
    
    
    @exqtSlot()
    def on_ACT_MODIFY_QUANTISE_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_modifications.quantise )
    
    
    @exqtSlot()
    def on_ACT_PRINT_FASTA_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_viewing.print_fasta, defaults = [ array_helper.first( self._view.selected_entities() ) ] )
    
    
    @exqtSlot()
    def on_ACT_PRINT_STATUS_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_viewing.print_status )
    
    
    @exqtSlot()
    def on_ACT_PRINT_ALIGNMENT_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_viewing.print_alignment, defaults = [ array_helper.first( self._view.selected_components() ) ] )
    
    
    @exqtSlot()
    def on_ACT_PRINT_CONSENSUS_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_viewing.print_consensus, defaults = [ array_helper.first( self._view.selected_components() ) ] )
    
    
    @exqtSlot()
    def on_ACT_PRINT_TREE_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_viewing.print_tree, defaults = [ array_helper.first( self._view.selected_components() ) ] )
    
    
    @exqtSlot()
    def on_ACT_PRINT_COMPONENT_EDGES_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_viewing.print_component_edges, defaults = [array_helper.first( self._view.selected_components() )] )
    
    
    @exqtSlot()
    def on_ACT_PRINT_COMPONENTS_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_viewing.print_components )
    
    
    @exqtSlot()
    def on_ACT_PRINT_FUSIONS_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_viewing.print_fusions )
    
    
    @exqtSlot()
    def on_ACT_PRINT_NRFG_triggered( self ) -> None:
        """
        Signal handler:
        """
        FrmArguments.request( self, COMMANDS.ext_viewing.print_nrfg )
    
    
    @exqtSlot()
    def on_ACTION_VIEW_INTERMAKE_triggered( self ) -> None:
        """
        Signal handler:
        """
        from intermake.hosts.frontends.gui_qt.frm_main import FrmMain as McFrmMain
        frm = McFrmMain( True )
        frm.show()
    
    
    @exqtSlot()
    def on_ACT_MODIFY_NEW_ENTITY_triggered( self ) -> None:
        """
        Signal handler: New entity
        """
        m = self._view.options.mode
        
        if m == EMode.SEQUENCE:
            COMMANDS.ext_modifications.new_sequence()
        elif m == EMode.SUBSEQUENCE:
            subsequences = self._view.selected_subsequences()
            
            if not subsequences:
                QMessageBox.information( self, self.windowTitle(), "Select a subsequence to split first." )
                return
            
            sequence = array_helper.first( subsequences ).sequence
            
            if not all( x.sequence is sequence for x in subsequences ):
                QMessageBox.information( self, self.windowTitle(), "All of the the selected subsequences must be in the same sequence." )
                return
            
            # noinspection PyUnresolvedReferences
            default_split = (min( x.start for x in subsequences ) + max( x.end for x in subsequences )) // 2
            split_point, ok = QInputDialog.getInt( self, self.windowTitle(), "Split the sequence '{0}' into [1:x] and [x+1:n] where x = ".format( sequence ), default_split, 1, sequence.length )
            
            if not ok:
                return
            
            COMMANDS.ext_modifications.new_subsequence( sequence, split_point )
        elif m == EMode.EDGE:
            subsequences = self.selected_subsequences()
            
            COMMANDS.ext_modifications.new_edge( subsequences )
        elif m == EMode.COMPONENT:
            QMessageBox.information( self, self.windowTitle(), "Components are automatically generated, you cannot create new ones manually." )
    
    
    @exqtSlot()
    def on_ACT_MODIFY_REMOVE_ENTITY_triggered( self ) -> None:
        """
        Signal handler: Remove entity
        """
        m = self._view.options.mode
        
        if m == EMode.SEQUENCE:
            sequences = self._view.selected_sequences()
            
            if sequences:
                if not self.__query_remove( sequences ):
                    return
                
                COMMANDS.ext_modifications.remove_sequence( sequences )
            else:
                QMessageBox.information( self, self.windowTitle(), "Please select a sequence first." )
        elif m == EMode.SUBSEQUENCE:
            subsequences = self._view.selected_subsequences()
            
            if len( subsequences ) >= 2:
                if not self.__query_remove( subsequences ):
                    return
                
                COMMANDS.ext_modifications.merge_subsequences( subsequences )
            else:
                QMessageBox.information( self, self.windowTitle(), "Please select at least two adjacent subsequences first." )
        elif m == EMode.EDGE:
            subsequences = self._view.selected_subsequences()
            edges = self._view.selected_edges()
            
            if not edges:
                QMessageBox.information( self, self.windowTitle(), "Please select a subsequence with edges first." )
                return
            
            edge_name, ok = QInputDialog.getItem( self, self.windowTitle(), "Select an edge to delink from the selected subsequence(s)", (str( x ) for x in edges) )
            
            if not ok:
                return
            
            COMMANDS.ext_modifications.remove_edges( subsequences, edges )
        elif m == EMode.COMPONENT:
            QMessageBox.information( self, self.windowTitle(), "Components are automatically generated, you cannot delete them." )
    
    
    @exqtSlot()
    def on_BTN_SELMASK_PREV_clicked( self ) -> None:
        """
        Signal handler: Pass. Handled in action.
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_SELMASK_ALL_clicked( self ) -> None:
        """
        Signal handler: Pass. Handled in action.
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_SELMASK_NEXT_clicked( self ) -> None:
        """
        Signal handler: Pass. Handled in action.
        """
        pass
    
    
    def __select_next( self, check_boxes: List[ QPushButton ] ):
        first = None
        multiple = False
        
        for check_box in check_boxes:
            if check_box.isChecked():
                if first is None:
                    first = check_box
                else:
                    multiple = True
        
        if first is None:
            first = array_helper.first( check_boxes )
            multiple = True
        
        defer = False
        
        for check_box in check_boxes:
            if check_box is first:
                if multiple:
                    check_box.setChecked( True )
                else:
                    defer = True
                    check_box.setChecked( False )
            elif defer:
                check_box.setChecked( True )
                defer = False
            else:
                check_box.setChecked( False )
            
            self.__update_for_checkbox( check_box )
        
        if defer:
            check_box = array_helper.first( check_boxes )
            
            if check_box is not None:
                check_box.setChecked( True )
                self.__update_for_checkbox( check_box )
        
        self._view.scene.update()
    
    
    @exqtSlot()
    def on_CHKBTN_DATA_BLAST_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot( bool )
    def on_CHKBTN_DATA_FASTA_clicked( self, _: bool ) -> None:
        """
        Signal handler: No action
        """
        pass
    
    
    @exqtSlot( bool )
    def on_CHKBTN_DATA_NEWICK_clicked( self, _: bool ) -> None:
        """
        Signal handler: No action
        """
        pass
    
    
    @exqtSlot( bool )
    def on_CHKBTN_DATA_FASTA_toggled( self, _: bool ) -> None:
        """
        Signal handler:
        """
        self.ILegoViewModelObserver_selection_changed()
    
    
    @exqtSlot( bool )
    def on_CHKBTN_DATA_NEWICK_toggled( self, _: bool ) -> None:
        """
        Signal handler: View data
        """
        self.ILegoViewModelObserver_selection_changed()
    
    
    @exqtSlot( int )
    def on_CHK_VIEW_EDGES_stateChanged( self, _: int ):
        self.update_options()
    
    
    @exqtSlot( int )
    def on_CHK_VIEW_NAMES_stateChanged( self, _: int ):
        self.update_options()
    
    
    @exqtSlot( int )
    def on_CHK_VIEW_PIANO_ROLLS_stateChanged( self, _: int ):
        self.update_options()
    
    
    @exqtSlot( int )
    def on_CHK_VIEW_POSITIONS_stateChanged( self, _: int ):
        self.update_options()
    
    
    @exqtSlot( int )
    def on_CHK_MOVE_XSNAP_stateChanged( self, _: int ):
        self.update_options()
    
    
    @exqtSlot( int )
    def on_CHK_MOVE_YSNAP_stateChanged( self, _: int ):
        self.update_options()
