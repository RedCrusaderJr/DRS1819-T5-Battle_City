from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QAction, QMenu, QSplitter, QHBoxLayout, QVBoxLayout, QFrame
import sys
from game_server_frame import GameServerFrame


class GameServerWidget(QWidget):
    def __init__(self, parent):
        super(GameServerWidget, self).__init__(parent)

        self.game_server_frame = GameServerFrame(self)


class GameServer(QMainWindow):
    def __init__(self):
        super().__init__()

        self.server_widget = GameServerWidget(self)

        self.show()


if __name__ == "__main__":
    app = QApplication([])

    gameServer = GameServer()

    sys.exit(app.exec_())
