from PyQt5.QtCore import QThread, Qt, pyqtSignal
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
        if key == Qt.Key_Up:
            y -= 1
            self.threadSignal.emit(x, y)
        elif key == Qt.Key_Down:
            y += 1
            self.threadSignal.emit(x, y)
        elif key == Qt.Key_Right:
            x += 1
            self.threadSignal.emit(x, y)
        elif key == Qt.Key_Left:
            x -= 1
            self.threadSignal.emit(x, y)
