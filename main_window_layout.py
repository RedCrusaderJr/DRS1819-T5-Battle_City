from PyQt5.QtWidgets import QWidget, QMainWindow, QApplication, QAction, QMenu, QSplitter, QHBoxLayout, QVBoxLayout, QFrame, QLabel
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QEvent, pyqtSignal
from game_board import GameBoard
from stat_frame import StatFrame
import sys
from enums import GameMode


class MainWindowLayout(QWidget):
    cancel_threads_signal = pyqtSignal()

    def __init__(self, parent, mode, board_size, stat_size, stat_font_size = 2):
        super(MainWindowLayout, self).__init__(parent)
        self.parent_widget = parent
        self.mode = mode
        self.board_width, self.board_height = board_size
        self.stat_width, self.stat_height = stat_size
        self.stat_font_size = stat_font_size

        self.parent_widget.restart_game_signal.connect(self.restartGame)

        self.game_board_frame = None
        self.stat_frame = None

        self.initGameBoardFrame()
        self.initStatFrame()

        self.h_layout = QHBoxLayout(self)
        self.h_layout.addWidget(self.game_board_frame)
        self.h_layout.addWidget(self.stat_frame)
        self.setLayout(self.h_layout)

        self.game_board_frame.setFocus()

    def initGameBoardFrame(self, width=None, height=None):
        if width is None or height is None:
            width = self.board_width
            height = self.board_height
        else:
            self.board_width = width
            self.board_height = height

        self.game_board_frame = GameBoard(self, self.mode)
        self.game_board_frame.setMinimumSize(width, height)
        self.game_board_frame.setMaximumSize(width, height)
        self.game_board_frame.setObjectName("game_board_frame")
        self.game_board_frame.show()

        self.game_board_frame.game_over_tool_bar_signal.connect(self.parent_widget.gameOver)

    def initStatFrame(self, width=None, height=None):
        if width is None or height is None:
            width = self.stat_width
            height = self.stat_height
        else:
            self.stat_width = width
            self.stat_height = height

        self.stat_frame = StatFrame(self, self.game_board_frame, self.stat_font_size)
        self.stat_frame.setMinimumSize(width, height)
        self.stat_frame.setMaximumSize(width, height)
        self.stat_frame.setObjectName("stat_frame")
        self.stat_frame.show()

    #def restartGame(self, mode=None):
    def restartGame(self, mode=None, board_size=None, stat_size=None, stat_font_size=None):
        if mode is None:
            mode = self.mode
        else:
            self.mode = mode

        if board_size is not None:
            board_width, board_height = board_size
            if board_width is not None and board_height is not None:
                self.board_width = board_width
                self.board_height = board_height
            else:
                board_width = self.board_width
                board_height = self.board_height
        else:
            board_width = self.board_width
            board_height = self.board_height

        if stat_size is not None:
            stat_width, stat_height = stat_size
            if stat_width is not None and stat_height is not None:
                self.stat_width = stat_width
                self.stat_height = stat_height
            else:
                stat_width = self.stat_width
                stat_height = self.stat_height
        else:
            stat_width = self.stat_width
            stat_height = self.stat_height

        if stat_font_size is None:
            stat_font_size = self.stat_font_size
        else:
            self.stat_font_size = stat_font_size

        self.game_board_frame = None
        self.stat_frame = None

        self.initGameBoardFrame()
        self.initStatFrame()

        #self.h_layout = QHBoxLayout(self)
        self.h_layout.addWidget(self.game_board_frame)
        self.h_layout.addWidget(self.stat_frame)
        self.setLayout(self.h_layout)

        self.game_board_frame.setFocus()