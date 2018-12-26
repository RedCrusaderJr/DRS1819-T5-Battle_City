from PyQt5.QtCore import pyqtSignal


class Tank:

    move_signal = pyqtSignal(object, int)

    def __init__(self):
        self.lives = 3
        self.x = 0
        self.y = 0
        self.image = 'tank.png'

    def move(self, direction):
        self.move_signal.emit(self, direction)

    def setCoordinates(self, newX, newY):
        self.x = newX
        self.y = newY

    def updateLives(self, newLives):
        self.lives = newLives
