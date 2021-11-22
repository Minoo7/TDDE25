import pygame
import pymunk

pygame.init()
pygame.font.init()
screen = pygame.display.set_mode((0,0), pygame.FULLSCREEN)
pygame.display.set_caption('Main Menu')
clock = pygame.time.Clock()
width = maps.map0.width
def singleplayer():
    print("hej") # ändra
def multiplayer():
    print("då") # ändra
def create_button(x, y, width, height, hovercolor, defaultcolor):
    mouse = pygame.mouse.get_pos()
    # Mouse get pressed can run without an integer, but needs a 3 or 5 to indicate how many buttons
    click = pygame.mouse.get_pressed(3)
    if x + width > mouse[0] > x and y + height > mouse[1] > y:
        pygame.draw.rect(screen, hovercolor, (x, y, width, height))
        if click[0] == 1:
            return True
    else:
        pygame.draw.rect(screen, defaultcolor, (x, y, width, height))

screen = pygame.display.set_mode((500, 500)) 

font = pygame.font.SysFont('Times New Roman', 30)
slategrey = (112, 128, 144)
lightgrey = (165, 175, 185)
lighterblack = (10, 10, 10)
white = (255, 255, 255)
black = (0, 0, 0)
neongreen = (57, 255, 20)



#welcome = pygame.image.load(images.welcome)

def gameintro():
    screen.fill(neongreen)
    ctf = font.render('Capture The Flag', False, black)
    screen.blit(ctf, (100,100))
    running = True
    print("lol")
    while running:
        singleplayer_button = create_button(30, 250, 125, 26, black, white)
        multiplayer_button = create_button(30, 300, 125, 26, black, white)
        quit_button = create_button(30, 350, 125, 26, black, white)

        if singleplayer_button:
            singleplayer()
        if multiplayer_button:
            multiplayer()
        if quit_button:
            pygame.quit()
            quit()
        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                pygame.quit()
                quit()
        pygame.display.update()


        clock.tick(15)

while True:
    gameintro()
    pygame.display.update()

    clock.tick(15)

