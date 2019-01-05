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

    # tile width/height in px
    TILE_SIZE = 16

    def __init__(self, parent):
        super().__init__(parent)
        self.commands_1 = []
        self.commands_2 = []
        self.initGameBoard()

    def initGameBoard(self):
        self.num_of_all_enemies = 10

        self.player_1 = Tank(PlayerType.PLAYER_1)
        self.player_1_label = QLabel(self)
        self.player_1_starting_position = ()
        self.player_2 = Tank(PlayerType.PLAYER_2)
        self.player_2_label = QLabel(self)
        self.player_2_starting_position = ()

        #self.player1.pixmap1 = self.player1.pixmap.scaled(self.squareWidth(), self.squareHeight())
        self.enemies = []
        self.random_values = []
        self.random_values = sample(range(1, 32), 4)
        for i in range(4):
            self.enemies.append(EnemyTank(self.random_values[i]))

        self.enemies_new_position = []
        for i in range(len(self.enemies)):
            self.enemies_new_position.append(EnemyTank(self.enemies[i].x))

        self.enemy_dictionary = {}
        for i in range(len(self.enemies)):
            self.enemy_dictionary[self.enemies_new_position[i]] = QLabel(self)

        self.bullets = []
        self.bullets_new_posiotion = []
        self.bullet_dictionary = {}

        self.board = []


        self.clearBoard()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWalls()

        self.move_player_1_thread = MovePlayerThread(self.commands_1, self.player_1, self)
        self.move_player_1_thread.player_moved_signal.connect(self.playerMoved)
        self.move_player_1_thread.bullet_fired_signal.connect(self.bulletFired)
        self.move_player_1_thread.bullet_impact_signal.connect(self.bulletMoved)

        self.move_player_2_thread = MovePlayerThread(self.commands_2, self.player_2, self)
        self.move_player_2_thread.player_moved_signal.connect(self.playerMoved)
        self.move_player_2_thread.bullet_fired_signal.connect(self.bulletFired)
        self.move_player_2_thread.bullet_impact_signal.connect(self.bulletMoved)

        self.move_enemy_thread = MoveEnemyThread(self)
        self.move_enemy_thread.thread_signal.connect(self.enemyMoved)
        self.move_enemy_thread.bullet_fired_signal.connect(self.bulletFired)
        self.move_enemy_thread.bullet_impact_signal.connect(self.bulletMoved)

        self.move_bullets_thread = MoveBulletsThread(self)
        self.move_bullets_thread.bullets_move_signal.connect(self.bulletMoved)
        #self.move_bullets_thread.bullet_impact_signal.connect(self.bulletImpacted)

    #region EVENTS
    def showEvent(self, *args, **kwargs):

        pixmap1 = self.player_1.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
        pixmap2 = self.player_2.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())


        self.player_1_label.setPixmap(pixmap1)
        self.setGameBoardLabelGeometry(self.player_1_label, self.player_1.x, self.player_1.y)
        self.player_1_label.orientation = Orientation.UP
        self.setShapeAt(self.player_1.x, self.player_1.y, ElementType.PLAYER1)

        self.player_2_label.setPixmap(pixmap2)
        self.setGameBoardLabelGeometry(self.player_2_label, self.player_2.x, self.player_2.y)
        self.player_2_label.orientation = Orientation.UP
        self.setShapeAt(self.player_2.x, self.player_2.y, ElementType.PLAYER2)

        for i in range(len(self.enemies)):
            pixmap3 = self.enemies[i].pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
            self.enemy_dictionary[self.enemies_new_position[i]].setPixmap(pixmap3)
            self.setGameBoardLabelGeometry(self.enemy_dictionary[self.enemies_new_position[i]], self.enemies_new_position[i].x, self.enemies_new_position[i].y)
            self.setShapeAt(self.enemies_new_position[i].x, self.enemies_new_position[i].y, ElementType.ENEMY)

        self.move_player_1_thread.start()
        self.move_player_2_thread.start()
        self.move_enemy_thread.start()
        time.sleep(0.001)
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
        self.loadLevel(6)

    def loadLevel(self, level_nr=1):
        """ Load specified level
        @return boolean Whether level was loaded
        """
        filename = "levels/"+str(level_nr)+".txt"
        if not os.path.isfile(filename):
            return False
        #level = []
        f = open(filename, "r")
        data = f.read().split("\n")
        #self.mapr = []
        x, y = 0, 0
        for row in data:
            for ch in row:
                if ch == "#":
                    self.setShapeAt(x, y, ElementType.WALL)
                   # print(f"{x} {y}")
                elif ch == "$":
                    self.setShapeAt(x, y, ElementType.BASE)
                elif ch == "1":
                    self.player_1.setCoordinates(x, y)
                    self.player_1_starting_position = (x, y)
                elif ch == "2":
                    self.player_2.setCoordinates(x, y)
                    self.player_2_starting_position = (x, y)
                x += 1
            x = 0
            y += 1
        return True

    def setPlayerToStartingPosition(self, old_x, old_y, tank):
        if (tank.player_type == PlayerType.PLAYER_1):
            new_x = self.player_1_starting_position[0]
            new_y = self.player_1_starting_position[1]
            el_type = ElementType.PLAYER1
            label = self.player_1_label
        else:
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

    """
    def removeBullet(self, bullet):
        
            index = self.bullets_new_posiotion.index(bullet)
            self.bullets_new_posiotion.remove(bullet)
            del self.bullets[index]
    """

    def clearBoard(self):
        for i in range(GameBoard.BoardHeight):
            for j in range(GameBoard.BoardWidth):
                self.board.append(ElementType.NONE)
    #endregion

    #region GET_METHODS
    def getShapeType(self, x, y):
        return self.board[(y * GameBoard.BoardWidth) + x]

    def getSquareWidth(self):
        return self.contentsRect().width() // GameBoard.BoardWidth

    def getSquareHeight(self):
        return self.contentsRect().height() // GameBoard.BoardHeight

    def findBulletAt(self, x, y):
        for bullet in self.bullets_new_posiotion:
            if bullet.x == x and bullet.y == y:
                return bullet
    #endregion

    #region CALLBACKS
    def playerMoved(self, tank, transform):
        #self.mutex.lock()

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

        #self.mutex.unlock()

    def enemyMoved(self):
        self.mutex.lock()

        for enemy in self.enemies:
            self.setShapeAt(enemy.x, enemy.y, ElementType.NONE)

        """for enemy in self.enemies_new_position:
            self.setShapeAt(enemy.x, enemy.y, ElementType.ENEMY)
            enemy_label = self.enemy_dictionary[enemy]
            self.setGameBoardLabelGeometry(enemy_label, enemy.x, enemy.y)"""

        #TODO refactor ---> enemy = self.enemies_new_position[i]  TO dimitrije :*
        for i in range(len(self.enemies)):
            for j in range(i+1, len(self.enemies)):

                if self.enemies_new_position[i].x == self.enemies_new_position[j].x and self.enemies_new_position[i].y == self.enemies_new_position[j].y:
                    self.enemies_new_position[i].x =  self.enemies[i].x
                    self.enemies_new_position[i].y = self.enemies[i].y

            self.setShapeAt(self.enemies_new_position[i].x, self.enemies_new_position[i].y, ElementType.ENEMY)
            enemy_label = self.enemy_dictionary[self.enemies_new_position[i]]
            self.setGameBoardLabelGeometry(enemy_label, self.enemies_new_position[i].x, self.enemies_new_position[i].y)


            transform = QTransform()
            pix = self.enemy_dictionary[self.enemies_new_position[i]].pixmap()
            transform.rotate(Helper.rotationFunction(self.enemies[i].direction, self.enemies_new_position[i].direction))
            self.enemy_dictionary[self.enemies_new_position[i]].setPixmap(pix.transformed(transform))

            self.enemies[i].x = self.enemies_new_position[i].x
            self.enemies[i].y = self.enemies_new_position[i].y
            self.enemies[i].direction = self.enemies_new_position[i].direction

        self.mutex.unlock()

    def bulletFired(self, bullet, transform):
        #self.mutex.lock()

        #self.bullets_new_posiotion.append(bullet)
        #bullet_old = Bullet(bullet.type, bullet.x, bullet.y, bullet.orientation, bullet.bullet_owner)
        #self.bullets.append(bullet_old)
        
        self.bullet_dictionary[bullet] = QLabel(self)
        bullet_label = self.bullet_dictionary[bullet]

        bullet.pm_flying = bullet.pm_flying.scaled(self.getSquareWidth(), self.getSquareHeight())
        bullet_label.setPixmap(bullet.pm_flying.transformed(transform))

        self.setGameBoardLabelGeometry(bullet_label, bullet.x, bullet.y)
        bullet_label.orientation = bullet.orientation
        bullet_label.show()
        
        #self.mutex.unlock()

    def bulletMoved(self, bullets_with_new_posiotion, bullets_to_be_removed, enemies_to_be_removed):
        for bullet in bullets_with_new_posiotion:
            if bullet in self.bullet_dictionary:
                bullet_label = self.bullet_dictionary[bullet]
                self.setGameBoardLabelGeometry(bullet_label, bullet.x, bullet.y)

                #if pocetna slicica:
                    #pix = self.bullet_dictionary[bullet].pixmap()
                    #self.bullet_dictionary[bullet].setPixmap(pix)

        for bullet in bullets_to_be_removed:
            bullet.bullet_owner.active_bullet = None
            if bullet in self.bullet_dictionary:
                self.bullet_dictionary[bullet].hide()
                del self.bullet_dictionary[bullet]

        for enemy in enemies_to_be_removed:
            if enemy in self.enemy_dictionary:
                self.enemy_dictionary[enemy].hide()
                del self.enemy_dictionary[enemy]

            self.num_of_all_enemies -= 1
            if self.num_of_all_enemies > 0:
                self.addEnemy()
            # else:
            # prelazak u sledeci level
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