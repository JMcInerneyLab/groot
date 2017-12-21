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

from groot import constants, extensions as COMMANDS
from groot.algorithms import fastaiser
from groot.data import global_view, user_options
from groot.data.lego_model import ILegoVisualisable, LegoComponent
from groot.frontends.cli import cli_view_utils
from groot.frontends.gui.forms.frm_view_options import FrmViewOptions
from groot.frontends.gui.gui_view import EMode, ESelect, ILegoViewModelObserver, LegoViewModel
from groot.frontends.gui.gui_view_utils import EChanges, MyView
from intermake import AsyncResult, MENV, Plugin, intermake_gui
from intermake.hosts.frontends.gui_qt.frm_arguments import FrmArguments
from intermake.hosts.gui import IGuiPluginHostWindow
from mhelper import SwitchError, ansi, array_helper, file_helper, string_helper
from mhelper_qt import qt_gui_helper
from mhelper_qt.qt_gui_helper import exceptToGui, exqtSlot


class FrmMain( QMainWindow, ILegoViewModelObserver, IGuiPluginHostWindow ):
    """
    Main window
    """
    
    
    def __init__( self ) -> None:
        """
        CONSTRUCTOR
        """
        # QT stuff
        QCoreApplication.setAttribute( Qt.AA_DontUseNativeMenuBar )
        QMainWindow.__init__( self )
        self.ui = Ui_MainWindow()
        self.ui.setupUi( self )
        self.setWindowTitle( "Lego Model Creator" )
        self.setStyleSheet( intermake_gui.default_style_sheet() )
        
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
        
        # Default (empty) scene
        scene = QGraphicsScene()
        scene.addRect( QRectF( -10, -10, 20, 20 ) )
        self.ui.graphicsView.setInteractive( True )
        self.ui.graphicsView.setScene( scene )
        
        for sample_dir in global_view.get_samples():
            action = QAction( file_helper.get_filename( sample_dir ), self )
            action.setStatusTip( sample_dir )
            action.triggered[bool].connect( self.__select_sample_data )
            self.ui.MNU_EXAMPLES.addAction( action )
        
        self._view: LegoViewModel = None
        self.__update_as_required( EChanges.MODEL_OBJECT | EChanges.FILE_NAME )
        
        # Misc
        self.__group_boxes = []
        self.ANSI_SCHEME = qt_gui_helper.ansi_scheme_dark( family = 'Consolas,"Courier New",monospace' )
    
    
    def __update_as_required( self, changes: EChanges ) -> None:
        view: MyView = cast( Any, self.ui ).graphicsView
        
        print( "updating to " + str( changes ) )
        
        if changes.MODEL_OBJECT or changes.MODEL_ENTITIES or changes.COMPONENTS:
            # The model or its contents have changed
            self.freeze_options = True
            
            # Create and apply a view for the model
            if self._view:
                self._view.scene.setParent( None )
            
            self._view = LegoViewModel( self, view, self._model )
            view.setScene( self._view.scene )
            
            # Track the selection
            self._view.scene.selectionChanged.connect( self.on_scene_selectionChanged )
        
        if changes.MODEL_OBJECT or changes.MODEL_ENTITIES or changes.COMPONENTS or changes.COMP_DATA or changes.MODEL_DATA:
            # Update the options
            self._update_status_checkbox_values()
        
        if changes.FILE_NAME:
            # The filename is only reflected in the title
            self.setWindowTitle( MENV.name + " - " + str( self._model ) )
            
            self.ui.MNU_RECENT.clear()
            
            for x in user_options.options().recent_files:
                action = QAction( x, self )
                action.setStatusTip( x )
                action.triggered.connect( self.recent_file_triggered )
                self.ui.MNU_RECENT.addAction( action )
    
    
    def _update_status_checkbox_values( self ):
        self.ui.BTN_STATUS_ALIGNMENTS.setChecked( all( x.alignment is not None for x in self._model.components ) )
        self.ui.BTN_STATUS_BLAST.setChecked( len( self._model.edges ) != 0 )
        self.ui.BTN_STATUS_FASTA.setChecked( all( x.site_array for x in self._model.sequences ) )
        self.ui.BTN_STATUS_FUSIONS.setChecked( bool( self._model.fusion_events ) )
        self.ui.BTN_STATUS_COMPONENTS.setChecked( len( self._model.components ) != 0 )
        self.ui.BTN_STATUS_TREES.setChecked( all( x.tree is not None for x in self._model.components ) )
        self.ui.BTN_STATUS_NRFG.setChecked( self._model.nrfg is not None )
    
    
    def plugin_completed( self, result: AsyncResult ):
        print( "plugin_completed : " + str( result ) )
        
        if result.is_error:
            qt_gui_helper.show_exception( self, "The operation did not complete.", result.exception )
        else:
            result_value = result.result
            
            if isinstance( result_value, EChanges ):
                self.__update_as_required( result_value )
    
    
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
    
    
    def ILegoViewModelObserver_selection_changed( self ):
        """
        Selection has changed.
        """
        
        #
        # What have we selected?
        #
        entities: Set[ILegoVisualisable] = self._view.selected_entities()
        first: ILegoVisualisable = array_helper.first( entities )
        type_name: str = (type( first ).__name__[4:].upper() + ("s" if len( entities ) > 1 else "")) if entities else None
        
        #
        # Delete existing controls
        #
        for group_box in self.__group_boxes:  # type: List[QWidget]
            for widget in group_box:
                if isinstance( widget, QWidget ):
                    widget.parentWidget().layout().removeWidget( widget )
                    sip.delete( widget )
        
        self.__group_boxes.clear()
        
        #
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
            assert isinstance( entity, ILegoVisualisable )
            entity_type = type( entity ).__name__[4:]
            entity_name = entity_type + " : " + str( entity )
            
            #
            # Controls
            #
            
            # - Frame
            group_box = QFrame()
            group_box.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Minimum )
            self.ui.SCR_AREA.layout().addWidget( group_box )
            
            # - Layout
            layout = QVBoxLayout()
            group_box.setLayout( layout )
            
            # - Highlight/name button
            select_only_button = QPushButton()
            select_only_button.setText( entity_name )
            handler = self.__on__check_box( self, entity )
            select_only_button.clicked[bool].connect( handler.call )
            select_only_button.setProperty( "entity", entity )
            layout.addWidget( select_only_button )
            
            # Text display
            multiline = len( entities ) > 1 or not self.ui.CHKBTN_DATA_FASTA.isChecked()
            
            text_edit = QTextEdit()
            text_edit.setLineWrapMode( QTextEdit.NoWrap if multiline else QTextEdit.WidgetWidth )
            text_edit.setSizePolicy( QSizePolicy.Expanding, QSizePolicy.Expanding if multiline else QSizePolicy.Minimum )
            text_edit.setHorizontalScrollBarPolicy( Qt.ScrollBarAlwaysOn )
            text_edit.setVerticalScrollBarPolicy( Qt.ScrollBarAlwaysOn )
            text_edit.setProperty( "style", "console" )
            layout.addWidget( text_edit )
            
            self.__group_boxes.append( (select_only_button, text_edit, group_box, handler) )
            
            if self.ui.CHKBTN_DATA_DATA.isChecked():
                r = []
                info = entity.visualisable_info()
                r.append( "[" + info.type_name + "]\n" )
                
                for property in info.iter_children():
                    r.append( property.key.ljust( 20 ) )
                    r.append( " = " )
                    
                    value = property.get_raw_value()
                    
                    if type( value ) in (list, set, tuple):
                        text = "{}: {}".format( len( cast( Sequence, value ) ), ", ".join( str( x ) for x in cast( Sequence, value ) ) )
                    else:
                        text = str( value )
                    
                    r.append( string_helper.max_width( text, 20 ) )
                    r.append( ansi.RESET + "\n" )
                
                content = qt_gui_helper.ansi_to_html( "".join( r ), self.ANSI_SCHEME )
            elif self.ui.CHKBTN_DATA_NEWICK.isChecked():
                if isinstance( entity, LegoComponent ):
                    if entity.tree:
                        content = entity.tree
                    else:
                        content = "; MISSING - Generate a tree first!"
                else:
                    content = "; NOT AVAILABLE - Trees are not available for {}".format( entity_type )
            elif self.ui.CHKBTN_DATA_FASTA.isChecked():
                fasta = fastaiser.to_fasta( entity )
                content = qt_gui_helper.ansi_to_html( cli_view_utils.colour_fasta_ansi( fasta, self._model.site_type ), self.ANSI_SCHEME )
            elif self.ui.CHKBTN_DATA_BLAST.isChecked():
                if hasattr( entity, "comments" ):
                    content = "\n".join( entity.comments )
                else:
                    content = "; NOT AVAILABLE - BLAST is not available for {}".format( entity_type )
            else:
                raise SwitchError( "ui selection", None )
            
            text_edit.setText( content )
    
    
    class __on__check_box:
        def __init__( self, form: "FrmMain", entity: ILegoVisualisable ):
            self.form = form
            self.entity = entity
        
        
        def call( self, _: bool ):
            self.form._view.select_entity( self.entity )
    
    
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
        first = array_helper.first( items )
        
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
    
    
    def request_plugin( self, plugin: Plugin, defaults = None ):
        arguments = FrmArguments.request( self, plugin, defaults )
        
        if arguments is not None:
            plugin.run( **arguments )  # --> self.plugin_completed
            
            
            # region Signal handlers
    
    
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
        if self._model.file_name:
            file_name = self._model.file_name
        else:
            file_name = qt_gui_helper.browse_save( self, constants.DIALOGUE_FILTER )
        
        if file_name:
            COMMANDS.ext_files.file_save( file_name )
    
    
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
        
        if file_name:
            COMMANDS.ext_files.file_save( file_name )
    
    
    @exqtSlot()
    def on_ACT_FILE_EXPORT_triggered( self ) -> None:
        """
        Signal handler: File - export
        """
        filter = constants.DIALOGUE_FILTER_FASTA if self.ui.CHKBTN_DATA_FASTA.isChecked() else constants.DIALOGUE_FILTER_NEWICK
        file_name = qt_gui_helper.browse_save( self, filter )
        
        if file_name:
            c = []
            
            for a in self.__group_boxes:
                b = a[0]  # type: QPushButton
                t = a[1]  # type: QTextEdit
                
                if b.isChecked():
                    c.append( t.toPlainText() )
            
            file_helper.write_all_text( file_name, "\n".join( c ) )
    
    
    @exqtSlot()
    def on_ACT_VIEW_ALIGN_triggered( self ) -> None:
        """
        Signal handler: Align selection
        """
        for userdomain_view in self._view.selected_userdomain_views():
            self._view.align_about_domain( userdomain_view )
    
    
    @exqtSlot()
    def on_ACT_VIEW_ALIGN_SUBSEQUENCES_triggered( self ) -> None:
        """
        Signal handler: View - align subsequences
        """
        for userdomain_view in self._view.selected_userdomain_views():
            self._view.align_about( userdomain_view )
    
    
    @exqtSlot()
    def on_ACT_VIEW_ALIGN_FIRST_SUBSEQUENCES_triggered( self ) -> None:
        """
        Signal handler: View - align first subsequences in sequence
        """
        userdomain_views = self._view.selected_userdomain_views()
        
        leftmost = min( x.pos().x() for x in userdomain_views )
        
        for userdomain_view in userdomain_views:
            userdomain_view.setX( leftmost )
            userdomain_view.save_state()
    
    
    @exqtSlot()
    def on_ACT_MAKE_COMPONENTS_triggered( self ) -> None:
        """
        Signal handler: Make - components
        """
        if len( self._model.edges ) == 0:
            QMessageBox.information( self, self.windowTitle(), "Load the edge data (BLAST) first." )
            return
        
        self.request_plugin( COMMANDS.ext_generating.make_components )
    
    
    @exqtSlot()
    def on_ACT_MAKE_ALIGNMENTS_triggered( self ) -> None:
        """
        Signal handler:
        """
        if not all( x.site_array for x in self._model.sequences ):
            QMessageBox.information( self, self.windowTitle(), "Load the site data (FASTA) first." )
            return
        
        self.request_plugin( COMMANDS.ext_generating.make_alignments, defaults = [list( self._view.selected_components() ) or None] )
    
    
    @exqtSlot()
    def on_ACT_MAKE_TREE_triggered( self ) -> None:
        """
        Signal handler:
        """
        if not all( x.alignment is not None for x in self._model.components ):
            QMessageBox.information( self, self.windowTitle(), "Align the sequences first." )
            return
        
        self.request_plugin( COMMANDS.ext_generating.make_trees, defaults = [list( self._view.selected_components() ) or None] )
    
    
    @exqtSlot()
    def on_ACT_MAKE_CONSENSUS_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_generating.make_consensus, defaults = [list( self._view.selected_components() ) or None] )
    
    
    @exqtSlot()
    def on_ACT_MAKE_NRFG_triggered( self ) -> None:
        """
        Signal handler:
        """
        if len( self._model.fusion_events ) == 0:
            QMessageBox.information( self, self.windowTitle(), "Find the fusion events first." )
            return
        
        self.request_plugin( COMMANDS.ext_generating.make_nrfg )
    
    
    @exqtSlot()
    def on_ACT_MAKE_FUSIONS_triggered( self ) -> None:
        """
        Signal handler:
        """
        if not all( x.tree is not None for x in self._model.components ):
            QMessageBox.information( self, self.windowTitle(), "Create the trees first." )
            return
        
        self.request_plugin( COMMANDS.ext_generating.make_fusions )
    
    
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
        self.request_plugin( COMMANDS.ext_modifications.set_tree )
    
    
    @exqtSlot()
    def on_ACT_MODIFY_SET_ALIGNMENT_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_modifications.set_alignment )
    
    
    @exqtSlot()
    def on_ACT_MODIFY_QUANTISE_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_modifications.quantise )
    
    
    @exqtSlot()
    def on_ACT_PRINT_FASTA_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_viewing.print_fasta, defaults = [array_helper.first( self._view.selected_entities() )] )
    
    
    @exqtSlot()
    def on_ACT_PRINT_STATUS_triggered( self ) -> None:
        """
        Signal handler:
        """
        COMMANDS.ext_viewing.print_status()
    
    
    @exqtSlot()
    def on_ACT_PRINT_ALIGNMENT_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_viewing.print_alignments, defaults = [array_helper.first( self._view.selected_components() )] )
    
    
    @exqtSlot()
    def on_ACT_PRINT_CONSENSUS_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_viewing.print_consensus, defaults = [array_helper.first( self._view.selected_components() )] )
    
    
    @exqtSlot()
    def on_ACT_PRINT_TREE_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_viewing.print_trees, defaults = [array_helper.first( self._view.selected_components() )] )
    
    
    @exqtSlot()
    def on_ACT_PRINT_COMPONENT_EDGES_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_viewing.print_component_edges, defaults = [array_helper.first( self._view.selected_components() )] )
    
    
    @exqtSlot()
    def on_ACT_PRINT_COMPONENTS_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_viewing.print_components )
    
    
    @exqtSlot()
    def on_ACT_PRINT_FUSIONS_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_viewing.print_fusions )
    
    
    @exqtSlot()
    def on_ACT_PRINT_NRFG_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_viewing.print_nrfg )
    
    
    @exqtSlot()
    def on_ACT_WINDOW_VIEW_triggered( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_ACT_DROP_COMPONENTS_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_dropping.drop_components )
    
    
    @exqtSlot()
    def on_ACT_DROP_ALIGNMENTS_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_dropping.drop_alignment )
    
    
    @exqtSlot()
    def on_ACT_DROP_TREE_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_dropping.drop_tree )
    
    
    @exqtSlot()
    def on_ACT_DROP_CONSENSUS_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_dropping.drop_consensus )
    
    
    @exqtSlot()
    def on_ACT_DROP_FUSIONS_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_dropping.drop_fusions )
    
    
    @exqtSlot()
    def on_ACT_DROP_NRFG_triggered( self ) -> None:
        """
        Signal handler:
        """
        self.request_plugin( COMMANDS.ext_dropping.drop_nrfg )
    
    
    @exqtSlot()
    def on_ACT_REFRESH_VIEW_triggered( self ) -> None:
        """
        Signal handler:
        """
        COMMANDS.ext_gui.refresh( EChanges.MODEL_OBJECT )
    
    
    @exqtSlot()
    def on_ACT_UPDATE_VIEW_triggered( self ) -> None:
        """
        Signal handler:
        """
        COMMANDS.ext_gui.refresh( EChanges.COMPONENTS )
    
    
    @exqtSlot()
    def on_ACT_DEBUG_triggered( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_BTN_STATUS_BLAST_clicked( self ) -> None:
        """
        Signal handler:
        """
        self._update_status_checkbox_values()
        self.on_ACT_FILE_IMPORT_triggered()
    
    
    @exqtSlot()
    def on_BTN_STATUS_FASTA_clicked( self ) -> None:
        """
        Signal handler:
        """
        self._update_status_checkbox_values()
        self.on_ACT_FILE_IMPORT_triggered()
    
    
    @exqtSlot()
    def on_BTN_STATUS_COMPONENTS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self._update_status_checkbox_values()
        self.on_ACT_MAKE_COMPONENTS_triggered()
    
    
    @exqtSlot()
    def on_BTN_STATUS_ALIGNMENTS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self._update_status_checkbox_values()
        self.on_ACT_MAKE_ALIGNMENTS_triggered()
    
    
    @exqtSlot()
    def on_BTN_STATUS_TREES_clicked( self ) -> None:
        """
        Signal handler:
        """
        self._update_status_checkbox_values()
        self.on_ACT_MAKE_TREE_triggered()
    
    
    @exqtSlot()
    def on_BTN_STATUS_FUSIONS_clicked( self ) -> None:
        """
        Signal handler:
        """
        self._update_status_checkbox_values()
        self.on_ACT_MAKE_FUSIONS_triggered()
    
    
    @exqtSlot()
    def on_BTN_STATUS_NRFG_clicked( self ) -> None:
        """
        Signal handler:
        """
        self._update_status_checkbox_values()
        self.on_ACT_MAKE_NRFG_triggered()
    
    
    @exqtSlot()
    def on_BTN_VIEW_SETTINGS_clicked( self ) -> None:
        """
        Signal handler:
        """
        if FrmViewOptions.request( self, self._view ):
            self.__update_as_required( EChanges.MODEL_ENTITIES )
    
    
    def change_selection_mode( self ):
        if self.ui.BTN_SEL_COMPONENT.isChecked():
            self._model.ui_options.mode = EMode.COMPONENT
        elif self.ui.BTN_SEL_SEQUENCE.isChecked():
            self._model.ui_options.mode = EMode.SEQUENCE
        elif self.ui.BTN_SEL_SUBSEQUENCE.isChecked():
            self._model.ui_options.mode = EMode.SUBSEQUENCE
        elif self.ui.BTN_SEL_EDGE.isChecked():
            self._model.ui_options.mode = EMode.EDGE
        
        self._view.select_all( ESelect.REMOVE )
    
    
    @exqtSlot()
    def on_BTN_SEL_COMPONENT_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.change_selection_mode()
    
    
    @exqtSlot()
    def on_BTN_SEL_EDGE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.change_selection_mode()
    
    
    @exqtSlot()
    def on_BTN_SEL_SEQUENCE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.change_selection_mode()
    
    
    @exqtSlot()
    def on_BTN_SEL_SUBSEQUENCE_clicked( self ) -> None:
        """
        Signal handler:
        """
        self.change_selection_mode()
    
    
    @exqtSlot()
    def on_ACT_MODIFY_NEW_ENTITY_triggered( self ) -> None:
        """
        Signal handler: New entity
        """
        m = self._view.options.mode
        
        if m == EMode.SEQUENCE:
            COMMANDS.ext_modifications.new_sequence()
        elif m == EMode.SUBSEQUENCE:
            subsequences = self._view.selected_userdomains()
            
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
                
                COMMANDS.ext_modifications.remove_sequences( list( sequences ) )
            else:
                QMessageBox.information( self, self.windowTitle(), "Please select a sequence first." )
        elif m == EMode.SUBSEQUENCE:
            subsequences = self._view.selected_userdomains()
            
            if len( subsequences ) >= 2:
                if not self.__query_remove( subsequences ):
                    return
                
                COMMANDS.ext_modifications.merge_subsequences( list( subsequences ) )
            else:
                QMessageBox.information( self, self.windowTitle(), "Please select at least two adjacent subsequences first." )
        elif m == EMode.EDGE:
            subsequences = self._view.selected_userdomains()
            edges = self._view.selected_edges()
            
            if not edges:
                QMessageBox.information( self, self.windowTitle(), "Please select a subsequence with edges first." )
                return
            
            edge_name, ok = QInputDialog.getItem( self, self.windowTitle(), "Select an edge to delink from the selected subsequence(s)", (str( x ) for x in edges) )
            
            if not ok:
                return
            
            COMMANDS.ext_modifications.remove_edges( list( subsequences ), list( edges ) )
        elif m == EMode.COMPONENT:
            QMessageBox.information( self, self.windowTitle(), "Components are automatically generated, you cannot delete them." )
    
    
    @exqtSlot()
    def on_CHKBTN_DATA_BLAST_clicked( self ) -> None:
        """
        Signal handler:
        """
        pass
    
    
    @exqtSlot()
    def on_CHKBTN_DATA_DATA_clicked( self ) -> None:
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
    
    
    def on_scene_selectionChanged( self ):
        if len( self._view.scene.selectedItems() ) == 0:
            self.ILegoViewModelObserver_selection_changed()
    
    
    @exqtSlot( bool )
    def on_ACT_APP_EXIT_triggered( self, _: bool ) -> None:
        """
        Signal handler: Exit application
        """
        self.close()
    
    
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
        if self.freeze_options:
            return
        
        self._view.options.mode = EMode.SEQUENCE
        self.update_options_from_ui()
    
    
    @exqtSlot()
    def on_ACT_SELECT_SUBSEQUENCE_triggered( self ) -> None:
        """
        Signal handler: Subsequence selection mode
        """
        if self.freeze_options:
            return
        
        self._view.options.mode = EMode.SUBSEQUENCE
        self.update_options_from_ui()
    
    
    @exqtSlot()
    def on_ACT_SELECT_EDGE_triggered( self ) -> None:
        """
        Signal handler: Edge selection mode
        """
        if self.freeze_options:
            return
        
        self._view.options.mode = EMode.EDGE
        self.update_options_from_ui()
    
    
    @exqtSlot()
    def on_ACT_SELECT_COMPONENT_triggered( self ) -> None:
        """
        Signal handler: Component selection mode
        """
        if self.freeze_options:
            return
        
        self._view.options.mode = EMode.COMPONENT
        self.update_options_from_ui()


# endregion
