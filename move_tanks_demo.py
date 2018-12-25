import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QWidget, QLabel, QApplication
from PyQt5.QtGui import QTransform

from key_notifier import KeyNotifier


class SimMoveDemo(QWidget):

    def __init__(self):
        super().__init__()

        pix_map = QPixmap('tank.png')
        self.pix1 = pix_map.scaled(50, 50)
        pix_map = QPixmap('tank.png')
        self.pix2 = pix_map.scaled(50, 50)

        self.label1 = QLabel(self)
        self.label2 = QLabel(self)

        self.setWindowState(Qt.WindowMaximized)
        self.__init_ui__()

        self.key_notifier = KeyNotifier()
        self.key_notifier.key_signal.connect(self.__update_position__)
        self.key_notifier.start()

    def __init_ui__(self):

        self.label1.setPixmap(self.pix1)
        self.label1.setGeometry(100, 40, 50, 50)
        self.label1.orientation = 0

        self.label2.setPixmap(self.pix2)
        self.label2.setGeometry(50, 40, 50, 50)
        self.label2.orientation = 0

        self.setWindowTitle('Moving tanks demo')
        self.show()

    def keyPressEvent(self, event):
        self.key_notifier.add_key(event.key())

    def keyReleaseEvent(self, event):
        self.key_notifier.rem_key(event.key())

    def __update_position__(self, key):
        rec1 = self.label1.geometry()
        rec2 = self.label2.geometry()

        orientation1 = self.label1.orientation
        orientation2 = self.label2.orientation
        transform = QTransform()

        if key == Qt.Key_Up:
            if orientation1 != 0:
                pix = self.label1.pixmap()
                transform.rotate(SimMoveDemo.rotation_function(orientation1, 0))
                self.label1.setPixmap(pix.transformed(transform))
                self.label1.orientation = 0
            self.label1.setGeometry(rec1.x(), rec1.y() - 5, rec1.width(), rec1.height())

        elif key == Qt.Key_Right:
            if orientation1 != 1:
                pix = self.label1.pixmap()
                transform.rotate(SimMoveDemo.rotation_function(orientation1, 1))
                self.label1.setPixmap(pix.transformed(transform))
                self.label1.orientation = 1
            self.label1.setGeometry(rec1.x() + 5, rec1.y(), rec1.width(), rec1.height())

        elif key == Qt.Key_Down:
            if orientation1 != 2:
                pix = self.label1.pixmap()
                transform.rotate(SimMoveDemo.rotation_function(orientation1, 2))
                self.label1.setPixmap(pix.transformed(transform))
                self.label1.orientation = 2
            self.label1.setGeometry(rec1.x(), rec1.y() + 5, rec1.width(), rec1.height())

        elif key == Qt.Key_Left:
            if orientation1 != 3:
                pix = self.label1.pixmap()
                transform.rotate(SimMoveDemo.rotation_function(orientation1, 3))
                self.label1.setPixmap(pix.transformed(transform))
                self.label1.orientation = 3
            self.label1.setGeometry(rec1.x() - 5, rec1.y(), rec1.width(), rec1.height())

        if key == Qt.Key_W:
            if orientation2 != 0:
                pix = self.label2.pixmap()
                transform.rotate(SimMoveDemo.rotation_function(orientation2, 0))
                self.label2.setPixmap(pix.transformed(transform))
                self.label2.orientation = 0
            self.label2.setGeometry(rec2.x(), rec2.y() - 5, rec2.width(), rec2.height())

        elif key == Qt.Key_D:
            if orientation2 != 1:
                pix = self.label2.pixmap()
                transform.rotate(SimMoveDemo.rotation_function(orientation2, 1))
                self.label2.setPixmap(pix.transformed(transform))
                self.label2.orientation = 1
            self.label2.setGeometry(rec2.x() + 5, rec2.y(), rec2.width(), rec2.height())

        elif key == Qt.Key_S:
            if orientation2 != 2:
                pix = self.label2.pixmap()
                transform.rotate(SimMoveDemo.rotation_function(orientation2, 2))
                self.label2.setPixmap(pix.transformed(transform))
                self.label2.orientation = 2
            self.label2.setGeometry(rec2.x(), rec2.y() + 5, rec2.width(), rec2.height())

        elif key == Qt.Key_A:
            if orientation2 != 3:
                pix = self.label2.pixmap()
                transform.rotate(SimMoveDemo.rotation_function(orientation2, 3))
                self.label2.setPixmap(pix.transformed(transform))
                self.label2.orientation = 3
            self.label2.setGeometry(rec2.x() - 5, rec2.y(), rec2.width(), rec2.height())

    @staticmethod
    def rotation_function(current_position, next_position):
        diff = current_position - next_position
        rotation_angle = 0 - diff * 90
        return rotation_angle

    def closeEvent(self, event):
        self.key_notifier.die()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    ex = SimMoveDemo()
    sys.exit(app.exec_())
