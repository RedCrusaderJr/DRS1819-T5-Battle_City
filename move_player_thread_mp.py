from PyQt5.QtCore import QThread, pyqtSignal
import time
from enemy_tank import EnemyTank
from enums import ElementType, Orientation, BulletType, PlayerType
from helper_mp import Helper
from bullet import Bullet
import pickle
import struct
from random import randint
from threading import Timer

class MovePlayerThreadMP(QThread):

    def __init__(self, player, parentQWidget = None):
        super(MovePlayerThreadMP, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.speed = 0.25
        self.was_canceled = False
        self.player_num = player
        self.player = None
        self.is_freezed = False

        if self.player_num == 1:
            self.socket = self.parent_widget.communication.conn1
            self.player = self.parent_widget.player_1
        else:
            self.socket = self.parent_widget.communication.conn2
            self.player = self.parent_widget.player_2


    def run(self):
        while not self.was_canceled:
            self.movePlayer()

    def cancel(self):
        self.was_canceled = True

    def movePlayer(self):
        #new_x, new_y, new_orientation = None

        text = ""
        changed = False
        while True:
            try:
                message = self.socket.recv(1024)
            except:
                self.cancel()
                return
            self.parent_widget.mutex.lock()

            new_x = self.player.x
            new_y = self.player.y
            new_orientation = self.player.orientation
            text += str(message, 'utf8')
            if not message or len(message) < 1024:
                break
            self.parent_widget.mutex.unlock()
        if not self.is_freezed:
            if text == "UP":
                new_y -= 1
                new_orientation = Orientation.UP
                changed = True
            elif text == "DOWN":
                new_y += 1
                new_orientation = Orientation.DOWN
                changed = True
            elif text == "RIGHT":
                new_x += 1
                new_orientation = Orientation.RIGHT
                changed = True
            elif text == "LEFT":
                new_x -= 1
                new_orientation = Orientation.LEFT
                changed = True
        if text == "FIRE":
            if self.player.fireBullet():

                if Helper.isCollision(self.parent_widget,
                                      self.player.active_bullet.x,
                                      self.player.active_bullet.y,
                                      ElementType.BULLET):

                    self.bulletImpactOnFire(self.player.active_bullet.x,
                                            self.player.active_bullet.y,
                                            self.player.active_bullet)
                else:
                    self.bulletFired()

        if changed:
            if Helper.isCollision(self.parent_widget, new_x, new_y, ElementType.PLAYER2):
                if not (
                        new_x >= self.parent_widget.BoardWidth or new_x < 0 or new_y >= self.parent_widget.BoardHeight or new_y < 0):
                    if self.parent_widget.getShapeType(new_x, new_y) == ElementType.FREEZE:
                        self.is_freezed = True
                        self.parent_widget.setShapeAt(self.player.x, self.player.y, ElementType.NONE)
                        self.player.x = new_x
                        self.player.y = new_y
                        self.parent_widget.setShapeAt(new_x, new_y, Helper.enumFromOrientationPlayer(self.player.player_type, self.player.orientation))
                        t = Timer(5, self.timeOut)
                        t.start()
                    elif self.parent_widget.getShapeType(new_x, new_y) == ElementType.LIFE:
                        self.player.lives += 1
                        if self.player.player_type == PlayerType.PLAYER_1:
                            self.send_status_update(player_1_lives=self.player.lives)
                        else:
                            self.send_status_update(player_2_lives=self.player.lives)
                    else:
                        new_x = self.player.x
                        new_y = self.player.y
                else:
                    new_x = self.player.x
                    new_y = self.player.y

                self.parent_widget.setShapeAt(new_x, new_y, Helper.enumFromOrientationPlayer(self.player.player_type, self.player.orientation))

            self.playerMoved(new_x, new_y, new_orientation)

        self.sendUpdatedPlayers()

        self.parent_widget.mutex.unlock()

    def bulletImpactOnFire(self, new_x, new_y, bullet):
        if not (0 <= new_x <= self.parent_widget.BoardWidth - 1 and 0 <= new_y <= self.parent_widget.BoardHeight - 1):
            bullet.bullet_owner.active_bullet = None
            return

        next_shape = self.parent_widget.getShapeType(new_x, new_y)

        if next_shape == ElementType.WALL:
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)

        elif next_shape == ElementType.BULLET or (ElementType.BULLET_UP <= next_shape <= ElementType.BULLET_LEFT):
            other_bullet = self.parent_widget.findBulletAt(new_x, new_y)
            if other_bullet is not None:
                self.parent_widget.setShapeAt(other_bullet.x, other_bullet.y,
                                              ElementType.NONE)
                self.parent_widget.bullet_list.remove(other_bullet)
            else:
                print("Move enemy thread: bulletImpactOnFire(): other_bullet is None")

        elif (next_shape == ElementType.ENEMY or ElementType.ENEMY_UP <= next_shape <= ElementType.ENEMY_LEFT) and bullet.type == BulletType.FRIEND:
            enemy_to_be_removed = self.parent_widget.findEnemyAt(new_x, new_y)
            self.parent_widget.setShapeAt(enemy_to_be_removed.x, enemy_to_be_removed.y, ElementType.NONE)

            self.parent_widget.enemy_list.remove(enemy_to_be_removed)
            self.parent_widget.num_of_all_enemies -= 1
            self.send_status_update(num_of_enemies=self.parent_widget.num_of_all_enemies)
            if self.parent_widget.num_of_all_enemies > 0:
                while (True):
                    rand_x = randint(0, self.parent_widget.BoardWidth)
                    if self.parent_widget.getShapeType(rand_x, 0) == ElementType.NONE:
                        break

                self.parent_widget.enemy_list.append(EnemyTank(rand_x))
                self.parent_widget.setShapeAt(rand_x, 0, ElementType.ENEMY_DOWN)
            elif self.parent_widget.num_of_all_enemies == -3:
                self.parent_widget.advanceToNextLevel()
        bullet.bullet_owner.active_bullet = None
        #self.bulletImpactSignal(bullets_to_be_removed, enemies_to_be_removed)


    def bulletFired(self):
        bullet = self.player.active_bullet
        self.parent_widget.setShapeAt(bullet.x, bullet.y, Helper.enumFromOrientationBullet(bullet.orientation))
        self.parent_widget.bullet_list.append(bullet)

    def playerMoved(self, new_x, new_y, new_orientation):
        self.parent_widget.setShapeAt(self.player.x, self.player.y, ElementType.NONE)
        self.player.x = new_x
        self.player.y = new_y
        self.player.orientation = new_orientation

        self.parent_widget.setShapeAt(self.player.x, self.player.y, Helper.enumFromOrientationPlayer(self.player.player_type, self.player.orientation))

    def send_msg(self, sock, msg):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        try:
            sock.sendall(msg)
        except:
            return

    def sendUpdatedPlayers(self):
        #id = "UPDATE_PLAYERS"
        data = pickle.dumps((str("UPDATE_PLAYERS"), self.parent_widget.board), -1)
        data2 = pickle.dumps((str("UPDATE_PLAYERS"), self.parent_widget.board), -1)

        #self.parent_widget.communication.conn1.send(data)
        #self.parent_widget.communication.conn2.send(data2)

        self.send_msg(self.parent_widget.communication.conn1, data)
        self.send_msg(self.parent_widget.communication.conn2, data2)


    def send_status_update(self,player_1_lives = None, player_2_lives = None, num_of_enemies = None):
        data = pickle.dumps((str("STATUS_UPDATE"), (player_1_lives, player_2_lives, num_of_enemies)), -1)

        self.send_msg(self.parent_widget.communication.conn1, data)
        self.send_msg(self.parent_widget.communication.conn2, data)


    def timeOut(self):
        self.is_freezed = False
