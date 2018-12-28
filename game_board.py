from PyQt5.QtWidgets import QFrame, QLabel
from PyQt5.QtGui import QPainter, QColor, QTransform, QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QMutex
from move_thread import MoveThread
from enum import Enum
from tank import Tank
import os


class GameBoard(QFrame):
    BoardWidth = 32
    BoardHeight = 18
    mutex = QMutex()

    # tile width/height in px
    TILE_SIZE = 16

    def __init__(self, parent):
        super().__init__(parent)
        self.commands1 = []
        self.commands2 = []
        self.initGameBoard()

    def initGameBoard(self):
        self.player1 = Tank(1)
        self.player1Label = QLabel(self)
        self.player2 = Tank(2)
        self.player2Label = QLabel(self)

        #self.player1.pixmap1 = self.player1.pixmap.scaled(self.squareWidth(), self.squareHeight())
        self.enemies = []
        self.bullets = []
        self.board = []
        self.clearBoard()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWalls()
        self.moveThread1 = MoveThread(self.commands1, self.player1, self)
        self.moveThread2 = MoveThread(self.commands2, self.player2, self)
        self.moveThread1.threadSignal.connect(self.moved)
        self.moveThread2.threadSignal.connect(self.moved)

    def showEvent(self, *args, **kwargs):
        rect = self.contentsRect()
        boardTop = rect.bottom() - GameBoard.BoardHeight * self.squareHeight()
        pixmap1 = self.player1.pixmap.scaled(self.squareWidth(), self.squareHeight())
        pixmap2 = self.player2.pixmap.scaled(self.squareWidth(), self.squareHeight())

        self.player1Label.setPixmap(pixmap1)
        self.player1Label.setGeometry(rect.left() + self.player1.x * self.squareWidth(),
                                      boardTop + self.player1.y * self.squareHeight(),
                                      self.squareWidth(), self.squareHeight())
        self.player1Label.orientation = 0
        self.setShapeAt(self.player1.x, self.player1.y, Element.PLAYER1)

        self.player2Label.setPixmap(pixmap2)
        self.player2Label.setGeometry(rect.left() + self.player2.x * self.squareWidth(),
                                      boardTop + self.player2.y * self.squareHeight(),
                                      self.squareWidth(), self.squareHeight())
        self.player2Label.orientation = 0
        self.setShapeAt(self.player2.x, self.player2.y, Element.PLAYER2)
        self.moveThread1.start()
        self.moveThread2.start()


    def squareWidth(self):
        return self.contentsRect().width() // GameBoard.BoardWidth

    def squareHeight(self):
        return self.contentsRect().height() // GameBoard.BoardHeight

    def shapeAt(self, x, y):
        return self.board[(y * GameBoard.BoardWidth) + x]

    def setShapeAt(self, x, y, shape):
        self.board[(y * GameBoard.BoardWidth) + x] = shape

    def setWalls(self):
        self.loadLevel(1)

    def clearBoard(self):
        for i in range(GameBoard.BoardHeight):
            for j in range(GameBoard.BoardWidth):
                self.board.append(Element.NONE)

    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        rect = self.contentsRect()
        boardTop = rect.bottom() - GameBoard.BoardHeight * self.squareHeight()
        for i in range(GameBoard.BoardHeight):
            for j in range(GameBoard.BoardWidth):
                shape = self.shapeAt(j, i)
                if shape == Element.WALL:
                    self.drawSquare(painter, rect.left() + j * self.squareWidth(), boardTop + i * self.squareHeight(),
                                    0xf90000)
                elif shape == Element.BASE:
                    self.drawSquare(painter, rect.left() + j * self.squareWidth(), boardTop + i * self.squareHeight(),
                                    0xeaa615)

    def drawSquare(self, painter, x, y, color):
        colorToDraw = QColor(color)
        painter.fillRect(x + 1, y + 1, self.squareWidth(), self.squareHeight(), colorToDraw)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down or event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
            self.commands1.append(event.key())
        elif event.key() == Qt.Key_W or event.key() == Qt.Key_S or event.key() == Qt.Key_A or event.key() == Qt.Key_D:
            self.commands2.append(event.key())

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down or event.key() == Qt.Key_Left or event.key() == Qt.Key_Right:
            self.commands1.remove(event.key())
        elif event.key() == Qt.Key_W or event.key() == Qt.Key_S or event.key() == Qt.Key_A or event.key() == Qt.Key_D:
            self.commands2.remove(event.key())

    def moved(self, x, y, tank, orientation):
        self.mutex.lock()
        transform = QTransform()

        if tank.player == 1:
            self.setShapeAt(self.player1.x, self.player1.y, Element.NONE)
            self.player1.x = x
            self.player1.y = y
            pix = self.player1Label.pixmap()
            transform.rotate(GameBoard.rotation_function(self.player1.orientation, orientation))
            self.player1Label.setPixmap(pix.transformed(transform))
            self.player1.orientation = orientation

            rect = self.contentsRect()
            boardTop = rect.bottom() - GameBoard.BoardHeight * self.squareHeight()
            self.player1Label.setGeometry(rect.left() + self.player1.x * self.squareWidth(), boardTop + self.player1.y
                                          * self.squareHeight(), self.squareWidth(), self.squareHeight())
            self.setShapeAt(self.player1.x, self.player1.y, Element.PLAYER1)
        elif tank.player == 2:
            self.setShapeAt(self.player2.x, self.player2.y, Element.NONE)
            self.player2.x = x
            self.player2.y = y
            pix = self.player2Label.pixmap()
            transform.rotate(GameBoard.rotation_function(self.player2.orientation, orientation))
            self.player2Label.setPixmap(pix.transformed(transform))
            self.player2.orientation = orientation
            rect = self.contentsRect()
            boardTop = rect.bottom() - GameBoard.BoardHeight * self.squareHeight()
            self.player2Label.setGeometry(rect.left() + self.player2.x * self.squareWidth(), boardTop + self.player2.y
                                          * self.squareHeight(), self.squareWidth(), self.squareHeight())
            self.setShapeAt(self.player2.x, self.player2.y, Element.PLAYER2)

        self.mutex.unlock()

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
                        self.setShapeAt(x, y, Element.WALL)
                       # print(f"{x} {y}")
                    elif ch == "$":
                        self.setShapeAt(x, y, Element.BASE)
                    elif ch == "1":
                        self.player1.setCoordinates(x, y)
                    elif ch == "2":
                        self.player2.setCoordinates(x, y)
                    x += 1
                x = 0
                y += 1
            return True

    @staticmethod
    def rotation_function(current_position, next_position):
        diff = current_position - next_position
        rotation_angle = 0 - diff * 90
        return rotation_angle

    #AKO NEMA KOLIZIJE - TENK SE POMERA I PROVERAVA "Da li je naleto na metak"



class Element(Enum):
    NONE = 0,
    PLAYER1 = 1,
    PLAYER2 = 2,
    ENEMY = 3,
    WALL = 4,
    BULLET = 5,
    BASE = 6


class WallType(Enum):
    TILE_EMPTY = 0,
    TILE_BRICK = 1,
    TILE_STEEL = 2,
    TILE_WATER = 3,
    TILE_GRASS = 4,
    TILE_FROZE = 5,

