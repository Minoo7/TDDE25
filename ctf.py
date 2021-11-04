import pygame
from pygame.locals import *
from pygame.color import *
import pymunk

#eget:
import math

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

static_lines = [
    pymunk.Segment(space.static_body, (0, 0), (9, 0), 0.0),
    pymunk.Segment(space.static_body, (0, 0), (0, 9), 0.0),
    pymunk.Segment(space.static_body, (0, 9), (9, 9), 0.0),
    pymunk.Segment(space.static_body, (9, 0), (9, 9), 0.0),
]
for line in static_lines:
    line.elasticity = 0.95
    line.friction = 0.9
space.add(*static_lines)

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
#   List of all game objects
game_objects_list   = []
tanks_list          = []

#-- Resize the screen to the size of the current level
screen = pygame.display.set_mode(current_map.rect().size)

#<INSERT GENERATE BACKGROUND>
#-- Generate the background
background = pygame.Surface(screen.get_size())

#   Copy the grass tile all over the level area
for x in range(0, current_map.width):
    for y in range(0,  current_map.height):
        # The call to the function "blit" will copy the image
        # contained in "images.grass" into the "background"
        # image at the coordinates given as the second argument
        background.blit(images.grass,  (x*images.TILE_SIZE, y*images.TILE_SIZE))


#<INSERT CREATE BOXES>
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

#<INSERT CREATE TANKS>
#-- Create the tanks
# Loop over the starting poistion
for i in range(0, len(current_map.start_positions)):
    # Get the starting position of the tank "i"
    pos = current_map.start_positions[i]
    # Create the tank, images.tanks contains the image representing the tank
    tank = gameobjects.Tank(pos[0], pos[1], pos[2], images.tanks[i], space)
    # Add the tank to the list of tanks
    game_objects_list.append(tank)
    tanks_list.append(tank)

#<INSERT CREATE FLAG>
#-- Create the flag
flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
base = gameobjects.GameVisibleObject(tanks_list[0].start_position.x, tanks_list[0].start_position.y, images.bases[0])

game_objects_list.append(flag)
game_objects_list.append(base)

#----- Main Loop -----#

#-- Control whether the game run
running = True
skip_update = 0

while running:
    #-- Handle the events
    for event in pygame.event.get():
        # Check if we receive a QUIT event (for instance, if the user press the
        # close button of the wiendow) or if the user press the escape key.
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            running = False
            exit() #*
        if event.type == KEYDOWN:
            if event.key == K_w:
                tanks_list[0].accelerate()
            if event.key == K_s:
                tanks_list[0].decelerate()
            if event.key == K_d:
                tanks_list[0].turn_right()
            if event.key == K_a:
                tanks_list[0].turn_left()
            if event.key == K_SPACE:
                print("h")
                tanks_list[0].shoot()
            ##testkey:
            if event.key == K_x:
                #game_objects_list.append(tanks_list[0].shoot(space))
                #pre = pygame.time.get_ticks()
                bullet = gameobjects.Bullet(tanks_list[0].body.position[0], tanks_list[0].body.position[1], math.degrees(tanks_list[0].body.angle), images.bullet, space)
                game_objects_list.append(bullet)
                tanks_list[0].shoot(space, bullet)

        elif event.type == KEYUP:
            if event.key in (K_w, K_s):
                tanks_list[0].stop_moving()
            if event.key in (K_a, K_d):
                tanks_list[0].stop_turning()
            
    
    #-- Update physics
    if skip_update == 0:
        # Loop over all the game objects and update their speed in function of their
        # acceleration.
        for obj in game_objects_list:
            obj.update()
            #if obj is
            if type(obj) is gameobjects.Tank:
                obj.try_grab_flag(flag)
                if obj.has_won():
                    print("Vinst")
                    quit()
                
        skip_update = 2
    else:
        skip_update -= 1

    #   Check collisions and update the objects position
    space.step(1 / FRAMERATE)

    #   Update object that depends on an other object position (for instance a flag)
    for obj in game_objects_list:
        obj.post_update()

    #-- Update Display

    #<INSERT DISPLAY BACKGROUND>

    # Display the background on the screen
    screen.blit(background, (0, 0))

    #<INSERT DISPLAY OBJECTS>
    # Update the display of the game objects on the screen
    for obj in game_objects_list:
        obj.update_screen(screen)
    #   Redisplay the entire screen (see double buffer technique)
    pygame.display.flip()

    #   Control the game framerate
    clock.tick(FRAMERATE)
