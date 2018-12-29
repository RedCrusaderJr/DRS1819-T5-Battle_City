from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap


class EnemyTank:

    def __init__(self):
        self.x = 0
        self.y = 2
        self.direction = 1
        self.pixmap = QPixmap('enemy.png')


    def setCoordinates(self, newX, newY):
        self.x = newX
        self.y = newY

