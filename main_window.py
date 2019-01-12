from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QAction, QMenu, QSplitter, QHBoxLayout, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt
from game_board import GameBoard
from stat_frame import StatFrame
import sys
from enums import GameMode

class MainWindowWidget(QWidget):

    def __init__(self, parent, mode):
        super(MainWindowWidget, self).__init__(parent)
        self.layout = QHBoxLayout(self)

        self.game_board_frame = GameBoard(self, mode)
        self.mode = mode
        self.game_board_frame.setMinimumSize(1000, 562.5)
        self.game_board_frame.setMaximumSize(1000, 562.5)
        self.game_board_frame.setObjectName("game_board_frame")
        self.layout.addWidget(self.game_board_frame)

        self.game_board_frame.restart_game_signal.connect(self.restartGame)

        self.stat_frame = StatFrame(self, self.game_board_frame)
        self.stat_frame.setMaximumHeight(562.5)
        self.stat_frame.setObjectName("stat_frame")
        self.layout.addWidget(self.stat_frame)

        self.game_board_frame.setFocus()

        self.setLayout(self.layout)

    def restartGame(self):
        self.game_board_frame.hide()
        self.stat_frame.hide()

        self.game_board_frame = GameBoard(self, self.mode)
        self.game_board_frame.setMinimumSize(1000, 562.5)
        self.game_board_frame.setMaximumSize(1000, 562.5)
        self.game_board_frame.setObjectName("game_board_frame")
        self.layout.addWidget(self.game_board_frame)

        self.game_board_frame.restart_game_signal.connect(self.restartGame)

        self.stat_frame = StatFrame(self, self.game_board_frame)
        self.stat_frame.setMaximumHeight(562.5)
        self.stat_frame.setObjectName("stat_frame")
        self.layout.addWidget(self.stat_frame)

        self.game_board_frame.setFocus()

        self.setLayout(self.layout)
    
    def onResize(self):
        print()

class BattleCity(QMainWindow):

    def __init__(self):
        super().__init__()

        self.initUI()

    def initUI(self):
        #self.setMaximumSize(1920, 1080)
        self.setMinimumSize(1500, 700)

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        menu_bar = self.menuBar()
        settings_menu = menu_bar.addMenu("&StartGame")

        mode_menu = QMenu("Mode", self)

        single_act = QAction("Single paleyer", self)
        single_act.triggered.connect(self.toggleSingle)
        mode_menu.addAction(single_act)

        multi_act = QAction("Multiplayer mode", self)
        multi_act.triggered.connect(self.toggleMulti)
        mode_menu.addAction(multi_act)

        online_host_act = QAction("Online multiplayer - HOST", self)
        online_host_act.triggered.connect(self.toggleOnlineHost)
        mode_menu.addAction(online_host_act)

        online_client_act = QAction("Online multiplayer - CLIENT", self)
        online_client_act.triggered.connect(self.toggleOnlineClient)
        mode_menu.addAction(online_client_act)

        settings_menu.addMenu(mode_menu)
        self.show()

    def toggleSingle(self, mode):
        self.status_bar.showMessage("MODE: SINGLE PLAYER")
        self.startNewGame(GameMode.SINGLEPLAYER)

    def toggleMulti(self, mode):
        self.status_bar.showMessage("MODE: MULTIPLAYER")
        self.startNewGame(GameMode.MULTIPLAYER_OFFLINE)

    def toggleOnlineHost(self, mode):
        self.status_bar.showMessage("MODE: ONLINE_HOST")
        self.startNewGame(GameMode.MULTIPLAYER_ONLINE_HOST)

    def toggleOnlineClient(self, mode):
        self.status_bar.showMessage("MODE: ONLINE_CLIENT")
        self.startNewGame(GameMode.MULTIPLAYER_ONLINE_CLIENT)

    def startNewGame(self, mode):
        self.form_widget = MainWindowWidget(self, mode)
        self.setCentralWidget(self.form_widget)
        self.setStyleSheet("""
            QFrame#game_board_frame{
                background-color: rgb(0, 0, 0);
                }
            QFrame#stat_frame{
                background-color: rgb(255, 0, 0);
                }
        """)
        self.show()

    def onResize(self):
        print()


        
if __name__ == "__main__":
    app = QApplication([])

    battleCity = BattleCity()
    sys.exit(app.exec_())