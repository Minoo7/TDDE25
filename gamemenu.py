"""File for implementing gamemenu for the game"""
#pylint: disable=no-member, invalid-name, consider-using-sys-exit, redefined-outer-name, too-many-arguments
import pygame
import pymunk
import maps
import images
import gameobjects
#from pygame.constants import FULLSCREEN

#-- Start a screen
WIDTH = HEIGHT = 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))

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
    """ Creates the grass for maps"""
    #-- Scales down images
    scl = pygame.transform.scale(images.grass, (PREVIEW_TILE_SIZE, PREVIEW_TILE_SIZE))

    #-- Render grass over the preview maps
    for x in range(0, current_map.width):
        for y in range(0,  current_map.height):
            background.blit(scl,  (x*PREVIEW_TILE_SIZE, y*PREVIEW_TILE_SIZE))

def create_boxes(background, current_map):
    """ Creates the boxes for maps"""
    for x in range(0, current_map.width):
        for y in range(0,  current_map.height):
            # Get the type of boxes
            box_type  = current_map.boxAt(x, y)
            # If the box type is not 0 (aka grass tile), create a box
            if box_type != 0:
                # Create a "Box" using the box_type, aswell as the x,y coordinates,
                # and the pymunk space
                background.blit(pygame.transform.scale(
                        gameobjects.get_box_with_type(x, y, box_type, space1).sprite,
                        (PREVIEW_TILE_SIZE, PREVIEW_TILE_SIZE)),
                        (x*PREVIEW_TILE_SIZE, y*PREVIEW_TILE_SIZE))

def display_update(background, coordinates):
    """ Update Display (for maps) """
    screen.blit(background, coordinates)
    pygame.display.flip()

#-- Fonts
font = pygame.font.SysFont('Tahoma', 30, bold=True)
smallerfont = pygame.font.SysFont('Tahoma', 20)


#-- Colors
slategrey = (112, 128, 144)
white = (255, 255, 255)
black = (0, 0, 0)
navajowhite = (255, 222, 173)


#-- Button creater
def create_button(x, y, width, height, hovercolor, defaultcolor):
    """ Creates a button with ability to hover and press """
    # Gets mouse x and y pos
    mouse = pygame.mouse
    # Checks if a mouse gets pressed with 3 buttons instead of 5
    click = pygame.mouse.get_pressed(3)
    # Draws a button and checks if we interact with the button
    rect = pygame.Rect(x, y, width, height)
    if rect.collidepoint(mouse.get_pos()):
        pygame.draw.rect(screen, hovercolor, (x, y, width, height))
        if click[0]:
            return True
    else:
        pygame.draw.rect(screen, defaultcolor, (x, y, width, height))
        return (x, y)

def gamemode():
    """ Creates a meny for choosing what gamemode we are playing """
    #-- Background color
    screen.fill(navajowhite)

    #-- Render texts
    choose_mode_txt = font.render('Choose a gamemode', False, black)
    time_cond_txt = smallerfont.render('Time limit', False, black)
    score_cond_txt = smallerfont.render('Score limit', False, black)
    rounds_cond_txt = smallerfont.render('Rounds limit', False, black)
    quitgame = smallerfont.render('Quit!', False, black)

    #-- Center of screen
    center = WIDTH / 2

    #-- Position of buttons
    btns_pos = [(90, (90 + (150/2))), (285, (285 + (150/2))), (480, (480 + (150/2)))]

    run = True
    while run:
        #-- Creates buttons
        time_cond_button = create_button(btns_pos[0][0], 340, 150, 35, slategrey, white)
        score_cond_button = create_button(btns_pos[1][0], 340, 150, 35, slategrey, white)
        rounds_cond_button = create_button(btns_pos[2][0], 340, 150, 35, slategrey, white)
        quit_button = create_button(25, 670, 125, 26, slategrey, white)

        #-- Shows text on buttons
        screen.blit(choose_mode_txt, (center - (choose_mode_txt.get_rect().width / 2), 100))

        screen.blit(time_cond_txt, (btns_pos[0][1] - (time_cond_txt.get_rect().width / 2), 345))
        screen.blit(score_cond_txt, (btns_pos[1][1] - (score_cond_txt.get_rect().width / 2), 345))
        screen.blit(rounds_cond_txt, (btns_pos[2][1] - (rounds_cond_txt.get_rect().width / 2), 345))
        screen.blit(quitgame, (65, 670))

        #-- If a button gets clicked
        if time_cond_button is True:
            run = False
            return "time"
        if score_cond_button is True:
            run = False
            return "score"
        if rounds_cond_button is True:
            run = False
            return "rounds"
        if quit_button is True:
            pygame.quit()
            quit()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and \
                event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()

        #-- Updates the screen
        pygame.display.update()

        #-- Set tickrate
        clock.tick(50)

def mappicker():
    """ Let user pick what map they are playing with a rendered small variant of each map """
    #-- Background color
    screen.fill(navajowhite)

    #-- Render texts
    mappick = font.render('Choose a map', False, black)
    dust2_txt = smallerfont.render('Dust 2', False, black)
    tilted_towers_txt = smallerfont.render('Tilted Towers', False, black)
    cobblestone_txt = smallerfont.render('Dalaran Arena', False, black)
    quitgame = smallerfont.render('Quit!', False, black)

    #-- Gets center of screen
    center = WIDTH / 2

    #-- Fills all screens with background color to fix overlapping screens from going black
    background.fill(navajowhite)
    background1.fill(navajowhite)
    background2.fill(navajowhite)

    #-- Buttons position
    btns_pos = [(90, (90 + (150/2))), (285, (285 + (150/2))), (480, (480 + (150/2)))]

    #-- Render preview maps
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
        #-- Creates buttons
        dust2_button = create_button(btns_pos[0][0], 400, 150, 35, slategrey, white)
        tilted_towers_button = create_button(btns_pos[1][0], 400, 150, 35, slategrey, white)
        cobblestone_button = create_button(btns_pos[2][0], 400, 150, 35, slategrey, white)
        quit_button = create_button(25, 670, 125, 26, slategrey, white)

        #-- Shows text on buttons
        screen.blit(mappick, (center - (mappick.get_rect().width / 2), 100))

        screen.blit(dust2_txt, (btns_pos[0][1] -
        (dust2_txt.get_rect().width / 2), 405))
        screen.blit(tilted_towers_txt, (btns_pos[1][1] -
        (tilted_towers_txt.get_rect().width / 2), 405))
        screen.blit(cobblestone_txt, (btns_pos[2][1] -
        (cobblestone_txt.get_rect().width / 2), 405))
        screen.blit(quitgame, (65, 670))

        #-- If a button gets clicked
        if dust2_button is True:
            current_map = maps.choose_map("map0")
            running = False
            return current_map
        if tilted_towers_button is True:
            current_map = maps.choose_map("map1")
            running = False
            return current_map
        if cobblestone_button is True:
            current_map = maps.choose_map("map2")
            running = False
            return current_map
        if quit_button is True:
            pygame.quit()
            quit()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and \
                event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()
        #-- Updates screen
        pygame.display.update()

        #-- Set tickrate
        clock.tick(50)

def gameintro():
    """Function for gameintro, (first screen)"""
    #-- Background color
    screen.fill(navajowhite)

    #-- Render text
    ctf = font.render('Capture The Flag', False, black)
    multiplayertext = smallerfont.render('Multiplayer', False, black)
    singleplayertext = smallerfont.render('Singleplayer', False, black)
    quitgame = smallerfont.render('Quit!', False, black)

    #-- Gets center of screen
    center = WIDTH / 2

    running = True
    while running:
        #-- Creates button
        singleplayer_button = create_button(30, 250, 125, 27, slategrey, white)
        multiplayer_button = create_button(30, 300, 125, 27, slategrey, white)
        quit_button = create_button(30, 350, 125, 27, slategrey, white)

        #-- Puts text on buttons
        screen.blit(ctf, (center - (ctf.get_rect().width / 2), 100))
        screen.blit(singleplayertext, (35, 250))
        screen.blit(multiplayertext, (37, 300))
        screen.blit(quitgame, (75, 350))

        #-- If a buttons gets clicked
        if singleplayer_button is True:
            return 1
        if multiplayer_button is True:
            return 2
        if quit_button is True:
            pygame.quit()
            quit()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and \
                event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()

        #-- Updates screen
        pygame.display.update()

        #-- Set tickrate
        clock.tick(50)
