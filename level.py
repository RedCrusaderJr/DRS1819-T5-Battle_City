"""
import os
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QPixmap


class myRect:
    def __init__(self, window, left, top, width, height, type):
        self.rectangle = QLabel(window)
        self.type = type
        self.pix_map = QPixmap()

        if self.type is Level.TILE_BRICK:
            self.pix_map = QPixmap('brick_wall.jpg')

        self.rectangle.setPixmap(self.pix_map)
        self.rectangle.setGeometry(left, top, width, height)


class LevelLoader:
    # tile constants
    (TILE_EMPTY, TILE_BRICK, TILE_STEEL, TILE_WATER, TILE_GRASS, TILE_FROZE) = range(6)

    # tile width/height in px
    TILE_SIZE = 16

    def __init__(self, window, level_nr=None):
        self.loadLevel(window, level_nr)

    def loadLevel(self, window, level_nr = 1):
            # Load specified level
            #@return boolean Whether level was loaded

            filename = "levels/"+str(level_nr)
            if not os.path.isfile(filename):
                return False
            level = []
            f = open(filename, "r")
            data = f.read().split("\n")
            self.mapr = []
            x, y = 0, 0
            for row in data:
                for ch in row:
                    if ch == "#":
                        self.mapr.append(myRect(window, x, y, self.TILE_SIZE, self.TILE_SIZE, self.TILE_BRICK))
                    x += self.TILE_SIZE
                x = 0
                y += self.TILE_SIZE
            return True
"""