from PyQt5.QtCore import QThread, Qt, pyqtSignal
import game_board as gb
import time


class MoveThread(QThread):
    threadSignal = pyqtSignal(int, int)

    def __init__(self, parentQWidget = None):
        super(MoveThread, self).__init__(parentQWidget)
        self.wasCanceled = False

    def run(self):
        while not self.wasCanceled:
            time.sleep(0.05)

    def cancel(self):
        self.wasCanceled = True

    def move(self, x, y, board, key):
        changed = False;
        if key == Qt.Key_Up:
            y -= 1
            changed = True
        elif key == Qt.Key_Down:
            y += 1
            changed = True
        elif key == Qt.Key_Right:
            x += 1
            changed = True
        elif key == Qt.Key_Left:
            x -= 1
            changed = True

        if not changed:
            return
        else:
            if self.isCollision(board, x, y):
                self.threadSignal.emit(x, y)
            else:
                return

    def isCollision(self, board, new_x, new_y):
        nextPositionShape = board[(new_y * gb.GameBoard.BoardWidth) + new_x]
        if (nextPositionShape is gb.Element.NONE) or (nextPositionShape is gb.Element.BULLET):
            return True
        return False