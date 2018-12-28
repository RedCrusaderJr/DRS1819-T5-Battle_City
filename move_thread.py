from PyQt5.QtCore import QThread, Qt, pyqtSignal
import game_board as gb
import time
from Tank import Tank


class MoveThread(QThread):
    threadSignal = pyqtSignal(int, int, Tank)

    def __init__(self, parentQWidget = None):
        super(MoveThread, self).__init__(parentQWidget)
        self.wasCanceled = False

    def run(self):
        while not self.wasCanceled:
            time.sleep(0.05)

    def cancel(self):
        self.wasCanceled = True

    def move(self, tank1, tank2, board, key):
        retTank = tank1
        x1 = tank1.x
        y1 = tank1.y
        x2 = tank2.x
        y2 = tank2.y
        changed = False
        if key == Qt.Key_Up:
            y1 -= 1
            changed = True
        elif key == Qt.Key_Down:
            y1 += 1
            changed = True
        elif key == Qt.Key_Right:
            x1 += 1
            changed = True
        elif key == Qt.Key_Left:
            x1 -= 1
            changed = True
        elif key == Qt.Key_W:
            y2 -= 1
            retTank = tank2
            changed = True
        elif key == Qt.Key_S:
            y2 += 1
            retTank = tank2
            changed = True
        elif key == Qt.Key_D:
            x2 += 1
            retTank = tank2
            changed = True
        elif key == Qt.Key_A:
            x2 -= 1
            retTank = tank2
            changed = True

        if not changed:
            return
        else:
            if retTank.player == 1:
                if self.isCollision(board, x1, y1):
                    self.threadSignal.emit(x1, y1, retTank)
                else:
                    return
            else:
                if self.isCollision(board, x2, y2):
                    self.threadSignal.emit(x2, y2, retTank)
                else:
                    return

    def isCollision(self, board, new_x, new_y):
        nextPositionShape = board[(new_y * gb.GameBoard.BoardWidth) + new_x]
        if (nextPositionShape is gb.Element.NONE) or (nextPositionShape is gb.Element.BULLET):
            return True
        return False