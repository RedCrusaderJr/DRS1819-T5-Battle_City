from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout
from enums import GameMode

class StatFrame(QFrame):

    def __init__(self, parent, game_board, font_size = 2):
        super().__init__(parent)

        self.font_size = font_size
        self.game_board = game_board
        self.game_board.change_lives_signal.connect(self.changeLives)
        self.game_board.change_level_signal.connect(self.changeLevel)
        self.game_board.change_enemies_left_signal.connect(self.changeEnemiesLeft)

        self.layout = QVBoxLayout()

        self.level_num = 1
        self.enemies_left = game_board.num_of_all_enemies + 3
        self.player_1_lives = 3
        if self.game_board.mode == GameMode.MULTIPLAYER_OFFLINE or self.game_board.mode == GameMode.MULTIPLAYER_ONLINE_CLIENT:
            self.player_2_lives = 3

        self.level_num_label = QLabel("Level number: " + str(self.level_num))
        self.enemies_left_label = QLabel("Enemies left: " + str(self.enemies_left))
        self.player_1_lives_label = QLabel("Player 1 lives: " + str(self.player_1_lives))

        if self.game_board.mode == GameMode.MULTIPLAYER_OFFLINE or self.game_board.mode == GameMode.MULTIPLAYER_ONLINE_CLIENT:
            self.player_2_lives_label = QLabel("Player 2 lives: " + str(self.player_2_lives))

        self.fontSizeChange()

        self.layout.addWidget(self.level_num_label)
        self.layout.addWidget(self.enemies_left_label)
        self.layout.addWidget(self.player_1_lives_label)
        if self.game_board.mode == GameMode.MULTIPLAYER_OFFLINE or self.game_board.mode == GameMode.MULTIPLAYER_ONLINE_CLIENT:
            self.layout.addWidget(self.player_2_lives_label)

        self.setLayout(self.layout)
        
    def changeLives(self, player, num_of_lives):
        if player == 1:
            self.player_1_lives = num_of_lives
            self.player_1_lives_label.setText("Player 1 lives: " + str(self.player_1_lives))
        elif player == 2 and (self.game_board.mode == GameMode.MULTIPLAYER_OFFLINE or self.game_board.mode == GameMode.MULTIPLAYER_ONLINE_CLIENT):
            self.player_2_lives = num_of_lives
            self.player_2_lives_label.setText("Player 2 lives: " + str(self.player_2_lives))

    def changeLevel(self):
        self.level_num += 1
        self.level_num_label.setText("Level number: " + str(self.level_num))

    def changeEnemiesLeft(self, num_of_enemies):
        self.enemies_left = num_of_enemies + 3
        self.enemies_left_label.setText("Enemies left: " + str(self.enemies_left))
        
    def fontSizeChange(self):
        print("fontSizeChange")
        if self.font_size == 1:
            self.level_num_label.setProperty('Size1', True)
            self.enemies_left_label.setProperty('Size1', True)
            self.player_1_lives_label.setProperty('Size1', True)

            self.level_num_label.setProperty('Size2', False)
            self.enemies_left_label.setProperty('Size2', False)
            self.player_1_lives_label.setProperty('Size2', False)

            self.level_num_label.setProperty('Size3', False)
            self.enemies_left_label.setProperty('Size3', False)
            self.player_1_lives_label.setProperty('Size3', False)

            if self.game_board.mode == GameMode.MULTIPLAYER_OFFLINE or self.game_board.mode == GameMode.MULTIPLAYER_ONLINE_CLIENT:
                self.player_2_lives_label.setProperty('Size1', True)
                self.player_2_lives_label.setProperty('Size2', False)
                self.player_2_lives_label.setProperty('Size3', False)

        elif self.font_size == 2:
            self.level_num_label.setProperty('Size1', False)
            self.enemies_left_label.setProperty('Size1', False)
            self.player_1_lives_label.setProperty('Size1', False)

            self.level_num_label.setProperty('Size2', True)
            self.enemies_left_label.setProperty('Size2', True)
            self.player_1_lives_label.setProperty('Size2', True)

            self.level_num_label.setProperty('Size3', False)
            self.enemies_left_label.setProperty('Size3', False)
            self.player_1_lives_label.setProperty('Size3', False)

            if self.game_board.mode == GameMode.MULTIPLAYER_OFFLINE or self.game_board.mode == GameMode.MULTIPLAYER_ONLINE_CLIENT:
                self.player_2_lives_label.setProperty('Size1', False)
                self.player_2_lives_label.setProperty('Size2', True)
                self.player_2_lives_label.setProperty('Size3', False)

        elif self.font_size == 3:
            self.level_num_label.setProperty('Size1', False)
            self.enemies_left_label.setProperty('Size1', False)
            self.player_1_lives_label.setProperty('Size1', False)

            self.level_num_label.setProperty('Size2', False)
            self.enemies_left_label.setProperty('Size2', False)
            self.player_1_lives_label.setProperty('Size2', False)

            self.level_num_label.setProperty('Size3', True)
            self.enemies_left_label.setProperty('Size3', True)
            self.player_1_lives_label.setProperty('Size3', True)

            if self.game_board.mode == GameMode.MULTIPLAYER_OFFLINE or self.game_board.mode == GameMode.MULTIPLAYER_ONLINE_CLIENT:
                self.player_2_lives_label.setProperty('Size1', False)
                self.player_2_lives_label.setProperty('Size2', False)
                self.player_2_lives_label.setProperty('Size3', True)

        self.setStyle(self.style())