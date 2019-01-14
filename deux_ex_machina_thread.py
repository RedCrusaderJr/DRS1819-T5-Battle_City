from PyQt5.QtCore import QThread, Qt, pyqtSignal
import game_board as gb
from multiprocessing import Pipe
from enums import ElementType
import time
import struct
import socket
import pickle


class DeuxExMachinaThread(QThread):

    def __init__(self, parentQWidget = None, multiplayer = False):
        super(DeuxExMachinaThread, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.was_canceled = False
        self.multiplayer = multiplayer

    def run(self):
        while not self.was_canceled:
            self.readPipe()

    def cancel(self):
        self.was_canceled = True

    def readPipe(self):
        element = self.parent_widget.in_pipe.recv()
        self.parent_widget.mutex.lock()
        #print(f"Recv: {element[0]} {element[1]} {element[2]}")
        width = element[0]
        height = element[1]
        force = element[2]

        element_type = self.parent_widget.getShapeType(width, height)
        if element_type == ElementType.NONE:
            #if self.parent_widget.force_x is not None and self.parent_widget.force_y is not None:
            #   self.parent_widget.setShapeAt(self.parent_widget.force_x, self.parent_widget.force_y, ElementType.NONE)
            self.parent_widget.setShapeAt(width, height, force)
            self.parent_widget.force_x = width
            self.parent_widget.force_y = height
            if self.multiplayer:
                self.sendBoard()
            #print("Postavio")
            self.parent_widget.mutex.unlock()
            time.sleep(2)
            self.parent_widget.mutex.lock()
            #TODO: PROVERI STA JE TU
            shape = self.parent_widget.getShapeType(width, height)

            if (shape == ElementType.FREEZE) or (shape == ElementType.LIFE):    #player pokupio
                self.parent_widget.setShapeAt(width, height, ElementType.NONE)
                if self.multiplayer:
                    self.sendBoard()

        #else:
            #print("Zauzeto polje")
        self.parent_widget.mutex.unlock()

    def send_msg(self, sock, msg):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        try:
            sock.sendall(msg)
        except:
            return

    def sendBoard(self):
        id = "LEVEL_GAMEBOARD_INIT"
        data = pickle.dumps((id, self.parent_widget.board), -1)

        self.send_msg(self.parent_widget.communication.conn1, data)
        self.send_msg(self.parent_widget.communication.conn2, data)
