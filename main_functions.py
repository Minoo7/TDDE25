import pygame
from pygame.locals import *
from pygame.color import *
import pymunk

# import gamemenu Under konstruktion

# https://gitlab.liu.se/tdde25/ctf/-/wikis/Tutorial


# ----- Initialisation ----- #

# gamemenu.gameintro() #Under Konstruktion

# -- Initialise the display
pygame.init()
pygame.display.set_mode()

# -- Initialise the clock
clock = pygame.time.Clock()

# -- Initialise the physics engine
space = pymunk.Space()
space.gravity = (0.0,  0.0)
space.damping = 0.1 # Adds friction to the ground for all objects

# -- Import from the ctf framework
import ai
import sounds
import images
import gameobjects
import maps
import argparse

# Loading and playing background music:
sounds.background_music()

# Sets a game caption
pygame.display.set_caption("Capture The Flag")

# -- Constants
FRAMERATE = 50

# -- Variables
arb = pymunk.Arbiter
score_dict = {}

# Define the current level
current_map         = maps.map0

# Define flags from commandline deciding between multiplayer and singleplayer

parser = argparse.ArgumentParser()
parser.add_argument('--hot-multiplayer', default=False, action='store_true') # Justera False till True för enklare testning
parser.add_argument('--singleplayer', default=False, action='store_true')
args = parser.parse_args()

# Initialize world border

width = current_map.width
height = current_map.height
static_lines = [
    pymunk.Segment(space.static_body, (0, 0), (width, 0), 0.0),
    pymunk.Segment(space.static_body, (0, 0), (0, height), 0.0),
    pymunk.Segment(space.static_body, (0, height), (width, height), 0.0),
    pymunk.Segment(space.static_body, (width, 0), (width, height), 0.0),
]

for line in static_lines:
    line.elasticity = 0.95
    line.friction = 0.9
space.add(*static_lines)

# Lists for all game objects
global game_objects_list
game_objects_list   = []
tanks_list          = []
ai_list = []

# -- Resize the screen to a fullscreen

screen = pygame.display.set_mode((current_map.rect().size), pygame.RESIZABLE)

# screen = pygame.display.set_mode((current_map.rect().size), pygame.FULLSCREEN) # Under konstruktion
# gamemenu.gameintro() # Under konstruktion

# -- Generate the background
background = pygame.Surface(screen.get_size())

def grass_background():
    
    # Copy the grass tile all over the level area
    for x in range(0, current_map.width):
        for y in range(0,  current_map.height):
            background.blit(images.grass,  (x*images.TILE_SIZE, y*images.TILE_SIZE))

def create_boxes():
    # -- Create the boxes
    for x in range(0, current_map.width):
        for y in range(0,  current_map.height):
            # Get the type of boxes
            box_type  = current_map.boxAt(x, y)
            # If the box type is not 0 (aka grass tile), create a box
            if(box_type != 0):
                # Create a "Box" using the box_type, aswell as the x,y coordinates,
                # and the pymunk space

                #box = gameobjects.get_box_with_type(x, y, box_type, space)
                #game_objects_list.append(box)
                game_objects_list.append(gameobjects.get_box_with_type(x, y, box_type, space))


def create_tanks():
    """Skapar alla tanks och lägger in dem i respektive listor"""

    # Loop over the starting poistion
    for i in range(0, len(current_map.start_positions)):
        # Get the starting position of the tank "i"
        pos = current_map.start_positions[i]
        
        # Create the tanks and assign player number
        tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[i], space)
        game_objects_list.append(tank)
        tanks_list.append(tank)

        tank.player_number = i + 1
        score_dict[tank.player_number] = tank.score

        # Create the bases
        base = gameobjects.GameVisibleObject(tanks_list[i].start_position.x, tanks_list[i].start_position.y, images.bases[i])
        game_objects_list.append(base)

        if (args.singleplayer and i > 0) or (args.hot_multiplayer and i > 1): 
            # Skapar ai-tanks
            tank_ai = ai.Ai(tank, game_objects_list, tanks_list, space, current_map)
            tank_ai.tank.bullet_speed *= 1.2
            tank_ai.tank.NORMAL_MAX_SPEED *= 1.3
            ai_list.append(tank_ai)


def reset_game():
    """Startar om spelet när någon har fått en poäng"""

    sounds.victory_sound()

    for obj in game_objects_list[:]:
        if type(obj) is gameobjects.Tank:
            obj.reset_tank(current_map.flag_position)
        if type(obj) is gameobjects.Flag:
            obj.is_on_tank = False
            obj.x = current_map.flag_position[0]
            obj.y = current_map.flag_position[1]
        if type(obj) is gameobjects.Box:
            if obj.movable:
                space.remove(obj.body)
            space.remove(obj.shape)
            game_objects_list.remove(obj)
        if type(obj) is ai.Ai:
            game_objects_list[game_objects_list.index(obj)] = ai.Ai(obj.tank, game_objects_list, tanks_list, space, current_map)
    
    create_boxes()
    
    for key, value in score_dict.items():
        print("Player", key, ' : ', value)

def ai_decide():
    """Ai:n bestämmer vad den ska göra"""
    for i in range(len(ai_list)):
        #ai = ai_list[i] 
        if ai_list[i].tank.protection:
            ai_list[i] = ai.Ai(ai_list[i].tank, game_objects_list, tanks_list, space, current_map)
        ai_list[i].decide(game_objects_list, pygame.time.get_ticks(), space)

def collision_bullet_tank(arb, space, data):
    """Hanterar kollision mellan tank och bullet"""
    tank = arb.shapes[0].parent
    bullet_shape = arb.shapes[1]
    if not tank.get_bullet() == bullet_shape.parent: # Förhindar tanks från att skjuta sig själv
        if not tank.protection:
            if tank.hitpoints > 1:
                tank.hitpoints -= 1
            else:
                tank_explosion = gameobjects.Explosion(tank.body.position[0], tank.body.position[1])
                game_objects_list.append(tank_explosion)
                sounds.explosion_sound()
                tank.alive = False
                tank.hitpoints = 2

            space.remove(bullet_shape, bullet_shape.body)

            if bullet_shape.parent in game_objects_list: # fix error
                game_objects_list.remove(bullet_shape.parent)

    return False

def collision_bullet_box(arb, space, data):
    """Hanterar kollision mellan boxes och bullets"""
    box = arb.shapes[1].parent
    bullet_shape = arb.shapes[0]
    if box.get_type():
        if box.hitpoints > 1:
            box.hitpoints -= 1
        else:
            space.remove(box.shape, box.body)
            game_objects_list.remove(box)
            box_explosion = gameobjects.Explosion(box.body.position[0], box.body.position[1])
            game_objects_list.append(box_explosion)
            sounds.explosion_sound()

    space.remove(bullet_shape, bullet_shape.body)

    if bullet_shape.parent in game_objects_list: # fixar error
        game_objects_list.remove(bullet_shape.parent)

    return False

def event_handler(running):
    """Hanterar key-presses/events"""
    for event in pygame.event.get():
        
        # Stäng av spelet - ESC
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False
            exit() #*

        # Spelarnas kontroller
        if event.type == KEYDOWN:
            if args.singleplayer or args.hot_multiplayer:
                if event.key == K_w:
                    tanks_list[0].accelerate()
                if event.key == K_s:
                    tanks_list[0].decelerate()
                if event.key == K_a:
                    tanks_list[0].turn_left()
                if event.key == K_d:
                    tanks_list[0].turn_right()
                if event.key == K_SPACE:
                    tanks_list[0].shoot(game_objects_list, pygame.time.get_ticks(), space)
                
                if event.key == K_x: # Test key
                    print(ai_list[1].pt)
                    pass

            if args.hot_multiplayer:
                if event.key == K_UP:
                    tanks_list[1].accelerate()
                if event.key == K_DOWN:
                    tanks_list[1].decelerate()
                if event.key == K_LEFT:
                    tanks_list[1].turn_left()
                if event.key == K_RIGHT:
                    tanks_list[1].turn_right()
                if event.key == K_RETURN:
                    tanks_list[1].shoot(game_objects_list, pygame.time.get_ticks(), space)
 
        elif event.type == KEYUP:
            if args.singleplayer or args.hot_multiplayer:
                if event.key in (K_w, K_s):
                    tanks_list[0].stop_moving()
                if event.key in (K_a, K_d):
                    tanks_list[0].stop_turning()
                if args.hot_multiplayer:
                    if event.key in (K_UP, K_DOWN):
                        tanks_list[1].stop_moving()
                    if event.key in (K_LEFT, K_RIGHT):
                        tanks_list[1].stop_turning()

#-- Update physics
def physics_update(skip_update): #update
    if skip_update == 0:
        # Loop over all the game objects and update their speed in function of their
        # acceleration.
        for obj in game_objects_list:
            obj.update()
            if type(obj) is gameobjects.Tank:
                obj.try_grab_flag(flag)
                if obj.has_won():
                    obj.flag = None
                    obj.score += 1
                    score_dict[obj.player_number] = obj.score
                    reset_game()



        skip_update = 2
    else:
        skip_update -= 1

def object_update():
    #   Check collisions and update the objects position
    space.step(1 / FRAMERATE)
    #   Update object that depends on an other object position (for instance a flag)
    for obj in game_objects_list: # for timers
        obj.post_update(pygame.time.get_ticks())
        if type(obj) is gameobjects.Explosion:
            if not obj.active:
                game_objects_list.remove(obj)

def display_update():
    #-- Update Display
    # Display the background on the screen
    screen.blit(background, (0, 0))
    # Update the display of the game objects on the screen
    for obj in game_objects_list:
        obj.update_screen(screen)
    # Redisplay the entire screen (see double buffer technique)
    pygame.display.flip()

#-- Create background, boxes and tanks
grass_background()
create_boxes()
create_tanks()

#-- Create the flag and the bases
flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
game_objects_list.append(flag)

#-- Collision Handlers

h_tank_bullet = space.add_collision_handler(1, 2)
h_tank_bullet.pre_solve = collision_bullet_tank
h_bullet_box = space.add_collision_handler(2, 3)
h_bullet_box.pre_solve = collision_bullet_box