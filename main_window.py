from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QAction, QMenu, QSplitter, QHBoxLayout, QVBoxLayout, QFrame
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QEvent
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
        self.game_board_frame.setMinimumSize(1200, 675)
        self.game_board_frame.setMaximumSize(1200, 675)
        self.game_board_frame.setObjectName("game_board_frame")
        self.layout.addWidget(self.game_board_frame)

        self.game_board_frame.restart_game_signal.connect(self.restartGame)

        self.stat_frame = StatFrame(self, self.game_board_frame)
        self.stat_frame.setMinimumSize(300, 675)
        self.stat_frame.setMaximumSize(300, 675)
        self.stat_frame.setObjectName("stat_frame")
        self.layout.addWidget(self.stat_frame)

        self.game_board_frame.setFocus()

        self.setLayout(self.layout)

    def restartGame(self):
        self.game_board_frame.hide()
        self.stat_frame.hide()

        self.game_board_frame = GameBoard(self, self.mode)
        self.game_board_frame.setMinimumSize(1200, 675)
        self.game_board_frame.setMaximumSize(1200, 675)
        self.game_board_frame.setObjectName("game_board_frame")
        self.layout.addWidget(self.game_board_frame)

        self.game_board_frame.restart_game_signal.connect(self.restartGame)

        self.stat_frame = StatFrame(self, self.game_board_frame)
        self.stat_frame.setMinimumSize(300, 675)
        self.stat_frame.setMaximumSize(300, 675)
        self.stat_frame.setObjectName("stat_frame")
        self.layout.addWidget(self.stat_frame)

        self.game_board_frame.setFocus()

        self.setLayout(self.layout)


class BattleCity(QMainWindow):

    def __init__(self):
        super().__init__()

        #flags = Qt.WindowFlags() & ~Qt.WindowMinimizeButtonHint
        #self.setWindowFlags(flags)
        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowIcon(QIcon('./images/enemy.png'))


        self.initUI()
        self.classicPalette()

    def initUI(self):
        self.setObjectName("main_window")

        self.resize(1600,900)
        self.setFixedSize(self.size());

        self.status_bar = self.statusBar()
        self.status_bar.showMessage("Ready")

        menu_bar = self.menuBar()
        settings_menu = menu_bar.addMenu("&StartGame")

        #region MODES
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
        #endregion

        #region THEMES
        palette_menu = QMenu("Theme", self)

        classic_palette_act = QAction("Classic palette", self)
        classic_palette_act.triggered.connect(self.classicPalette)
        palette_menu.addAction(classic_palette_act)

        cold_whisper_palette_act = QAction("Cold whisper palette", self)
        cold_whisper_palette_act.triggered.connect(self.coldWhisperPalette)
        palette_menu.addAction(cold_whisper_palette_act)

        raspberry_bush_palette_act = QAction("Raspberry bush palette", self)
        raspberry_bush_palette_act.triggered.connect(self.raspberryBushPalette)
        palette_menu.addAction(raspberry_bush_palette_act)

        #endregion

        settings_menu.addMenu(mode_menu)
        settings_menu.addMenu(palette_menu)

        self.show()

    #region TOGGLE_MODE
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
        self.show()

    #endregion

    #region TOGGLE_PALETTES
    def classicPalette(self):
        self.setStyleSheet("""
            QMainWindow#main_window{
                background-color: #ffffff;
            }
            QFrame#stat_frame{
                background-color: #000000;
            }
            QFrame#game_board_frame{
                background-color: #000000;
            }
            QLabel {
                color: 	#ffffff;
            }
        """)

    def coldWhisperPalette(self):
        self.setStyleSheet("""
            QMainWindow#main_window{
                background-color: #51766c;
            }
            QFrame#stat_frame{
                background-color: #14291f;
            }
            QFrame#game_board_frame{
                background-color: #06130d;
            }
            QLabel {
                color: 	#869267;
            }
        """)

    def raspberryBushPalette(self):
        self.setStyleSheet("""
            QMainWindow#main_window{
                background-color: #810c41;
            }
            QFrame#stat_frame{
                background-color: #330120;
            }
            QFrame#game_board_frame{
                background-color: #1a001a;
            }
            QLabel {
                color: #bf004d;
            }
        """)
    #endregion

if __name__ == "__main__":
    app = QApplication([])

    battleCity = BattleCity()
    sys.exit(app.exec_())