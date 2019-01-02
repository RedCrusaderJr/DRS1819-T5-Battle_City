from PyQt5.QtCore import QThread, Qt, pyqtSignal
import game_board as gb
import time
from bullet import Bullet
from enums import Orientation, ElementType
from helper import Helper


class MoveBulletsThread(QThread):
    thread_signal = pyqtSignal(int, int, Bullet)

    def __init__(self, parentQWidget = None):
        super(MoveBulletsThread, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.was_canceled = False

    def run(self):
        while not self.was_canceled:
            self.moveBullets()
            time.sleep(0.5)

    def cancel(self):
        self.was_canceled = True
        
    def moveBullets(self):
        for bullet in self.parent_widget.bullet_dictionary:
            isChanged = False

            if bullet.orientation is Orientation.UP:
                new_x = bullet.x
                new_y = bullet.y - 1
                isChanged = True
            elif bullet.orientation is Orientation.RIGHT:
                new_x = bullet.x + 1
                new_y = bullet.y
                isChanged = True
            elif bullet.orientation is Orientation.DOWN:
                new_x = bullet.x
                new_y = bullet.y + 1
                isChanged = True
            elif bullet.orientation is Orientation.LEFT:
                new_x = bullet.x - 1
                new_y = bullet.y
                isChanged = True

            if isChanged:
                #if impact logic
                if Helper.isCollision(self.parent_widget, new_x, new_y, ElementType.BULLET):
                    print(f"moveBullets(): bullet: {bullet} impact")
                    #TODO tank.active_bullet = None !!!
                else:
                    print
                    self.thread_signal.emit(new_x, new_y, bullet)
            # time.sleep(0.05)