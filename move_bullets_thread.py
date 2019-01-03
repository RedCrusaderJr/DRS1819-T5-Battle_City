from PyQt5.QtCore import QThread, Qt, pyqtSignal
import game_board as gb
import time
from bullet import Bullet
from enums import Orientation, ElementType
from helper import Helper


class MoveBulletsThread(QThread):
    thread_signal = pyqtSignal()
    #bullet_impact_signal = pyqtSignal(int, int, Bullet)

    def __init__(self, parentQWidget = None):
        super(MoveBulletsThread, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.was_canceled = False

    def run(self):
        while not self.was_canceled:
            self.parent_widget.mutex.lock()
            self.moveBullets()
            self.parent_widget.mutex.unlock()
            time.sleep(0.05)

    def cancel(self):
        self.was_canceled = True
        
    def moveBullets(self):
        for bullet in self.parent_widget.bullets_new_posiotion:
            if bullet.orientation is Orientation.UP:
                if not Helper.isCollision(self.parent_widget, bullet.x, bullet.y - 1, ElementType.BULLET):
                    bullet.y -= 1
            elif bullet.orientation is Orientation.RIGHT:
                if not Helper.isCollision(self.parent_widget, bullet.x + 1, bullet.y, ElementType.BULLET):
                    bullet.x += 1
            elif bullet.orientation is Orientation.DOWN:
                if not Helper.isCollision(self.parent_widget, bullet.x, bullet.y + 1, ElementType.BULLET):
                    bullet.y += 1
            elif bullet.orientation is Orientation.LEFT:
                if not Helper.isCollision(self.parent_widget, bullet.x - 1, bullet.y, ElementType.BULLET):
                    bullet.x -= 1

            """if isChanged:
                #if impact logic
                if Helper.isCollision(self.parent_widget, new_x, new_y, ElementType.BULLET):
                    self.bullet_impact_signal.emit(new_x, new_y, bullet)
                    #TODO tank.active_bullet = None !!!
                else:
                    self.thread_signal.emit(new_x, new_y, bullet)
            # time.sleep(0.05)"""

        self.thread_signal.emit()
