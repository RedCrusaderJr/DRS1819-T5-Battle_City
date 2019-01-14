from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QAction, QMenu, QSplitter, QHBoxLayout, QVBoxLayout, QFrame, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from game_board import GameBoard
from stat_frame import StatFrame
import sys
from enums import GameMode
from main_window_layout import MainWindowLayout
from pygame import mixer


class BattleCity(QMainWindow):
    restart_game_signal = pyqtSignal(int, object, object, int)

    def __init__(self):
        super(BattleCity, self).__init__()

        self.setWindowFlags(Qt.WindowCloseButtonHint)
        self.setWindowIcon(QIcon('./images/tank_icon.png'))
        self.setWindowTitle("Battle City")

        mixer.init()
        self.channel_0 = mixer.Channel(0)
        self.channel_1 = mixer.Channel(1)
        self.channel_2 = mixer.Channel(2)
        self.channel_3 = mixer.Channel(3)

        self.gameplay_soundtrack = mixer.Sound("./sounds/gameplay_sountrack.ogg")
        self.losing_sound = mixer.Sound("./sounds/losing_sound.ogg")
        self.bullet_fired_sound = mixer.Sound("./sounds/fire_sound.wav")
        self.bullet_impact_sound = mixer.Sound("./sounds/impact_sound.wav")

        self.main_window_width = 1600
        self.main_window_height = 900
        self.board_width = 1200
        self.board_height = 675
        self.stat_width = 300
        self.stat_height = 675

        self.stat_font_size = 2
        self.main_window_layout = None
        self.mode = None

        self.initUI()
        self.classicPalette()

    def initUI(self):
        self.setObjectName("main_window")

        self.resize(self.main_window_width, self.main_window_height)
        self.setFixedSize(self.size())

        self.status_bar = self.statusBar()
        self.status_bar.setObjectName("status_bar")
        self.status_bar.showMessage("Ready")

        self.menu_bar = self.menuBar()
        self.menu_bar.start_game = self.menu_bar.addMenu("&Start Game")
        self.menu_bar.theme_menu = self.menu_bar.addMenu("&Theme")
        self.menu_bar.window_size_menu = self.menu_bar.addMenu("&Window Size")

        #region START GAME
        self.menu_bar.start_game.single_act = QAction("Single player", self)
        self.menu_bar.start_game.single_act.triggered.connect(self.toggleSingle)
        self.menu_bar.start_game.addAction(self.menu_bar.start_game.single_act)

        self.menu_bar.start_game.multi_act = QAction("Multiplayer mode", self)
        self.menu_bar.start_game.multi_act.triggered.connect(self.toggleMulti)
        self.menu_bar.start_game.addAction(self.menu_bar.start_game.multi_act)

        self.menu_bar.start_game.online_client_act = QAction("Online multiplayer - CLIENT", self)
        self.menu_bar.start_game.online_client_act.triggered.connect(self.toggleOnlineClient)
        self.menu_bar.start_game.addAction(self.menu_bar.start_game.online_client_act)
        #endregion

        #region THEMES
        self.menu_bar.theme_menu.classic_palette_act = QAction("Classic palette", self)
        self.menu_bar.theme_menu.classic_palette_act.triggered.connect(self.classicPalette)
        self.menu_bar.theme_menu.addAction(self.menu_bar.theme_menu.classic_palette_act)

        self.menu_bar.theme_menu.cold_whisper_palette_act = QAction("Cold whisper palette", self)
        self.menu_bar.theme_menu.cold_whisper_palette_act.triggered.connect(self.coldWhisperPalette)
        self.menu_bar.theme_menu.addAction(self.menu_bar.theme_menu.cold_whisper_palette_act)

        self.menu_bar.theme_menu.raspberry_bush_palette_act = QAction("Raspberry bush palette", self)
        self.menu_bar.theme_menu.raspberry_bush_palette_act.triggered.connect(self.raspberryBushPalette)
        self.menu_bar.theme_menu.addAction(self.menu_bar.theme_menu.raspberry_bush_palette_act)
        #endregion

        #region WINDOW_SIZE
        self.menu_bar.window_size_menu.small_act = QAction("Small", self)
        self.menu_bar.window_size_menu.small_act.triggered.connect(self.smallWindow)
        self.menu_bar.window_size_menu.addAction(self.menu_bar.window_size_menu.small_act)

        self.menu_bar.window_size_menu.medium_act = QAction("Medium", self)
        self.menu_bar.window_size_menu.medium_act.triggered.connect(self.mediumWindow)
        self.menu_bar.window_size_menu.addAction(self.menu_bar.window_size_menu.medium_act)

        self.menu_bar.window_size_menu.large_act = QAction("Large", self)
        self.menu_bar.window_size_menu.large_act.triggered.connect(self.largeWindow)
        self.menu_bar.window_size_menu.addAction(self.menu_bar.window_size_menu.large_act)
        #endregion

        self.menu_bar.restart_game_act = QAction("Restart Game", self)
        self.menu_bar.restart_game_act.triggered.connect(self.toggleRestartGame)
        self.menu_bar.addAction(self.menu_bar.restart_game_act)
        self.menu_bar.restart_game_act.setEnabled(False)

        self.menu_bar.end_game_act = QAction("End Game", self)
        self.menu_bar.end_game_act.triggered.connect(self.toggleEndGame)
        self.menu_bar.addAction(self.menu_bar.end_game_act)
        self.menu_bar.end_game_act.setEnabled(False)

        self.show()

    #region TOGGLE_GAME
    def toggleSingle(self, mode):
        self.status_bar.showMessage("MODE: SINGLE PLAYER")
        self.startNewGame(GameMode.SINGLEPLAYER)

    def toggleMulti(self, mode):
        self.status_bar.showMessage("MODE: MULTIPLAYER")
        self.startNewGame(GameMode.MULTIPLAYER_OFFLINE)

    def toggleOnlineClient(self, mode):
        self.status_bar.showMessage("MODE: ONLINE_CLIENT")
        self.startNewGame(GameMode.MULTIPLAYER_ONLINE_CLIENT)

    def toggleEndGame(self, mode):
        print("toggleEndGame")
        self.endGame()

    def toggleRestartGame(self, mode):
        print("toggleRestartGame")
        self.restartGame()
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
            QLabel[Size1=true] {
                color: 	#ffffff;
                font: 6pt;
            }
            QLabel[Size2=true] {
                color: 	#ffffff;
                font: 18pt;
            }
            QLabel[Size3=true] {
                color: 	#ffffff;
                font: 24pt;
            }
            #status_bar {
                background-color: 	#ffffff;
            }
        """)
        self.setStyle(self.style())
        if self.main_window_layout is not None:
            self.main_window_layout.stat_frame.fontSizeChange()

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
            QLabel[Size1=true] {
                color: 	#869267;
                font: 6pt;
            }
            QLabel[Size2=true] {
                color: 	#869267;
                font: 18pt;
            }
            QLabel[Size3=true] {
                color: 	#869267;
                font: 24pt;
            }
            #status_bar {
                background-color: 	#ffffff;
            }
        """)
        self.setStyle(self.style())
        if self.main_window_layout is not None:
            self.main_window_layout.stat_frame.fontSizeChange()

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
            QLabel[Size1=true] {
                color: #bf004d;
                font: 6pt;
            }
            QLabel[Size2=true] {
                color: #bf004d;
                font: 18pt;
            }
            QLabel[Size3=true] {
                color: #bf004d;
                font: 24pt;
            }
            #status_bar {
                background-color: 	#ffffff;
            }
        """)
        self.setStyle(self.style())
        if self.main_window_layout is not None:
            self.main_window_layout.stat_frame.fontSizeChange()
    #endregion

    #region TOGGLE_WINDOW_SIZE
    def smallWindow(self):
        self.main_window_width = 640
        self.main_window_height = 360
        self.board_width = 480
        self.board_height = 270
        self.stat_width = 100
        self.stat_height = 270

        self.setFixedSize(self.main_window_width, self.main_window_height);
        self.resize(self.main_window_width, self.main_window_height)
        self.setCentralWidget(self.main_window_layout)

        self.stat_font_size = 1
        if self.main_window_layout is not None:
            if self.main_window_layout.stat_frame is not None:
                self.main_window_layout.stat_frame.font_size = self.stat_font_size
                self.main_window_layout.stat_frame.fontSizeChange()

    def mediumWindow(self):
        self.main_window_width = 1600
        self.main_window_height = 900
        self.board_width = 1200
        self.board_height = 675
        self.stat_width = 300
        self.stat_height = 675

        self.setFixedSize(self.main_window_width, self.main_window_height);
        self.resize(self.main_window_width, self.main_window_height)
        self.setCentralWidget(self.main_window_layout)

        self.stat_font_size = 2
        if self.main_window_layout is not None:
            if self.main_window_layout.stat_frame is not None:
                self.main_window_layout.stat_frame.font_size = self.stat_font_size
                self.main_window_layout.stat_frame.fontSizeChange()

    def largeWindow(self):
        self.main_window_width = 1760
        self.main_window_height = 990
        self.board_width = 1328
        self.board_height = 747
        self.stat_width = 340
        self.stat_height = 747

        self.setFixedSize(self.main_window_width, self.main_window_height);
        self.resize(self.main_window_width, self.main_window_height)
        self.setCentralWidget(self.main_window_layout)

        self.stat_font_size = 3
        if self.main_window_layout is not None:
            if self.main_window_layout.stat_frame is not None:
                self.main_window_layout.stat_frame.font_size = self.stat_font_size
                self.main_window_layout.stat_frame.fontSizeChange()
    #endregion

    def startNewGame(self, mode=None):
        if mode is None:
            mode = 2
        self.mode = mode

        if self.main_window_layout is None:
            self.main_window_layout = MainWindowLayout(self,
                                                       self.mode,
                                                       (self.board_width, self.board_height),
                                                       (self.stat_width, self.stat_height),
                                                       self.stat_font_size)
        else:
            self.main_window_layout.game_board_frame.hide()
            self.main_window_layout.stat_frame.hide()
            self.restart_game_signal.emit(self.mode,
                                          (self.board_width, self.board_height),
                                          (self.stat_width, self.stat_height),
                                          self.stat_font_size)

        self.main_window_layout.game_board_frame.fire_sound_signal.connect(self.bulletFiredSound)
        self.main_window_layout.game_board_frame.impact_sound_signal.connect(self.bulletImpactSound)

        self.setCentralWidget(self.main_window_layout)

        self.menu_bar.start_game.setEnabled(False)
        self.menu_bar.theme_menu.setEnabled(False)
        self.menu_bar.window_size_menu.setEnabled(False)

        if self.mode == GameMode.MULTIPLAYER_ONLINE_CLIENT:
            self.menu_bar.restart_game_act.setEnabled(False)
            self.menu_bar.end_game_act.setEnabled(False)
        else:
            self.menu_bar.restart_game_act.setEnabled(True)
            self.menu_bar.end_game_act.setEnabled(True)

        self.show()

        self.channel_0.play(self.gameplay_soundtrack, loops=-1)

    def gameOver(self):
        self.menu_bar.start_game.setEnabled(True)
        self.menu_bar.theme_menu.setEnabled(True)
        self.menu_bar.window_size_menu.setEnabled(True)
        self.menu_bar.end_game_act.setEnabled(False)

        self.channel_0.stop()
        self.channel_1.play(self.losing_sound)

    def restartGame(self):
        print("restartGame")

        if self.main_window_layout is not None:
            self.main_window_layout.cancel_threads_signal.emit()

            self.main_window_layout.game_board_frame.hide()
            self.main_window_layout.stat_frame.hide()

            self.menu_bar.start_game.setEnabled(False)
            self.menu_bar.theme_menu.setEnabled(False)
            self.menu_bar.window_size_menu.setEnabled(False)
            self.menu_bar.restart_game_act.setEnabled(True)
            self.menu_bar.end_game_act.setEnabled(True)

            self.restart_game_signal.emit(self.mode,
                                          (self.board_width, self.board_height),
                                          (self.stat_width, self.stat_height),
                                          self.stat_font_size)
            self.channel_0.play(self.gameplay_soundtrack, loops=-1)
            self.main_window_layout.game_board_frame.fire_sound_signal.connect(self.bulletFiredSound)
            self.main_window_layout.game_board_frame.impact_sound_signal.connect(self.bulletImpactSound)

    def endGame(self):
        print("endGame")
        if self.main_window_layout is not None:
            self.main_window_layout.cancel_threads_signal.emit()

            self.main_window_layout.game_board_frame.hide()
            self.main_window_layout.stat_frame.hide()

            self.menu_bar.start_game.setEnabled(True)
            self.menu_bar.theme_menu.setEnabled(True)
            self.menu_bar.window_size_menu.setEnabled(True)
            self.menu_bar.restart_game_act.setEnabled(True)
            self.menu_bar.end_game_act.setEnabled(False)

        self.channel_0.stop()

    def bulletFiredSound(self):
        self.channel_2.play(self.bullet_fired_sound)

    def bulletImpactSound(self):
        self.channel_3.play(self.bullet_impact_sound)

if __name__ == "__main__":
    app = QApplication([])

    battleCity = BattleCity()
    sys.exit(app.exec_())