from PyQt5.QtWidgets import QFrame, QLabel, QVBoxLayout

class StatFrame(QFrame):

    def __init__(self, parent, game_board):
        super().__init__(parent)

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

        self.level_num_label = QLabel("Level number: " + str(self.level_num))
        self.enemies_left_label = QLabel("Enemies left: " + str(self.enemies_left))
        self.player_1_lives_label = QLabel("Player 1 lives: " + str(self.player_1_lives))
        if self.game_board.mode == 2:
            self.player_2_lives_label = QLabel("Player 2 lives: " + str(self.player_2_lives))

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
        self.level_num_label.seText("Level number: " + str(self.level_num))

    def changeEnemiesLeft(self, num_of_enemies):
        self.enemies_left = num_of_enemies + 3
        self.enemies_left_label.setText("Enemies left: " + str(self.enemies_left))
