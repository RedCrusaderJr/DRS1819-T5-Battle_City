from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap


class Tank:

    move_signal = pyqtSignal(object, int)

    def __init__(self):
        self.pixmap = QPixmap('tank.png')
        self.lives = 3
        self.x = 6
        self.y = 6

    def move(self, direction):
        self.move_signal.emit(self, direction)

    def setCoordinates(self, newX, newY):
        self.x = newX
        self.y = newY

    def updateLives(self, newLives):
        self.lives = newLives
