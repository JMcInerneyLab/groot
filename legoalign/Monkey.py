from random import randint

from PyQt5.QtGui import QColor


def random_colour(  ):
    return QColor( randint( 0, 255 ), randint( 0, 255 ), randint( 0, 255 ) )



def triangle(sequence):
    """
    Yields the triangle
    """
    for i, a in enumerate(sequence):
        for j in range(0, i):
            yield a, sequence[j]