from PyQt5.QtCore import QThread, pyqtSignal
import time
from enemy_tank import EnemyTank
from enums import ElementType, Orientation, BulletType
from helper_mp import Helper
from bullet import Bullet
import pickle

class MoveEnemyThreadMP(QThread):

    def __init__(self, parentQWidget = None):
        super(MoveEnemyThreadMP, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.speed = 0.25
        self.was_canceled = False
        self.iterator = 0
        self.chosen_enemy = None

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
        #enemies_to_be_removed = []
        #bullets_to_be_removed = []

        for enemy in self.parent_widget.enemy_list:
            new_x = enemy.x
            new_y = enemy.y

            if enemy.direction is Orientation.UP:
                new_y -= 1
                new_orientation = Orientation.RIGHT
            elif enemy.direction is Orientation.RIGHT:
                new_x += 1
                new_orientation = Orientation.DOWN
            elif enemy.direction is Orientation.DOWN:
                new_y += 1
                new_orientation = Orientation.LEFT
            elif enemy.direction is Orientation.LEFT:
                new_x -= 1
                new_orientation = Orientation.UP

            if Helper.isCollision(self.parent_widget, new_x, new_y, ElementType.ENEMY):
                is_bullet_collision = False
                board_width = self.parent_widget.BoardWidth
                board_height = self.parent_widget.BoardHeight

                #if 0 <= new_x <= board_width - 1 and 0 <= new_y <= board_height - 1:
                #    next_shape = self.parent_widget.getShapeType(new_x, new_y)

                    #if next_shape == ElementType.BULLET:
                    #    self.parent_widget.setShapeAt(enemy.x, enemy.y, ElementType.NONE)
                    #    self.parent_widget.enemy_list.remove(enemy)
                        # bullet_to_die = self.parent_widget.findBulletAt(new_x, new_y)
                        #if bullet_to_die is not None:
                        #    self.parent_widget.setShapeAt(bullet_to_die.x, bullet_to_die.y, ElementType.NONE)
                        #    bullets_to_be_removed.append(bullet_to_die)
                        #else:
                        #    print("moveEnemy(): bullet_to_die is None")

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

        #self.chosen_enemy = self.chooseRandomEnemy()
       #if self.chosen_enemy is not None:
       #    if self.chosen_enemy.fireBullet():
       #        if Helper.isCollision(self.parent_widget,
       #                              self.chosen_enemy.active_bullet.x,
       #                              self.chosen_enemy.active_bullet.y,
       #                              ElementType.BULLET):
       #            self.bulletImpactOnFire(self.chosen_enemy.active_bullet.x,
       #                               self.chosen_enemy.active_bullet.y,
       #                               self.chosen_enemy.active_bullet,
       #                               bullets_to_be_removed,
       #                               [])
       #        else:
       #            self.bulletFired()

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

    def sendUpdatedEnemies(self):
        id = "UPDATE_ENEMY"
        data = pickle.dumps((id, self.parent_widget.board), -1)
        self.parent_widget.communication.conn1.sendall(data)
        self.parent_widget.communication.conn2.sendall(data)

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
