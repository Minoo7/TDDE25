"""File for ai class and functions"""
import math
from collections import deque
import pymunk
from pymunk import Vec2d
#from pymunk.query_info import SegmentQueryInfo #pylint: disable=unused-import
#from pymunk.shapes import Shape
import gameobjects

#pylint: disable= missing-function-docstring, invalid-name, no-self-use

# NOTE: use only 'map0' during development!

MIN_ANGLE_DIF = math.radians(3) # 3 degrees, a bit more than we can turn each tick

def angle_between_vectors(vec1, vec2):
    """ Since Vec2d operates in a cartesian coordinate space we have to
        convert the resulting vector to get the correct angle for our space.
    """
    vec = vec1 - vec2
    vec = vec.perpendicular()
    return vec.angle

def periodic_difference_of_angles(angle1, angle2):
    return  (angle1% (2*math.pi)) - (angle2% (2*math.pi))


class Ai:
    """ A simple ai that finds the shortest path to the target using
    a breadth first search. Also capable of shooting other tanks and or wooden
    boxes. """

    def __init__(self, tank,  game_objects_list, tanks_list, space, nodeentmap): #pylint: disable=too-many-arguments
        self.tank               = tank
        self.game_objects_list  = game_objects_list
        self.tanks_list         = tanks_list
        self.space              = space
        self.nodeentmap         = nodeentmap
        self.flag = None
        self.max_x = nodeentmap.width - 1
        self.max_y = nodeentmap.height - 1

        self.path = deque()
        self.move_cycle = self.move_cycle_gen()
        self.update_grid_pos()

        self.angle = 1
        self.pos = 0
        self.prev = 0
        self.metal = False

    def ray_cast(self):
        """Function for detecting ray cast for ai shoot function"""
        tank_pos = self.tank.body.position
        curr_map = self.nodeentmap
        angle = self.tank.body.angle + math.pi/2

        #Ray start
        x_start = 0.5 * math.cos(angle)
        y_start = 0.5 * math.sin(angle)

        ray_x_start = tank_pos[0] + x_start
        ray_y_start = tank_pos[1] + y_start

        ray_start = (ray_x_start, ray_y_start)

        #Ray end
        x_end = curr_map.width * math.cos(angle)
        y_end = curr_map.height * math.sin(angle)

        ray_x_end = tank_pos[0] + x_end
        ray_y_end = tank_pos[1] + y_end

        ray_end = (ray_x_end, ray_y_end)

        return self.space.segment_query_first(ray_start, ray_end, 0, pymunk.ShapeFilter())

    def update_grid_pos(self):
        """ This should only be called in the beginning, or at the end of a move_cycle. """
        self.grid_pos = self.get_tile_of_position(self.tank.body.position)

    def maybe_shoot(self, lst, time, space):
        """ Makes a raycast query in front of the tank. If another tank
            or a wooden box is found, then we shoot.
        """
        res = self.ray_cast()
        if hasattr(res, "shape"):
            col_type = res.shape.collision_type
            if col_type == 1 or \
            (col_type == 3 and res.shape.parent.destructable):
                self.tank.shoot(lst, time, space)

    def find_shortest_path(self):
        """ A simple Breadth First Search using integer coordinates as our nodes.
            Edges are calculated as we go, using an external function.
        """
        shortest_path = []
        spawn = self.grid_pos
        queue = deque()
        visited = set()
        path = {}

        queue.appendleft(spawn)
        visited.add(spawn.int_tuple)
        path[spawn.int_tuple] = []

        while queue:
            node = queue.popleft()
            if node == self.get_target_tile(): # our target (search is done)
                shortest_path = path[node.int_tuple]
                break
            for neighbour in self.get_tile_neighbors(node, self.metal):
                if not neighbour.int_tuple in visited:
                    queue.append(neighbour)
                    # (path to neighbour) = (path to previous pos) + (neighbour pos)
                    path[neighbour.int_tuple] = path[node.int_tuple] + [neighbour]

            visited.add(node.int_tuple)
        if not shortest_path:
            self.metal = True
        else:
            self.metal = False
            return deque(shortest_path)


    def turn(self):
        self.tank.stop_moving()
        if self.angle < -math.pi:
            self.tank.turn_left()
        elif 0 > self.angle > -math.pi:
            self.tank.turn_right()
        elif math.pi > self.angle > 0:
            self.tank.turn_left()
        else:
            self.tank.turn_right()

    def update_angle(self, coord):
        self.angle = periodic_difference_of_angles(self.tank.body.angle,
        angle_between_vectors(self.tank.body.position, coord + Vec2d(0.5, 0.5)))

    def correct_angle(self):
        if abs(self.angle) < MIN_ANGLE_DIF:
            self.tank.stop_turning()
            self.tank.accelerate()
            return True
        return False

    def correct_pos(self, next_coord):
        self.update_pos(next_coord)
        if self.pos > self.prev:
            self.update_grid_pos()
            self.prev = self.pos + 1
            return True
        self.prev = self.pos
        return False

    def update_pos(self, next_coord):
        self.pos = self.tank.body.position.get_distance(next_coord + Vec2d(0.5, 0.5))

    def move_cycle_gen(self):
        """ A generator that iteratively goes through all the required steps
            to move to our goal.
        """
        while True:
            path = self.find_shortest_path()
            if not path:
                # Start from the top of our cycle
                yield
                continue # Start from top
            next_coord = path.popleft()
            yield
            self.update_angle(next_coord)
            self.turn()
            while not self.correct_angle(): #while not correct_angle()
                self.update_angle(next_coord)
                yield
            self.update_pos(next_coord)
            self.prev = self.pos
            while not self.correct_pos(next_coord):
                yield

    def decide(self, lst, time, space):
        """ Main decision function that gets called on every tick of the game. """
        self.maybe_shoot(lst, time, space)
        if next(self.move_cycle, False) is False:
            pass

    def get_target_tile(self):
        """ Returns position of the flag if we don't have it. If we do have the flag,
            return the position of our home base.
        """
        if self.tank.flag is not None:
            x, y = self.tank.start_position
        else:
            self.get_flag() # Ensure that we have initialized it.
            x, y = self.flag.x, self.flag.y
        return Vec2d(int(x), int(y))

    def get_flag(self):
        """ This has to be called to get the flag, since we don't know
            where it is when the Ai object is initialized.
        """
        if self.flag is None:
        # Find the flag in the game objects list
            for obj in self.game_objects_list:
                if isinstance(obj, gameobjects.Flag):
                    self.flag = obj
                    break
        return self.flag

    def get_tile_of_position(self, position_vector):
        """ Converts and returns the float position of our tank to an integer position. """
        x, y = position_vector
        return Vec2d(int(x), int(y))

    def get_tile_neighbors(self, coord_vec, metal = None):
        """ Returns all bordering grid squares of the input coordinate.
            A bordering square is only considered accessible if it is grass
            or a wooden box.
        """
        neighbours = [] # Find the coordinates of the tiles' four neighbors
        neighbours.append(coord_vec + (0, 1)) # skriv om på snyggare sätt*
        neighbours.append(coord_vec + (-1, 0))
        neighbours.append(coord_vec + (0, -1))
        neighbours.append(coord_vec + (1, 0))

        if not metal:
            return filter(self.filter_tile_neighbours, neighbours)
        return filter(self.filter_tile_neighbours_metal, neighbours)

    def filter_tile_neighbours(self, coord, metal = None):
        tile = self.get_tile_of_position(coord)
        box_type = self.nodeentmap.boxAt

        if coord.x >= 0 and coord.x <= self.max_x and \
            coord.y >= 0 and coord.y <= self.max_y:
            if metal:
                if box_type(tile[0], tile[1]) != 1:
                    return True
            if (box_type(tile[0], tile[1]) == 0 or box_type(tile[0], tile[1]) == 2):
                return True
        return False

    def filter_tile_neighbours_metal(self, coord):
        return self.filter_tile_neighbours(coord, metal = True)

SimpleAi = Ai # Legacy
