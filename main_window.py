from PyQt5.QtWidgets import QMainWindow, QApplication
from game_board import GameBoard
import sys


class BattleCity(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.showFullScreen()
        self.show()
        self.gameBoard = GameBoard(self)
        self.setCentralWidget(self.gameBoard)

if __name__ == "__main__":
    app = QApplication([])
    battleCity = BattleCity()
    sys.exit(app.exec_())