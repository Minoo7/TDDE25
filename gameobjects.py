"""File for gameobjects classes"""
#pylint: disable=no-self-use, invalid-name, unused-argument, no-member, too-many-arguments, attribute-defined-outside-init, c-extension-no-member, missing-function-docstring
import math
import copy
import pygame
import pymunk
import images
import sounds

DEBUG = False # Change this to set it in debug mode


def physics_to_display(x):
    """ This function is used to convert coordinates in the physic engine
        into the display coordinates """
    return x * images.TILE_SIZE


class GameObject:
    """ Mostly handles visual aspects (pygame) of an object.
        Subclasses need to implement two functions:
        - screen_position    that will return the position of the object on the screen
        - screen_orientation that will return how much the object
        is rotated on the screen (in degrees). """

    def __init__(self, sprite):
        self.sprite         = sprite


    def update(self):
        """ Placeholder, supposed to be implemented in a subclass.
            Should update the current state (after a tick) of the object."""
        return

    def post_update(self, time):
        """ Should be implemented in a subclass. Make updates that depend on
            other objects than itself."""
        return


    def update_screen(self, screen):
        """ Updates the visual part of the game. Should NOT need to be changed
            by a subclass."""
        sprite = self.sprite

        pos = self.screen_position() # Get the position of the object (pygame coordinates)
        sprite = pygame.transform.rotate(sprite,
                self.screen_orientation()) # Rotate the sprite using the rotation of the object

        # The position of the screen correspond to the center of the object,
        # but the function screen.blit expect to receive the top left corner
        # as argument, so we need to adjust the position p with an offset
        # which is the vector between the center of the sprite and the top left
        # corner of the sprite
        offset = pymunk.Vec2d(sprite.get_size()) / 2.
        pos -= offset
        screen.blit(sprite, pos) # Copy the sprite on the screen



class GamePhysicsObject(GameObject):
    """ This class extends GameObject and it is used for objects which have a
        physical shape (such as tanks and boxes). This class handle the physical
        interaction of the objects.
    """

    def __init__(self, x, y, orientation, sprite, space, movable):
        """ Takes as parameters the starting coordinate (x,y), the orientation, the sprite
            (aka the image representing the object), the physic engine object (space) and
            whether the object can be moved (movable).
        """

        super().__init__(sprite)

        # Half dimensions of the object converted from screen coordinates to physic coordinates
        half_width          = 0.5 * self.sprite.get_width() / images.TILE_SIZE
        half_height         = 0.5 * self.sprite.get_height() / images.TILE_SIZE

        # Physical objects have a rectangular shape,
        # the points correspond to the corners of that shape.
        points              = [[-half_width, -half_height],
                            [-half_width, half_height],
                            [half_width, half_height],
                            [half_width, -half_height]]
        self.points = points
        # Create a body (which is the physical representation of this game object
        # in the physic engine)
        if movable:
            # Create a movable object with some mass and moments
            # (considering the game is a top view game, with no gravity,
            # the mass is set to the same value for all objects)."""
            mass = 10
            moment = pymunk.moment_for_poly(mass, points)
            self.body         = pymunk.Body(mass, moment)
        else:
            # Create a non movable (static) object
            self.body = pymunk.Body(body_type=pymunk.Body.STATIC)

        self.body.position  = x, y
        # orientation is provided in degress, but pymunk expects radians.
        self.body.angle     = math.radians(orientation)
        # Create a polygon shape using the corner of the rectangle
        self.shape          = pymunk.Poly(self.body, points)
        self.shape.parent = self

        # Set some value for friction and elasticity,
        # which defines interraction in case of a colision
        #self.shape.friction = 0.5
        #self.shape.elasticity = 0.1

        # Add the object to the physic engine
        if movable:
            space.add(self.body, self.shape)
        else:
            space.add(self.shape)

    def screen_position(self):
        """ Converts the body's position in the physics engine to screen coordinates. """
        return physics_to_display(self.body.position)

    def screen_orientation(self):
        """ Angles are reversed from the engine to the display. """
        return -math.degrees(self.body.angle)

    def update_screen(self, screen):
        super().update_screen(screen)
        # debug draw
        if DEBUG:
            ps = [self.body.position+p for p in self.points]

            ps = [physics_to_display(p) for p in ps]
            ps += [ps[0]]
            pygame.draw.lines(screen, pygame.color.THECOLORS["red"], False, ps, 1)

def clamp(min_max, value):
    """ Convenient helper function to bound a value to a specific interval. """
    return min(max(-min_max, value), min_max)

class Tank(GamePhysicsObject):
    """ Extends GamePhysicsObject and handles aspects which are specific to our tanks. """

    # Constant values for the tank, acessed like: Tank.ACCELERATION
    # You can add more constants here if needed later
    ACCELERATION = 0.4

    def __init__(self, x, y, orientation, sprite, space):
        super().__init__(x, y, orientation, sprite, space, True)
        # Define variable used to apply motion to the tanks
        self.acceleration = 0 # 1 forward, 0 for stand still, -1 for backwards
        self.rotation = 0 # 1 clockwise, 0 for no rotation, -1 counter clockwise

        self.normal_max_speed = 2.0
        self.FLAG_MAX_SPEED = self.normal_max_speed * 0.5
        self.x = x
        self.y = y
        # This variable is used to access the flag object, if the current tank is carrying the flag
        self.flag               = None
        self.max_speed          = self.normal_max_speed   # Impose a maximum speed to the tank
        # Define the start pos, which is also the pos where the tank has to return with the flag
        self.start_position       = pymunk.Vec2d(x, y)
        self.shape.collision_type = 1                   # Define the collision type of the tank as 1

        #Eget:
        self.player_number = None
        self.bullet = None
        self.shooting = False
        self.timer = 0
        self.hitpoints = 2
        self.wins = 0
        self.score = 0
        self.bullet_speed = 2.0
        self.protection = False
        self.blink_count = 0
        self.protec_timer = 0
        self.respawn = False
        self.orientation = orientation
        self.alive = True

    def accelerate(self):
        """ Call this function to make the tank move forward. """
        self.acceleration = 1

    def stop_moving(self):
        """ Call this function to make the tank stop moving. """
        self.acceleration  = 0
        self.body.velocity = pymunk.Vec2d.zero()

    def decelerate(self):
        """ Call this function to make the tank move backward. """
        self.acceleration = -1

    def turn_left(self):
        """ Makes the tank turn left (counter clock-wise). """
        self.rotation = -1

    def turn_right(self):
        """ Makes the tank turn right (clock-wise). """
        self.rotation = 1

    def stop_turning(self):
        """ Call this function to make the tank stop turning. """
        self.rotation = 0
        self.body.angular_velocity = 0

    def update(self):
        """ A function to update the objects coordinates. Gets called at every tick of the game. """

        # Creates a vector in the direction we want accelerate / decelerate
        acc_vector = pymunk.Vec2d(0, self.ACCELERATION * self.acceleration).rotated(self.body.angle)
        # Applies the vector to our velocity
        self.body.velocity += acc_vector

        # Makes sure that we dont exceed our speed limit
        velocity = clamp(self.max_speed, self.body.velocity.length)
        self.body.velocity = pymunk.Vec2d(velocity, 0).rotated(self.body.velocity.angle)

        # Updates the rotation
        self.body.angular_velocity += self.rotation * self.ACCELERATION
        self.body.angular_velocity = clamp(self.max_speed, self.body.angular_velocity)

        if not self.alive:
            if self.flag is not None:
                if self.flag.is_on_tank is not None:
                    self.flag_pos = pymunk.Vec2d(self.flag.x, self.flag.y)
                    self.flag.is_on_tank = False
                    self.flag = None
            self.protection = True
            self.spawn_reset()
            self.respawn = True
            self.alive = True

    def spawn_reset(self):
        self.stop_moving()
        self.body.position = self.start_position
        self.body.angle     = math.radians(self.orientation)

    def reset_tank(self, flag_start):
        self.flag_pos = pymunk.Vec2d(flag_start[0], flag_start[1])
        if self.flag is not None:
            self.flag.is_on_tank = False
            self.flag = None
        self.spawn_reset()


    def post_update(self, time):
        if self.bullet is not None:
            self.bullet.x           = self.body.position[0]
            self.bullet.y           = self.body.position[1]
        # If the tank carries the flag, then update the positon of the flag
        if self.flag is not None:
            self.flag.x           = self.body.position[0]
            self.flag.y           = self.body.position[1]
            self.flag.orientation = -math.degrees(self.body.angle)
        # Else ensure that the tank has its normal max speed
        else:
            self.max_speed = self.normal_max_speed

        if self.protection:
            if (time - self.protec_timer) > 500:
                self.blink_count += 1
                alpha = self.sprite.get_alpha()
                if alpha in (200, 255):
                    val = 50
                elif alpha == 50:
                    val = 200
                self.sprite.set_alpha(val)
                self.protec_timer = time
            if self.blink_count > 6:
                self.blink_count = 0
                self.sprite.set_alpha(255)
                self.protec_timer = 0
                self.protection = False

    def try_grab_flag(self, flag):
        """ Call this function to try to grab the flag, if the flag is not on other tank
            and it is close to the current tank, then the current tank will grab the flag.
        """
        # Check that the flag is not on other tank
        if not flag.is_on_tank:
            # Check if the tank is close to the flag
            flag_pos = pymunk.Vec2d(flag.x, flag.y)
            if (flag_pos - self.body.position).length < 0.6:
                # Grab the flag !
                self.flag           = flag
                flag.is_on_tank     = True
                self.max_speed  = self.FLAG_MAX_SPEED
                sounds.flag_sound()

    def has_won(self):
        """ Check if the current tank has won (if the flag is picked up and at base position)"""
        self.wins += 1
        return self.flag is not None and (self.start_position - self.body.position).length < 0.2

    def shoot(self, lst, time, space):
        """ Function to shoot a bullet """
        if (time - self.timer) > 1000:
            self.timer = time
            bullet = Bullet(self.body.position[0], self.body.position[1],
                            math.degrees(self.body.angle), images.bullet, space, self.bullet_speed)
            bullet.is_shot          = True
            self.bullet             = bullet
            self.bullet.x           = self.body.position[0]
            self.bullet.y           = self.body.position[1]
            self.bullet.orientation = math.degrees(self.body.angle)
            lst.append(bullet)
            sounds.shoot_sound()

    def get_bullet(self):
        return self.bullet


class Box(GamePhysicsObject):
    """ This class extends the GamePhysicsObject to handle box objects. """

    def __init__(self, x, y, sprite, movable, space, destructable):
        """ It takes as arguments the coordinate of the starting position of the box (x,y)
        and the box model (boxmodel). """
        super().__init__(x, y, 0, sprite, space, movable)
        self.movable = movable
        self.destructable = destructable
        self.shape.collision_type = 3              #Define the collision type of the boxes as 3
        self.x = x
        self.y = y
        self.hitpoints = 2

    def get_type(self):
        return self.destructable

def get_box_with_type(x, y, b_type, space):
    (x, y) = (x + 0.5, y + 0.5) # Offsets the coordinate to the center of the tile
    if b_type == 1: # Creates a non-movable non-destructable rockbox
        return Box(x, y, images.rockbox, False, space, False)
    if b_type == 2: # Creates a movable destructable woodbox
        return Box(x, y, images.woodbox, True, space, True)
    if b_type == 3: # Creates a movable non-destructable metalbox
        return Box(x, y, images.metalbox, True, space, False)



class GameVisibleObject(GameObject):
    """ This class extends GameObject for object that are visible on screen
        but have no physical representation (bases and flag) """

    def __init__(self, x, y, sprite):
        """ It takes argument the coordinates (x,y) and the sprite. """
        self.x            = x
        self.y            = y
        self.orientation  = 0
        super().__init__(sprite)

    def screen_position(self):
        return physics_to_display(pymunk.Vec2d(self.x, self.y))

    def screen_orientation(self):
        return self.orientation


class Flag(GameVisibleObject):
    """ This class extends GameVisibleObject for representing flags."""

    def __init__(self, x, y):
        self.is_on_tank   = False
        super().__init__(x, y,  images.flag)

class Explosion(GameVisibleObject):
    """ This class extends GameVisibleObject for explosions."""

    def __init__(self, x, y, game_objects_list):
        super().__init__(x, y,  copy.copy(images.explosion))
        self.timer = 0
        self.opacity = 0
        self.game_objects_list = game_objects_list

    def post_update(self, time):
        if (time - self.timer) > 2000:
            self.sprite.set_alpha(self.sprite.get_alpha() - 10)
        if self.sprite.get_alpha() < 1: # if invisible
            self.timer = 0
            self.opacity = 0
            self.game_objects_list.remove(self)


class Bullet(GamePhysicsObject):
    """ This class is for bullets shot from a Tank."""

    def __init__(self, x, y, orientation, sprite, space, speed):
        super().__init__(x, y, orientation, sprite, space, True)
        # Define variable used to apply motion to the tanks
        self.acceleration = 10
        self.velocity = 10
        self.rotation = 0
        self.ACCELERATION = 0.4
        self.normal_max_speed = speed

        self.active = False
        self.max_speed        = 10.0
        self.shape.collision_type = 2  # Define the collision type of the bullet as 2

    def update(self):
        """ A function to update the objects coordinates. Gets called at every tick of the game. """

        # Creates a vector in the direction we want accelerate / decelerate
        acc_vector = pymunk.Vec2d(0, self.ACCELERATION * self.acceleration).rotated(self.body.angle)
        # Applies the vector to our velocity
        self.body.velocity += acc_vector
