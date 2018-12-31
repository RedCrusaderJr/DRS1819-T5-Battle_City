import game_board as gb
from enums import ElementType

class Helper:

    @staticmethod
    def rotationFunction(current_position, next_position):
        diff = int(current_position) - int(next_position)
        rotation_angle = 0 - diff * 90
        return rotation_angle

    @staticmethod
    def isCollision(parent_widget, new_x, new_y):
        parent_widget.mutex.lock()
        next_position_shape = parent_widget.board[(new_y * gb.GameBoard.BoardWidth) + new_x]
        parent_widget.mutex.unlock()

        if (new_x >= 0 and new_y >= 0) and ((next_position_shape is ElementType.NONE) or (next_position_shape is ElementType.BULLET)):
            return False
        return True