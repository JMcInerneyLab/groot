from random import randint
from typing import FrozenSet, Iterable

from mhelper import MFlags, array_helper, string_helper, SwitchError
from PyQt5.QtCore import Qt, QPoint
from PyQt5.QtGui import QColor, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView, QMenu, QAction, QWidget

from groot.data.lego_model import ILegoSelectable, LegoComponent, LegoEdge, LegoModel, LegoSequence, LegoUserDomain
from groot.data import global_view

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
    
class LegoSelection:
    def __init__( self, items: Iterable[ILegoSelectable] = None ):
        if items is None:
            items = frozenset()
        
        if not isinstance( items, FrozenSet ):
            items = frozenset( items )
        
        self.items: FrozenSet[ILegoSelectable] = items
        self.sequences = frozenset( x for x in self.items if isinstance( x, LegoSequence ) )
        self.user_domains = frozenset( x for x in self.items if isinstance( x, LegoUserDomain ) )
        self.components = frozenset( x for x in self.items if isinstance( x, LegoComponent ) )
        self.edges = frozenset( x for x in self.items if isinstance( x, LegoEdge ) )
    
    
    def is_empty( self ):
        return not self.items
    
    
    def selection_type( self ):
        return type( array_helper.first_or_none( self.items ) )
    
    
    def __iter__( self ):
        return iter( self.items )
    
    
    def __contains__( self, item ):
        return item in self.items
    
    
    def __str__( self ):
        if len( self.items ) == 0:
            return "No selection"
        elif len( self.items ) == 1:
            return str( array_helper.first_or_error( self.items ) )
        
        r = []
        
        if self.sequences:
            r.append( "{} genes".format( len( self.sequences ) ) )
        
        if self.user_domains:
            r.append( "{} domains".format( len( self.user_domains ) ) )
        
        if self.components:
            r.append( "{} components".format( len( self.components ) ) )
        
        if self.edges:
            r.append( "{} edges".format( len( self.edges ) ) )
        
        return string_helper.format_array( r, final = " and " )


class MyView( QGraphicsView ):
    def wheelEvent( self, event: QWheelEvent ):
        """
        Zoom in or out of the view.
        """
        if event.modifiers() & Qt.ControlModifier or event.modifiers() & Qt.MetaModifier:
            zoomInFactor = 1.25
            zoomOutFactor = 1 / zoomInFactor
            
            # Save the scene pos
            oldPos = self.mapToScene( event.pos() )
            
            # Zoom
            if event.angleDelta().y() > 0:
                zoomFactor = zoomInFactor
            else:
                zoomFactor = zoomOutFactor
            self.scale( zoomFactor, zoomFactor )
            
            # Get the new position
            newPos = self.mapToScene( event.pos() )
            
            # Move scene to old position
            delta = newPos - oldPos
            self.translate( delta.x(), delta.y() )


def random_colour():
    return QColor( randint( 0, 255 ), randint( 0, 255 ), randint( 0, 255 ) )


def triangle( sequence ):
    """
    Yields the triangle
    """
    for i, a in enumerate( sequence ):
        for j in range( 0, i ):
            yield a, sequence[j]


class EChanges( MFlags ):
    """
    Describes the changes after a command has been issued.
    Used by the GUI.
    
    :data MODEL_OBJECT:     The model object itself has changed.
                            Implies FILE_NAME, MODEL_ENTITIES
    :data FILE_NAME:        The filename of the model has changed and/or the recent files list.
    :data MODEL_ENTITIES:   The entities within the model have changed.
    :data COMPONENTS:       The components within the model have changed.
    :data COMP_DATA:        Meta-data (e.g. trees) on the components have changed
    :data MODEL_DAT:        Meta-data (e.g. the NRFG) on the model has changed
    :data INFORMATION:      The text printed during the command's execution is of primary concern to the user.
    """
    __no_flags_name__ = "NONE"
    
    MODEL_OBJECT = 1 << 0
    FILE_NAME = 1 << 1
    MODEL_ENTITIES = 1 << 2
    COMPONENTS = 1 << 3
    COMP_DATA = 1 << 4
    MODEL_DATA = 1 << 5
    INFORMATION = 1 << 6
    DOMAINS = 1 << 7


class SelectionManipulator:
    def select_left( self, model: LegoModel, selection: LegoSelection ) -> LegoSelection:
        select = set()
        
        for domain1 in model.user_domains:
            for domain2 in selection.user_domains:
                if domain1.sequence is domain2.sequence and domain1.start <= domain2.start:
                    select.add( domain1 )
                    break
        
        return LegoSelection( select )
    
    
    def select_right( self, model: LegoModel, selection: LegoSelection ) -> LegoSelection:
        select = set()
        
        for domain1 in model.user_domains:
            for domain2 in selection.user_domains:
                if domain1.sequence is domain2.sequence and domain1.start <= domain2.start:
                    select.add( domain1 )
                    break
        
        return LegoSelection( select )
    
    
    def select_direct_connections( self, _: LegoModel, selection: LegoSelection ) -> LegoSelection:
        edges = set()
        
        for domain in selection.user_domains:
            edges.update( domain.edges )
        
        select = set()
        
        for edge in edges:
            select.add( edge.start )
            select.add( edge.end )
        
        return LegoSelection( select )
    
    
    def select_all( self, model: LegoModel, _: LegoSelection ) -> LegoSelection:
        """
        Selects everything.
        """
        return LegoSelection( model.user_domains )

def show_selection_menu(control:QWidget, actions, choice: ESelMenu = ESelMenu.ALL):
    model = global_view.current_model()
    selection = global_view.current_selection()
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
    selected = root.exec_( control.mapToGlobal( QPoint( 0, control.height() ) ) )
    
    if selected is None:
        return
    
    tag = selected.tag

    from groot.frontends.gui.gui_menu import GuiActions
    assert isinstance(actions, GuiActions)
    
    if tag == 1:
        actions.show_entities()
    elif tag == 2:
        actions.show_lego()
    elif tag == 3:
        actions.show_workflow()
    elif isinstance( tag, ILegoSelectable ):
        actions.set_selection( LegoSelection( frozenset( { tag } ) ) )
    else:
        raise SwitchError( "tag", tag, instance = True )