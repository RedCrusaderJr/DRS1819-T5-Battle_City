from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from enum import Enum


class Bullet:
    move_signal = pyqtSignal(object, int)

    def __init__(self, x, y, orientation, player_type):
        #print("init bullet ({x}, {y}) - orientation: {orientation} - self: {self}")

        #self.pm_launched = QPixmap('./images/launched_bullet.png')
        self.pm_flying = QPixmap('./images/bullet.png')
        #self.pm_impact = QPixmap('./images/impact_bullet.png')
        self.x = x
        self.y = y
        self.orientation = orientation
        self.player_type = player_type

    def setCoordinates(self, new_x, new_y):
        self.x = new_x
        self.y = new_y