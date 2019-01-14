import socket
from enums import GameMode
import struct
import pickle
import time

class Communication:

    def __init__(self, mode, port=50005, host_mode=1):
        HOST = ""
        CLIENT_HOST = "localhost"
        PORT = port
        self.socket = None
        self.conn = None
        if mode == GameMode.MULTIPLAYER_ONLINE_HOST:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.socket.bind((HOST, PORT))
            if PORT == 50005 and host_mode == 2:
                self.socket.listen(4)
                print("wait for accept")
                self.conn1, self.addr1 = self.socket.accept()
                print(f"client1 accepted -> address: {self.addr1}")
                data = pickle.dumps((str("PORT_INIT"), 50006), -1)
                self.send_msg(self.conn1, data)
                self.conn2, self.addr2 = self.socket.accept()
                print(f"client2 accepted -> address: {self.addr2}")
                data = pickle.dumps((str("PORT_INIT"), 50006), -1)
                self.send_msg(self.conn2, data)
                self.conn3, self.addr3 = self.socket.accept()
                print(f"client1 accepted -> address: {self.addr3}")
                data = pickle.dumps((str("PORT_INIT"), 50007), -1)
                self.send_msg(self.conn3, data)
                self.conn4, self.addr4 = self.socket.accept()
                print(f"client2 accepted -> address: {self.addr4}")
                data = pickle.dumps((str("PORT_INIT"), 50007), -1)
                self.send_msg(self.conn4, data)
            elif PORT == 50005 and host_mode == 1:
                self.socket.listen(2)
                print("wait for accept")
                self.conn1, self.addr1 = self.socket.accept()
                print(f"client1 accepted -> address: {self.addr1}")
                self.conn2, self.addr2 = self.socket.accept()
                print(f"client1 accepted -> address: {self.addr2}")
            else:
                self.socket.listen(2)
                print("wait for accept")
                self.conn1, self.addr1 = self.socket.accept()
                print(f"client1 accepted -> address: {self.addr1}")
                self.conn2, self.addr2 = self.socket.accept()
                print(f"client2 accepted -> address: {self.addr2}")

        elif mode is GameMode.MULTIPLAYER_ONLINE_CLIENT:
            while True:
                try:
                    self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self.socket.connect((CLIENT_HOST, PORT))
                    break
                except:
                    time.sleep(1)
                    continue

    def closeCommunication(self):
        self.socket.close()

    def send_msg(self, sock, msg):
        # Prefix each message with a 4-byte length (network byte order)
        msg = struct.pack('>I', len(msg)) + msg
        try:
            sock.sendall(msg)
        except:
            return
