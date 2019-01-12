from enum import IntEnum

#TODO: refaktorisati

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
    FREEZE = 8,
    ENEMY_UP = 9,
    ENEMY_RIGHT = 10,
    ENEMY_DOWN = 11,
    ENEMY_LEFT = 12,
    BULLET_UP = 13,
    BULLET_RIGHT = 14,
    BULLET_DOWN = 15,
    BULLET_LEFT = 16,
    PLAYER1_UP = 17,
    PLAYER1_RIGHT = 18,
    PLAYER1_DOWN = 19,
    PLAYER1_LEFT = 20,
    PLAYER2_UP = 21,
    PLAYER2_RIGHT = 22,
    PLAYER2_DOWN = 23,
    PLAYER2_LEFT = 24

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

class GameMode(IntEnum):
    SINGLEPLAYER = 1,
    MULTIPLAYER_OFFLINE = 2,
    MULTIPLAYER_ONLINE_HOST = 3,
    MULTIPLAYER_ONLINE_CLIENT = 4,