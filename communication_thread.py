from enums import GameMode
import pickle
from PyQt5.QtCore import QThread, Qt, pyqtSignal
from PyQt5.QtGui import QTransform
from bullet import  Bullet
from tank import Tank

class CommunicationThread(QThread):
    player_move_signal = pyqtSignal(Tank, QTransform)
    bullet_fired_signal = pyqtSignal(Bullet, QTransform)
    bullets_move_signal = pyqtSignal(list, list, list)
    enemy_move_signal = pyqtSignal(list, list, list)

    def __init__(self, parentQWidget = None):
        super(CommunicationThread, self).__init__(parentQWidget)
        self.parent_widget = parentQWidget
        self.socket = self.parent_widget.socket
        self.was_canceled = False
        self.iterator = 0

    def run(self):
        while not self.was_canceled:
            self.communication()

    def cancel(self):
        self.was_canceled = True

    def communication(self):
        conn, addr = self.socket.accept()
        with conn:
            text = ""
            while True:
                bin = conn.recv(1024)
                self.parent_widget.mutex.lock()
                if not bin or len(bin) < 1024:
                    break

            id, data = pickle.loads(bin)

            if id is "ENEMY_MOVED":
                enemies_with_new_position, enemies_with_new_orientation, enemies_to_be_removed, bullets_to_be_removed = data
                self.enemyMove(enemies_with_new_position,
                               enemies_with_new_orientation,
                               enemies_to_be_removed,
                               bullets_to_be_removed)
                self.enemy_move_signal.emit(enemies_with_new_position,
                                            enemies_with_new_orientation,
                                            enemies_to_be_removed,
                                            bullets_to_be_removed)

            elif id is "PLAYER_MOVED":
                tank, transform = data
                self.playerMove(tank, transform)
                self.player_move_signal.emit(tank, transform)

            elif id is "BULLET_FIRED":
                bullet, transform = data
                self.bulletFired(bullet, transform)
                self.bullet_fired_signal.emit(bullet, transform)

            #TODO: PREBACITI NA BULLETS_MOVED!
            elif id is "BULLET_IMPACT":
                empty, bullets_to_be_removed, enemies_to_be_removed = data
                self.bulletImpact(empty, bullets_to_be_removed, enemies_to_be_removed)
                self.bullets_move_signal.emit(empty, bullets_to_be_removed, enemies_to_be_removed)

            elif id is "BULLETS_MOVED":
                bullets_with_new_position, bullets_to_be_removed, enemies_to_be_removed = data
                self.bulletsMove(bullets_with_new_position, bullets_to_be_removed, enemies_to_be_removed)
                self.bullets_move_signal.emit(bullets_with_new_position, bullets_to_be_removed, enemies_to_be_removed)

            self.parent_widget.mutex.unlock()
        print("out of with")

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