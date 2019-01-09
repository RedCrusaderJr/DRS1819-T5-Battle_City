from enum import IntEnum

class PlayerType(IntEnum):
    PLAYER_1 = 1
    PLAYER_2 = 2


class ElementType(IntEnum):
    NONE = 0,
    PLAYER1 = 1,
    PLAYER2 = 2,
    ENEMY = 3,
    WALL = 4,
    BULLET = 5,
    BASE = 6,
    LIFE = 7,
    FREEZE = 8


class WallType(IntEnum):
    TILE_EMPTY = 0,
    TILE_BRICK = 1,
    TILE_STEEL = 2,
    TILE_WATER = 3,
    TILE_GRASS = 4,
    TILE_FROZE = 5,


class Orientation(IntEnum):
    UP = 0,
    RIGHT = 1,
    DOWN = 2,
    LEFT = 3,

class BulletType(IntEnum):
    FRIEND = 0,
    ENEMY = 1,