from enums import GameMode, ElementType
import pickle
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QTransform, QPainter
from bullet import  Bullet
from tank import Tank
import struct
import socket
from communication import Communication


class CommunicationThread(QThread):
    player_move_signal = pyqtSignal(Tank, QTransform)
    bullet_fired_signal = pyqtSignal(Bullet, QTransform)
    bullets_move_signal = pyqtSignal(list, list, list)
    enemy_move_signal = pyqtSignal(list, list, list)
    update_signal = pyqtSignal()

    def __init__(self, parentQWidget = None):
        super(CommunicationThread, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.was_canceled = False
        self.iterator = 0

    def run(self):
        while not self.was_canceled:
            self.communication()

    def cancel(self):
        self.was_canceled = True

    def recv_msg(self):
        # Read message length and unpack it into an integer
        raw_msglen = self.recvall(self.parent_widget.socket, 4)
        if not raw_msglen:
            return None
        msglen = struct.unpack('>I', raw_msglen)[0]
        # Read the message data
        return self.recvall(self.parent_widget.socket, msglen)

    def recvall(self, sock, n):
        # Helper function to recv n bytes or return None if EOF is hit
        data = b''
        while len(data) < n:
            packet = sock.recv(n - len(data))
            if not packet:
                return None
            data += packet
        return data

    def communication(self):
        text = self.recv_msg()

        if text is None:
            self.parent_widget.socket.close()
            print("KRAJ")
            self.cancel()

        self.parent_widget.mutex.lock()
        if text is not None:
            id, data = pickle.loads(text)

            if id == "GAMEBOARD_INIT":
                self.parent_widget.clearBoard()
                self.parent_widget.board = data
                self.update_signal.emit()

            elif id == "UPDATE_ENEMY":
                self.parent_widget.board = data
                self.update_signal.emit()

            elif id == "UPDATE_BULLET":
                self.parent_widget.board = data
                self.update_signal.emit()

            elif id == "UPDATE_PLAYERS":
                self.parent_widget.clearBoard()
                self.parent_widget.board = data
                self.update_signal.emit()

            elif id == "WINNER":
                self.parent_widget.clearBoard()
                self.parent_widget.board = data[0]
                self.update_signal.emit()
                print("I WON")
                self.parent_widget.mutex.unlock()
                self.parent_widget.communnication.socket.shutdown(socket.SHUT_RDWR)
                self.parent_widget.communnication = Communication(GameMode.MULTIPLAYER_ONLINE_CLIENT, data[1])
                self.parent_widget.socket = self.parent_widget.communnication.socket
                self.parent_widget.mutex.lock()

            elif id == "LOSER":
                self.parent_widget.clearBoard()
                self.parent_widget.board = data
                self.update_signal.emit()
                print("I LOSE :(")

            elif id == "STATUS_UPDATE":
                if data[0] is not None:
                    self.parent_widget.change_lives_signal.emit(1, data[0])

                if data[1] is not None:
                    self.parent_widget.change_lives_signal.emit(2, data[1])

                if data[2] is not None:
                    self.parent_widget.change_enemies_left_signal.emit(data[2])

            elif id == "UPDATE_LEVEL":
                if data[0] is not None:
                    self.parent_widget.change_enemies_left_signal.emit(data[0])

                if data[1] is not None:
                    self.parent_widget.change_level_signal.emit()

            elif id == "PORT_INIT":
                self.parent_widget.communnication.socket.shutdown(socket.SHUT_RDWR)
                self.parent_widget.communnication = Communication(GameMode.MULTIPLAYER_ONLINE_CLIENT, data)
                self.parent_widget.socket = self.parent_widget.communnication.socket

        self.parent_widget.mutex.unlock()

