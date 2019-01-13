from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout, QHBoxLayout, QPushButton, QGridLayout

class StatFrame(QFrame):

    def __init__(self, parent, game_board, font_size = 2):
        super().__init__(parent)

        self.font_size = font_size
        self.game_board = game_board
        self.game_board.change_lives_signal.connect(self.changeLives)
        self.game_board.change_level_signal.connect(self.changeLevel)
        self.game_board.change_enemies_left_signal.connect(self.changeEnemiesLeft)

        self.layout = QVBoxLayout()
        # self.label = QLabel("My text")

        self.level_num = 1
        self.enemies_left = game_board.num_of_all_enemies + 3
        self.player_1_lives = 3
        if self.game_board.mode == 2:
            self.player_2_lives = 3

        # name_font = self.level_num_label.font()
        # name_font.setPointSize(20)

        self.level_num_label = QLabel("Level number: " + str(self.level_num))
        #self.level_num_label.setFont(name_font)

        self.enemies_left_label = QLabel("Enemies left: " + str(self.enemies_left))
        #self.enemies_left_label.setFont(name_font)

        self.player_1_lives_label = QLabel("Player 1 lives: " + str(self.player_1_lives))
        #self.player_1_lives_label.setFont(name_font)

        if self.game_board.mode == 2:
            self.player_2_lives_label = QLabel("Player 2 lives: " + str(self.player_2_lives))
            #self.player_2_lives_label.setFont(name_font)

        self.fontSizeChange()

        self.layout.addWidget(self.level_num_label)
        self.layout.addWidget(self.enemies_left_label)
        self.layout.addWidget(self.player_1_lives_label)
        if self.game_board.mode == 2:
            self.layout.addWidget(self.player_2_lives_label)

        # self.layout.addWidget(self.label)
        self.setLayout(self.layout)
        
    def changeLives(self, player, num_of_lives):
        if player == 1:
            self.player_1_lives = num_of_lives
            self.player_1_lives_label.setText("Player 1 lives: " + str(self.player_1_lives))
        elif player == 2 and self.game_board.mode == 2:
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

            if self.game_board.mode == 2:
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

            if self.game_board.mode == 2:
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

            if self.game_board.mode == 2:
                self.player_2_lives_label.setProperty('Size1', False)
                self.player_2_lives_label.setProperty('Size2', False)
                self.player_2_lives_label.setProperty('Size3', True)

        self.setStyle(self.style())

class DecisionFrame(QFrame):
    def __init__(self, parent):
        super().__init__(parent)

        self.decision_frame_layout = QGridLayout()

        self.button_restart = QPushButton('Restart', self)
        self.button_restart.clicked.connect(self.restartGame)
        self.button_restart.resize(200, 50)
        self.decision_frame_layout.addWidget(self.button_restart, 0, 1)

        #self.button_restart.move(250, 480)


        #name_font = self.button_restart.font()
        #name_font.setPointSize(15)
        #self.button_restart.setFont(name_font)
        #self.button_restart.hide()

        self.button_end = QPushButton('End', self)
        self.button_end.clicked.connect(self.endGame)
        self.button_end.resize(200, 50)
        self.decision_frame_layout.addWidget(self.button_end, 0, 5)
        #self.decision_frame_layout.setColumnStretch(0, 1)
        #self.button_end.move(550, 480)


        #self.button_end.setFont(name_font)
        #self.button_end.hide()
        self.setLayout(self.decision_frame_layout)
        #self.hide()

        #self.parent_widget.game_over_signal.connect(self.gameOver)