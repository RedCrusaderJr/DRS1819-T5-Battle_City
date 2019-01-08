from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QAction, QMenu, QSplitter, QHBoxLayout, QVBoxLayout, QFrame
from PyQt5.QtCore import Qt
from game_board import GameBoard
from stat_frame import StatFrame
import sys


class MainWindowWidget(QWidget):

    def __init__(self, parent, mode):
        super(MainWindowWidget, self).__init__(parent)
        self.layout = QHBoxLayout(self)

        self.game_board_frame = GameBoard(self, mode)
        self.game_board_frame.setMinimumSize(1000, 562.5)
        self.game_board_frame.setMaximumSize(1000, 562.5)
        self.game_board_frame.setObjectName("game_board_frame")
        self.layout.addWidget(self.game_board_frame)

        self.stat_frame = StatFrame(self, self.game_board_frame)
        self.stat_frame.setMaximumHeight(562.5)
        self.stat_frame.setObjectName("stat_frame")
        self.layout.addWidget(self.stat_frame)

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
        settings_menu = menu_bar.addMenu("&Settings")

        mode_menu = QMenu("Mode", self)

        single_act = QAction("Single paleyer", self)
        single_act.triggered.connect(self.toggleSingle)
        multi_act = QAction('Multipaleyer mode', self)
        multi_act.triggered.connect(self.toggleMulti)

        mode_menu.addAction(single_act)
        mode_menu.addAction(multi_act)

        # start_act = QAction('Start game', self)
        # start_act.triggered.connect(self.startGame)

        settings_menu.addMenu(mode_menu)
        # settings_menu.addAction(start_act)

        self.show()

    def toggleSingle(self, mode):
        self.status_bar.showMessage("MODE: SINGLE PLAYER")
        self.form_widget = MainWindowWidget(self, 1)
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

    def toggleMulti(self, mode):
        self.status_bar.showMessage("MODE: MULTIPLAYER")
        self.form_widget = MainWindowWidget(self, 2)
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