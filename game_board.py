from PyQt5.QtWidgets import QFrame, QLabel
from PyQt5.QtGui import QPainter, QColor
from enum import Enum
from Tank import Tank



class GameBoard(QFrame):
    BoardWidth = 32
    BoardHeight = 18

    def __init__(self, parent):
        super().__init__(parent)
        self.initGameBoard()

    def initGameBoard(self):
        self.player1 = Tank()
        self.player1Label = QLabel(self)
        #self.player1.pixmap1 = self.player1.pixmap.scaled(self.squareWidth(), self.squareHeight())
        self.enemies = []
        self.bullets = []
        self.board = []
        self.clearBoard()
        self.setWalls()

    def showEvent(self, *args, **kwargs):
        rect = self.contentsRect()
        boardTop = rect.bottom() - GameBoard.BoardHeight * self.squareHeight()
        pixmap1 = self.player1.pixmap.scaled(self.squareWidth(), self.squareHeight())

        self.player1Label.setPixmap(pixmap1)
        self.player1Label.setGeometry(rect.left() + self.player1.x * self.squareWidth(), boardTop + self.player1.y
                                      * self.squareHeight(), self.squareWidth(), self.squareHeight())
        self.player1Label.orientation = 0
        self.setShapeAt(self.player1.x, GameBoard.BoardHeight - self.player1.y - 1, Element.PLAYER1)

    def squareWidth(self):
        return self.contentsRect().width() // GameBoard.BoardWidth

    def squareHeight(self):
        return self.contentsRect().height() // GameBoard.BoardHeight

    def shapeAt(self, x, y):
        return self.board[(y * GameBoard.BoardWidth) + x]

    def setShapeAt(self, x, y, shape):
        self.board[(y * GameBoard.BoardWidth) + x] = shape

    def setWalls(self):
        for i in range(3):
            self.setShapeAt(0, GameBoard.BoardHeight - i - 1, Element.WALL)
        #self.update()

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

    def drawSquare(self, painter, x, y, color):
        colorToDraw = QColor(color)
        painter.fillRect(x + 1, y + 1, self.squareWidth(), self.squareHeight(), colorToDraw)


class Element(Enum):
    NONE = 0,
    PLAYER1 = 1,
    PLAYER2 = 2,
    ENEMY = 3,
    WALL = 4,
    BULLET = 5





