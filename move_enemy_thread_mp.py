from PyQt5.QtCore import QThread, pyqtSignal
import time
from enemy_tank import EnemyTank
from enums import ElementType, Orientation, BulletType, PlayerType
from helper_mp import Helper
from bullet import Bullet
import pickle
import struct
from random import randint

class MoveEnemyThreadMP(QThread):

    def __init__(self, parentQWidget = None):
        super(MoveEnemyThreadMP, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.speed = 0.25
        self.was_canceled = False
        self.iterator = 0
        self.chosen_enemy = None
        self.parent_widget.speed_up_signal.connect(self.speedUp)

    def run(self):
        while not self.was_canceled:
            self.parent_widget.mutex.lock()
            self.moveEnemy()
            self.iterator += 1
            if self.iterator >= len(self.parent_widget.enemy_list):
                self.iterator = 0
            self.parent_widget.mutex.unlock()
            time.sleep(self.speed)

    def cancel(self):
        self.was_canceled = True

    def speedUp(self):
        if self.speed - 0.03 > 0.07:
            self.speed -= 0.03

    def moveEnemy(self):
        #enemies_with_new_position = []
        #enemies_with_new_orientation = []
        enemies_to_be_removed = []
        #bullets_to_be_removed = []

        for enemy in self.parent_widget.enemy_list:
            new_x = enemy.x
            new_y = enemy.y

            if enemy.direction == Orientation.UP:
                new_y -= 1
                new_orientation = Orientation.RIGHT
            elif enemy.direction == Orientation.RIGHT:
                new_x += 1
                new_orientation = Orientation.DOWN
            elif enemy.direction == Orientation.DOWN:
                new_y += 1
                new_orientation = Orientation.LEFT
            elif enemy.direction == Orientation.LEFT:
                new_x -= 1
                new_orientation = Orientation.UP

            if Helper.isCollision(self.parent_widget, new_x, new_y, ElementType.ENEMY):
                is_bullet_collision = False
                board_width = self.parent_widget.BoardWidth
                board_height = self.parent_widget.BoardHeight

                if 0 <= new_x <= board_width - 1 and 0 <= new_y <= board_height - 1:
                    next_shape = self.parent_widget.getShapeType(new_x, new_y)

                    try:
                        type = self.parent_widget.findBulletAt(new_x, new_y).type
                    except:
                        type = BulletType.ENEMY

                    if (next_shape == ElementType.BULLET or ElementType.BULLET_UP <= next_shape <= ElementType.BULLET_LEFT)  and type == BulletType.FRIEND:
                        is_bullet_collision = True
                        self.parent_widget.setShapeAt(enemy.x, enemy.y, ElementType.NONE)
                        enemies_to_be_removed.append(enemy)
                        bullet_to_die = self.parent_widget.findBulletAt(new_x, new_y)
                        if bullet_to_die is not None:
                            self.parent_widget.setShapeAt(bullet_to_die.x, bullet_to_die.y, ElementType.NONE)
                            self.parent_widget.bullet_list.remove(bullet_to_die)
                            bullet_to_die.bullet_owner.active_bullet = None


                if not is_bullet_collision:
                    #transform = QTransform()
                    #transform.rotate(Helper.rotationFunction(enemy.direction, new_orientation))
                    enemy.direction = new_orientation
                    self.parent_widget.setShapeAt(enemy.x, enemy.y, Helper.enumFromOrientationEnemy(new_orientation))
                    #enemies_with_new_orientation.append((enemy, transform))
            else:
                self.parent_widget.setShapeAt(enemy.x, enemy.y, ElementType.NONE)
                enemy.x = new_x
                enemy.y = new_y
                self.parent_widget.setShapeAt(enemy.x, enemy.y, Helper.enumFromOrientationEnemy(enemy.direction))

        for elemnt in enemies_to_be_removed:
            self.parent_widget.enemy_list.remove(elemnt)
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



        self.chosen_enemy = self.chooseRandomEnemy()
        if self.chosen_enemy is not None:
            if self.chosen_enemy.fireBullet():
                if Helper.isCollision(self.parent_widget,
                                      self.chosen_enemy.active_bullet.x,
                                      self.chosen_enemy.active_bullet.y,
                                      ElementType.BULLET):
                    self.bulletImpactOnFire(self.chosen_enemy.active_bullet.x,
                                            self.chosen_enemy.active_bullet.y,
                                            self.chosen_enemy.active_bullet)
                else:
                    self.bulletFired()

        self.sendUpdatedEnemies()

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


        elif (next_shape == ElementType.PLAYER1 or (
                ElementType.PLAYER1_UP <= next_shape <= ElementType.PLAYER1_LEFT) or next_shape == ElementType.PLAYER2 or (
                      ElementType.PLAYER2_UP <= next_shape <= ElementType.PLAYER2_LEFT)) and bullet.type == BulletType.ENEMY:

            if next_shape == ElementType.PLAYER1 or (ElementType.PLAYER1_UP <= next_shape <= ElementType.PLAYER1_LEFT):
                gb_player = self.parent_widget.player_1
                starting_position = self.parent_widget.player_1_starting_position
            elif next_shape == ElementType.PLAYER2 or (ElementType.PLAYER2_UP <= next_shape <= ElementType.PLAYER2_LEFT):
                gb_player = self.parent_widget.player_2
                starting_position = self.parent_widget.player_2_starting_position


            gb_player.lives -= 1
            if gb_player.player_type == PlayerType.PLAYER_1:
                self.send_status_update(player_1_life=gb_player.lives)
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

        elif next_shape == ElementType.BASE and bullet.type == BulletType.ENEMY:
            self.parent_widget.gameOver()

        bullet.bullet_owner.active_bullet = None
        #self.bulletImpactSignal(bullets_to_be_removed, enemies_to_be_removed)

    def send_msg(self, sock, msg):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        try:
            sock.sendall(msg)
        except:
            return

    def sendUpdatedEnemies(self):
        #id = "UPDATE_ENEMY"

        data = pickle.dumps((str("UPDATE_ENEMY"), self.parent_widget.board), -1)
        data2 = pickle.dumps((str("UPDATE_ENEMY"), self.parent_widget.board), -1)

        #print(len(data))

        #self.parent_widget.communication.conn1.send(data)
        #self.parent_widget.communication.conn2.send(data2)

        self.send_msg(self.parent_widget.communication.conn1, data)
        self.send_msg(self.parent_widget.communication.conn2, data2)

    def chooseRandomEnemy(self):
        if self.iterator >= len(self.parent_widget.enemy_list):
            self.iterator = 0

        i = 0
        chosen_enemy = None
        for enemy in self.parent_widget.enemy_list:
            if i == self.iterator:
                chosen_enemy = enemy
                break
            i += 1
        return  chosen_enemy

    def bulletFired(self):
        bullet = self.chosen_enemy.active_bullet
        self.parent_widget.setShapeAt(bullet.x, bullet.y, Helper.enumFromOrientationBullet(bullet.orientation))
        self.parent_widget.bullet_list.append(bullet)

    def send_status_update(self, player_1_life = None, player_2_life = None, enemies_left = None):
        data = pickle.dumps((str("STATUS_UPDATE"), (player_1_life, player_2_life, enemies_left)), -1)

        self.send_msg(self.parent_widget.communication.conn1, data)
        self.send_msg(self.parent_widget.communication.conn2, data)
