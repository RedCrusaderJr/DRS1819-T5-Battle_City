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
        is_collision = True
        if 0 <= new_x <= parent_widget.BoardWidth - 1 and 0 <= new_y <= parent_widget.BoardHeight - 1:
            next_position_shape = parent_widget.getShapeType(new_x, new_y) #parent_widget.board[(new_y * gb.GameBoard.BoardWidth) + new_x]

            if (element_type is ElementType.PLAYER1) or (element_type is ElementType.PLAYER2) or (element_type is ElementType.ENEMY):
                #if (next_position_shape is ElementType.NONE) or (next_position_shape is ElementType.BULLET):
                if next_position_shape is ElementType.NONE:
                    is_collision = False

            elif element_type is ElementType.BULLET:
                if next_position_shape is ElementType.NONE:
                    is_collision = False
                    #print(f"Collision: bullet with {element_type}")

        return is_collision
