from PyQt5.QtCore import QThread, Qt, pyqtSignal, QMutex
from PyQt5.QtGui import QTransform
import time
from tank import Tank
from enums import PlayerType, ElementType, Orientation
from helper import Helper
from bullet import Bullet



class MovePlayerThread(QThread):
    player_moved_signal = pyqtSignal(Tank, QTransform)
    bullet_fired_signal = pyqtSignal(Bullet, QTransform)
    bullet_impact_signal = pyqtSignal(list, list, list)

    #thread_mutex = QMutex()

    def __init__(self, commands, tank, parentQWidget = None):
        super(MovePlayerThread, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.was_canceled = False
        self.commands = commands
        self.tank = tank

    def run(self):
        while not self.was_canceled:
            self.parent_widget.mutex.lock()
            self.playerControlls()
            self.parent_widget.mutex.unlock()

            time.sleep(0.05)


    def cancel(self):
        self.was_canceled = True

    def playerControlls(self):
        bullets_to_be_removed = []

        com = list(self.commands)
        x = self.tank.x
        y = self.tank.y
        orientation = self.tank.orientation
        for key in com:
            changed = False
            if self.tank.player_type == PlayerType.PLAYER_1:
                if key == Qt.Key_Up:
                    y -= 1
                    changed = True
                    orientation = Orientation.UP
                elif key == Qt.Key_Down:
                    y += 1
                    changed = True
                    orientation = Orientation.DOWN
                elif key == Qt.Key_Right:
                    x += 1
                    changed = True
                    orientation = Orientation.RIGHT
                elif key == Qt.Key_Left:
                    x -= 1
                    changed = True
                    orientation = Orientation.LEFT
                elif key == Qt.Key_Space:
                    if self.tank.fireBullet():
                        if Helper.isCollision(self.parent_widget,
                                              self.tank.active_bullet.x,
                                              self.tank.active_bullet.y,
                                              ElementType.BULLET):
                            self.bullet_impact_signal.emit(self.tank.active_bullet.x,
                                                           self.tank.active_bullet.y,
                                                           self.tank.active_bullet)
                        else:
                            self.bullet_fired_signal.emit(self.tank.active_bullet)

            elif self.tank.player_type == PlayerType.PLAYER_2:
                if key == Qt.Key_W:
                    y -= 1
                    changed = True
                    orientation = Orientation.UP
                elif key == Qt.Key_S:
                    y += 1
                    changed = True
                    orientation = Orientation.DOWN
                elif key == Qt.Key_D:
                    x += 1
                    changed = True
                    orientation = Orientation.RIGHT
                elif key == Qt.Key_A:
                    x -= 1
                    changed = True
                    orientation = Orientation.LEFT
                elif key == Qt.Key_F:
                    if self.tank.fireBullet():
                        if Helper.isCollision(self.parent_widget,
                                              self.tank.active_bullet.x,
                                              self.tank.active_bullet.y,
                                              ElementType.BULLET):

                            self.bulletImpactOnFire(new_x, new_y, bullet, bullets_to_be_removed, enemies_to_be_removed)

                        else:
                            self.bulletFired()

            if changed:
                if self.tank.player_type is PlayerType.PLAYER_1:
                    element_type = ElementType.PLAYER1
                elif self.tank.player_type is PlayerType.PLAYER_2:
                    element_type = ElementType.PLAYER2

                if Helper.isCollision(self.parent_widget, x, y, element_type):
                    x = self.tank.x
                    y = self.tank.y

                self.playerMoved(x, y, orientation)

            time.sleep(0.05)

    def playerMoved(self, new_x, new_y, new_orientation):
        if self.tank.player_type == PlayerType.PLAYER_1:
            gb_player = self.parent_widget.player_1
            element_type = ElementType.PLAYER1
        elif self.tank.player_type == PlayerType.PLAYER_2:
            gb_player = self.parent_widget.player_2
            element_type = ElementType.PLAYER2

        self.parent_widget.setShapeAt(gb_player.x, gb_player.y, ElementType.NONE)
        gb_player.x = new_x
        gb_player.y = new_y

        transform = QTransform()
        transform.rotate(Helper.rotationFunction(gb_player.orientation, new_orientation))
        gb_player.orientation = new_orientation
        self.parent_widget.setShapeAt(gb_player.x, gb_player.y, element_type)
        
        self.player_moved_signal.emit(self.tank, transform)

    def bulletFired(self):
        bullet = self.tank.active_bullet

        transform = QTransform()
        transform.rotate(Helper.rotationFunction(Orientation.UP, bullet.orientation))

        self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.BULLET)

        self.bullet_fired_signal.emit(bullet, transform)

    def bulletImpactOnFire(self, new_x, new_y, bullet, bullets_to_be_removed, enemies_to_be_removed):
        if not (0 <= new_x <= self.parent_widget.BoardWidth - 1 and 0 <= new_y <= self.parent_widget.BoardHeight - 1):
            bullet.bullet_owner.active_bullet = None
            # if (bullet.x < 0 or bullet.x > self.parent_widget.BoardWidth - 1) or (bullet.y < 0 or bullet.y > self.BoardHeight - 1):
            #   bullet.bullet_owner.active_bullet = None
            #  return
            #self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            # bullet.bullet_owner.active_bullet = None
            #bullets_to_be_removed.append(bullet)
            return

        next_shape = self.parent_widget.getShapeType(new_x, new_y)

        if next_shape is ElementType.WALL:
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)
            #self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            #bullets_to_be_removed.append(bullet)

        elif next_shape is ElementType.BULLET:
            #self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            #bullets_to_be_removed.append(bullet)

            other_bullet = self.findBulletAt(new_x, new_y)
            self.parent_widget.setShapeAt(other_bullet.x, other_bullet.y, ElementType.NONE)
            bullets_to_be_removed.append(other_bullet)


        elif (next_shape is ElementType.PLAYER1 or next_shape is ElementType.PLAYER2) and bullet.type is BulletType.ENEMY:
            if next_shape is ElementType.PLAYER1:
                gb_player = self.parent_widget.player_1
            elif next_shape is ElementType.PLAYER2:
                gb_player = self.parent_widget.player_1

            if gb_player.lives > 0:
                self.parent_widget.setPlayerToStartingPosition(gb_player.x, gb_player.y, gb_player)
                gb_player.lives -= 1
            #self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            #bullets_to_be_removed.append(bullet)


        elif next_shape is ElementType.ENEMY and bullet.type is BulletType.FRIEND:
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)

            for enemy in self.parent_widget.enemy_dictionary:
                if new_x == enemy.x and new_y == enemy.y:
                    enemies_to_be_removed.append()
                    break
            #self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            #bullets_to_be_removed.append(bullet)

        elif next_shape is ElementType.BASE:
            #self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            #bullets_to_be_removed.append(bullet)
            print("game over")

        bullet.bullet_owner.active_bullet = None
        self.bullet_impact_signal.emit([], bullets_to_be_removed, enemies_to_be_removed)
