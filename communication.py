import socket
from enums import GameMode

class Communication:

    def __init__(self, mode):
        HOST = "147.91.160.149"
        PORT = 50005
        self.socket = None
        self.conn = None
        if mode is GameMode.MULTIPLAYER_ONLINE_HOST:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((HOST, PORT))
            self.socket.listen(1)
            print("wait for accept")
            self.conn, self.addr = self.socket.accept()
            print(f"client accepted -> address: {self.addr}")

        elif mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            print("Legen... wait for it...")
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.connect((HOST, PORT))
            print("...daryyyyyy!")

    def closeCommunication(self):
        self.socket.close()