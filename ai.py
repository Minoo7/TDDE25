import math
import pymunk
from pymunk import Vec2d
import gameobjects
from collections import defaultdict, deque
import copy

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

    def __init__(self, tank,  game_objects_list, tanks_list, space, currentmap):
        self.tank               = tank
        self.game_objects_list  = game_objects_list
        self.tanks_list         = tanks_list
        self.space              = space
        self.currentmap         = currentmap
        self.flag = None
        self.MAX_X = currentmap.width - 1 
        self.MAX_Y = currentmap.height - 1

        self.path = deque()
        self.move_cycle = self.move_cycle_gen()
        self.update_grid_pos()

        

    def update_grid_pos(self):
        """ This should only be called in the beginning, or at the end of a move_cycle. """
        self.grid_pos = self.get_tile_of_position(self.tank.body.position)

    def maybe_shoot(self):
        """ Makes a raycast query in front of the tank. If another tank
            or a wooden box is found, then we shoot. 
        """
        pass # To be implemented
        
    def find_shortest_path(self):
        """ A simple Breadth First Search using integer coordinates as our nodes.
            Edges are calculated as we go, using an external function.
        """
        shortest_path = []
        #self.update_grid_pos() #to find the source of our search.
        #tile_neighbors = self.get_tile_neighbors(pos) #(that we implemented before) to find neighbors of a specific tile.
        init_pos = self.grid_pos
        queue = deque()
        queue.appendleft(init_pos)
        visited = set(init_pos.int_tuple)
        #visited = set()
        path = {}

        #while True:
        while len(queue) > 0:
            node = queue.popleft()
            if node == self.get_target_tile(): # our target (search is done)
                shortest_path = path[node]
                break
            for neighbour in self.get_tile_neighbors(node):
                if not neighbour.int_tuple in visited:
                    queue.appendleft(neighbour)
                    visited.add(neighbour.int_tuple)
                    #path[neighbour.int_tuple] = path[node.int_tuple].copy() + [neighbour]
                    print(f"node.int_tuple: {node.int_tuple}")
                    print(f"neighbour.int_tuple: {neighbour.int_tuple}")
                    print(f"node: {node}")
                    #print(path[node.int_tuple].copy())
                    #path[neighbour.int_tuple] = path[node.int_tuple].copy() + node
                    #path[neighbour.int_tuple] = neighbour + path[node.int_tuple]

        print("shortestpath: ", shortest_path)
        return deque(shortest_path)

    def turn(self, angle):
        self.stop_moving()
        if angle < 0:
            self.turn_right()
        else:
            self.turn_left()
    
    def correct_angle(self):
        self.angle = self.periodic_difference_of_angles(self.body, self.temp)
        if -MIN_ANGLE_DIF < self.angle and self.angle < MIN_ANGLE_DIF:
            return True
        else:
            return False
    
    def move_cycle_gen(self):
        """ A generator that iteratively goes through all the required steps
            to move to our goal.
        """ 
        #print(self.find_shortest_path())
        while True:
            path = self.find_shortest_path()
            if not path:
                #break # Start from the top of our cycle
                yield
                continue # Start from top
            next_coord = path.popleft()
            yield
            #turn
            self.temp = self.angle_between_vectors(self.body, next_coord)
            self.angle = self.periodic_difference_of_angles(self.body, self.temp)
            self.turn(self.angle)
            while not self.correct_angle(): #while not correct_angle()
                yield

            self.stop_turning()

            while True: 
                
                middle_next = next_coord + Vec2d(0.5, 0.5) # ---------------- Kan vara fel -               
                
                if not last_dist:
                    last_dist = self.tank.body.position.get_distance(middle_next)

                current_dist = self.tank.body.position.get_distance(middle_next)
                if current_dist > last_dist:
                    self.update_grid_pos()
                    break
                else:
                    self.tank.accelerate()
                    last_dist = current_dist
            

    
    def decide(self):
        """ Main decision function that gets called on every tick of the game. """
        move_cycle = self.move_cycle_gen()
        #self.maybe_shoot()
        next(move_cycle)
        #self.move_cycle_gen()

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
        #pos = self.get_tile_of_position(coord_vec)
        neighbours.append(coord_vec + (0, 1)) # skriv om på snyggare sätt*
        neighbours.append(coord_vec + (-1, 0))
        neighbours.append(coord_vec + (0, -1))
        neighbours.append(coord_vec + (1, 0))
        return filter(self.filter_tile_neighbors, neighbours)

    def filter_tile_neighbors(self, coord):
        tile = self.get_tile_of_position(coord)
        if 0 < coord.x and coord.x <= self.MAX_X and \
            0 < coord.y and coord.y <= self.MAX_Y and \
                self.currentmap.boxAt(tile[0], tile[1]) == 0:
            return True
        return False

SimpleAi = Ai # Legacy