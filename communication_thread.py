from enums import GameMode, ElementType
import pickle
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QTransform, QPainter
from bullet import  Bullet
from tank import Tank
import struct

class CommunicationThread(QThread):
    player_move_signal = pyqtSignal(Tank, QTransform)
    bullet_fired_signal = pyqtSignal(Bullet, QTransform)
    bullets_move_signal = pyqtSignal(list, list, list)
    enemy_move_signal = pyqtSignal(list, list, list)

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
        print("Dobio")

        self.parent_widget.mutex.lock()
        id, data = pickle.loads(text)

        if id == "GAMEBOARD_INIT":
            self.parent_widget.clearBoard()
            self.parent_widget.board = data
            self.parent_widget.update()

        elif id == "UPDATE_ENEMY":
            #self.parent_widget.clearBoard()
            self.parent_widget.board = data
            print(id)
            #if len(self.parent_widget.enemies_list) > 0:
            #    self.parent_widget.enemies_list.clear()
            self.parent_widget.update()
            #rect = self.parent_widget.contentsRect()
            #board_top = rect.bottom() - GameServerFrame.BoardHeight * self.parent_widget.getSquareHeight()
            #painter = QPainter(self.parent_widget)
            #for enemy in data[1]:
            #    self.parent_widget.drawSquare(painter,
            #                    enemy.x,
            #                    enemy.y,
            #                    ElementType.ENEMY,
            #                    enemy.direction)
        elif id == "UPDATE_BULLET":
            #self.parent_widget.clearBoard()
            self.parent_widget.board = data
            print(id)
            #if len(self.parent_widget.bullets_list) > 0:
            #    self.parent_widget.bullets_list.clear()
            self.parent_widget.update()

        elif id == "UPDATE_PLAYERS":
            self.parent_widget.clearBoard()
            self.parent_widget.board = data
            print(id)
            self.parent_widget.update()


        self.parent_widget.mutex.unlock()

    def enemyMoved(self, enemies_with_new_position, enemies_with_new_orientation, enemies_to_be_removed, bullets_to_be_removed):
        print("enemyMoved")

    def playerMoved(self, tank, transform):
        print("playerMoved")

    def bulletFired(self, bullet, transform):
        print("bulletFired")

    def bulletImpact(self, empty, bullets_to_be_removed, enemies_to_be_removed):
        print("bulletImpact")

    def bulletsMoved(self, bullets_with_new_position, bullets_to_be_removed, enemies_to_be_removed):
        print("bulletsMoved")