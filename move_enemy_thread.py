from PyQt5.QtCore import QThread, pyqtSignal
from PyQt5.QtGui import QTransform
import time
from enemy_tank import EnemyTank
from enums import ElementType, Orientation, BulletType, PlayerType
from helper import Helper
from bullet import Bullet


class MoveEnemyThread(QThread):
    bullet_fired_signal = pyqtSignal(Bullet, QTransform)
    bullet_impact_signal = pyqtSignal(list, list, list)
    enemy_move_signal = pyqtSignal(list, list, list, list)
    dead_player_signal = pyqtSignal(int)
    game_over_signal = pyqtSignal()

    def __init__(self, parentQWidget = None):
        super(MoveEnemyThread, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.parent_widget.speed_up_signal.connect(self.speedUp)
        self.speed = 0.25
        if self.parent_widget.socket is not None:
            self.socket = self.parent_widget.socket
        else:
            self.socket = None
        self.was_canceled = False
        self.iterator = 0
        self.chosen_enemy = None

    def run(self):
        while not self.was_canceled:
            self.parent_widget.mutex.lock()
            self.moveEnemy()
            self.iterator += 1
            if self.iterator >= len(self.parent_widget.enemy_dictionary):
                self.iterator = 0
            self.parent_widget.mutex.unlock()
            time.sleep(self.speed)

    def cancel(self):
        self.was_canceled = True

    def speedUp(self):
        if self.speed - 0.03 > 0.07:
            self.speed -= 0.03

    def moveEnemy(self):
        enemies_with_new_position = []
        enemies_with_new_orientation = []
        enemies_to_be_removed = []
        bullets_to_be_removed = []

        for enemy in self.parent_widget.enemy_dictionary:
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

                if 0 <= new_x <= board_width - 1 and 0 <= new_y <= board_height - 1:
                    next_shape = self.parent_widget.getShapeType(new_x, new_y)

                    try:
                        type = self.parent_widget.findBulletAt(new_x, new_y).type
                    except:
                        type = BulletType.ENEMY

                    if next_shape == ElementType.BULLET and  type == BulletType.FRIEND:
                        is_bullet_collision = True
                        self.parent_widget.setShapeAt(enemy.x, enemy.y, ElementType.NONE)
                        enemies_to_be_removed.append(enemy)
                        bullet_to_die = self.parent_widget.findBulletAt(new_x, new_y)
                        if bullet_to_die is not None:
                            self.parent_widget.setShapeAt(bullet_to_die.x, bullet_to_die.y, ElementType.NONE)
                            bullets_to_be_removed.append(bullet_to_die)
                        #else:
                            #print("moveEnemy(): bullet_to_die is None")

                if not is_bullet_collision:
                    transform = QTransform()
                    transform.rotate(Helper.rotationFunction(enemy.direction, new_orientation))
                    enemy.direction = new_orientation
                    enemies_with_new_orientation.append((enemy, transform))
            else:
                self.parent_widget.setShapeAt(enemy.x, enemy.y, ElementType.NONE)
                enemy.x = new_x
                enemy.y = new_y
                self.parent_widget.setShapeAt(enemy.x, enemy.y, ElementType.ENEMY)
                enemies_with_new_position.append(enemy)

        self.enemyMoveSignal(enemies_with_new_position,
                                    enemies_with_new_orientation,
                                    enemies_to_be_removed,
                                    bullets_to_be_removed)

        self.chosen_enemy = self.chooseRandomEnemy()
        if self.chosen_enemy is not None:
            if self.chosen_enemy.fireBullet():
                if Helper.isCollision(self.parent_widget,
                                      self.chosen_enemy.active_bullet.x,
                                      self.chosen_enemy.active_bullet.y,
                                      ElementType.BULLET):
                    self.bulletImpactOnFire(self.chosen_enemy.active_bullet.x,
                                       self.chosen_enemy.active_bullet.y,
                                       self.chosen_enemy.active_bullet,
                                       bullets_to_be_removed,
                                       [])
                else:
                    self.bulletFired()

    def bulletFired(self):
        bullet = self.chosen_enemy.active_bullet

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
            #else:
                #print("Move enemy thread: bulletImpactOnFire(): other_bullet is None")

        elif (next_shape is ElementType.PLAYER1 or next_shape is ElementType.PLAYER2) and bullet.type is BulletType.ENEMY:
            if next_shape is ElementType.PLAYER1:
                gb_player = self.parent_widget.player_1
            elif next_shape is ElementType.PLAYER2:
                gb_player = self.parent_widget.player_2

            if gb_player.lives > 0:
                self.parent_widget.setPlayerToStartingPosition(gb_player.x, gb_player.y, gb_player)
                gb_player.lives -= 1
                if gb_player.player_type == PlayerType.PLAYER_1:
                    self.parent_widget.change_lives_signal.emit(1, gb_player.lives)
                    if gb_player.lives <= 0 and self.parent_widget.player_2.lives <= 0:
                        self.dead_player_signal.emit(1)
                        self.game_over_signal.emit()
                    elif gb_player.lives <= 0:
                        self.dead_player_signal.emit(1)
                else:
                    self.parent_widget.change_lives_signal.emit(2, gb_player.lives)
                    if gb_player.lives <= 0 and self.parent_widget.player_1.lives <= 0:
                        self.dead_player_signal.emit(2)
                        self.game_over_signal.emit()
                    elif gb_player.lives <= 0:
                        self.dead_player_signal.emit(2)
            #else:
                #print(f"game over for {next_shape}")

        elif next_shape is ElementType.BASE:
            self.game_over_signal.emit()
    
        bullet.bullet_owner.active_bullet = None
        self.bulletImpactSignal(bullets_to_be_removed, enemies_to_be_removed)

    #region SIGNAL_EMITS
    def enemyMoveSignal(self, enemies_with_new_position, enemies_with_new_orientation, enemies_to_be_removed, bullets_to_be_removed):
        self.enemy_move_signal.emit(enemies_with_new_position,
                                    enemies_with_new_orientation,
                                    enemies_to_be_removed,
                                    bullets_to_be_removed)
        #TODO: SEND ENEMY_MOVED
        if self.parent_widget.socket is not None:
            data = pickle.dumps(("ENEMY_MOVED", (enemies_with_new_position,
                                                enemies_with_new_orientation,
                                                enemies_to_be_removed,
                                                bullets_to_be_removed)))
            with self.socket:
                self.socket.sendall(data)

    def bulletFiredSignal(self, bullet, transform):
        self.bullet_fired_signal.emit(bullet, transform)
        #TODO: SEND BULLET_FIRED
        if self.parent_widget.socket is not None:
            data = pickle.dumps(("BULLET_FIRED", (bullet, transform)))
            with self.socket:
                self.socket.sendall(data)

    def bulletImpactSignal(self, bullets_to_be_removed, enemies_to_be_removed):
        self.bullet_impact_signal.emit([], bullets_to_be_removed, enemies_to_be_removed)
        #TODO: SEND BULLET_IMPACT
        if self.parent_widget.socket is not None:
            data = pickle.dumps(("BULLET_IMPACT", ([], bullets_to_be_removed, enemies_to_be_removed)))
            with self.socket:
                self.socket.sendall(data)
    #endregion

    def chooseRandomEnemy(self):
        if self.iterator >= len(self.parent_widget.enemy_dictionary):
            self.iterator = 0

        i = 0
        chosen_enemy = None
        for enemy in self.parent_widget.enemy_dictionary:
            if i == self.iterator:
                chosen_enemy = enemy
                break
            i += 1

        return  chosen_enemy