import pygame
from pygame.constants import FULLSCREEN
import pymunk

#Intiliaze game
pygame.init()
pygame.font.init()
pygame.display.set_caption('Main Menu')
clock = pygame.time.Clock()

#-- Fonts
font = pygame.font.SysFont('Tahoma', 30, bold=True)
smallerfont = pygame.font.SysFont('Tahoma', 20)
#font.Font.bold = 

#-- Colors
slategrey = (112, 128, 144)
lightgrey = (165, 175, 185)
lighterblack = (10, 10, 10)
white = (255, 255, 255)
black = (0, 0, 0)
neongreen = (57, 255, 20)
navajowhite = (255, 222, 173)

#-- Start a screen
width = height = 720
screen = pygame.display.set_mode((width, height))

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

def mappicker():
    screen.fill(navajowhite)

    mappick = font.render('Choose a map', False, black)
    play = smallerfont.render('Play!', False, black)
    quitgame = smallerfont.render('Quit!', False, black)
    tiltedtower = smallerfont.render('Tilted Towers', False, black)
    retailrow = smallerfont.render

    center = width / 2

    while True:
        start_button = create_button(30, 250, 125, 26, slategrey, white)
        quit_button = create_button(30, 300, 125, 26, slategrey, white)

        screen.blit(mappick, (center - (mappick.get_rect().width / 2), 100))
        screen.blit(play, (75, 250))
        screen.blit(quitgame, (75, 300))
        
        if start_button:
            pass
        if quit_button:
            pygame.quit()
            quit()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()
        pygame.display.update()


        clock.tick(10)

def gameintro():
    screen.fill(navajowhite)

    playerpicker = font.render('Capture The Flag', False, black)
    multiplayertext = smallerfont.render('Multiplayer', False, black)
    singleplayertext = smallerfont.render('Singleplayer', False, black)
    quitgame = smallerfont.render('Quit!', False, black)

    center = width / 2

    while True:
        singleplayer_button = create_button(30, 250, 125, 27, slategrey, white)
        multiplayer_button = create_button(30, 300, 125, 27, slategrey, white)
        quit_button = create_button(30, 350, 125, 27, slategrey, white)

        screen.blit(playerpicker, (center - (playerpicker.get_rect().width / 2), 100))
        screen.blit(singleplayertext, (35, 250))
        screen.blit(multiplayertext, (37, 300))
        screen.blit(quitgame, (75, 350))

        if singleplayer_button:
            mappicker()
        if multiplayer_button:
            mappicker()
        if quit_button:
            pygame.quit()
            quit()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()
        pygame.display.update()

        clock.tick(10)

gameintro()

