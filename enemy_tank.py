from PyQt5.QtCore import pyqtSignal, QTimer


class EnemyTank:

    move_signal = pyqtSignal(object, int)

    def __init__(self):
        self.x = 0
        self.y = 0
        self.direction = 3
        self.image = 'tank.png'
        self.timer = QTimer()
        self.timer.timeout.connect(self.move(self, self.direction))
        self.time.start(1000)

    def move(self, direction):
        self.move_signal.emit(self, direction)

    def setCoordinates(self, newX, newY):
        self.x = newX
        self.y = newY
