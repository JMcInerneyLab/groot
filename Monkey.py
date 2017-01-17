from random import randint

from PyQt5.QtGui import QColor


def random_colour(  ):
    return QColor( randint( 0, 255 ), randint( 0, 255 ), randint( 0, 255 ) )


