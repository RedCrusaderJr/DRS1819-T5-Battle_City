import socket
from enums import GameMode

class Communication:

    def __init__(self, mode):
        HOST = ""
        CLIENT_HOST = "localhost"
        PORT = 50005
        self.socket = None
        self.conn = None
        if mode is GameMode.MULTIPLAYER_ONLINE_HOST:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((HOST, PORT))
            self.socket.listen(2)
            print("wait for accept")
            self.conn1, self.addr1 = self.socket.accept()
            print(f"client1 accepted -> address: {self.addr1}")
            self.conn2, self.addr2 = self.socket.accept()
            print(f"client2 accepted -> address: {self.addr2}")

        elif mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((CLIENT_HOST, PORT))

    def closeCommunication(self):
        self.socket.close()