import pygame
from pygame import time
from pygame.event import wait
from pygame.locals import *
from pygame.color import *
import pymunk

#eget:
import math
import argparse

# https://gitlab.liu.se/tdde25/ctf/-/wikis/Tutorial

#----- Initialisation -----#

#-- Initialise the display
pygame.init()
pygame.display.set_mode()

#-- Initialise the clock
clock = pygame.time.Clock()

#-- Initialise the physics engine
space = pymunk.Space()
space.gravity = (0.0,  0.0)
space.damping = 0.1 # Adds friction to the ground for all objects

#--defs
arb = pymunk.Arbiter

 
# Loading and playing background music:

pygame.mixer.music.load("background_music.mp3")
pygame.mixer.music.play(-1, 0.0)


#-- Import from the ctf framework
import ai

import images
import gameobjects
import maps

#-- Constants
FRAMERATE = 50

#-- Variables
#   Define the current level
current_map         = maps.map0

# Define flags from commandline

parser = argparse.ArgumentParser()
parser.add_argument('--hot-multiplayer', default=True, action='store_true') # GLöm inte ändra tillbaka till false
parser.add_argument('--singleplayer', default=False, action='store_true')
args = parser.parse_args()

# Intiliaze world border

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
#   List of all game objects
global game_objects_list
game_objects_list   = []
tanks_list          = []
ai_list = []

#-- Resize the screen to the size of the current level
screen = pygame.display.set_mode(current_map.rect().size)

#-- Generate the background
background = pygame.Surface(screen.get_size())

def grass_background():
    
    #   Copy the grass tile all over the level area
    for x in range(0, current_map.width):
        for y in range(0,  current_map.height):
            # The call to the function "blit" will copy the image
            # contained in "images.grass" into the "background"
            # image at the coordinates given as the second argument
            background.blit(images.grass,  (x*images.TILE_SIZE, y*images.TILE_SIZE))


def create_boxes():
    #-- Create the boxes
    for x in range(0, current_map.width):
        for y in range(0,  current_map.height):
            # Get the type of boxes
            box_type  = current_map.boxAt(x, y)
            # If the box type is not 0 (aka grass tile), create a box
            if(box_type != 0):
                # Create a "Box" using the box_type, aswell as the x,y coordinates,
                # and the pymunk space
                box = gameobjects.get_box_with_type(x, y, box_type, space)
                game_objects_list.append(box)

def create_tanks():
    #-- Create the tanks
    # Loop over the starting poistion
    for i in range(0, len(current_map.start_positions)):
        # Get the starting position of the tank "i"
        pos = current_map.start_positions[i]
        # Create the tank, images.tanks contains the image representing the tank
        tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[i], space)
        game_objects_list.append(tank)
        tanks_list.append(tank)
        if i > 0:
            tank_ai = ai.Ai(tank, game_objects_list, tanks_list, space, current_map)
            ai_list.append(tank_ai)




# Tank and bullet handler
def collision_bullet_tank(arb, space, data):
    
    tank = arb.shapes[0].parent
    bullet_shape = arb.shapes[1]
    if not tank.get_bullet() == bullet_shape.parent: # not shoot itself
        if not tank.respawning:
            tank.is_alive = False
            space.remove(bullet_shape, bullet_shape.body)

            explosion = gameobjects.Explosion(tank.x, tank.y)
            game_objects_list.append(explosion)
            explosion_sound = pygame.mixer.Sound("explosion_sound.wav")
            explosion_sound.play()

            if bullet_shape.parent in game_objects_list: # fix error
                game_objects_list.remove(bullet_shape.parent)
                #gameobjects.Explosion.explosion_remove(game_objects_list, explosion, pygame.time.get_ticks())
    return False

def collision_bullet_box(arb, space, data):
    box = arb.shapes[1].parent
    bullet_shape = arb.shapes[0]
    #print(box.get_type())
    if box.get_type():
        space.remove(box.shape, box.body)
        game_objects_list.remove(box)
    
    space.remove(bullet_shape, bullet_shape.body)
    if bullet_shape.parent in game_objects_list: # fixar error
        game_objects_list.remove(bullet_shape.parent)
        
        explosion_sound = pygame.mixer.Sound("explosion_sound.wav")
        explosion_sound.play()
    return False


#Handle the events
def event_handler(running):
    for event in pygame.event.get():
        # Check if we receive a QUIT event (for instance, if the user press the
        # close button of the wiendow) or if the user press the escape key.
        
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False
            exit() #*
        
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
                if event.key == K_x:
                    print(tanks_list[0].body.angle)
                    #ai_list[0].find_shortest_path()

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
                    victory_sound = pygame.mixer.Sound("victory_sound.wav")
                    victory_sound.play()
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
    #   Redisplay the entire screen (see double buffer technique)
    pygame.display.flip()

grass_background()
create_boxes()
create_tanks()

#-- Create the flag and the bases
flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
base = gameobjects.GameVisibleObject(tanks_list[0].start_position.x, tanks_list[0].start_position.y, images.bases[0])

game_objects_list.append(flag)
game_objects_list.append(base)

h_tank_bullet = space.add_collision_handler(1, 2)
h_tank_bullet.pre_solve = collision_bullet_tank

h_bullet_box = space.add_collision_handler(2, 3)
h_bullet_box.pre_solve = collision_bullet_box

#----- Main Loop -----#

#-- Control whether the game run
running = True
skip_update = 0

while running:
    
    event_handler(running)
    
    
    for tank_ai in ai_list:
        tank_ai.decide()
    
            
    physics_update(skip_update)
    object_update()
    display_update()




    #   Control the game framerate
    clock.tick(FRAMERATE)
