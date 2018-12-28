from PyQt5.QtWidgets import QMainWindow, QApplication
from game_board import GameBoard
import sys
#from level import Level

class BattleCity(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        self.showFullScreen()
        self.gameBoard = GameBoard(self)
        self.setCentralWidget(self.gameBoard)
        self.setStyleSheet("""
        QFrame{
            background-color: rgb(0, 0, 0);
            }
        """)
        self.show()


if __name__ == "__main__":
    app = QApplication([])

    battleCity = BattleCity()
    sys.exit(app.exec_())

