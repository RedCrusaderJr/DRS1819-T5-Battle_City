from PyQt5.QtCore import QThread, pyqtSignal
import game_board as gb
import time
from enemy_tank import EnemyTank


class MoveEnemyThread(QThread):
    threadSignal = pyqtSignal()

    def __init__(self, parentQWidget = None):
        super(MoveEnemyThread, self).__init__(parentQWidget)
        self.pparent = parentQWidget
        self.wasCanceled = False

    def run(self):
        while not self.wasCanceled:
            self.moveEnemy()
            time.sleep(0.5)

    def cancel(self):
        self.wasCanceled = True

    def moveEnemy(self):
        for enemy in self.pparent.enemiesNewPosition:
            if enemy.direction == 0:
                if self.noCollision(enemy.x, enemy.y-1):
                    enemy.y -= 1
                else:
                    enemy.direction = 1
            elif enemy.direction == 1:
                if self.noCollision(enemy.x+1, enemy.y):
                    enemy.x += 1
                else:
                    enemy.direction = 2
            elif enemy.direction == 2:
                if self.noCollision(enemy.x, enemy.y+1):
                    enemy.y += 1
                else:
                    enemy.direction = 3
            else:
                if self.noCollision(enemy.x-1, enemy.y):
                    enemy.x -= 1
                else:
                    enemy.direction = 0
        self.threadSignal.emit()



    def noCollision(self, new_x, new_y):
        self.pparent.mutex.lock()
        nextPositionShape = self.pparent.board[(new_y * gb.GameBoard.BoardWidth) + new_x]
        self.pparent.mutex.unlock()
        if (nextPositionShape is gb.Element.NONE) or (nextPositionShape is gb.Element.BULLET):
            return True
        return False