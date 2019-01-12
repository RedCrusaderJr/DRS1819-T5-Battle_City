from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import QMutex
from communication import Communication
from enums import GameMode, ElementType, PlayerType
from tank import Tank
import os
from random import sample
from enemy_tank import EnemyTank
import pickle
from move_enemy_thread_mp import MoveEnemyThreadMP
from move_bullets_thread_mp import MoveBulletsThreadMP

class GameServerFrame(QFrame):
    BoardWidth = 32
    BoardHeight = 18
    mutex = QMutex()

    def __init__(self, parent):
        super().__init__(parent)

        self.communication = Communication(GameMode.MULTIPLAYER_ONLINE_HOST)

        self.board = []

        self.initGameBoard()
        self.move_enemy_thread_mp = MoveEnemyThreadMP(self)
        self.move_enemy_thread_mp.start()
        self.move_bullets_thread_mp = MoveBulletsThreadMP(self)
        self.move_bullets_thread_mp.start()

    def initGameBoard(self):
        self.num_of_all_enemies = 7
        self.num_of_enemies_per_level = 4
        self.current_level = 1
        self.force_x = None
        self.force_y = None
        self.enemies_increaser = 0
        self.chosen_enemy = None

        self.bullet_list = []
        self.enemy_list = []

        self.random_values = []
        self.random_values = sample(range(1, 32), self.num_of_enemies_per_level)



        self.player_1 = Tank(PlayerType.PLAYER_1)
        self.player_1_starting_position = ()
        self.player_2 = Tank(PlayerType.PLAYER_2)
        self.player_2_starting_position = ()

        self.clearBoard()

        self.loadLevel(self.current_level)
        for i in range(self.num_of_enemies_per_level):
            self.enemy_list.append(EnemyTank(self.random_values[i]))
            self.setShapeAt(self.enemy_list[i].x, self.enemy_list[i].y, ElementType.ENEMY)
        self.sendBoard()

    def sendBoard(self):
        id = "GAMEBOARD_INIT"
        data = pickle.dumps((id, self.board), -1)
        self.communication.conn1.sendall(data)
        self.communication.conn2.sendall(data)

    def getShapeType(self, x, y):
        return self.board[(y * GameServerFrame.BoardWidth) + x]

    def setShapeAt(self, x, y, shape_type):
        self.board[(y * GameServerFrame.BoardWidth) + x] = shape_type

    def clearBoard(self):
        if len(self.board) > 0:
            self.board.clear()

        for i in range(GameServerFrame.BoardHeight):
            for j in range(GameServerFrame.BoardWidth):
                self.board.append(ElementType.NONE)

    def loadLevel(self, level_nr=1):
        self.clearBoard()
        """ Load specified level
        @return boolean Whether level was loaded
        """
        if level_nr == 0:
            filename = "levels/game_over.txt"
        else:
            filename = "levels/"+str(level_nr)+".txt"

        if not os.path.isfile(filename):
            return False
        #level = []
        f = open(filename, "r")
        data = f.read().split("\n")
        #self.mapr = []
        x, y = 0, 0
        for row in data:
            for ch in row:
                if ch == "#":
                    self.setShapeAt(x, y, ElementType.WALL)
                   # print(f"{x} {y}")
                elif ch == "$":
                    self.setShapeAt(x, y, ElementType.BASE)
                elif ch == "1" and self.player_1.lives > 0:
                    self.player_1.setCoordinates(x, y)
                    self.player_1_starting_position = (x, y)
                    self.setShapeAt(x, y, ElementType.PLAYER1)
                elif ch == "2" and self.player_2.lives > 0:
                    self.player_2.setCoordinates(x, y)
                    self.player_2_starting_position = (x, y)
                    self.setShapeAt(x, y, ElementType.PLAYER2)
                x += 1
            x = 0
            y += 1
        return True

    def findBulletAt(self, x, y):
        for bullet in self.bullet_list:
            if bullet.x == x and bullet.y == y:
                return bullet
