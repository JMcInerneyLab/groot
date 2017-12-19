from random import randint

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QColor, QWheelEvent
from PyQt5.QtWidgets import QGraphicsView
from typing import Tuple

from mhelper import MFlags


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
    
