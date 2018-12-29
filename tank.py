from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap


class Tank:

    move_signal = pyqtSignal(object, int)

    def __init__(self, pl):
        if pl == 1:
            self.pixmap = QPixmap('tank1.png')
        else:
            self.pixmap = QPixmap('tank2.png')
        self.lives = 3
        self.x = 6
        self.y = 6
        self.player = pl
        self.orientation = 0

    def move(self, direction):
        self.move_signal.emit(self, direction)

    def setCoordinates(self, newX, newY):
        self.x = newX
        self.y = newY

    def updateLives(self, newLives):
        self.lives = newLives
