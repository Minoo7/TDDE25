import pygame
from pygame.constants import FULLSCREEN
import pymunk
import maps
import images
import gameobjects

#-- Start a screen
width = height = 720
screen = pygame.display.set_mode((width, height))

# CONSTANT
PREVIEW_TILE_SIZE = 10

# Intiliaze game
pygame.init()
pygame.font.init()
pygame.display.set_caption('Main Menu')
clock = pygame.time.Clock()

# Intiliaze objects for map preview
game_objects_list = []
space1 = pymunk.Space()

# Map creator
background = pygame.Surface(screen.get_size())
background1 = pygame.Surface(screen.get_size())
background2 = pygame.Surface(screen.get_size())

def grass_background(background, current_map):
    # Copy the grass tile all over the level area
    scl = pygame.transform.scale(images.grass, (PREVIEW_TILE_SIZE, PREVIEW_TILE_SIZE))
    for x in range(0, current_map.width):
        for y in range(0,  current_map.height):
            background.blit(scl,  (x*PREVIEW_TILE_SIZE, y*PREVIEW_TILE_SIZE))

def create_boxes(background, current_map):
    # -- Create the boxes
    for x in range(0, current_map.width):
        for y in range(0,  current_map.height):
            # Get the type of boxes
            box_type  = current_map.boxAt(x, y)
            # If the box type is not 0 (aka grass tile), create a box
            if box_type != 0:
                # Create a "Box" using the box_type, aswell as the x,y coordinates,
                # and the pymunk space
                background.blit(pygame.transform.scale(gameobjects.get_box_with_type(x, y, box_type, space1).sprite,
                (PREVIEW_TILE_SIZE, PREVIEW_TILE_SIZE)), (x*PREVIEW_TILE_SIZE, y*PREVIEW_TILE_SIZE))

def display_update(background, coordinates):
    #-- Update Display
    # Display the background on the screen
    screen.blit(background, coordinates)
    # Update the display of the game objects on the screen
    #for obj in game_objects_list:
    #    obj.update_screen(screen)
    # Redisplay the entire screen (see double buffer technique)
    pygame.display.flip()

#-- Fonts
font = pygame.font.SysFont('Tahoma', 30, bold=True)
smallerfont = pygame.font.SysFont('Tahoma', 20)


#-- Colors
slategrey = (112, 128, 144)
lightgrey = (165, 175, 185)
lighterblack = (10, 10, 10)
white = (255, 255, 255)
black = (0, 0, 0)
neongreen = (57, 255, 20)
navajowhite = (255, 222, 173)


#-- Button creater
def create_button(x, y, width, height, hovercolor, defaultcolor):
    """Creates a button with ability to hover and press"""
    # Gets mouse x and y pos
    mouse = pygame.mouse.get_pos()
    # Checks if a mouse gets pressed
    click = pygame.mouse.get_pressed(3)
    # Draws a button and checks if we interact with the button
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, hovercolor, (x, y, width, height))
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, defaultcolor, (x, y, width, height))
        return (x, y)

def gamemode():
    screen.fill(navajowhite)
    choose_mode_text = font.render('Choose a gamemode', False, black)
    time_condition_text = font.render('Time limit', False, black)
    score_condition_text = font.render('Score limit', False, black)
    rounds_condition_text = font.render('Rounds limit', False, black)
    quitgame = smallerfont.render('Quit!', False, black)

    center = width / 2

    btns_pos = [(90, (90 + (150/2))), (285, (285 + (150/2))), (480, (480 + (150/2)))]

    running = True
    while running:
        time_condition_button = create_button(btns_pos[0][0], 400, 150, 35, slategrey, white)
        score_condition_button = create_button(btns_pos[1][0], 400, 150, 35, slategrey, white)
        rounds_button = create_button(btns_pos[2][0], 400, 150, 35, slategrey, white)
        quit_button = create_button(25, 670, 125, 26, slategrey, white)

        screen.blit(choose_mode_text, (center - (choose_mode_text.get_rect().width / 2), 100))

        screen.blit(time_condition_text, (btns_pos[0][1] - (time_condition_text.get_rect().width / 2), 405))
        screen.blit(score_condition_text, (btns_pos[1][1] - (score_condition_text.get_rect().width / 2), 405))
        screen.blit(rounds_condition_text, (btns_pos[2][1] - (rounds_condition_text.get_rect().width / 2), 405))
        screen.blit(quitgame, (65, 670))

        if time_condition_button == True:
            gamemode = 1 
            running = False
            return gamemode
        if score_condition_button == True:
            gamemode = 2
            running = False
            return gamemode
        if rounds_button == True:
            gamemode = 3
            running = False
            return gamemode
        if quit_button == True:
            pygame.quit()
            quit()

def mappicker():
    screen.fill(navajowhite)
    mappick = font.render('Choose a map', False, black)
    dust2_text = smallerfont.render('Dust 2', False, black)
    tilted_towers_text = smallerfont.render('Tilted Towers', False, black)
    cobblestone_text = smallerfont.render('Dalaran Arena', False, black)
    quitgame = smallerfont.render('Quit!', False, black)

    center = width / 2

    background.fill(navajowhite)
    background1.fill(navajowhite)
    background2.fill(navajowhite)

    btns_pos = [(90, (90 + (150/2))), (285, (285 + (150/2))), (480, (480 + (150/2)))]

    grass_background(background, maps.choose_map("map0"))
    create_boxes(background, maps.choose_map("map0"))
    display_update(background, (btns_pos[0][1] - (90 / 2), 400 - 25 - 90)) #90

    grass_background(background1, maps.choose_map("map1"))
    create_boxes(background1, maps.choose_map("map1"))
    display_update(background1, (btns_pos[1][1] - (150 / 2), 400 - 25 - 110)) #110

    grass_background(background2, maps.choose_map("map2"))
    create_boxes(background2, maps.choose_map("map2"))
    display_update(background2, (btns_pos[2][1] - (100 / 2), 400 - 25 - 50)) #50

    
    
    running = True
    while running:
        dust2_button = create_button(btns_pos[0][0], 400, 150, 35, slategrey, white)
        tilted_towers_button = create_button(btns_pos[1][0], 400, 150, 35, slategrey, white)
        cobblestone_button = create_button(btns_pos[2][0], 400, 150, 35, slategrey, white)
        quit_button = create_button(25, 670, 125, 26, slategrey, white)

        screen.blit(mappick, (center - (mappick.get_rect().width / 2), 100))

        screen.blit(dust2_text, (btns_pos[0][1] - (dust2_text.get_rect().width / 2), 405))
        screen.blit(tilted_towers_text, (btns_pos[1][1] - (tilted_towers_text.get_rect().width / 2), 405))
        screen.blit(cobblestone_text, (btns_pos[2][1] - (cobblestone_text.get_rect().width / 2), 405))
        screen.blit(quitgame, (65, 670))

        if dust2_button == True:
            current_map = maps.choose_map("map0") 
            running = False
            return current_map
        if tilted_towers_button == True:
            current_map = maps.choose_map("map1") 
            running = False
            return current_map
        if cobblestone_button == True:
            current_map = maps.choose_map("map2") 
            running = False
            return current_map
        if quit_button == True:
            pygame.quit()
            quit()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()
        pygame.display.update()


        clock.tick(50)

def gameintro():
    screen.fill(navajowhite)

    ctf = font.render('Capture The Flag', False, black)
    multiplayertext = smallerfont.render('Multiplayer', False, black)
    singleplayertext = smallerfont.render('Singleplayer', False, black)
    quitgame = smallerfont.render('Quit!', False, black)

    center = width / 2

    running = True
    while running:
        singleplayer_button = create_button(30, 250, 125, 27, slategrey, white)
        multiplayer_button = create_button(30, 300, 125, 27, slategrey, white)
        quit_button = create_button(30, 350, 125, 27, slategrey, white)

        screen.blit(ctf, (center - (ctf.get_rect().width / 2), 100))
        screen.blit(singleplayertext, (35, 250))
        screen.blit(multiplayertext, (37, 300))
        screen.blit(quitgame, (75, 350))

        if singleplayer_button == True:
            gamemode = 1
            return gamemode
        if multiplayer_button == True:
            gamemode = 2
            return gamemode
        if quit_button == True:
            pygame.quit()
            quit()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()
        pygame.display.update()

        clock.tick(50)


