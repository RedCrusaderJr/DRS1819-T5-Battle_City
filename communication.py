import socket
from enums import GameMode

class Communication:

    def __init__(self, mode):
        HOST = "localhost"
        PORT = 50005
        self.socket = None
        if mode is GameMode.MULTIPLAYER_ONLINE_HOST:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.bind((HOST, PORT))
            s.listen(True)
            self.socket = s
            self.conn, self.addr = self.socket.accept()

        elif mode is GameMode.MULTIPLAYER_ONLINE_CLINET:
            s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            s.connect((HOST, PORT))
            self.socket = s

    def closeCommunication(self):
        self.socket.close()