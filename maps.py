"""Maps"""
import pygame
import images
#pylint: disable=eval-used, invalid-name, missing-function-docstring

class Map:
    """ An instance of Map is a blueprint for how the game map will look. """
    def __init__(self,  width,  height,  boxes,  start_positions, flag_position): #pylint: disable=too-many-arguments
        """ Takes as argument the size of the map (width, height), an array with the boxes type,
    the start position of tanks (start_positions) and the position of the flag (flag_position). """
        self.width              = width
        self.height             = height
        self.boxes              = boxes
        self.start_positions    = start_positions
        self.flag_position      = flag_position

    def rect(self):
        return pygame.Rect(0, 0, images.TILE_SIZE*self.width, images.TILE_SIZE*self.height)
    def boxAt(self, x, y):
        """ Return the type of the box at coordinates (x, y). """
        return self.boxes[y][x]


def choose_map(map_name):
    """ Loads in a map from a textfile """
    with open(f"data/maps/{map_name}.txt") as map_choice:
        map_list = []
        size = map_choice.readline().split(" ")
        width = eval(size[0])
        height = eval(size[1])
        for _ in range(height):
            map_list.append([eval(x) for x in map_choice.readline().strip().split(" ")])
        tank_start_pos = map_choice.readline().strip().split("#")
        for i in enumerate(tank_start_pos):
            tank_start_pos[i[0]] = eval(tank_start_pos[i[0]])
        flag_pos = map_choice.readline().strip().split("!")
        for i in enumerate(flag_pos):
            flag_pos[i[0]] = eval(flag_pos[i[0]])

        return Map(width, height, map_list, tank_start_pos, flag_pos)
