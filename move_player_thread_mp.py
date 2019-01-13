from PyQt5.QtCore import QThread, pyqtSignal
import time
from enemy_tank import EnemyTank
from enums import ElementType, Orientation, BulletType
from helper_mp import Helper
from bullet import Bullet
import pickle

class MovePlayerThreadMP(QThread):

    def __init__(self, player, parentQWidget = None):
        super(MovePlayerThreadMP, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.speed = 0.25
        self.was_canceled = False
        self.player_num = player
        self.player = None

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
        new_x = self.player.x
        new_y = self.player.y
        new_orientation = self.player.orientation

        text = ""
        changed = False
        while True:
            message = self.socket.recv(1024)
            self.parent_widget.mutex.lock()
            text += str(message, 'utf8')
            print(f"{text} {self.player_num}")
            if not message or len(message) < 1024:
                break
            self.parent_widget.mutex.unlock()

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
        elif text == "FIRE":
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
            print(f"{new_x} {new_y}")
            if Helper.isCollision(self.parent_widget, new_x, new_y, ElementType.PLAYER2):
                if not (
                        new_x >= self.parent_widget.BoardWidth or new_x < 0 or new_y >= self.parent_widget.BoardHeight or new_y < 0):
                    print("freeeeezeeeeeeee")
                    if self.parent_widget.getShapeType(new_x, new_y) == ElementType.FREEZE:
                        print("freeeeezeeeeeeee")
                    elif self.parent_widget.getShapeType(new_x, new_y) == ElementType.LIFE:
                        self.player.lives += 1
                    else:
                        new_x = self.player.x
                        new_y = self.player.y
                else:
                    print("freeeeezeeeeeeee2")
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

        if next_shape is ElementType.WALL:
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)

        elif next_shape is ElementType.BULLET:
            other_bullet = self.parent_widget.findBulletAt(new_x, new_y)
            if other_bullet is not None:
                self.parent_widget.setShapeAt(other_bullet.x, other_bullet.y,
                                              ElementType.NONE)
                self.parent_widget.bullet_list.remove(other_bullet)
            else:
                print("Move enemy thread: bulletImpactOnFire(): other_bullet is None")

        #elif (
        #        next_shape is ElementType.PLAYER1 or next_shape is ElementType.PLAYER2) and bullet.type is BulletType.ENEMY:
        #    if next_shape is ElementType.PLAYER1:
        #        gb_player = self.parent_widget.player_1
        #    elif next_shape is ElementType.PLAYER2:
        #        gb_player = self.parent_widget.player_2
#
        #    if gb_player.lives > 0:
        #        self.parent_widget.setPlayerToStartingPosition(gb_player.x, gb_player.y, gb_player)
        #        gb_player.lives -= 1
        #    else:
        #        print(f"game over for {next_shape}")

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

    def sendUpdatedPlayers(self):
        id = "UPDATE_PLAYERS"
        print(f"{self.parent_widget.player_2_starting_position} {self.player.x} {self.player.y}")
        data = pickle.dumps((id, self.parent_widget.board), -1)
        self.parent_widget.communication.conn1.sendall(data)
        self.parent_widget.communication.conn2.sendall(data)



