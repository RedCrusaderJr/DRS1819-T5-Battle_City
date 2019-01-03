from PyQt5.QtCore import pyqtSignal
from PyQt5.QtGui import QPixmap
from enums import PlayerType, Orientation, BulletType
from bullet import Bullet


class Tank:

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
        self.active_bullet = None

    def move(self, direction):
        self.move_signal.emit(self, direction)

    def updateLives(self, new_lives):
        self.lives = new_lives

    def setCoordinates(self, x, y):
        self.x = x
        self.y = y

    def fireBullet(self):
        isBulletFired = False

        if self.active_bullet is None:
            bullet_x = self.x
            bullet_y = self.y

            if self.orientation is Orientation.UP:
                bullet_x = self.x
                bullet_y = self.y - 1
                isBulletFired = True
            elif self.orientation is Orientation.RIGHT:
                bullet_x = self.x + 1
                bullet_y = self.y
                isBulletFired = True
            elif self.orientation is Orientation.DOWN:
                bullet_x = self.x
                bullet_y = self.y + 1
                isBulletFired = True
            elif self.orientation is Orientation.LEFT:
                bullet_x = self.x - 1
                bullet_y = self.y
                isBulletFired = True

            self.active_bullet = Bullet(BulletType.FRIEND, bullet_x, bullet_y, self.orientation, self)
            print(f"fireBullet({self}): bullet: {self.active_bullet} fired")

        return isBulletFired