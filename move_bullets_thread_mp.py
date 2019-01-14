from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QThread, Qt, pyqtSignal
import game_board as gb
import time
from bullet import Bullet
from enums import Orientation, ElementType, BulletType, PlayerType
from helper_mp import Helper
from enemy_tank import EnemyTank
import sys
import pickle
import struct
from random import randint

class MoveBulletsThreadMP(QThread):
    def __init__(self, parentQWidget=None):
        super(MoveBulletsThreadMP, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.speed = 0.05
        self.was_canceled = False
        self.parent_widget.speed_up_signal.connect(self.speedUp)

    def run(self):
        while not self.was_canceled:
            self.parent_widget.mutex.lock()
            self.moveBullets()
            self.parent_widget.mutex.unlock()
            time.sleep(self.speed)

    def cancel(self):
        self.was_canceled = True

    def speedUp(self):
        if self.speed - 0.01 > 0.02:
            self.speed -= 0.01


    def moveBullets(self):
        bullets_to_be_removed = []
        for bullet in self.parent_widget.bullet_list:
            if bullet in bullets_to_be_removed:
                continue
            self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)

            new_x = bullet.x
            new_y = bullet.y

            if bullet.orientation == Orientation.UP:
                new_y -= 1
            elif bullet.orientation == Orientation.RIGHT:
                new_x += 1
            elif bullet.orientation == Orientation.DOWN:
                new_y += 1
            elif bullet.orientation == Orientation.LEFT:
                new_x -= 1

            if Helper.isCollision(self.parent_widget, new_x, new_y, ElementType.BULLET):
                self.bulletImpact(new_x, new_y, bullet, bullets_to_be_removed)
            else:
                bullet.x = new_x
                bullet.y = new_y
                self.parent_widget.setShapeAt(bullet.x, bullet.y, Helper.enumFromOrientationBullet
                (bullet.orientation))

        for bullet in bullets_to_be_removed:
            if bullet in self.parent_widget.bullet_list:
                self.parent_widget.bullet_list.remove(bullet)
                self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
                bullet.bullet_owner.active_bullet = None

        self.sendUpdatedBullets()

    def send_msg(self, sock, msg):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        try:
            sock.sendall(msg)
        except:
            return

    def sendUpdatedBullets(self):
        data = pickle.dumps((str("UPDATE_BULLET"), self.parent_widget.board), -1)
        data2 = pickle.dumps((str("UPDATE_BULLET"), self.parent_widget.board), -1)

        self.send_msg(self.parent_widget.communication.conn1, data)
        self.send_msg(self.parent_widget.communication.conn2, data2)


    def send_status_update(self, player_1_life=None, player_2_life=None, enemies_left=None):
        data = pickle.dumps((str("STATUS_UPDATE"), (player_1_life, player_2_life, enemies_left)), -1)

        self.send_msg(self.parent_widget.communication.conn1, data)
        self.send_msg(self.parent_widget.communication.conn2, data)

    def bulletImpact(self, new_x, new_y, bullet, bullets_to_be_removed):
        if not (0 <= new_x <= self.parent_widget.BoardWidth - 1 and 0 <= new_y <= self.parent_widget.BoardHeight - 1):
            self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            bullets_to_be_removed.append(bullet)
            return

        next_shape = self.parent_widget.getShapeType(new_x, new_y)
        levelChanged = False
        if next_shape == ElementType.WALL:
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)

        elif next_shape == ElementType.BULLET or (ElementType.BULLET_UP <= next_shape <= ElementType.BULLET_LEFT):
            other_bullet = self.findBulletAt(new_x, new_y)
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)
            if other_bullet is not None:
                # self.parent_widget.setShapeAt(other_bullet.x, other_bullet.y, ElementType.NONE) #mozda setShape na new_x, new_y?
                bullets_to_be_removed.append(other_bullet)
                print("find other bullet!")
            else:
                print("bulletImpact(): other_bullet is None")

        elif (next_shape == ElementType.PLAYER1 or (ElementType.PLAYER1_UP <= next_shape <= ElementType.PLAYER1_LEFT) or next_shape == ElementType.PLAYER2 or (ElementType.PLAYER2_UP <= next_shape <= ElementType.PLAYER2_LEFT)) and bullet.type == BulletType.ENEMY:
            if next_shape == ElementType.PLAYER1 or (ElementType.PLAYER1_UP <= next_shape <= ElementType.PLAYER1_LEFT):
                gb_player = self.parent_widget.player_1
                starting_position = self.parent_widget.player_1_starting_position
            elif next_shape == ElementType.PLAYER2 or (ElementType.PLAYER2_UP <= next_shape <= ElementType.PLAYER2_LEFT):
                gb_player = self.parent_widget.player_2
                starting_position = self.parent_widget.player_2_starting_position



            gb_player.lives -= 1
            if gb_player.player_type == PlayerType.PLAYER_1:
                self.send_status_update(player_1_life=gb_player.lives) #slanje zahteva na klijent za osvezavanje stat framea
            elif gb_player.player_type == PlayerType.PLAYER_2:
                self.send_status_update(player_2_life=gb_player.lives)

            if gb_player.lives > 0:
                self.parent_widget.setShapeAt(gb_player.x, gb_player.y, ElementType.NONE)
                gb_player.x = starting_position[0]
                gb_player.y = starting_position[1]
                gb_player.orientation = Orientation.UP
                self.parent_widget.setShapeAt(gb_player.x, gb_player.y, Helper.enumFromOrientationPlayer(gb_player.player_type, Orientation.UP))
            else:
                self.parent_widget.gameOver()
        elif (next_shape == ElementType.ENEMY or (ElementType.ENEMY_UP <= next_shape <= ElementType.ENEMY_LEFT)) and bullet.type == BulletType.FRIEND:
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)

            for enemy in self.parent_widget.enemy_list:
                if new_x == enemy.x and new_y == enemy.y:
                    self.parent_widget.enemy_list.remove(enemy)
                    self.parent_widget.num_of_all_enemies -= 1
                    self.send_status_update(enemies_left=self.parent_widget.num_of_all_enemies)
                    if self.parent_widget.num_of_all_enemies > 0:
                        while (True):
                            rand_x = randint(0, self.parent_widget.BoardWidth)
                            if self.parent_widget.getShapeType(rand_x, 0) == ElementType.NONE:
                                break

                        self.parent_widget.enemy_list.append(EnemyTank(rand_x))
                        self.parent_widget.setShapeAt(rand_x, 0, ElementType.ENEMY_DOWN)
                    elif self.parent_widget.num_of_all_enemies == -3:
                        self.parent_widget.advanceToNextLevel()
                        levelChanged = True
                    break

        elif next_shape == ElementType.BASE and bullet.type == BulletType.ENEMY:
            self.parent_widget.gameOver()

        if not levelChanged:
            bullets_to_be_removed.append(bullet)
            self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)




    def findBulletAt(self, x, y):
        for bullet in self.parent_widget.bullet_list:
            if bullet.x == x and bullet.y == y:
                return bullet
