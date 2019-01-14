from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QAction, QMenu, QSplitter, QHBoxLayout, QVBoxLayout, QFrame
import sys
from game_server_frame import GameServerFrame
from communication import Communication
from enums import GameMode
import time


class GameServerWidget(QWidget):
    def __init__(self, parent, mode):
        super(GameServerWidget, self).__init__(parent)
        self.is_started = False
        self.port = 50006
        self.mode = mode

        if self.mode == 1: #multiplayer
            self.game_server_frame1 = GameServerFrame(self, 50005)
        else:
            self.communication = Communication(GameMode.MULTIPLAYER_ONLINE_HOST, 50005, 2)

            self.game_server_frame1 = GameServerFrame(self, self.port)
            self.port += 1
            self.game_server_frame2 = GameServerFrame(self, self.port)
            self.port += 1
            self.game_server_frame3 = GameServerFrame(self, self.port, True)



class GameServer(QMainWindow):
    def __init__(self):
        super().__init__()


        self.initUI()
        self.show()







    def initUI(self):
        self.menu_bar = self.menuBar()
        self.menu_bar.start_game = self.menu_bar.addMenu("&Start Game")

        self.menu_bar.start_game.multi_act = QAction("Multiplayer mode", self)
        self.menu_bar.start_game.multi_act.triggered.connect(self.toggleMulti)
        self.menu_bar.start_game.addAction(self.menu_bar.start_game.multi_act)

        self.menu_bar.start_game.single_act = QAction("Tournament", self)
        self.menu_bar.start_game.single_act.triggered.connect(self.toggleTournament)
        self.menu_bar.start_game.addAction(self.menu_bar.start_game.single_act)


    def toggleMulti(self, mode):
        self.server_widget = GameServerWidget(self, 1)

    def toggleTournament(self, mode):
        self.server_widget = GameServerWidget(self, 2)


if __name__ == "__main__":
    app = QApplication([])

    gameServer = GameServer()

    sys.exit(app.exec_())
