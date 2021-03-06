import game_server_frame as gb
from enums import ElementType, Orientation

class Helper:

    @staticmethod
    def rotationFunction(current_position, next_position):
        diff = int(current_position) - int(next_position)
        rotation_angle = 0 - diff * 90
        return rotation_angle

    @staticmethod
    def isCollision(parent_widget, new_x, new_y, element_type):
        is_collision = True
        if 0 <= new_x <= parent_widget.BoardWidth - 1 and 0 <= new_y <= parent_widget.BoardHeight - 1:
            next_position_shape = parent_widget.getShapeType(new_x, new_y)

            if (element_type is ElementType.PLAYER1 or ElementType.PLAYER1_UP <= next_position_shape <= ElementType.PLAYER1_LEFT) or (element_type is ElementType.PLAYER2 or ElementType.PLAYER2_UP <= next_position_shape <= ElementType.PLAYER2_LEFT) or (element_type is ElementType.ENEMY or ElementType.ENEMY_UP <= next_position_shape <= ElementType.ENEMY_LEFT):
                #if (next_position_shape is ElementType.NONE) or (next_position_shape is ElementType.BULLET):
                if next_position_shape is ElementType.NONE:
                    is_collision = False

            elif element_type is ElementType.BULLET or (ElementType.BULLET_UP <= next_shape <= ElementType.BULLET_LEFT):
                if next_position_shape is ElementType.NONE:
                    is_collision = False
                    #print(f"Collision: bullet with {element_type}")

        return is_collision

    @staticmethod
    def enumFromOrientationBullet(orientation):
        if orientation == Orientation.UP:
            return ElementType.BULLET_UP
        elif orientation == Orientation.RIGHT:
            return ElementType.BULLET_RIGHT
        elif orientation == Orientation.DOWN:
            return ElementType.BULLET_DOWN
        else:
            return ElementType.BULLET_LEFT

    @staticmethod
    def enumFromOrientationEnemy(orientation):
        if orientation == Orientation.UP:
            return ElementType.ENEMY_UP
        elif orientation == Orientation.RIGHT:
            return ElementType.ENEMY_RIGHT
        elif orientation == Orientation.DOWN:
            return ElementType.ENEMY_DOWN
        else:
            return ElementType.ENEMY_LEFT

    @staticmethod
    def enumFromOrientationPlayer(player_type, orientation):
        if player_type == 1:
            if orientation == Orientation.UP:
                return ElementType.PLAYER1_UP
            elif orientation == Orientation.RIGHT:
                return ElementType.PLAYER1_RIGHT
            elif orientation == Orientation.DOWN:
                return ElementType.PLAYER1_DOWN
            else:
                return ElementType.PLAYER1_LEFT
        if player_type == 2:
            if orientation == Orientation.UP:
                return ElementType.PLAYER2_UP
            elif orientation == Orientation.RIGHT:
                return ElementType.PLAYER2_RIGHT
            elif orientation == Orientation.DOWN:
                return ElementType.PLAYER2_DOWN
            else:
                return ElementType.PLAYER2_LEFT