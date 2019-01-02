from PyQt5.QtCore import QThread, Qt, pyqtSignal
import time
from tank import Tank
from enums import PlayerType, ElementType, Orientation
from helper import Helper
from bullet import Bullet


class MovePlayerThread(QThread):
    thread_signal = pyqtSignal(int, int, Tank, int)
    fire_bullet_signal = pyqtSignal(Tank)

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
            bullet_changed = False
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
                    if self.tank.active_bullet is None:
                        bullet_changed = True


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
                    if self.tank.active_bullet is None:
                        bullet_changed = True

            if changed:
                if Helper.isCollision(self.parent_widget, x, y):
                    x = self.tank.x
                    y = self.tank.y
                    self.thread_signal.emit(x, y, self.tank, orientation)
                else:
                    self.thread_signal.emit(x, y, self.tank, orientation)

            if bullet_changed:
                bullet_x = self.tank.x
                bullet_y = self.tank.y
                if self.tank.orientation == Orientation.UP:
                    bullet_y -= 1
                elif self.tank.orientation == Orientation.RIGHT:
                    bullet_x += 1
                elif self.tank.orientation == Orientation.DOWN:
                    bullet_y += 1
                elif self.tank.orientation == Orientation.LEFT:
                    bullet_x -= 1
                if not Helper.isBulletCollision(self.parent_widget, bullet_x, bullet_y):
                    self.tank.active_bullet = Bullet(bullet_x, bullet_y, self.tank.orientation, self.tank.player_type)
                    self.fire_bullet_signal.emit(self.tank)
            time.sleep(0.05)