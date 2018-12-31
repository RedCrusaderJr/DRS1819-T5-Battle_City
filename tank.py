from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from enums import PlayerType, Orientation


class Tank:

    move_signal = pyqtSignal(object, int)

    def __init__(self, player_type):
        if player_type == PlayerType.PLAYER_1:
            self.pix_map = QPixmap('./images/tank1.png')
        elif player_type == PlayerType.PLAYER_2:
            self.pix_map = QPixmap('./images/tank2.png')

        self.lives = 3
        self.x = 6
        self.y = 6
        self.player_type = player_type
        self.orientation = Orientation.UP

    def move(self, direction):
        self.move_signal.emit(self, direction)

    def updateLives(self, new_lives):
        self.lives = new_lives

    def setCoordinates(self, x, y):
        self.x = x
        self.y = y