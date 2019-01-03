from PyQt5.QtCore import QThread, Qt, pyqtSignal, QMutex
import time
from tank import Tank
from enums import PlayerType, ElementType, Orientation
from helper import Helper
from bullet import Bullet



class MovePlayerThread(QThread):
    thread_signal = pyqtSignal(int, int, Tank, Orientation)
    bullet_fired_signal = pyqtSignal(Bullet)
    bullet_impact_signal = pyqtSignal(int, int, Bullet)
    thread_mutex = QMutex()

    def __init__(self, commands, tank, parentQWidget = None):
        super(MovePlayerThread, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.was_canceled = False
        self.commands = commands
        self.tank = tank

    def run(self):
        while not self.was_canceled:
            self.move()
            time.sleep(0.05)

    def cancel(self):
        self.was_canceled = True

    def move(self):
        com = list(self.commands)
        x = self.tank.x
        y = self.tank.y
        orientation = self.tank.orientation
        for key in com:
            changed = False
            if self.tank.player_type == PlayerType.PLAYER_1:
                if key == Qt.Key_Up:
                    y -= 1
                    changed = True
                    orientation = Orientation.UP
                elif key == Qt.Key_Down:
                    y += 1
                    changed = True
                    orientation = Orientation.DOWN
                elif key == Qt.Key_Right:
                    x += 1
                    changed = True
                    orientation = Orientation.RIGHT
                elif key == Qt.Key_Left:
                    x -= 1
                    changed = True
                    orientation = Orientation.LEFT
                elif key == Qt.Key_Space:
                    if self.tank.fireBullet():
                        if Helper.isCollision(self.parent_widget, self.tank.active_bullet.x, self.tank.active_bullet.y,
                                              ElementType.BULLET):
                            self.bullet_impact_signal.emit(self.tank.active_bullet.x, self.tank.active_bullet.y,
                                                           self.tank.active_bullet)
                        else:
                            self.bullet_fired_signal.emit(self.tank.active_bullet)

            elif self.tank.player_type == PlayerType.PLAYER_2:
                if key == Qt.Key_W:
                    y -= 1
                    changed = True
                    orientation = Orientation.UP
                elif key == Qt.Key_S:
                    y += 1
                    changed = True
                    orientation = Orientation.DOWN
                elif key == Qt.Key_D:
                    x += 1
                    changed = True
                    orientation = Orientation.RIGHT
                elif key == Qt.Key_A:
                    x -= 1
                    changed = True
                    orientation = Orientation.LEFT
                elif key == Qt.Key_F:
                    if self.tank.fireBullet():
                        if Helper.isCollision(self.parent_widget, self.tank.active_bullet.x, self.tank.active_bullet.y,
                                              ElementType.BULLET):

                            self.bullet_impact_signal.emit(self.tank.active_bullet.x, self.tank.active_bullet.y,
                                                           self.tank.active_bullet)

                        else:
                            self.bullet_fired_signal.emit(self.tank.active_bullet)

            if changed:
                if self.tank.player_type is PlayerType.PLAYER_1:
                    element_type = ElementType.PLAYER1
                elif self.tank.player_type is PlayerType.PLAYER_2:
                    element_type = ElementType.PLAYER2

                if Helper.isCollision(self.parent_widget, x, y, element_type):
                    x = self.tank.x
                    y = self.tank.y
                    self.thread_signal.emit(x, y, self.tank, orientation)
                else:
                    self.thread_signal.emit(x, y, self.tank, orientation)
            time.sleep(0.05)
