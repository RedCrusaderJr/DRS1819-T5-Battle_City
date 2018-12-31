from PyQt5.QtCore import QThread, Qt, pyqtSignal
import time
from tank import Tank
from enums import PlayerType, ElementType, Orientation
from helper import Helper

class MovePlayerThread(QThread):
    thread_signal = pyqtSignal(int, int, Tank, int)

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

            if changed:
                if Helper.isCollision(self.parent_widget, x, y):
                    x = self.tank.x
                    y = self.tank.y
                    self.thread_signal.emit(x, y, self.tank, orientation)
                else:
                    self.thread_signal.emit(x, y, self.tank, orientation)
            time.sleep(0.05)