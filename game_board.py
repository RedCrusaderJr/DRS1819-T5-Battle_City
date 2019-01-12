from PyQt5.QtWidgets import QFrame, QLabel
from PyQt5.QtGui import QPainter, QColor, QTransform, QPixmap
from PyQt5.QtCore import pyqtSignal, Qt, QMutex
from move_player_thread import MovePlayerThread
from move_enemy_thread import MoveEnemyThread
from move_bullets_thread import MoveBulletsThread
from tank import Tank
from enemy_tank import EnemyTank
import os
from enums import PlayerType, ElementType, WallType, Orientation, BulletType, GameMode
from helper import Helper
from bullet import Bullet
from random import sample, randint
import time
from multiprocessing import Process, Pipe
from deux_ex_machina import DeuxExMachina
from deux_ex_machina_thread import DeuxExMachinaThread
from communication import Communication
import pickle
from communication_thread import CommunicationThread

class GameBoard(QFrame):
    #TODO: refactor ovo staviti negde
    BoardWidth = 32
    BoardHeight = 18
    mutex = QMutex()

    change_lives_signal = pyqtSignal(int, int)
    change_level_signal = pyqtSignal()
    change_enemies_left_signal = pyqtSignal(int)
    restart_game_signal = pyqtSignal()
    speed_up_signal = pyqtSignal()
    game_over_signal = pyqtSignal()

    # tile width/height in px
    TILE_SIZE = 16

    def __init__(self, parent, mode):
        super().__init__(parent)
        self.mode = mode
        self.commands_1 = []
        self.commands_2 = []

        self.enemies_list = []
        self.bullets_list = []

        self.socket = None
        if mode is GameMode.MULTIPLAYER_ONLINE_HOST or mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            self.communnication = Communication(mode)
            if self.communnication.socket is not None:
                self.socket = self.communnication.socket
                self.conn = self.communnication.conn
            else:
                print("Error on socket creation.")

        self.initGameBoard()


    #region INIT_METHODS
    def initGameBoard(self):
        self.num_of_all_enemies = 7
        self.num_of_enemies_per_level = 4
        self.current_level = 1
        self.force_x = None
        self.force_y = None
        self.enemies_increaser = 0

        if self.mode is GameMode.SINGLEPLAYER:
            self.initSingleplayer()
        elif self.mode is GameMode.MULTIPLAYER_OFFLINE:
            self.initMultiplayerOffline()
        elif self.mode is GameMode.MULTIPLAYER_ONLINE_HOST:
            self.initMultiplayerOnlineHost()
        elif self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            self.initMultiplayerOnlineClient()

    def initSingleplayer(self):
        self.random_values = []
        self.random_values = sample(range(1, 32), self.num_of_enemies_per_level)

        self.board = []
        self.bullet_dictionary = {}
        self.enemy_dictionary = {}
        for i in range(self.num_of_enemies_per_level):
            self.enemy_dictionary[EnemyTank(self.random_values[i])] = QLabel(self)

        self.player_1 = Tank(PlayerType.PLAYER_1)
        self.player_1_label = QLabel(self)
        self.player_1_starting_position = ()

        self.clearBoard()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setInitialMap()


        # region THREADS
        self.move_player_1_thread = MovePlayerThread(self.commands_1, self.player_1, self)
        self.move_player_1_thread.player_moved_signal.connect(self.playerMoved)
        self.move_player_1_thread.bullet_fired_signal.connect(self.bulletFired)
        self.move_player_1_thread.bullet_impact_signal.connect(self.bulletMoved)

        self.move_enemy_thread = MoveEnemyThread(self)
        self.move_enemy_thread.bullet_fired_signal.connect(self.bulletFired)
        self.move_enemy_thread.bullet_impact_signal.connect(self.bulletMoved)
        self.move_enemy_thread.enemy_move_signal.connect(self.enemyCallback)

        self.move_bullets_thread = MoveBulletsThread(self)
        self.move_bullets_thread.bullets_move_signal.connect(self.bulletMoved)
        self.move_bullets_thread.dead_player_signal.connect(self.removeDeadPlayer)

        self.ex_pipe, self.in_pipe = Pipe()
        self.deux_ex_machina_process = DeuxExMachina(pipe=self.ex_pipe,
                                                     boardWidth=GameBoard.BoardWidth,
                                                     boardHeight=GameBoard.BoardHeight)

        self.deux_ex_machina_thread = DeuxExMachinaThread(self)
        # endregion

    def initMultiplayerOffline(self):
        self.random_values = []
        self.random_values = sample(range(1, 32), self.num_of_enemies_per_level)

        self.board = []
        self.bullet_dictionary = {}
        self.enemy_dictionary = {}
        for i in range(self.num_of_enemies_per_level):
            self.enemy_dictionary[EnemyTank(self.random_values[i])] = QLabel(self)

        self.player_1 = Tank(PlayerType.PLAYER_1)
        self.player_1_label = QLabel(self)
        self.player_1_starting_position = ()

        self.player_2 = Tank(PlayerType.PLAYER_2)
        self.player_2_label = QLabel(self)
        self.player_2_starting_position = ()

        self.clearBoard()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setInitialMap()


        # region THREADS
        self.move_player_1_thread = MovePlayerThread(self.commands_1, self.player_1, self)
        self.move_player_1_thread.player_moved_signal.connect(self.playerMoved)
        self.move_player_1_thread.bullet_fired_signal.connect(self.bulletFired)
        self.move_player_1_thread.bullet_impact_signal.connect(self.bulletMoved)

        self.move_player_2_thread = MovePlayerThread(self.commands_2, self.player_2, self)
        self.move_player_2_thread.player_moved_signal.connect(self.playerMoved)
        self.move_player_2_thread.bullet_fired_signal.connect(self.bulletFired)
        self.move_player_2_thread.bullet_impact_signal.connect(self.bulletMoved)

        self.move_enemy_thread = MoveEnemyThread(self)
        self.move_enemy_thread.bullet_fired_signal.connect(self.bulletFired)
        self.move_enemy_thread.bullet_impact_signal.connect(self.bulletMoved)
        self.move_enemy_thread.enemy_move_signal.connect(self.enemyCallback)
        self.move_enemy_thread.dead_player_signal.connect(self.removeDeadPlayer)
        self.move_bullets_thread = MoveBulletsThread(self)
        self.move_bullets_thread.bullets_move_signal.connect(self.bulletMoved)
        self.move_bullets_thread.dead_player_signal.connect(self.removeDeadPlayer)

        self.ex_pipe, self.in_pipe = Pipe()
        self.deux_ex_machina_process = DeuxExMachina(pipe=self.ex_pipe,
                                                     boardWidth=GameBoard.BoardWidth,
                                                     boardHeight=GameBoard.BoardHeight)

        self.deux_ex_machina_thread = DeuxExMachinaThread(self)
        # endregion

    def initMultiplayerOnlineHost(self):
        self.random_values = []
        self.random_values = sample(range(1, 32), self.num_of_enemies_per_level)

        self.board = []
        self.bullet_dictionary = {}
        self.enemy_dictionary = {}
        for i in range(self.num_of_enemies_per_level):
            self.enemy_dictionary[EnemyTank(self.random_values[i])] = QLabel(self)

        self.sendInitEnemiesToClient()
        self.receiveOkFromClient()

        self.player_1 = Tank(PlayerType.PLAYER_1)
        self.player_1_label = QLabel(self)
        self.player_1_starting_position = ()

        self.player_2 = Tank(PlayerType.PLAYER_2)
        self.player_2_label = QLabel(self)
        self.player_2_starting_position = ()

        self.clearBoard()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setInitialMap()


        #region THREADS
        self.move_player_1_thread = MovePlayerThread(self.commands_1, self.player_1, self)
        self.move_player_1_thread.player_moved_signal.connect(self.playerMoved)
        self.move_player_1_thread.bullet_fired_signal.connect(self.bulletFired)
        self.move_player_1_thread.bullet_impact_signal.connect(self.bulletMoved)

        #TODO: thred za pozicije pl 2
        self.communnication_thread = CommunicationThread()

        self.move_enemy_thread = MoveEnemyThread(self)
        self.move_enemy_thread.bullet_fired_signal.connect(self.bulletFired)
        self.move_enemy_thread.bullet_impact_signal.connect(self.bulletMoved)
        self.move_enemy_thread.enemy_move_signal.connect(self.enemyCallback)

        self.move_bullets_thread = MoveBulletsThread(self)
        self.move_bullets_thread.bullets_move_signal.connect(self.bulletMoved)
        self.move_bullets_thread.dead_player_signal.connect(self.removeDeadPlayer)

        self.ex_pipe, self.in_pipe = Pipe()
        self.deux_ex_machina_process = DeuxExMachina(pipe=self.ex_pipe,
                                                     boardWidth=GameBoard.BoardWidth,
                                                     boardHeight=GameBoard.BoardHeight)

        self.deux_ex_machina_thread = DeuxExMachinaThread(self)
        #endregion

    def initMultiplayerOnlineClient(self):
        self.board = []

        self.clearBoard()
        self.setFocusPolicy(Qt.StrongFocus)
        # region THREADS
        # TODO: thred za pozicije pl 1, bulleta, i svega ostalog....
        self.communnication_thread = CommunicationThread(self)
        #self.communnication_thread.player_move_signal.connect()
        #self.communnication_thread.bullet_fired_signal.connect()
        #self.communnication_thread.bullets_move_signal.connect()
        #self.communnication_thread.enemy_move_signal.connect()

        #self.move_player_2_thread = MovePlayerThread(self.commands_2, self.player_2, self)
        #self.move_player_2_thread.player_moved_signal.connect(self.playerMoved)
        #self.move_player_2_thread.bullet_fired_signal.connect(self.bulletFired)
        #self.move_player_2_thread.bullet_impact_signal.connect(self.bulletMoved)
        # endregion

    def sendInitEnemiesToClient(self):
        enemy_list = list(self.enemy_dictionary.keys())
        data = pickle.dumps(("INIT_ENEMY", enemy_list))
            
        #with self.socket:
        self.conn.sendall(data)

    def receiveOkFromClient(self):
        #with self.socket:
        
        #with conn:
        while True: #waiting for OK
            text = ""
            while True:
                bin = self.conn.recv(1024)
                if not bin or len(bin) < 1024:
                    break

            msg = pickle.loads(bin)
            if msg is "OK":
                break

    def receiveInitEnemyFromHost(self):
        #with self.socket:
            #conn, addr = self.socket.accept()
           # with conn:
            text = ""
            while True:
                bin = self.socket.recv(1024)
                if not bin or len(bin) < 1024:
                    break

            id, data = pickle.loads(bin)

            if id is "INIT_ENEMY":
                for i in range(data):
                    self.enemy_dictionary[EnemyTank(data[i])] = QLabel(self)
                text = "OK"
                self.socket.sendall(text.encode("utf8"))
    #endregion


    # region EVENTS
    def showEvent(self, *args, **kwargs):
        print("show event")
        if self.mode is not GameMode.MULTIPLAYER_ONLINE_CLIENT:
            self.setPlayersForNextLevel()

            for enemy in self.enemy_dictionary:
                pixmap3 = enemy.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
                self.enemy_dictionary[enemy].setPixmap(pixmap3)
                self.setGameBoardLabelGeometry(self.enemy_dictionary[enemy], enemy.x, enemy.y)
                self.setShapeAt(enemy.x, enemy.y, ElementType.ENEMY)


        if self.mode is GameMode.SINGLEPLAYER:
            self.move_player_1_thread.start()
            #self.move_player_2_thread.start()
            self.move_enemy_thread.start()
            self.move_bullets_thread.start()
            self.deux_ex_machina_process.start()
            self.deux_ex_machina_thread.start()

        elif self.mode is GameMode.MULTIPLAYER_OFFLINE:
            self.move_player_1_thread.start()
            self.move_player_2_thread.start()
            self.move_enemy_thread.start()
            self.move_bullets_thread.start()
            self.deux_ex_machina_process.start()
            self.deux_ex_machina_thread.start()

        elif self.mode is GameMode.MULTIPLAYER_ONLINE_HOST:
            self.move_player_1_thread.start()
            #self.move_player_2_thread.start()
            self.move_enemy_thread.start()
            self.move_bullets_thread.start()
            self.deux_ex_machina_process.start()
            self.deux_ex_machina_thread.start()

        elif self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            self.communnication_thread.start()
            #self.move_player_1_thread.start()
            #self.move_player_2_thread.start()
            #self.move_bullets_thread.start()
            #self.deux_ex_machina_process.start()
            #self.deux_ex_machina_thread.start()


    def paintEvent(self, QPaintEvent):
        painter = QPainter(self)
        rect = self.contentsRect()
        board_top = rect.bottom() - GameBoard.BoardHeight * self.getSquareHeight()
        self.mutex.lock()
        for i in range(GameBoard.BoardHeight):
            for j in range(GameBoard.BoardWidth):
                shape_type = self.getShapeType(j, i)
                if shape_type == ElementType.WALL:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.WALL)
                elif shape_type == ElementType.BASE:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.BASE)
                elif shape_type == ElementType.LIFE:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.LIFE)
                elif shape_type == ElementType.FREEZE:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.FREEZE)
                elif shape_type == ElementType.PLAYER1:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.PLAYER1)
                elif shape_type == ElementType.PLAYER2:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.PLAYER2)
                elif shape_type == ElementType.ENEMY_UP:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.ENEMY_UP)
                elif shape_type == ElementType.ENEMY_RIGHT:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.ENEMY_RIGHT)
                elif shape_type == ElementType.ENEMY_DOWN:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.ENEMY_DOWN)
                elif shape_type == ElementType.ENEMY_LEFT:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.ENEMY_LEFT)
                elif shape_type == ElementType.BULLET_UP:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.BULLET_UP)
                elif shape_type == ElementType.BULLET_RIGHT:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.BULLET_RIGHT)
                elif shape_type == ElementType.BULLET_DOWN:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.BULLET_DOWN)
                elif shape_type == ElementType.BULLET_LEFT:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.BULLET_LEFT)
                elif shape_type == ElementType.PLAYER1_LEFT:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.PLAYER1_LEFT)
                elif shape_type == ElementType.PLAYER1_RIGHT:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.PLAYER1_RIGHT)
                elif shape_type == ElementType.PLAYER1_DOWN:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.PLAYER1_DOWN)
                elif shape_type == ElementType.PLAYER1_UP:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.PLAYER1_UP)
                elif shape_type == ElementType.PLAYER2_LEFT:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.PLAYER2_LEFT)
                elif shape_type == ElementType.PLAYER2_RIGHT:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.PLAYER2_RIGHT)
                elif shape_type == ElementType.PLAYER2_DOWN:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.PLAYER2_DOWN)
                elif shape_type == ElementType.PLAYER2_UP:
                    self.drawSquare(painter,
                                    rect.left() + j * self.getSquareWidth(),
                                    board_top + i * self.getSquareHeight(),
                                    ElementType.PLAYER2_UP)
        self.mutex.unlock()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down or  \
                                       event.key() == Qt.Key_Left or  \
                                       event.key() == Qt.Key_Right or \
                                       event.key() == Qt.Key_Space:
            if self.mode is not GameMode.MULTIPLAYER_ONLINE_CLIENT:
                self.commands_1.append(event.key())
            else:
                self.sendCommand(event.key())
        elif event.key() == Qt.Key_W or event.key() == Qt.Key_S or \
                                        event.key() == Qt.Key_A or \
                                        event.key() == Qt.Key_D or \
                                        event.key() == Qt.Key_F:
            self.commands_2.append(event.key())

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Up or event.key() == Qt.Key_Down or  \
                                       event.key() == Qt.Key_Left or  \
                                       event.key() == Qt.Key_Right or \
                                       event.key() == Qt.Key_Space:
            if self.mode is not GameMode.MULTIPLAYER_ONLINE_CLIENT:
                self.commands_1.remove(event.key())
        elif event.key() == Qt.Key_W or event.key() == Qt.Key_S or \
                                        event.key() == Qt.Key_A or \
                                        event.key() == Qt.Key_D or \
                                        event.key() == Qt.Key_F:
            self.commands_2.remove(event.key())
    # endregion

    def sendCommand(self, key):
        if key == Qt.Key_Up:
            msg = "UP"
        elif key == Qt.Key_Down:
            msg = "DOWN"
        elif key == Qt.Key_Left:
            msg = "LEFT"
        elif key == Qt.Key_Right:
            msg = "RIGHT"
        elif key == Qt.Key_Space:
            msg = "FIRE"

        self.socket.sendall(msg.encode('utf8'))


    #region EVIDENTION_METHODS
    def setShapeAt(self, x, y, shape_type):
        self.board[(y * GameBoard.BoardWidth) + x] = shape_type

    def setInitialMap(self):
        self.loadLevel(self.current_level)

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
                elif ch == "2" and self.mode is not GameMode.SINGLEPLAYER and self.player_2.lives > 0:
                    self.player_2.setCoordinates(x, y)
                    self.player_2_starting_position = (x, y)
                    self.setShapeAt(x, y, ElementType.PLAYER2)
                x += 1
            x = 0
            y += 1
        return True

    def advanceToNextLevel(self):
        if len(self.bullet_dictionary) > 0:
            for bullet in self.bullet_dictionary:
                self.bullet_dictionary[bullet].hide()
            self.bullet_dictionary.clear()

        if len(self.enemy_dictionary) > 0:
            for enemy in self.enemy_dictionary:
                self.enemy_dictionary[enemy].hide()
            self.enemy_dictionary.clear()

        for i in range(self.num_of_enemies_per_level):
            self.enemy_dictionary[EnemyTank(self.random_values[i])] = QLabel(self)

        for enemy in self.enemy_dictionary:
            pixmap3 = enemy.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
            self.enemy_dictionary[enemy].setPixmap(pixmap3)
            self.setGameBoardLabelGeometry(self.enemy_dictionary[enemy], enemy.x, enemy.y)
            self.setShapeAt(enemy.x, enemy.y, ElementType.ENEMY)
            self.enemy_dictionary[enemy].show()

        if self.current_level >= 6:
            self.current_level = 0

        self.enemies_increaser += 1

        self.force_y = None
        self.force_x = None
        self.num_of_all_enemies = 7 + self.enemies_increaser
        self.current_level += 1
        self.setPlayersForNextLevel()
        self.loadLevel(self.current_level)
        self.change_enemies_left_signal.emit(self.num_of_all_enemies)
        self.change_level_signal.emit()
        self.speed_up_signal.emit()
        time.sleep(0.5)


    def setPlayersForNextLevel(self):
        # self.player_1_label.hide()
        # self.player_2_label.hide()

        if self.player_1.lives > 0:
            self.player_1.reset()
            pixmap_1 = self.player_1.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
            self.setPlayerToStartingPosition(self.player_1.x, self.player_1.y, self.player_1)

            self.player_1_label.setPixmap(pixmap_1)
            self.setGameBoardLabelGeometry(self.player_1_label, self.player_1.x, self.player_1.y)
            self.player_1_label.orientation = Orientation.UP
            self.setShapeAt(self.player_1.x, self.player_1.y, ElementType.PLAYER1)
            self.player_1_label.show()

        if self.mode == GameMode.MULTIPLAYER_OFFLINE and self.player_2.lives > 0:
            self.player_2.reset()
            pixmap_2 = self.player_2.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
            self.setPlayerToStartingPosition(self.player_2.x, self.player_2.y, self.player_2)

            self.player_2_label.setPixmap(pixmap_2)
            self.setGameBoardLabelGeometry(self.player_2_label, self.player_2.x, self.player_2.y)
            self.player_2_label.orientation = Orientation.UP
            self.setShapeAt(self.player_2.x, self.player_2.y, ElementType.PLAYER2)
            self.player_2_label.show()

    def setPlayerToStartingPosition(self, old_x, old_y, tank):
        if (tank.player_type == PlayerType.PLAYER_1):
            new_x = self.player_1_starting_position[0]
            new_y = self.player_1_starting_position[1]
            el_type = ElementType.PLAYER1
            label = self.player_1_label
        else:
            if self.mode == 2:
                new_x = self.player_2_starting_position[0]
                new_y = self.player_2_starting_position[1]
                el_type = ElementType.PLAYER2
                label = self.player_2_label

        for i in range(new_y, self.BoardHeight):
            for j in range(new_x, self.BoardWidth):
                shape = self.getShapeType(j, i)
                if shape is ElementType.NONE:
                    self.setShapeAt(old_x, old_y, ElementType.NONE)
                    self.setGameBoardLabelGeometry(label, j, i)
                    self.setShapeAt(j, i, el_type)
                    tank.x = j
                    tank.y = i
                    return True
                elif shape is el_type:
                    return True
            for j in range(0, new_x):
                shape = self.getShapeType(j, i)
                if shape is ElementType.NONE:
                    self.setShapeAt(old_x, old_y, ElementType.NONE)
                    self.setGameBoardLabelGeometry(label, j, i)
                    self.setShapeAt(j, i, el_type)
                    tank.x = j
                    tank.y = i
                    return True
                elif shape is el_type:
                    return True

        for i in range(0, new_y):
            for j in range(new_x, self.BoardWidth):
                shape = self.getShapeType(j, i)
                if shape is ElementType.NONE:
                    self.setShapeAt(old_x, old_y, ElementType.NONE)
                    self.setGameBoardLabelGeometry(label, j, i)
                    self.setShapeAt(j, i, el_type)
                    tank.x = j
                    tank.y = i
                    return True
                elif shape is el_type:
                    return True
            for j in range(0, new_x):
                shape = self.getShapeType(j, i)
                if shape is ElementType.NONE:
                    self.setShapeAt(old_x, old_y, ElementType.NONE)
                    self.setGameBoardLabelGeometry(label, j, i)
                    self.setShapeAt(j, i, el_type)
                    tank.x = j
                    tank.y = i
                    return True
                elif shape is el_type:
                    return True

        return False

    def addEnemy(self):
        rand_x = 0
        while(True):
            rand_x = randint(0, self.BoardWidth)
            if self.getShapeType(rand_x, 0) == ElementType.NONE:
                break

        current_enemy = EnemyTank(rand_x)
        self.enemy_dictionary[current_enemy] = QLabel(self)
        enemy_label = self.enemy_dictionary[current_enemy]

        pix_map = current_enemy.pix_map.scaled(self.getSquareWidth(), self.getSquareHeight())
        enemy_label.setPixmap(pix_map)
        self.setGameBoardLabelGeometry(enemy_label, current_enemy.x, current_enemy.y)
        self.setShapeAt(current_enemy.x, current_enemy.y, ElementType.ENEMY)
        enemy_label.show()

    def removeDeadPlayer(self, player_num):
        if player_num == 1:
            self.player_1_label.hide()
            self.move_player_1_thread.cancel()
        elif player_num == 2:
            self.player_2_label.hide()
            self.move_player_2_thread.cancel()

    def clearBoard(self):
        if len(self.board) > 0:
            self.board.clear()

        for i in range(GameBoard.BoardHeight):
            for j in range(GameBoard.BoardWidth):
                self.board.append(ElementType.NONE)
        self.update()
    #endregion


    #region GET_METHODS
    def getShapeType(self, x, y):
        return self.board[(y * GameBoard.BoardWidth) + x]

    def getSquareWidth(self):
        return self.contentsRect().width() // GameBoard.BoardWidth

    def getSquareHeight(self):
        return self.contentsRect().height() // GameBoard.BoardHeight

    def findBulletAt(self, x, y):
        for bullet in self.bullet_dictionary:
            if bullet.x == x and bullet.y == y:
                return bullet
    #endregion


    #region CALLBACKS
    def enemyCallback(self, enemies_with_new_position, enemies_with_new_orientation, enemies_to_be_removed, bullets_to_be_removed):

        for enemy in enemies_with_new_position:
            if enemy in self.enemy_dictionary:
                enemy_label = self.enemy_dictionary[enemy]
                self.setGameBoardLabelGeometry(enemy_label, enemy.x,enemy.y)
            else:
                print(f"enemy({enemy}) from enemies_with_new_position is not in enemy_dictionary")

        for element in enemies_with_new_orientation:
            enemy, transform = element
            if enemy in self.enemy_dictionary:
                enemy_label = self.enemy_dictionary[enemy]
                pix = enemy_label.pixmap()
                enemy_label.setPixmap(pix.transformed(transform))
            else:
                print(f"enemy({enemy}) from enemies_with_new_orientation is not in enemy_dictionary")
        self.mutex.lock()
        for enemy in enemies_to_be_removed:
            if enemy in self.enemy_dictionary:
                enemy_label = self.enemy_dictionary[enemy]
                enemy_label.hide()
                del self.enemy_dictionary[enemy]

                self.num_of_all_enemies -= 1
                self.change_enemies_left_signal.emit(self.num_of_all_enemies)
                print(f"enemyCallback(){self.num_of_all_enemies}")
                if self.num_of_all_enemies > 0:
                    self.addEnemy()
                elif self.num_of_all_enemies == -3:
                    self.advanceToNextLevel()
                
            else:
                print(f"enemy({enemy}) from enemies_to_be_removed is not in enemy_dictionary")

        for bullet in bullets_to_be_removed:
            bullet.bullet_owner.active_bullet = None
            if bullet in self.bullet_dictionary:
                bullet_label = self.bullet_dictionary[bullet]
                bullet_label.hide()
                del self.bullet_dictionary[bullet]
            else:
                print(f"bullet({bullet}) from bullets_to_be_removed is not in bullet_dictionary")
        self.mutex.unlock()
        self.update()
        
    def playerMoved(self, tank, transform):
        if tank.player_type == PlayerType.PLAYER_1:
            gb_player = self.player_1
            gb_player_label = self.player_1_label
        elif tank.player_type == PlayerType.PLAYER_2:
            gb_player = self.player_2
            gb_player_label = self.player_2_label

        pix = gb_player_label.pixmap()
        gb_player_label.setPixmap(pix.transformed(transform))
        #gb_player_label.setPixmap(gb_player.pix_map.transformed(transform))
        gb_player_label.orientation = gb_player.orientation

        self.setGameBoardLabelGeometry(gb_player_label, gb_player.x, gb_player.y)

    def bulletFired(self, bullet, transform):
        self.mutex.lock()
        self.bullet_dictionary[bullet] = QLabel(self)
        bullet_label = self.bullet_dictionary[bullet]
        self.mutex.unlock()

        bullet.pm_flying = bullet.pm_flying.scaled(self.getSquareWidth(), self.getSquareHeight())
        bullet_label.setPixmap(bullet.pm_flying.transformed(transform))

        self.setGameBoardLabelGeometry(bullet_label, bullet.x, bullet.y)
        bullet_label.orientation = bullet.orientation
        bullet_label.show()

    def bulletMoved(self, bullets_with_new_posiotion, bullets_to_be_removed, enemies_to_be_removed):

        for bullet in bullets_with_new_posiotion:
            if bullet in self.bullet_dictionary:
                bullet_label = self.bullet_dictionary[bullet]
                self.setGameBoardLabelGeometry(bullet_label, bullet.x, bullet.y)
            else:
                print(f"bullet({bullet}) from bullets_with_new_posiotion is not in bullet_dictionary")

                #if pocetna slicica:
                    #pix = self.bullet_dictionary[bullet].pixmap()
                    #self.bullet_dictionary[bullet].setPixmap(pix)

        self.mutex.lock()
        for bullet in bullets_to_be_removed:
            bullet.bullet_owner.active_bullet = None
            if bullet in self.bullet_dictionary:
                bullet_label = self.bullet_dictionary[bullet]
                bullet_label.hide()
                del self.bullet_dictionary[bullet]
            else:
                print(f"bullet({bullet}) from bullets_to_be_removed is not in bullet_dictionary")

        for enemy in enemies_to_be_removed:
            if enemy in self.enemy_dictionary:
                enemy_label = self.enemy_dictionary[enemy]
                enemy_label.hide()
                del self.enemy_dictionary[enemy]

                self.num_of_all_enemies -= 1
                print(f"BulletMoved(){self.num_of_all_enemies}")
                self.change_enemies_left_signal.emit(self.num_of_all_enemies)
                if self.num_of_all_enemies > 0:
                    self.addEnemy()
                elif self.num_of_all_enemies == -3:
                    #print(f"BulletMoved(){self.num_of_all_enemies}")
                    self.advanceToNextLevel()
            else:
                print(f"enemy({enemy}) from enemies_to_be_removed is not in enemy_dictionary")
        self.mutex.unlock()
        self.update()

    def communicationCallback(self):
        print("communicationCallback()")
    #endregion

    def drawSquare(self, painter, x, y, type):
        if type == ElementType.WALL:
            pix = QPixmap('./images/wall.jpg')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.BASE:
            pix = QPixmap('./images/lightning.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.LIFE:
            pix = QPixmap('./images/heart.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.FREEZE:
            pix = QPixmap('./images/freeze.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.PLAYER1 and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/tank1.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.PLAYER2 and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/tank2.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.ENEMY_UP and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/enemy0.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.ENEMY_RIGHT and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/enemy1.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.ENEMY_DOWN and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/enemy2.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.ENEMY_LEFT and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/enemy3.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.BULLET_UP and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/flying_bullet0.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.BULLET_RIGHT and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/flying_bullet1.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.BULLET_DOWN and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/flying_bullet2.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.BULLET_LEFT and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/flying_bullet3.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)

        elif type == ElementType.PLAYER1_UP and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/tank10.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.PLAYER1_RIGHT and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/tank11.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.PLAYER1_DOWN and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/tank12.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.PLAYER1_LEFT and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/tank13.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)

        elif type == ElementType.PLAYER2_UP and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/tank20.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.PLAYER2_RIGHT and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/tank21.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.PLAYER2_DOWN and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/tank22.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)
        elif type == ElementType.PLAYER2_LEFT and self.mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            pix = QPixmap('./images/tank23.png')
            pix1 = pix.scaled(self.getSquareWidth(), self.getSquareHeight())
            painter.drawPixmap(x + 1, y + 1, pix1)

    def setGameBoardLabelGeometry(self, label, x, y):
        rect = self.contentsRect()
        height = self.getSquareHeight()
        bottom = rect.bottom()
        board_top = rect.bottom() - GameBoard.BoardHeight * self.getSquareHeight()
        label.setGeometry(rect.left() + x * self.getSquareWidth(),
                          board_top + y * self.getSquareHeight(),
                          self.getSquareWidth(),
                          self.getSquareHeight())

    def gameOver(self):
        self.game_over_signal.emit()