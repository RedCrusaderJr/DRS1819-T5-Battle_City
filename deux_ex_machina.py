from multiprocessing import Pipe, Process
from enums import ElementType
import random
import time

class DeuxExMachina(Process):

    def __init__(self, pipe: Pipe, boardWidth: int, boardHeight: int):
        super().__init__(target=self.__run__, args=[pipe])
        self.board_width = boardWidth
        self.board_height = boardHeight

    def __run__(self, pipe: Pipe):
        print("Process started")
        while True:
            time.sleep(random.randint(15, 31))
            rand_width = random.randint(0, self.board_width - 1)
            rand_height = random.randint(0, self.board_height - 1)
            rand_force = random.randint(ElementType.LIFE, ElementType.FREEZE)

            pipe.send((rand_width, rand_height, rand_force))
            print(f"Send: {rand_force}")