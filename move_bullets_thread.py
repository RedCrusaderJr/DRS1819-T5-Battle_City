from PyQt5.QtWidgets import QPushButton
from PyQt5.QtCore import QThread, Qt, pyqtSignal
import game_board as gb
import time
from bullet import Bullet
from enums import Orientation, ElementType, BulletType, PlayerType
from helper import Helper
import sys

class MoveBulletsThread(QThread):
    bullets_move_signal = pyqtSignal(list, list, list)
    dead_player_signal = pyqtSignal(int)

    def __init__(self, parentQWidget = None):
        super(MoveBulletsThread, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.speed = 0.07
        if self.parent_widget.socket is not None:
            self.socket = self.parent_widget.socket
        else:
            self.socket = None
        self.was_canceled = False

        #self.button_restart = QPushButton('Restart', self.parent_widget)
        #self.button_restart.clicked.connect(self.restartGame)
        self.parent_widget.speed_up_signal.connect(self.speedUp)
        #self.button_restart.move(250, 480)
        #self.button_restart.resize(200, 50)
        #name_font = self.button_restart.font()
        #name_font.setPointSize(15)
        #self.button_restart.setFont(name_font)
        #self.button_restart.hide()
#
        #self.button_end = QPushButton('End', self.parent_widget)
        #self.button_end.clicked.connect(self.endGame)
        #self.button_end.move(550, 480)
        #self.button_end.resize(200, 50)
        #self.button_end.setFont(name_font)
        #self.button_end.hide()
        #self.parent_widget.game_over_signal.connect(self.gameOver)

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
        bullets_with_new_position = []
        bullets_to_be_removed = []
        enemies_to_be_removed = []

        for bullet in self.parent_widget.bullet_dictionary:
            if bullet in bullets_to_be_removed:
                continue
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
                self.bulletImpact(new_x, new_y, bullet, bullets_to_be_removed, enemies_to_be_removed)

            else:
                bullet.x = new_x
                bullet.y = new_y
                self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.BULLET)
                bullets_with_new_position.append(bullet)

        self.bulletsMoveSignal(bullets_with_new_position, bullets_to_be_removed, enemies_to_be_removed)

    def bulletImpact(self, new_x, new_y, bullet, bullets_to_be_removed, enemies_to_be_removed):
        if not(0 <= new_x <= self.parent_widget.BoardWidth - 1 and 0 <= new_y <= self.parent_widget.BoardHeight - 1):
            self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
            bullets_to_be_removed.append(bullet)
            return

        next_shape = self.parent_widget.getShapeType(new_x, new_y)

        if next_shape is ElementType.WALL:
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)

        elif next_shape is ElementType.BULLET:
            other_bullet = self.findBulletAt(new_x, new_y)
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)
            if other_bullet is not None:
                #self.parent_widget.setShapeAt(other_bullet.x, other_bullet.y, ElementType.NONE) #mozda setShape na new_x, new_y?
                bullets_to_be_removed.append(other_bullet)
                #("find other bullet!")
            #else:
                #print("bulletImpact(): other_bullet is None")

        elif (next_shape is ElementType.PLAYER1 or next_shape is ElementType.PLAYER2) and bullet.type is BulletType.ENEMY:
            if next_shape is ElementType.PLAYER1:
                gb_player = self.parent_widget.player_1
            elif next_shape is ElementType.PLAYER2:
                gb_player = self.parent_widget.player_2

            gb_player.lives -= 1
            if gb_player.lives > 0:
                self.parent_widget.setPlayerToStartingPosition(gb_player.x, gb_player.y, gb_player)
                if gb_player.player_type == PlayerType.PLAYER_1:
                    #TODO: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    self.parent_widget.change_lives_signal.emit(1, gb_player.lives)
                elif gb_player.player_type == PlayerType.PLAYER_2:
                    #TODO: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    self.parent_widget.change_lives_signal.emit(2, gb_player.lives)
            else:
                #print(f"game over for {next_shape}")
                self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)
                if next_shape is ElementType.PLAYER1:
                    self.parent_widget.change_lives_signal.emit(1, gb_player.lives)
                    #TODO:!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    self.dead_player_signal.emit(1)
                    if self.parent_widget.mode == 1 or self.parent_widget.player_2.lives <= 0:
                        self.gameOver()

                elif next_shape is ElementType.PLAYER2:
                    self.parent_widget.change_lives_signal.emit(2, gb_player.lives)
                    #TODO: !!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
                    self.dead_player_signal.emit(2)
                    if self.parent_widget.player_1.lives <= 0:
                        self.gameOver()

        elif next_shape is ElementType.ENEMY and bullet.type == BulletType.FRIEND:
            self.parent_widget.setShapeAt(new_x, new_y, ElementType.NONE)

            for enemy in self.parent_widget.enemy_dictionary:
                if new_x == enemy.x and new_y == enemy.y:
                    enemies_to_be_removed.append(enemy)
                    break

        elif next_shape is ElementType.BASE and bullet.type == BulletType.ENEMY:
            #print("game over")
            self.gameOver()

        self.parent_widget.setShapeAt(bullet.x, bullet.y, ElementType.NONE)
        bullets_to_be_removed.append(bullet)

    # region SIGNAL_EMITS
    def bulletsMoveSignal(self, bullets_with_new_position, bullets_to_be_removed, enemies_to_be_removed):
        self.bullets_move_signal.emit(bullets_with_new_position,
                                      bullets_to_be_removed,
                                      enemies_to_be_removed)
        #TODO: SEND BULLETS_MOVE
        if self.parent_widget.socket is not None:
            data = pickle.dumps(("BULLETS_MOVED", (bullets_with_new_position, bullets_to_be_removed, enemies_to_be_removed)))
            with self.socket:
                self.socket.sendall(data)
    # endregion

    def gameOver(self):
        self.parent_widget.clearBoard()
        self.parent_widget.move_enemy_thread.cancel()
        self.parent_widget.player_1.lives = 0
        #!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!! ubaci enum
        if self.parent_widget.mode == 2:
            self.parent_widget.player_2.lives = 0

        for enemy in self.parent_widget.enemy_dictionary:
            self.parent_widget.enemy_dictionary[enemy].hide()
        self.parent_widget.loadLevel(0)

        #self.button_restart.show()
        #self.button_end.show()

    def restartGame(self):
        # self.parent_widget.clearBoard()
        self.parent_widget.move_player_1_thread.cancel()
        if self.parent_widget.mode == 2:
            self.parent_widget.move_player_2_thread.cancel()
        self.parent_widget.move_bullets_thread.cancel()
        self.parent_widget.restart_game_signal.emit()

    def endGame(self):
        self.parent_widget.move_player_1_thread.cancel()
        if self.parent_widget.mode == 2:
            self.parent_widget.move_player_2_thread.cancel()
        self.parent_widget.move_bullets_thread.cancel()
        #print('endddddddddddddd')


    def findBulletAt(self, x, y):
        for bullet in self.parent_widget.bullet_dictionary:
            if bullet.x == x and bullet.y == y:
                return bullet