from PyQt5.QtCore import QThread, Qt, pyqtSignal
import game_board as gb
import time
from tank import Tank


class MoveThread(QThread):
    threadSignal = pyqtSignal(int, int, Tank, int)

    def __init__(self, commands, tank, parentQWidget = None):
        super(MoveThread, self).__init__(parentQWidget)
        self.pparent = parentQWidget
        self.wasCanceled = False
        self.commands = commands
        self.tank = tank

    def run(self):
        while not self.wasCanceled:
            self.move()
            time.sleep(0.05)

    def cancel(self):
        self.wasCanceled = True

    def move(self):
        com = list(self.commands)
        x = self.tank.x
        y = self.tank.y
        orientation = self.tank.orientation
        for key in com:
            changed = False
            if self.tank.player == 1:
                if key == Qt.Key_Up:
                    y -= 1
                    changed = True
                    orientation = 0
                elif key == Qt.Key_Down:
                    y += 1
                    changed = True
                    orientation = 2
                elif key == Qt.Key_Right:
                    x += 1
                    changed = True
                    orientation = 1
                elif key == Qt.Key_Left:
                    x -= 1
                    changed = True
                    orientation = 3
            elif self.tank.player == 2:
                if key == Qt.Key_W:
                    y -= 1
                    changed = True
                    orientation = 0
                elif key == Qt.Key_S:
                    y += 1
                    changed = True
                    orientation = 2
                elif key == Qt.Key_D:
                    x += 1
                    changed = True
                    orientation = 1
                elif key == Qt.Key_A:
                    x -= 1
                    changed = True
                    orientation = 3
            if changed:
                if self.noCollision(x, y):
                    self.threadSignal.emit(x, y, self.tank, orientation)
                else:
                    x = self.tank.x
                    y = self.tank.y
                    self.threadSignal.emit(x, y, self.tank, orientation)
            time.sleep(0.05)

    def noCollision(self, new_x, new_y):
        self.pparent.mutex.lock()
        nextPositionShape = self.pparent.board[(new_y * gb.GameBoard.BoardWidth) + new_x]
        self.pparent.mutex.unlock()
        if (nextPositionShape is gb.Element.NONE) or (nextPositionShape is gb.Element.BULLET):
            return True
        return False
