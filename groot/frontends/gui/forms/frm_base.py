from typing import Optional

from PyQt5.QtCore import QPoint
from PyQt5.QtGui import QCloseEvent
from PyQt5.QtWidgets import QAction, QDialog, QMenu

from groot.data import global_view
from groot.data.lego_model import ILegoSelectable, LegoSequence
from groot.frontends.gui.gui_view_utils import EChanges, LegoSelection
from intermake import ArgsKwargs, intermake_gui
from intermake.engine.plugin import Plugin
from intermake.hosts.frontends.gui_qt.frm_arguments import FrmArguments
from mhelper import MFlags, SwitchError
from mhelper_qt import menu_helper


class ESelMenu( MFlags ):
    SEQUENCES = 1 << 0
    DOMAINS = 1 << 1
    EDGES = 1 << 2
    COMPONENTS = 1 << 3
    FUSIONS = 1 << 4
    POINTS = 1 << 5
    NRFG = 1 << 6
    EXPLORER = 1 << 7
    LEGO = 1 << 8
    RELATIONAL = 1 << 9
    META_GRAPHS = COMPONENTS | NRFG


class FrmBase( QDialog ):
    def __init__( self, parent ):
        from groot.frontends.gui.forms.frm_main import FrmMain
        super().__init__( parent )
        self.parent: FrmMain = parent
        self.setStyleSheet( intermake_gui.default_style_sheet() )
    
    
    def on_plugin_completed( self, change: EChanges ):
        self.on_refresh_data()
        self.on_fusions_changed()  # TODO
    
    
    def on_selection_changed( self ):
        self.on_refresh_data()
    
    
    def on_refresh_data( self ):
        pass
    
    
    def on_fusions_changed( self ):
        pass
    
    
    def set_selected( self, item, selected ):
        selection: LegoSelection = self.get_selection()
        existing = item in selection
        
        if selected == existing:
            return
        
        if selected:
            if selection.is_empty() or selection.selection_type() != type( item ):
                self.set_selection( LegoSelection( frozenset( { item } ) ) )
            else:
                self.set_selection( LegoSelection( selection.items.union( { item } ) ) )
        else:
            self.set_selection( LegoSelection( selection.items - { item } ) )
    
    
    def show_selection_menu( self, choice: ESelMenu = ESelMenu.ALL ):
        model = self.get_model()
        selection = self.get_selection()
        alive = []
        
        root = QMenu()
        
        # Meta
        if choice.RELATIONAL:
            relational = QMenu()
            relational.setTitle( "Relational" )
            OPTION_1 = "Select all"
            OPTION_2 = "Select none"
            OPTION_3 = "Invert selection"
            OPTION_4 = "Select sequences with no site data"
            OPTION_5 = "Select domains to left of selected domains"
            OPTION_6 = "Select domains to right of selected domains"
            OPTION_7 = "Select domains connected to selected domains"
            
            for option in (OPTION_1, OPTION_2, OPTION_3, OPTION_4, OPTION_5, OPTION_6, OPTION_7):
                action = QAction()
                action.setCheckable( True )
                action.setText( option )
                action.tag = option
                alive.append( action )
                relational.addAction( action )
                
            alive.append( relational )
            root.addMenu( relational )
        
        
        # Sequences
        if choice.SEQUENCES and model.sequences:
            sequences = QMenu()
            sequences.setTitle( "Genes" )
            
            for sequence in model.sequences:
                action = QAction()
                action.setCheckable( True )
                action.setChecked( sequence in selection )
                action.setText( str( sequence ) )
                action.tag = sequence
                alive.append( action )
                sequences.addAction( action )
            
            alive.append( sequences )
            root.addMenu( sequences )
        
        # Domains
        if choice.DOMAINS and model.user_domains:
            domains = QMenu()
            domains.setTitle( "Domains" )
            
            for domain in model.user_domains:
                action = QAction()
                action.setCheckable( True )
                action.setChecked( domain in selection )
                action.setText( str( domain ) )
                action.tag = domain
                alive.append( action )
                domains.addAction( action )
            
            alive.append( domains )
            root.addMenu( domains )
        
        # Edges
        if choice.EDGES and model.edges:
            edges = QMenu()
            edges.setTitle( "Edges" )
            
            for sequence in model.sequences:
                assert isinstance( sequence, LegoSequence )
                sequence_edges = QMenu()
                sequence_edges.setTitle( str( sequence ) )
                
                for edge in model.edges:
                    if edge.left.sequence is not sequence and edge.right.sequence is not sequence:
                        continue
                    
                    action = QAction()
                    action.setCheckable( True )
                    action.setChecked( edge in selection )
                    action.setText( str( edge ) )
                    action.tag = edge
                    alive.append( action )
                    sequence_edges.addAction( action )
                
                alive.append( sequence_edges )
                edges.addMenu( sequence_edges )
            
            alive.append( edges )
            root.addMenu( edges )
        
        # Components
        if choice.COMPONENTS and model.components:
            components = QMenu()
            components.setTitle( "Components" )
            
            for component in model.components:
                action = QAction()
                action.setCheckable( True )
                action.setChecked( component in selection )
                action.setText( str( component ) )
                action.tag = component
                alive.append( action )
                components.addAction( action )
            
            alive.append( components )
            root.addMenu( components )
        
        # Fusions
        if choice.FUSIONS and model.fusion_events:
            fusions = QMenu()
            fusions.setTitle( "Fusions" )
            
            for fusion in model.fusion_events:
                action = QAction()
                action.setCheckable( True )
                action.setChecked( fusion in selection )
                action.setText( str( fusion ) )
                action.tag = fusion
                alive.append( action )
                fusions.addAction( action )
            
            alive.append( fusions )
            root.addMenu( fusions )
        
        # Fusion points
        if choice.POINTS and model.fusion_events:
            fusion_points = QMenu()
            fusion_points.setTitle( "Fusion points" )
            
            for fusion in model.fusion_events:
                fusions_points = QMenu()
                fusions_points.setTitle( str( fusion ) )
                
                for fusion_point in fusion.points:
                    action = QAction()
                    action.setCheckable( True )
                    action.setChecked( fusion_point in selection )
                    action.setText( str( fusion_point ) )
                    action.tag = fusion_point
                    alive.append( action )
                    fusions_points.addAction( action )
                
                alive.append( fusions_points )
                fusion_points.addMenu( fusions_points )
            
            alive.append( fusion_points )
            root.addMenu( fusion_points )
        
        # NRFG
        if choice.NRFG and model.nrfg:
            action = QAction()
            action.setCheckable( True )
            action.setChecked( model.nrfg in selection )
            action.setText( str( model.nrfg ) )
            action.tag = model.nrfg
            alive.append( action )
            root.addAction( action )
        
        # Special
        if not alive:
            action = QAction()
            action.setText( "Load some data first!" )
            action.tag = 3
            alive.append( action )
            root.addAction( action )
        else:
            if choice.EXPLORER:
                action = QAction()
                action.setText( "Entity explorer..." )
                action.tag = 1
                alive.append( action )
                root.addAction( action )
            
            if choice.LEGO:
                action = QAction()
                action.setText( "Lego explorer..." )
                action.tag = 2
                alive.append( action )
                root.addAction( action )
        
        # Show menu
        control = self.sender()
        selected = root.exec_( control.mapToGlobal( QPoint( 0, control.height() ) ) )
        
        if selected is None:
            return
        
        tag = selected.tag
        
        if tag == 1:
            from groot.frontends.gui.forms.frm_selection_list import FrmSelectionList
            self.show_form( FrmSelectionList )
        elif tag == 2:
            from groot.frontends.gui.forms.frm_lego import FrmLego
            self.show_form( FrmLego )
        elif tag == 3:
            from groot.frontends.gui.forms.frm_workflow import FrmWorkflow
            self.show_form( FrmWorkflow )
        elif isinstance( tag, ILegoSelectable ):
            self.set_selection( LegoSelection( frozenset( { tag } ) ) )
        else:
            raise SwitchError( "tag", tag, instance = True )
    
    
    def get_selection( self ) -> LegoSelection:
        return global_view.current_selection()
    
    
    def set_selection( self, value: LegoSelection ):
        global_view.set_selection( value )
    
    
    def get_model( self ):
        return global_view.current_model()
    
    
    def closeEvent( self, event: QCloseEvent ):
        self.parent.remove_form( self )
    
    
    def show_menu( self, *args ):
        return menu_helper.show( self.sender(), *args )
    
    
    def show_form( self, form_class ):
        self.parent.show_form( form_class )
        
    def close_form( self, form ):
        self.parent.close_form( form )
    
    
    def request( self, plugin: Plugin, *args, **kwargs ):
        if args is None:
            args = ()
        
        arguments: Optional[ArgsKwargs] = FrmArguments.request( self, plugin, *args, **kwargs )
        
        if arguments is not None:
            plugin.run( *arguments.args, **arguments.kwargs )  # --> self.plugin_completed
