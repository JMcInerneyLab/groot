from random import randint

from PyQt5.QtGui import QColor
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QGraphicsView


class MyView(QGraphicsView):
    def wheelEvent(self, event:QWheelEvent):
        """
        Zoom in or out of the view.
        """
        if event.modifiers() & Qt.ControlModifier or event.modifiers() & Qt.MetaModifier:
            zoomInFactor = 1.25
            zoomOutFactor = 1 / zoomInFactor
        
            # Save the scene pos
            oldPos = self.mapToScene(event.pos())
        
            # Zoom
            if event.angleDelta().y() > 0:
                zoomFactor = zoomInFactor
            else:
                zoomFactor = zoomOutFactor
            self.scale(zoomFactor, zoomFactor)
        
            # Get the new position
            newPos = self.mapToScene(event.pos())
        
            # Move scene to old position
            delta = newPos - oldPos
            self.translate(delta.x(), delta.y())
            
            
def random_colour(  ):
    return QColor( randint( 0, 255 ), randint( 0, 255 ), randint( 0, 255 ) )



def triangle(sequence):
    """
    Yields the triangle
    """
    for i, a in enumerate(sequence):
        for j in range(0, i):
            yield a, sequence[j]