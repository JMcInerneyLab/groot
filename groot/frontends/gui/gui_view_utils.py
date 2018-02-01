from random import randint
from typing import FrozenSet, Iterable
from mhelper import MFlags, array_helper, string_helper
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView

from groot.data.lego_model import ILegoSelectable, LegoComponent, LegoEdge, LegoModel, LegoSequence, LegoUserDomain


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
