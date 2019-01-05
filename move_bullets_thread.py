from PyQt5.QtCore import QThread, Qt, pyqtSignal
import game_board as gb
import time
from bullet import Bullet
from enums import Orientation, ElementType
from helper import Helper


class MoveBulletsThread(QThread):
    bullets_move_signal = pyqtSignal(list, list, list)
    #bullet_impact_signal = pyqtSignal(int, int, Bullet)

    def __init__(self, parentQWidget = None):
        super(MoveBulletsThread, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.was_canceled = False

    def run(self):
        while not self.was_canceled:
            self.parent_widget.mutex.lock()
            self.moveBullets()
            self.parent_widget.mutex.unlock()
            time.sleep(0.05)

    def cancel(self):
        self.was_canceled = True
        
    def moveBullets(self):
        """
        for bullet in self.parent_widget.bullet_dictionary:
            if bullet.orientation is Orientation.UP:
                if not Helper.isCollision(self.parent_widget, bullet.x, bullet.y - 1, ElementType.BULLET):
                    bullet.y -= 1
            elif bullet.orientation is Orientation.RIGHT:
                if not Helper.isCollision(self.parent_widget, bullet.x + 1, bullet.y, ElementType.BULLET):
                    bullet.x += 1
            elif bullet.orientation is Orientation.DOWN:
                if not Helper.isCollision(self.parent_widget, bullet.x, bullet.y + 1, ElementType.BULLET):
                    bullet.y += 1
            elif bullet.orientation is Orientation.LEFT:
                if not Helper.isCollision(self.parent_widget, bullet.x - 1, bullet.y, ElementType.BULLET):
                    bullet.x -= 1

            if isChanged:
                #if impact logic
                if Helper.isCollision(self.parent_widget, new_x, new_y, ElementType.BULLET):
                    self.bullet_impact_signal.emit(new_x, new_y, bullet)
                    #TODO tank.active_bullet = None !!!
                else:
                    self.thread_signal.emit(new_x, new_y, bullet)
            # time.sleep(0.05)"""
        bullets_with_new_position = []
        bullets_to_be_removed = []
        enemies_to_be_removed = []

        for bullet in self.parent_widget.bullet_dictionary:
            self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)

            new_x = bullet.x
            new_y = bullet.y

            if bullet.orientation is Orientation.UP:
                new_y -= 1
            elif bullet.orientation is Orientation.RIGHT:
                new_x += 1
            elif bullet.orientation is Orientation.DOWN:
                new_y += 1
            elif bullet.orientation is Orientation.LEFT:
                new_x -= 1

            if Helper.isCollision(self.parent_widget, new_x, new_y, ElementType.BULLET):
                print("bullet_impact")
                self.bulletImpact(new_x, new_y, bullet, bullets_to_be_removed, enemies_to_be_removed)

            else:
                bullet.x = new_x
                bullet.y = new_y
                self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.BULLET)
                bullets_with_new_position.append(bullet)

        self.bullets_move_signal.emit(bullets_with_new_position,
                                      bullets_to_be_removed,
                                      enemies_to_be_removed)

    def bulletImpact(self, new_x, new_y, bullet, bullets_to_be_removed, enemies_to_be_removed):
        if not(0 <= new_x <= self.parent_widget.BoardWidth - 1 and 0 <= new_y <= self.parent_widget.BoardHeight - 1):
            #if (bullet.x < 0 or bullet.x > self.parent_widget.BoardWidth - 1) or (bullet.y < 0 or bullet.y > self.BoardHeight - 1):
             #   bullet.bullet_owner.active_bullet = None
              #  return
            self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            #bullet.bullet_owner.active_bullet = None
            bullets_to_be_removed.append(bullet)
            return

        next_shape = self.parent_widget.getShapeType(new_x, new_y)

        if next_shape is ElementType.WALL:
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)
            self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            bullets_to_be_removed.append(bullet)

        elif next_shape is ElementType.BULLET:
            self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            bullets_to_be_removed.append(bullet)

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
            self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            bullets_to_be_removed.append(bullet)


        elif next_shape is ElementType.ENEMY and bullet.type is BulletType.FRIEND:
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)

            for enemy in self.parent_widget.enemy_dictionary:
                if new_x == enemy.x and  new_y == enemy.y:
                    enemies_to_be_removed.append()
                    break
            self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            bullets_to_be_removed.append(bullet)

        elif next_shape is ElementType.BASE:
            self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            bullets_to_be_removed.append(bullet)
            print("game over")

    def findBulletAt(self, x, y):
        for bullet in self.parent_widget.bullet_dictionary:
            if bullet.x == x and bullet.y == y:
                return bullet