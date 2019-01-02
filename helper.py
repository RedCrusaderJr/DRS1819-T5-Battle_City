import game_board as gb
from enums import ElementType

class Helper:

    @staticmethod
    def rotationFunction(current_position, next_position):
        diff = int(current_position) - int(next_position)
        rotation_angle = 0 - diff * 90
        return rotation_angle

    @staticmethod
    def isCollision(parent_widget, new_x, new_y, element_type):
        parent_widget.mutex.lock()
        next_position_shape = parent_widget.getShapeType(new_x, new_y) #parent_widget.board[(new_y * gb.GameBoard.BoardWidth) + new_x]
        parent_widget.mutex.unlock()

        is_collision = True
        if (element_type is ElementType.PLAYER1) or (element_type is ElementType.PLAYER2) or (element_type is ElementType.ENEMY):
            if (new_x >= 0 and new_y >= 0) and ((next_position_shape is ElementType.NONE) or (next_position_shape is ElementType.BULLET)):
                is_collision = False

        elif element_type is ElementType.BULLET:
            if (new_x >= 0 and new_y >= 0) and (next_position_shape is ElementType.NONE):
                is_collision = False
            else:
                print("isCollision(bullet): True")

        return is_collision
