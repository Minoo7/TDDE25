import math
import pymunk
from pymunk import Vec2d
import gameobjects
from collections import defaultdict, deque
#import copy

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

    def __init__(self, tank,  game_objects_list, tanks_list, space, nodeentmap):
        self.tank               = tank
        self.game_objects_list  = game_objects_list
        self.tanks_list         = tanks_list
        self.space              = space
        self.nodeentmap         = nodeentmap
        self.flag = None
        self.MAX_X = nodeentmap.width - 1 
        self.MAX_Y = nodeentmap.height - 1

        self.path = deque()
        self.move_cycle = self.move_cycle_gen()
        self.update_grid_pos()

        self.angle = 1
        self.pos = 0
        self.prev = 0

    def cartesian(self, pos):
        angle = self.tank.body.angle + math.pi/2

        x = math.cos(pos[0]) + angle
        y = math.sin(pos[1]) + angle
        #if angle < 0:
        #    x -= 0.5
        #else:
        #    x += 0.5
        #if angle < 0:
        #    y -= 0.5
        #else:
        #    y += 0.5
        #print(f"math.cos: {math.cos(pos[0])}")
        #print(f"angle: {angle}")
        return (x, y)
        #x += math.pi/2
        #y += math.pi/2


        #print(f"angle: {x*(180/math.pi)}, {y*(180/math.pi)}")

        #angle = self.tank.body.angle + math.pi/2
    
    def prnt_ang(self):
        print(f"angle: {self.tank.body.angle}")
        print(f"cartesian start: {self.cartesian(self.tank.body.position + (0.5, 0.5))}")
        print(f"cartesian end : {(self.nodeentmap.width, self.nodeentmap.height)}")
        res = self.ray_cast()
        print(f"res: {res}")
    
    def ray_cast(self):
        
        self.space.segment_query_first(self.cartesian(self.tank.body.position + (0.5, 0.5)),
        self.cartesian((self.nodeentmap.width, self.nodeentmap.height)),
        0, pymunk.ShapeFilter())

    def update_grid_pos(self):
        """ This should only be called in the beginning, or at the end of a move_cycle. """
        self.grid_pos = self.get_tile_of_position(self.tank.body.position)

    def maybe_shoot(self):
        """ Makes a raycast query in front of the tank. If another tank
            or a wooden box is found, then we shoot. 
        """
        #print(f"start: {self.cartesian(self.tank.body.position + (0.5, 0.5))}")
        #end = (self.nodeentmap.width, self.nodeentmap.height)
        #print(f"end: {self.cartesian(end)}")
        res = self.ray_cast()
        #print(f"res: {res}")
        return True
        #pass
        
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

        #while len(queue) > 0:
        while queue:
            node = queue.popleft()
            if node == self.get_target_tile(): # our target (search is done)
                shortest_path = path[node.int_tuple]
                break
            for neighbour in self.get_tile_neighbors(node):
                if not neighbour.int_tuple in visited:
                    queue.append(neighbour)
                    path[neighbour.int_tuple] = path[node.int_tuple] + [neighbour] # (path to neighbour) = (path to previous pos) + (neighbour pos) .copy()?

            visited.add(node.int_tuple)

        #print("\n shortestpath: ", shortest_path)
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
        
    def update_angle(self, next_coord):
        self.angle = periodic_difference_of_angles(self.tank.body.angle,
        angle_between_vectors(self.tank.body.position, next_coord + Vec2d(0.5, 0.5)))
    
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
            self.tank.stop_moving()
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
                #break # Start from the top of our cycle
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

    def decide(self):
        """ Main decision function that gets called on every tick of the game. """
        next(self.move_cycle)
        if self.maybe_shoot():
            return True
        return False

    def get_target_tile(self):
        """ Returns position of the flag if we don't have it. If we do have the flag,
            return the position of our home base.
        """
        if self.tank.flag != None:
            x, y = self.tank.start_position
        else:
            self.get_flag() # Ensure that we have initialized it.
            x, y = self.flag.x, self.flag.y
        return Vec2d(int(x), int(y))

    def get_flag(self):
        """ This has to be called to get the flag, since we don't know
            where it is when the Ai object is initialized.
        """
        if self.flag == None:
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

    def get_tile_neighbors(self, coord_vec):
        """ Returns all bordering grid squares of the input coordinate.
            A bordering square is only considered accessible if it is grass
            or a wooden box.
        """
        neighbours = [] # Find the coordinates of the tiles' four neighbors
        neighbours.append(coord_vec + (0, 1)) # skriv om på snyggare sätt*
        neighbours.append(coord_vec + (-1, 0))
        neighbours.append(coord_vec + (0, -1))
        neighbours.append(coord_vec + (1, 0))

        return filter(self.filter_tile_neighbors, neighbours)

    def filter_tile_neighbors(self, coord):
        tile = self.get_tile_of_position(coord)
        if coord.x >= 0 and coord.x <= self.MAX_X and \
            coord.y >= 0 and coord.y <= self.MAX_Y and \
                self.nodeentmap.boxAt(tile[0], tile[1]) == 0:
            return True
        return False

SimpleAi = Ai # Legacy