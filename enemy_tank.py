from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from enums import Orientation

class EnemyTank:

    def __init__(self, x):
        self.x = x
        self.y = 0
        self.direction = Orientation.DOWN
        self.pix_map = QPixmap('./images/enemy.png')
        self.active_bullet = None

    def setCoordinates(self, x, y):
        self.x = x
        self.y = y

