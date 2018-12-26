from PyQt5.QtWidgets import QFrame
from PyQt5.QtGui import QPainter, QColor
from enum import Enum


class GameBoard(QFrame):
    BoardWidth = 32
    BoardHeight = 18

    def __init__(self, parent):
        super().__init__(parent)
        self.initGameBoard()

    def initGameBoard(self):
        self.player1 = 1 #ovo ce biti instanca tenka
        self.enemies = []
        self.bullets = []
        self.board = []
        self.clearBoard()
        self.setWalls()

    def squareWidth(self):
        return self.contentsRect().width() // GameBoard.BoardWidth

    def squareHeight(self):
        return self.contentsRect().height() // GameBoard.BoardHeight

    def shapeAt(self, x, y):
        return self.board[(y * GameBoard.BoardWidth) + x]

    def setShapeAt(self, x, y, shape):
        self.board[(y * GameBoard.BoardWidth) + x] = shape

    def setWalls(self):
        for i in range(6):
            self.setShapeAt(0, 0 + i, Element.WALL)
        self.update()

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
                if shape == Element.NONE:
                    self.drawSquare(painter, rect.left() + j * self.squareWidth(), boardTop + i * self.squareHeight(),
                                    0x000000)
                elif shape == Element.WALL:
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





