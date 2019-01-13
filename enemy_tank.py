from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from enums import PlayerType, Orientation, BulletType
from bullet import Bullet

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

    def fireBullet(self):
        is_bullet_fired = False

        if self.active_bullet is None:
            bullet_x = self.x
            bullet_y = self.y

            if self.direction is Orientation.UP:
                bullet_x = self.x
                bullet_y = self.y - 1
                is_bullet_fired = True
            elif self.direction is Orientation.RIGHT:
                bullet_x = self.x + 1
                bullet_y = self.y
                is_bullet_fired = True
            elif self.direction is Orientation.DOWN:
                bullet_x = self.x
                bullet_y = self.y + 1
                is_bullet_fired = True
            elif self.direction is Orientation.LEFT:
                bullet_x = self.x - 1
                bullet_y = self.y
                is_bullet_fired = True

            self.active_bullet = Bullet(BulletType.ENEMY, bullet_x, bullet_y, self.direction, self)

        return is_bullet_fired

    def __getstate__(self):
        state = self.__dict__.copy()
        del state["pix_map"]
        return state

    def __setstate__(self, state):
        self.__dict__.update(state)
        self.pix_map = QPixmap('./images/enemy.png')
