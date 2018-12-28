from PyQt5.QtWidgets import QFrame, QLabel
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import pyqtSignal, Qt
from move_thread import MoveThread
from enum import Enum
from Tank import Tank
import os


class GameBoard(QFrame):
    BoardWidth = 32
    BoardHeight = 18
    signal = pyqtSignal(int, int, list, object)


    # tile width/height in px
    TILE_SIZE = 16

    def __init__(self, parent):
        super().__init__(parent)
        self.initGameBoard()

    def initGameBoard(self):
        self.player1 = Tank()
        self.player1Label = QLabel(self)
        self.player2 = Tank()
        self.player2Label = QLabel(self)

        #self.player1.pixmap1 = self.player1.pixmap.scaled(self.squareWidth(), self.squareHeight())
        self.enemies = []
        self.bullets = []
        self.board = []
        self.clearBoard()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setWalls()
        self.moveThread = MoveThread(self)
        self.signal.connect(self.moveThread.move)
        self.moveThread.threadSignal.connect(self.moved)

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
        self.setShapeAt(self.player1.x, GameBoard.BoardHeight - self.player1.y - 1, Element.PLAYER1)
        self.moveThread.start()

        self.player2Label.setPixmap(pixmap2)
        self.player2Label.setGeometry(rect.left() + self.player2.x * self.squareWidth(),
                                      boardTop + self.player2.y * self.squareHeight(),
                                      self.squareWidth(), self.squareHeight())
        self.player2Label.orientation = 0
        self.setShapeAt(self.player2.x, GameBoard.BoardHeight - self.player2.y - 1, Element.PLAYER2)

        for i in range(self.BoardHeight):
            for j in range(self.BoardWidth):
                print(f"Board({i}, {j}) - {str(self.board[i * self.BoardWidth + j])}")

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

        """
        for i in range(3):
            self.setShapeAt(0, GameBoard.BoardHeight - i - 1, Element.WALL)
        #self.update()
        """

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
                shape = self.shapeAt(j, GameBoard.BoardHeight - i - 1)
                """if shape == Element.NONE:
                    self.drawSquare(painter, rect.left() + j * self.squareWidth(), boardTop + i * self.squareHeight(),
                                    0x000000)"""
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
        self.signal.emit(self.player1.x, self.player1.y, self.board, event.key())

    def moved(self, x, y):
        self.setShapeAt(self.player1.x, self.player1.y, Element.NONE)
        self.player1.x = x
        self.player1.y = y
        rect = self.contentsRect()
        boardTop = rect.bottom() - GameBoard.BoardHeight * self.squareHeight()
        self.player1Label.setGeometry(rect.left() + self.player1.x * self.squareWidth(), boardTop + self.player1.y
                                      * self.squareHeight(), self.squareWidth(), self.squareHeight())
        self.setShapeAt(self.player1.x, self.player1.y, Element.PLAYER1)

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
                        self.setShapeAt(x, GameBoard.BoardHeight - y - 1, Element.WALL)
                        print(f"{x} {y}")
                    elif ch == "$":
                        self.setShapeAt(x, GameBoard.BoardHeight - y - 1, Element.BASE)
                    elif ch == "1":
                        self.player1.setCoordinates(x, y)
                    elif ch == "2":
                        self.player2.setCoordinates(x, y)
                    x += 1
                x = 0
                y += 1
            return True

    #AKO NEMA KOLIZIJE - TENK SE POMERA I PROVERAVA "Da li je naleto na metak"
    def isCollision(self, new_x, new_y):
        nextPositionShape = self.board[(new_y * GameBoard.BoardWidth) + new_x]
        if (nextPositionShape is Element.NONE) | (nextPositionShape is Element.BULLET):
            return False

        return True


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

