from PyQt5.QtWidgets import QFrame, QLabel
from PyQt5.QtGui import QPainter, QColor, QTransform, QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QMutex
from move_player_thread import MovePlayerThread
from move_enemy_thread import MoveEnemyThread
from move_bullets_thread import MoveBulletsThread
from tank import Tank
from enemy_tank import EnemyTank
import os
from enums import PlayerType, ElementType, WallType, Orientation, BulletType
from helper import Helper
from bullet import Bullet
from random import sample, randint
import time

class GameBoard(QFrame):
    #TODO: refactor ovo staviti negde
    BoardWidth = 32
    BoardHeight = 18
    mutex = QMutex()

    change_lives_signal = pyqtSignal(int, int)
    change_level_signal = pyqtSignal()
    change_enemies_left_signal = pyqtSignal(int)

    # tile width/height in px
    TILE_SIZE = 16

    def __init__(self, parent, mode):
        super().__init__(parent)
        self.mode = mode
        self.commands_1 = []
        self.commands_2 = []
        self.initGameBoard()

    def initGameBoard(self):
        self.num_of_all_enemies = 5
        self.num_of_enemies_per_level = 4
        self.current_level = 1

        self.player_1 = Tank(PlayerType.PLAYER_1)
        self.player_1_label = QLabel(self)
        self.player_1_starting_position = ()

        if self.mode == 2:
            self.player_2 = Tank(PlayerType.PLAYER_2)
            self.player_2_label = QLabel(self)
            self.player_2_starting_position = ()

        self.random_values = []
        self.random_values = sample(range(1, 32), self.num_of_enemies_per_level)

        self.bullet_dictionary = {}
        self.enemy_dictionary = {}
        for i in range(self.num_of_enemies_per_level):
            self.enemy_dictionary[EnemyTank(self.random_values[i])] = QLabel(self)

        self.board = []
        self.clearBoard()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWalls()


        self.move_player_1_thread = MovePlayerThread(self.commands_1, self.player_1, self)
        self.move_player_1_thread.player_moved_signal.connect(self.playerMoved)
        self.move_player_1_thread.bullet_fired_signal.connect(self.bulletFired)
        self.move_player_1_thread.bullet_impact_signal.connect(self.bulletMoved)

        if self.mode == 2:
            self.move_player_2_thread = MovePlayerThread(self.commands_2, self.player_2, self)
            self.move_player_2_thread.player_moved_signal.connect(self.playerMoved)
            self.move_player_2_thread.bullet_fired_signal.connect(self.bulletFired)
            self.move_player_2_thread.bullet_impact_signal.connect(self.bulletMoved)

        self.move_enemy_thread = MoveEnemyThread(self)
        self.move_enemy_thread.bullet_fired_signal.connect(self.bulletFired)
        self.move_enemy_thread.bullet_impact_signal.connect(self.bulletMoved)
        self.move_enemy_thread.enemy_move_signal.connect(self.enemyCallback)

        self.move_bullets_thread = MoveBulletsThread(self)
        self.move_bullets_thread.bullets_move_signal.connect(self.bulletMoved)
        self.move_bullets_thread.dead_player_signal.connect(self.removeDeadPlayer)

    def initPlayers(self):
        #self.player_1_label.hide()
        #self.player_2_label.hide()

        self.player_1.reset()
        pixmap_1 = self.player_1.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
        self.setPlayerToStartingPosition(self.player_1.x, self.player_1.y, self.player_1)

        self.player_1_label.setPixmap(pixmap_1)
        self.setGameBoardLabelGeometry(self.player_1_label, self.player_1.x, self.player_1.y)
        self.player_1_label.orientation = Orientation.UP
        self.setShapeAt(self.player_1.x, self.player_1.y, ElementType.PLAYER1)
        self.player_1_label.show()


        if self.mode == 2:
            self.player_2.reset()
            pixmap_2 = self.player_2.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
            self.setPlayerToStartingPosition(self.player_2.x, self.player_2.y, self.player_2)
            
            self.player_2_label.setPixmap(pixmap_2)
            self.setGameBoardLabelGeometry(self.player_2_label, self.player_2.x, self.player_2.y)
            self.player_2_label.orientation = Orientation.UP
            self.setShapeAt(self.player_2.x, self.player_2.y, ElementType.PLAYER2)
            self.player_2_label.show()

    #region EVENTS
    def showEvent(self, *args, **kwargs):
        print("show event")

        self.initPlayers()


        for enemy in self.enemy_dictionary:
            pixmap3 = enemy.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
            self.enemy_dictionary[enemy].setPixmap(pixmap3)
            self.setGameBoardLabelGeometry(self.enemy_dictionary[enemy], enemy.x, enemy.y)
            self.setShapeAt(enemy.x, enemy.y, ElementType.ENEMY)

        self.move_player_1_thread.start()
        if self.mode == 2:
            self.move_player_2_thread.start()
        self.move_enemy_thread.start()
        self.move_bullets_thread.start()

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        rect = self.contentsRect()
        board_top = rect.bottom() - GameBoard.BoardHeight * self.getSquareHeight()
        for i in range(GameBoard.BoardHeight):
            for j in range(GameBoard.BoardWidth):
                shape_type = self.getShapeType(j, i)
                if shape_type == ElementType.WALL:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.WALL)
                elif shape_type == ElementType.BASE:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.BASE)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up or  event.key() == Qt.Key_Down or  \
                                        event.key() == Qt.Key_Left or  \
                                        event.key() == Qt.Key_Right or \
                                        event.key() == Qt.Key_Space:
            self.commands_1.append(event.key())
        elif event.key() == Qt.Key_W or event.key() == Qt.Key_S or \
                                        event.key() == Qt.Key_A or \
                                        event.key() == Qt.Key_D or \
                                        event.key() == Qt.Key_F:
            self.commands_2.append(event.key())

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down or event.key() == Qt.Key_Left\
                or event.key() == Qt.Key_Right or event.key() == Qt.Key_Space:
            self.commands_1.remove(event.key())
        elif event.key() == Qt.Key_W or event.key() == Qt.Key_S or event.key() == Qt.Key_A or event.key() == Qt.Key_D\
                or event.key() == Qt.Key_F:
            self.commands_2.remove(event.key())
    #endregion

    #region EVIDENTION_METHODS
    def setShapeAt(self, x, y, shape_type):
        self.board[(y * GameBoard.BoardWidth) + x] = shape_type

    def setWalls(self):
        self.loadLevel(self.current_level)

    def loadLevel(self, level_nr=1):
        self.clearBoard()
        """ Load specified level
        @return boolean Whether level was loaded
        """
        filename = "levels/"+str(level_nr)+".txt"
        # filename = "levels/game_over.txt"
        if not os.path.isfile(filename):
            return False
        #level = []
        f = open(filename, "r")
        data = f.read().split("\n")
        #self.mapr = []
        x, y = 0, 0
        cnt = 0
        for row in data:
            for ch in row:
                print(cnt)
                cnt += 1
                if ch == "#":
                    self.setShapeAt(x, y, ElementType.WALL)
                   # print(f"{x} {y}")
                elif ch == "$":
                    self.setShapeAt(x, y, ElementType.BASE)
                elif ch == "1":
                    self.player_1.setCoordinates(x, y)
                    self.player_1_starting_position = (x, y)
                    print("Namestio tuple")
                elif ch == "2" and self.mode == 2:
                    self.player_2.setCoordinates(x, y)
                    self.player_2_starting_position = (x, y)
                x += 1
            x = 0
            y += 1
        return True

    def advanceToNextLevel(self):
        #self.move_player_1_thread.cancel()
        #self.move_player_2_thread.cancel()
        #self.move_enemy_thread.cancel()
        #self.move_bullets_thread.cancel()

        if len(self.bullet_dictionary) > 0:
            for bullet in self.bullet_dictionary:
                self.bullet_dictionary[bullet].hide()
            self.bullet_dictionary.clear()

        if len(self.enemy_dictionary) > 0:
            for enemy in self.enemy_dictionary:
                self.enemy_dictionary[enemy].hide()
            self.enemy_dictionary.clear()

        for i in range(self.num_of_enemies_per_level):
            self.enemy_dictionary[EnemyTank(self.random_values[i])] = QLabel(self)

        for enemy in self.enemy_dictionary:
            pixmap3 = enemy.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
            self.enemy_dictionary[enemy].setPixmap(pixmap3)
            self.setGameBoardLabelGeometry(self.enemy_dictionary[enemy], enemy.x, enemy.y)
            self.setShapeAt(enemy.x, enemy.y, ElementType.ENEMY)
            self.enemy_dictionary[enemy].show()

        self.num_of_all_enemies = 10
        self.current_level += 1
        self.initPlayers()
        self.loadLevel(self.current_level)

    def setPlayerToStartingPosition(self, old_x, old_y, tank):
        if (tank.player_type == PlayerType.PLAYER_1):
            new_x = self.player_1_starting_position[0]
            new_y = self.player_1_starting_position[1]
            el_type = ElementType.PLAYER1
            label = self.player_1_label
        else:
            if self.mode == 2:
                new_x = self.player_2_starting_position[0]
                new_y = self.player_2_starting_position[1]
                el_type = ElementType.PLAYER2
                label = self.player_2_label

        for i in range(new_y, self.BoardHeight):
            for j in range(new_x, self.BoardWidth):
                shape = self.getShapeType(j, i)
                if shape is ElementType.NONE:
                    self.setShapeAt(old_x, old_y, ElementType.NONE)
                    self.setGameBoardLabelGeometry(label, j, i)
                    self.setShapeAt(j, i, el_type)
                    tank.x = j
                    tank.y = i
                    return True
                elif shape is el_type:
                    return True
            for j in range(0, new_x):
                shape = self.getShapeType(j, i)
                if shape is ElementType.NONE:
                    self.setShapeAt(old_x, old_y, ElementType.NONE)
                    self.setGameBoardLabelGeometry(label, j, i)
                    self.setShapeAt(j, i, el_type)
                    tank.x = j
                    tank.y = i
                    return True
                elif shape is el_type:
                    return True

        for i in range(0, new_y):
            for j in range(new_x, self.BoardWidth):
                shape = self.getShapeType(j, i)
                if shape is ElementType.NONE:
                    self.setShapeAt(old_x, old_y, ElementType.NONE)
                    self.setGameBoardLabelGeometry(label, j, i)
                    self.setShapeAt(j, i, el_type)
                    tank.x = j
                    tank.y = i
                    return True
                elif shape is el_type:
                    return True
            for j in range(0, new_x):
                shape = self.getShapeType(j, i)
                if shape is ElementType.NONE:
                    self.setShapeAt(old_x, old_y, ElementType.NONE)
                    self.setGameBoardLabelGeometry(label, j, i)
                    self.setShapeAt(j, i, el_type)
                    tank.x = j
                    tank.y = i
                    return True
                elif shape is el_type:
                    return True

        return False

    def addEnemy(self):
        rand_x = 0
        while(True):
            rand_x = randint(0, self.BoardWidth)
            if self.getShapeType(rand_x, 0) == ElementType.NONE:
                break

        current_enemy = EnemyTank(rand_x)
        self.enemy_dictionary[current_enemy] = QLabel(self)
        enemy_label = self.enemy_dictionary[current_enemy]

        pix_map = current_enemy.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
        enemy_label.setPixmap(pix_map)
        self.setGameBoardLabelGeometry(enemy_label, current_enemy.x, current_enemy.y)
        self.setShapeAt(current_enemy.x, current_enemy.y, ElementType.ENEMY)
        enemy_label.show()

    def clearBoard(self):
        if len(self.board) > 0:
            self.board.clear()

        for i in range(GameBoard.BoardHeight):
            for j in range(GameBoard.BoardWidth):
                self.board.append(ElementType.NONE)
        self.update()
    #endregion

    #region GET_METHODS
    def getShapeType(self, x, y):
        return self.board[(y * GameBoard.BoardWidth) + x]

    def getSquareWidth(self):
        return self.contentsRect().width() // GameBoard.BoardWidth

    def getSquareHeight(self):
        return self.contentsRect().height() // GameBoard.BoardHeight

    def findBulletAt(self, x, y):
        for bullet in self.bullet_dictionary:
            if bullet.x == x and bullet.y == y:
                return bullet
    #endregion

    #region CALLBACKS
    def enemyCallback(self, enemies_with_new_position, enemies_with_new_orientation, enemies_to_be_removed, bullets_to_be_removed):

        for enemy in enemies_with_new_position:
            if enemy in self.enemy_dictionary:
                enemy_label = self.enemy_dictionary[enemy]
                self.setGameBoardLabelGeometry(enemy_label, enemy.x,enemy.y)
            else:
                print(f"enemy({enemy}) from enemies_with_new_position is not in enemy_dictionary")

        for element in enemies_with_new_orientation:
            enemy, transform = element
            if enemy in self.enemy_dictionary:
                enemy_label = self.enemy_dictionary[enemy]
                pix = enemy_label.pixmap()
                enemy_label.setPixmap(pix.transformed(transform))
            else:
                print(f"enemy({enemy}) from enemies_with_new_orientation is not in enemy_dictionary")
        self.mutex.lock()
        for enemy in enemies_to_be_removed:
            if enemy in self.enemy_dictionary:
                enemy_label = self.enemy_dictionary[enemy]
                enemy_label.hide()
                del self.enemy_dictionary[enemy]

                self.num_of_all_enemies -= 1
                self.change_enemies_left_signal.emit(self.num_of_all_enemies)
                print(f"enemyCallback(){self.num_of_all_enemies}")
                if self.num_of_all_enemies > 0:
                    self.addEnemy()
                elif self.num_of_all_enemies == -3:
                    self.advanceToNextLevel()
                
            else:
                print(f"enemy({enemy}) from enemies_to_be_removed is not in enemy_dictionary")

        for bullet in bullets_to_be_removed:
            bullet.bullet_owner.active_bullet = None
            if bullet in self.bullet_dictionary:
                bullet_label = self.bullet_dictionary[bullet]
                bullet_label.hide()
                del self.bullet_dictionary[bullet]
            else:
                print(f"bullet({bullet}) from bullets_to_be_removed is not in bullet_dictionary")
        self.mutex.unlock()
        self.update()
        
    def playerMoved(self, tank, transform):
        if tank.player_type == PlayerType.PLAYER_1:
            gb_player = self.player_1
            gb_player_label = self.player_1_label
        elif tank.player_type == PlayerType.PLAYER_2:
            gb_player = self.player_2
            gb_player_label = self.player_2_label

        pix = gb_player_label.pixmap()
        gb_player_label.setPixmap(pix.transformed(transform))
        gb_player_label.orientation = gb_player.orientation

        self.setGameBoardLabelGeometry(gb_player_label, gb_player.x, gb_player.y)

    def bulletFired(self, bullet, transform):
        self.mutex.lock()
        self.bullet_dictionary[bullet] = QLabel(self)
        bullet_label = self.bullet_dictionary[bullet]
        self.mutex.unlock()

        bullet.pm_flying = bullet.pm_flying.scaled(self.getSquareWidth(), self.getSquareHeight())
        bullet_label.setPixmap(bullet.pm_flying.transformed(transform))

        self.setGameBoardLabelGeometry(bullet_label, bullet.x, bullet.y)
        bullet_label.orientation = bullet.orientation
        bullet_label.show()

    def bulletMoved(self, bullets_with_new_posiotion, bullets_to_be_removed, enemies_to_be_removed):

        for bullet in bullets_with_new_posiotion:
            if bullet in self.bullet_dictionary:
                bullet_label = self.bullet_dictionary[bullet]
                self.setGameBoardLabelGeometry(bullet_label, bullet.x, bullet.y)
            else:
                print(f"bullet({bullet}) from bullets_with_new_posiotion is not in bullet_dictionary")

                #if pocetna slicica:
                    #pix = self.bullet_dictionary[bullet].pixmap()
                    #self.bullet_dictionary[bullet].setPixmap(pix)

        self.mutex.lock()
        for bullet in bullets_to_be_removed:
            bullet.bullet_owner.active_bullet = None
            if bullet in self.bullet_dictionary:
                bullet_label = self.bullet_dictionary[bullet]
                bullet_label.hide()
                del self.bullet_dictionary[bullet]
            else:
                print(f"bullet({bullet}) from bullets_to_be_removed is not in bullet_dictionary")

        for enemy in enemies_to_be_removed:
            if enemy in self.enemy_dictionary:
                enemy_label = self.enemy_dictionary[enemy]
                enemy_label.hide()
                del self.enemy_dictionary[enemy]

                self.num_of_all_enemies -= 1
                print(f"BulletMoved(){self.num_of_all_enemies}")
                self.change_enemies_left_signal.emit(self.num_of_all_enemies)
                if self.num_of_all_enemies > 0:
                    self.addEnemy()
                elif self.num_of_all_enemies == -3:
                    #print(f"BulletMoved(){self.num_of_all_enemies}")
                    self.advanceToNextLevel()
            else:
                print(f"enemy({enemy}) from enemies_to_be_removed is not in enemy_dictionary")
        self.mutex.unlock()
        self.update()
    #endregion

    def drawSquare(self, painter, x, y, type):
        if type == ElementType.WALL:
            pix = QPixmap('./images/wall.jpg')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.BASE:
            pix = QPixmap('./images/lightning.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)

    def setGameBoardLabelGeometry(self, label, x, y):
        rect = self.contentsRect()
        height = self.getSquareHeight()
        bottom = rect.bottom()
        board_top = rect.bottom() - GameBoard.BoardHeight * self.getSquareHeight()
        label.setGeometry(rect.left() + x * self.getSquareWidth(),
                          board_top + y * self.getSquareHeight(),
                          self.getSquareWidth(),
                          self.getSquareHeight())

    def removeDeadPlayer(self, player_num):
        if player_num == 1:
            self.player_1_label.hide()
            self.move_player_1_thread.cancel()
        elif player_num == 2:
            self.player_2_label.hide()
            self.move_player_2_thread.cancel()
