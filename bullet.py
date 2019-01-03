from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from enum import Enum


class Bullet:

    def __init__(self, bullet_type, x, y, orientation):
        #print(f"init bullet ({x}, {y}) - orientation: {orientation} - self: {self}")

        self.pm_launched = QPixmap('./images/launched_bullet.png')
        self.pm_flying = QPixmap('./images/flying_bullet.png')
        self.pm_impact = QPixmap('./images/impact_bullet.png')
        self.x = x
        self.y = y
        self.type = bullet_type
        self.orientation = orientation

    def setCoordinates(self, new_x, new_y):
        self.x = new_x
        self.y = new_y