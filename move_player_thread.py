from PyQt5.QtCore import QThread, Qt, pyqtSignal, QMutex
from PyQt5.QtGui import QTransform
import time, pickle
from tank import Tank
from enums import PlayerType, ElementType, Orientation, BulletType
from helper import Helper
from bullet import Bullet
from threading import Timer


class MovePlayerThread(QThread):
    player_moved_signal = pyqtSignal(Tank, QTransform)
    bullet_fired_signal = pyqtSignal(Bullet, QTransform)
    bullet_impact_signal = pyqtSignal(list, list, list)

    #thread_mutex = QMutex()

    def __init__(self, commands, tank, parentQWidget = None):
        super(MovePlayerThread, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        if self.parent_widget.socket is not None:
            self.socket = self.parent_widget.socket
        else:
            self.socket = None
        self.was_canceled = False
        self.commands = commands
        self.tank = tank
        self.is_freezed = False

    def run(self):
        #self.was_canceled = False
        while not self.was_canceled:
            self.parent_widget.mutex.lock()
            self.playerControlls()
            self.parent_widget.mutex.unlock()
            time.sleep(0.05)


    def cancel(self):
        self.was_canceled = True

    def playerControlls(self):
        bullets_to_be_removed = []
        enemies_to_be_removed = []

        com = list(self.commands)
        new_x = self.tank.x
        new_y = self.tank.y
        new_orientation = self.tank.orientation
        for key in com:
            changed = False
            if self.tank.player_type == PlayerType.PLAYER_1 and self.is_freezed == False:
                if key == Qt.Key_Up:
                    new_y -= 1
                    changed = True
                    new_orientation = Orientation.UP
                elif key == Qt.Key_Down:
                    new_y += 1
                    changed = True
                    new_orientation = Orientation.DOWN
                elif key == Qt.Key_Right:
                    new_x += 1
                    changed = True
                    new_orientation = Orientation.RIGHT
                elif key == Qt.Key_Left:
                    new_x -= 1
                    changed = True
                    new_orientation = Orientation.LEFT
                elif key == Qt.Key_Space:
                    if self.tank.fireBullet():
                        if Helper.isCollision(self.parent_widget,
                                              self.tank.active_bullet.x,
                                              self.tank.active_bullet.y,
                                              ElementType.BULLET):
                            
                            self.bulletImpactOnFire(self.tank.active_bullet.x,
                                                    self.tank.active_bullet.y,
                                                    self.tank.active_bullet,
                                                    bullets_to_be_removed,
                                                    enemies_to_be_removed)
                        else:
                            self.bulletFired()

            elif self.tank.player_type == PlayerType.PLAYER_2 and self.is_freezed == False:
                if key == Qt.Key_W:
                    new_y -= 1
                    changed = True
                    new_orientation = Orientation.UP
                elif key == Qt.Key_S:
                    new_y += 1
                    changed = True
                    new_orientation = Orientation.DOWN
                elif key == Qt.Key_D:
                    new_x += 1
                    changed = True
                    new_orientation = Orientation.RIGHT
                elif key == Qt.Key_A:
                    new_x -= 1
                    changed = True
                    new_orientation = Orientation.LEFT
                elif key == Qt.Key_F:
                    if self.tank.fireBullet():
                        if Helper.isCollision(self.parent_widget,
                                              self.tank.active_bullet.x,
                                              self.tank.active_bullet.y,
                                              ElementType.BULLET):

                            self.bulletImpactOnFire(self.tank.active_bullet.x,
                                                    self.tank.active_bullet.y,
                                                    self.tank.active_bullet,
                                                    bullets_to_be_removed,
                                                    enemies_to_be_removed)
                        else:
                            self.bulletFired()

            if changed:
                if self.tank.player_type is PlayerType.PLAYER_1:
                    element_type = ElementType.PLAYER1
                elif self.tank.player_type is PlayerType.PLAYER_2:
                    element_type = ElementType.PLAYER2

                if Helper.isCollision(self.parent_widget, new_x, new_y, element_type):
                    if not (new_x >= self.parent_widget.BoardWidth or new_x < 0 or new_y >= self.parent_widget.BoardHeight or new_y < 0):
                        if self.parent_widget.getShapeType(new_x, new_y) == ElementType.FREEZE:
                            # freezuj
                            self.is_freezed = True
                            self.parent_widget.setShapeAt(new_x, new_y, element_type)
                            self.playerMoved(new_x, new_y, new_orientation)
                            t = Timer(5, self.timeout)
                            t.start()
                            # wait for time completion
                            # t.join()
                        elif self.parent_widget.getShapeType(new_x, new_y) == ElementType.LIFE:
                            if element_type == ElementType.PLAYER1:
                                self.parent_widget.player_1.lives += 1
                                self.parent_widget.change_lives_signal.emit(1, self.parent_widget.player_1.lives)
                            elif element_type == ElementType.PLAYER2:
                                self.parent_widget.player_2.lives += 1
                                self.parent_widget.change_lives_signal.emit(2, self.parent_widget.player_2.lives)
                        else:
                            new_x = self.tank.x
                            new_y = self.tank.y
                    else:
                        new_x = self.tank.x
                        new_y = self.tank.y

                    self.parent_widget.setShapeAt(new_x, new_y, element_type)
                self.playerMoved(new_x, new_y, new_orientation)

            self.parent_widget.mutex.unlock()
            time.sleep(0.05)
            self.parent_widget.mutex.lock()

    def playerMoved(self, new_x, new_y, new_orientation):
        if self.tank.player_type == PlayerType.PLAYER_1:
            gb_player = self.parent_widget.player_1
            # gb_player = self.tank
            element_type = ElementType.PLAYER1
        elif self.tank.player_type == PlayerType.PLAYER_2:
            gb_player = self.parent_widget.player_2
            # gb_player = self.tank
            element_type = ElementType.PLAYER2

        self.parent_widget.setShapeAt(gb_player.x, gb_player.y, ElementType.NONE)
        gb_player.x = new_x
        gb_player.y = new_y

        transform = QTransform()
        transform.rotate(Helper.rotationFunction(gb_player.orientation, new_orientation))
        gb_player.orientation = new_orientation

        self.parent_widget.setShapeAt(gb_player.x, gb_player.y, element_type)
        self.playerMoveSignal(transform)

    def bulletFired(self):
        bullet = self.tank.active_bullet

        transform = QTransform()
        transform.rotate(Helper.rotationFunction(Orientation.UP, bullet.orientation))

        self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.BULLET)
        self.bulletFiredSignal(bullet, transform)

    def bulletImpactOnFire(self, new_x, new_y, bullet, bullets_to_be_removed, enemies_to_be_removed):
        if not (0 <= new_x <= self.parent_widget.BoardWidth - 1 and 0 <= new_y <= self.parent_widget.BoardHeight - 1):
            bullet.bullet_owner.active_bullet = None
            return

        next_shape = self.parent_widget.getShapeType(new_x, new_y)

        if next_shape is ElementType.WALL:
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)

        elif next_shape is ElementType.BULLET:
            other_bullet = self.parent_widget.findBulletAt(new_x, new_y)
            if other_bullet is not None:
                self.parent_widget.setShapeAt(other_bullet.x, other_bullet.y, ElementType.NONE) #mozda setShape na new_x, new_y?
                bullets_to_be_removed.append(other_bullet)
            else:
                print("Move player thread: bulletImpactOnFire(): other_bullet is None")

        elif next_shape is ElementType.ENEMY and bullet.type is BulletType.FRIEND:
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)

            for enemy in self.parent_widget.enemy_dictionary:
                if new_x == enemy.x and new_y == enemy.y:
                    enemies_to_be_removed.append(enemy)
                    break

        elif next_shape is ElementType.BASE:
            print("game over")
        bullet.bullet_owner.active_bullet = None

        self.bulletImpactSignal(bullets_to_be_removed, enemies_to_be_removed)


    # region SIGNAL_EMITS
    def playerMoveSignal(self, transform):
        self.player_moved_signal.emit(self.tank, transform)
        # TODO: SEND PLAYER_MOVED
        if self.parent_widget.socket is not None:
            data = pickle.dumps(("PLAYER_MOVED", (self.tank, transform)))
            with self.socket:
                self.socket.sendall(data)

    def bulletFiredSignal(self, bullet, transform):
        self.bullet_fired_signal.emit(bullet, transform)
        # TODO: SEND BULLET_FIRED
        if self.parent_widget.socket is not None:
            data = pickle.dumps(("BULLET_FIRED", (bullet, transform)))
            with self.socket:
                self.socket.sendall(data)

    def bulletImpactSignal(self, bullets_to_be_removed, enemies_to_be_removed):
        self.bullet_impact_signal.emit([], bullets_to_be_removed, enemies_to_be_removed)
        # TODO: SEND BULLET_IMPACT
        if self.parent_widget.socket is not None:
            data = pickle.dumps(("BULLET_IMPACT", ([], bullets_to_be_removed, enemies_to_be_removed)))
            with self.socket:
                self.socket.sendall(data)
    # endregion

    def timeout(self):
        self.is_freezed = False
