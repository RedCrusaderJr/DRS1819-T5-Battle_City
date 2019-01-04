from PyQt5.QtCore import QThread, pyqtSignal
import time
from enemy_tank import EnemyTank
from enums import ElementType, Orientation
from helper import Helper
from bullet import Bullet


class MoveEnemyThread(QThread):
    thread_signal = pyqtSignal()
    bullet_fired_signal = pyqtSignal(Bullet)
    bullet_impact_signal = pyqtSignal(int, int, Bullet)

    def __init__(self, parentQWidget = None):
        super(MoveEnemyThread, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.was_canceled = False
        self.iterator = 0
        self.current_enemy = None

    def run(self):
        while not self.was_canceled:
            self.parent_widget.mutex.lock()
            self.moveEnemy()
            self.iterator += 1
            if self.iterator >= len(self.parent_widget.enemies_new_position):
                self.iterator = 0
            self.parent_widget.mutex.unlock()
            time.sleep(0.25)

    def cancel(self):
        self.was_canceled = True
        

    def moveEnemy(self):
        for enemy in self.parent_widget.enemies_new_position:
            if enemy.direction == Orientation.UP:
                if not Helper.isCollision(self.parent_widget, enemy.x, enemy.y-1, ElementType.ENEMY):
                    enemy.y -= 1
                else:
                    if self.parent_widget.getShapeType(enemy.x, enemy.y) == ElementType.BULLET:
                        self.parent_widget.bulletImpacted(enemy.x, enemy.y, self.parent_widget.findBulletAt(enemy.x,
                                                                                                        enemy.y - 1))
                    enemy.direction = Orientation.RIGHT

            elif enemy.direction == Orientation.RIGHT:
                if not Helper.isCollision(self.parent_widget, enemy.x+1, enemy.y, ElementType.ENEMY):
                    enemy.x += 1
                else:
                    if self.parent_widget.getShapeType(enemy.x, enemy.y) == ElementType.BULLET:
                        self.parent_widget.bulletImpacted(enemy.x, enemy.y, self.parent_widget.findBulletAt(enemy.x + 1,
                                                                                                        enemy.y))
                    enemy.direction = Orientation.DOWN

            elif enemy.direction == Orientation.DOWN:
                if not Helper.isCollision(self.parent_widget, enemy.x, enemy.y+1, ElementType.ENEMY):
                    enemy.y += 1
                else:
                    if self.parent_widget.getShapeType(enemy.x, enemy.y) == ElementType.BULLET:
                        self.parent_widget.bulletImpacted(enemy.x, enemy.y, self.parent_widget.findBulletAt(enemy.x,
                                                                                                        enemy.y + 1))
                    enemy.direction = Orientation.LEFT

            else:
                if not Helper.isCollision(self.parent_widget, enemy.x-1, enemy.y, ElementType.ENEMY):
                    enemy.x -= 1
                else:
                    if self.parent_widget.getShapeType(enemy.x, enemy.y) == ElementType.BULLET:
                        self.parent_widget.bulletImpacted(enemy.x, enemy.y, self.parent_widget.findBulletAt(enemy.x - 1,
                                                                                                        enemy.y))
                    enemy.direction = Orientation.UP

        if self.iterator >= len(self.parent_widget.enemies_new_position):
            self.iterator = 0
        current_enemy = self.parent_widget.enemies_new_position[self.iterator]
        if current_enemy.fireBullet():
            if Helper.isCollision(self.parent_widget, current_enemy.active_bullet.x, current_enemy.active_bullet.y,
                                  ElementType.BULLET):

                self.bullet_impact_signal.emit(current_enemy.active_bullet.x, current_enemy.active_bullet.y,
                                               current_enemy.active_bullet)

            else:
                self.bullet_fired_signal.emit(current_enemy.active_bullet)
        self.thread_signal.emit()
