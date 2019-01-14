from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QAction, QMenu, QSplitter, QHBoxLayout, QVBoxLayout, QFrame
import sys
from game_server_frame import GameServerFrame
from communication import Communication
from enums import GameMode


class GameServerWidget(QWidget):
    def __init__(self, parent):
        super(GameServerWidget, self).__init__(parent)
        self.is_started = False
        self.port = 50006

        self.communication = Communication(GameMode.MULTIPLAYER_ONLINE_HOST, 50005)

        self.game_server_frame1 = GameServerFrame(self, self.port)
        self.port += 1
        self.game_server_frame2 = GameServerFrame(self, self.port)
        self.port += 1
        self.game_server_frame3 = GameServerFrame(self, self.port)


class GameServer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.server_widget = GameServerWidget(self)

        self.show()


if __name__ == "__main__":
    app = QApplication([])

    gameServer = GameServer()

    sys.exit(app.exec_())
