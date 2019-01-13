from PyQt5.QtWidgets import QFrame
from PyQt5.QtCore import QMutex
from communication import Communication
from enums import GameMode, ElementType, PlayerType, Orientation
from tank import Tank
import os
from random import sample
from enemy_tank import EnemyTank
import pickle
from move_enemy_thread_mp import MoveEnemyThreadMP
from move_bullets_thread_mp import MoveBulletsThreadMP
from move_player_thread_mp import MovePlayerThreadMP
import struct
import socket


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
        self.move_player_thread_mp1 = MovePlayerThreadMP(1, self)
        self.move_player_thread_mp1.start()
        self.move_player_thread_mp2 = MovePlayerThreadMP(2, self)
        self.move_player_thread_mp2.start()

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

    def send_msg(self, sock, msg):
        # Prefix each message with a 4-byte length (network byte order)
        print("Poslato")
        msg = struct.pack('>I', len(msg)) + msg
        sock.sendall(msg)

    def sendBoard(self):
        id = "GAMEBOARD_INIT"
        data = pickle.dumps((id, self.board), -1)

        self.send_msg(self.communication.conn1, data)
        self.send_msg(self.communication.conn2, data)

    def updateLevel(self):
        data = pickle.dumps((str("UPDATE_LEVEL"), (self.num_of_all_enemies, self.current_level)), -1)

        self.send_msg(self.communication.conn1, data)
        self.send_msg(self.communication.conn2, data)

    def sendWinner(self, player):
        self.loadLevel(-1)
        data = pickle.dumps((str("WINNER"), self.board), -1)
        if player == 1:
            self.send_msg(self.communication.conn1, data)
            self.communication.conn1.shutdown(socket.SHUT_RDWR)
            self.communication.conn1.close()
        else:
            self.send_msg(self.communication.conn2, data)
            self.communication.conn2.shutdown(socket.SHUT_RDWR)
            self.communication.conn2.close()


    def sendLoser(self, player):
        self.loadLevel(-2)
        data = pickle.dumps((str("LOSER"), self.board), -1)
        if player == 1:
            self.send_msg(self.communication.conn1, data)
            self.communication.conn1.shutdown(socket.SHUT_RDWR)
            self.communication.conn1.close()
        else:
            self.send_msg(self.communication.conn2, data)
            self.communication.conn2.shutdown(socket.SHUT_RDWR)
            self.communication.conn2.close()

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
        elif level_nr == -1:
            filename = "levels/winner.txt"
        elif level_nr == -2:
            filename = "levels/loser.txt"
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
                    self.player_1.orientation = Orientation.UP
                    self.player_1_starting_position = (x, y)
                    self.setShapeAt(x, y, ElementType.PLAYER1_UP)
                elif ch == "2" and self.player_2.lives > 0:
                    self.player_2.setCoordinates(x, y)
                    self.player_2.orientation = Orientation.UP
                    self.player_2_starting_position = (x, y)
                    self.setShapeAt(x, y, ElementType.PLAYER2_UP)
                x += 1
            x = 0
            y += 1
        return True

    def findBulletAt(self, x, y):
        for bullet in self.bullet_list:
            if bullet.x == x and bullet.y == y:
                return bullet

    def findEnemyAt(self, x, y):
        for enemy in self.enemy_list:
            if enemy.x == x and enemy.y == y:
                return enemy

    def gameOver(self):
        self.enemy_list = []
        self.bullet_list = []

        self.move_player_thread_mp1.cancel()
        self.move_player_thread_mp2.cancel()
        self.move_enemy_thread_mp.cancel()
        self.move_bullets_thread_mp.cancel()
        if self.player_1.lives == 0:
            self.sendLoser(1)
            self.sendWinner(2)
        elif self.player_2.lives == 0:
            self.sendLoser(2)
            self.sendWinner(1)
        elif self.player_1.lives > self.player_2.lives:
            self.sendLoser(2)
            self.sendWinner(1)
        elif self.player_1.lives < self.player_2.lives:
            self.sendLoser(1)
            self.sendWinner(2)
        else:
            self.sendLoser(2)
            self.sendWinner(1)

    def advanceToNextLevel(self):
        self.bullet_list = []
        self.player_2.active_bullet = None
        self.player_1.active_bullet = None

        self.current_level += 1
        if (self.current_level > 6):
            self.current_level = 1
        self.loadLevel(self.current_level)

        self.random_values = []
        self.random_values = sample(range(1, 32), self.num_of_enemies_per_level)

        for i in range(self.num_of_enemies_per_level):
            self.enemy_list.append(EnemyTank(self.random_values[i]))
            self.setShapeAt(self.enemy_list[i].x, self.enemy_list[i].y, ElementType.ENEMY)

        self.enemies_increaser += 1

        self.num_of_all_enemies = 7 + self.enemies_increaser


        self.sendBoard()

        self.updateLevel()

        #TODO FORCE



