from PyQt5.QtWidgets import QFrame, QLabel
from PyQt5.QtGui import QPainter, QColor, QTransform, QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QMutex
from move_player_thread import MovePlayerThread
from move_enemy_thread import MoveEnemyThread
from tank import Tank
from enemy_tank import EnemyTank
import os
from enums import PlayerType, ElementType, WallType, Orientation
from helper import Helper

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
        self.player_1 = Tank(PlayerType.PLAYER_1)
        self.player_1_label = QLabel(self)
        self.player_2 = Tank(PlayerType.PLAYER_2)
        self.player_2_label = QLabel(self)

        #self.player1.pixmap1 = self.player1.pixmap.scaled(self.squareWidth(), self.squareHeight())
        self.enemies = []
        self.enemies.append(EnemyTank())
        self.enemies_new_position = []
        self.enemies_new_position.append(EnemyTank())
        self.enemy_dictionary = {}
        self.enemy_dictionary[self.enemies_new_position[0]] = QLabel(self)

        self.bullets = []
        self.board = []

        self.clearBoard()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWalls()

        self.move_player_1_thread = MovePlayerThread(self.commands_1, self.player_1, self)
        self.move_player_1_thread.thread_signal.connect(self.playerMoved)

        self.move_player_2_thread = MovePlayerThread(self.commands_2, self.player_2, self)
        self.move_player_2_thread.thread_signal.connect(self.playerMoved)

        self.move_enemy_thread = MoveEnemyThread(self)
        self.move_enemy_thread.thread_signal.connect(self.enemyMoved)

    #region EVENTS
    def showEvent(self, *args, **kwargs):

        pixmap1 = self.player_1.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
        pixmap2 = self.player_2.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
        pixmap3 = self.enemies[0].pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())

        self.player_1_label.setPixmap(pixmap1)
        self.setGameBoardLabelGeometry(self.player_1_label, self.player_1.x, self.player_1.y)
        self.player_1_label.orientation = Orientation.UP
        self.setShapeAt(self.player_1.x, self.player_1.y, ElementType.PLAYER1)

        self.player_2_label.setPixmap(pixmap2)
        self.setGameBoardLabelGeometry(self.player_2_label, self.player_2.x, self.player_2.y)
        self.player_2_label.orientation = Orientation.UP
        self.setShapeAt(self.player_2.x, self.player_2.y, ElementType.PLAYER2)

        enemy_label = self.enemy_dictionary[self.enemies_new_position[0]]
        enemy_label.setPixmap(pixmap3)
        self.setGameBoardLabelGeometry(enemy_label, self.enemies_new_position[0].x, self.enemies_new_position[0].y)
        self.setShapeAt(self.enemies_new_position[0].x, self.enemies_new_position[0].y, ElementType.ENEMY)

        self.move_player_1_thread.start()
        self.move_player_2_thread.start()
        self.move_enemy_thread.start()

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
                                    0xf90000)
                elif shape_type == ElementType.BASE:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    0xeaa615)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down or event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
            self.commands_1.append(event.key())
        elif event.key() == Qt.Key_W or event.key() == Qt.Key_S or event.key() == Qt.Key_A or event.key() == Qt.Key_D:
            self.commands_2.append(event.key())

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down or event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
            self.commands_1.remove(event.key())
        elif event.key() == Qt.Key_W or event.key() == Qt.Key_S or event.key() == Qt.Key_A or event.key() == Qt.Key_D:
            self.commands_2.remove(event.key())
    #endregion

    #region EVIDENTION_METHODS
    def setShapeAt(self, x, y, shape_type):
        self.board[(y * GameBoard.BoardWidth) + x] = shape_type

    def setWalls(self):
        self.loadLevel(1)

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
                elif ch == "2":
                    self.player_2.setCoordinates(x, y)
                x += 1
            x = 0
            y += 1
        return True

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
    #endregion

    #region CALLBACKS
    def playerMoved(self, x, y, tank, orientation):
        self.mutex.lock()
        transform = QTransform()

        if tank.player_type == PlayerType.PLAYER_1:
            self.setShapeAt(self.player_1.x, self.player_1.y, ElementType.NONE)
            self.player_1.x = x
            self.player_1.y = y

            pix = self.player_1_label.pixmap()
            transform.rotate(Helper.rotationFunction(self.player_1.orientation, orientation))
            self.player_1_label.setPixmap(pix.transformed(transform))
            self.player_1.orientation = orientation

            self.setGameBoardLabelGeometry(self.player_1_label, self.player_1.x, self.player_1.y)
            self.setShapeAt(self.player_1.x, self.player_1.y, ElementType.PLAYER1)

        elif tank.player_type == PlayerType.PLAYER_2:
            self.setShapeAt(self.player_2.x, self.player_2.y, ElementType.NONE)
            self.player_2.x = x
            self.player_2.y = y

            pix = self.player_2_label.pixmap()
            transform.rotate(Helper.rotationFunction(self.player_2.orientation, orientation))
            self.player_2_label.setPixmap(pix.transformed(transform))
            self.player_2.orientation = orientation

            self.setGameBoardLabelGeometry(self.player_2_label, self.player_2.x, self.player_2.y)
            self.setShapeAt(self.player_2.x, self.player_2.y, ElementType.PLAYER2)

        self.mutex.unlock()

    def enemyMoved(self):
        self.mutex.lock()

        transform = QTransform()

        for enemy in self.enemies:
            self.setShapeAt(enemy.x, enemy.y, ElementType.NONE)

        for enemy in self.enemies_new_position:
            self.setShapeAt(enemy.x, enemy.y, ElementType.ENEMY)
            enemy_label = self.enemy_dictionary[enemy]
            self.setGameBoardLabelGeometry(enemy_label, enemy.x, enemy.y)

        for i in range(len(self.enemies)):
            pix = self.enemy_dictionary[self.enemies_new_position[0]].pixmap()
            transform.rotate(Helper.rotationFunction(self.enemies[0].direction, self.enemies_new_position[0].direction))
            self.enemy_dictionary[self.enemies_new_position[0]].setPixmap(pix.transformed(transform))

            self.enemies[i].x = self.enemies_new_position[i].x
            self.enemies[i].y = self.enemies_new_position[i].y
            self.enemies[i].direction = self.enemies_new_position[i].direction

        self.mutex.unlock()
    #endregion

    def drawSquare(self, painter, x, y, color):
        colorToDraw = QColor(color)
        painter.fillRect(x + 1, y + 1, self.getSquareWidth(), self.getSquareHeight(), colorToDraw)

    def setGameBoardLabelGeometry(self, label, x, y):
        rect = self.contentsRect()
        board_top = rect.bottom() - GameBoard.BoardHeight * self.getSquareHeight()
        label.setGeometry(rect.left() + x * self.getSquareWidth(),
                          board_top + y * self.getSquareHeight(),
                          self.getSquareWidth(), self.getSquareHeight())