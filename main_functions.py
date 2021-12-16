"""Functions to be used by ctf"""
# pylint: disable=wrong-import-position, redefined-outer-name, unused-argument, consider-using-enumerate, unused-wildcard-import, wildcard-import, no-name-in-module, ungrouped-imports, no-member
import argparse
import pygame
from pygame.locals import *
from pygame.color import *
import pymunk

from pygame.constants import (
    QUIT, KEYUP, KEYDOWN, K_ESCAPE, K_SPACE, K_RETURN, K_w, K_a, K_s, K_d, K_UP, K_LEFT, K_DOWN,
    K_RIGHT
)

# ----- Initialisation ----- #

# -- Initialise the display
pygame.init()
pygame.display.set_mode()

# -- Import from the ctf framework
import ai
import sounds
import images
import gameobjects
import gamemenu

# -- Initialise the clock
clock = pygame.time.Clock()

# -- Initialise the physics engine
space = pymunk.Space()
space.gravity = (0.0,  0.0)
space.damping = 0.1  # Adds friction to the ground for all objects

# Loading and playing background music:
sounds.background_music()

# Sets a game caption
pygame.display.set_caption("Capture The Flag")

# -- Constants
FRAMERATE = 50

# -- Variables
arbiter = pymunk.Arbiter
score_dict = {}
rounds_played = 0
score_time_comp = 0

# Define flags from commandline deciding between multiplayer and singleplayer
parser = argparse.ArgumentParser()
parser.add_argument('--hot-multiplayer', default=False, action='store_true')
parser.add_argument('--singleplayer', default=False, action='store_true')
parser.add_argument('--time-condition', default=False, action='store_true')
parser.add_argument('--score-condition', default=False, action='store_true')
parser.add_argument('--rounds-condition', default=False, action='store_true')
args = parser.parse_args()


if not any([args.hot_multiplayer, args.singleplayer]):
    AMOUNT_PLAYERS = gamemenu.gameintro()
    if AMOUNT_PLAYERS == 1:
        args.singleplayer = True
    if AMOUNT_PLAYERS == 2:
        args.hot_multiplayer = True

singleplayer = args.singleplayer
multiplayer = args.hot_multiplayer

# Choose gamemode
if not any([args.time_condition, args.score_condition, args.rounds_condition]):
    GAMEMODE = gamemenu.gamemode()
    if GAMEMODE == "time":
        args.time_condition = True
    elif GAMEMODE == "score":
        args.score_condition = True
    elif GAMEMODE == "rounds":
        args.rounds_condition = True


# Define the current map by calling the gamemenu map-picker

current_map = gamemenu.mappicker()

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
game_objects_list = []
tanks_list = []
ai_list = []

# -- Set the screen to fullscreen

screen = pygame.display.set_mode((current_map.rect().size),
pygame.RESIZABLE)

# -- Generate the background
background = pygame.Surface(screen.get_size())

def score_board():
    """Function for showing player score board"""
    font = pygame.font.SysFont("Tahoma", 24)

    box_x = current_map.rect().size[0]//4
    box_w = current_map.rect().size[0]//2
    box_y = current_map.rect().size[1]//4
    box_h = current_map.rect().size[1]//2

    # Draws the base for the scoreboard
    rect_outer = (box_x, box_y, box_w, box_h)
    pygame.draw.rect(screen, (255, 255, 255), rect_outer)
    rect_inner = (box_x+5, box_y+5, box_w-10, box_h-10)
    pygame.draw.rect(screen, (0, 0, 0), rect_inner)

    str_start = box_y + 10

    # Draws the text for the players score
    for player in score_dict.items():
        score_str = f"Player {player[0]} : {player[1]}"
        board = font.render(f"{score_str}", False, (255, 255, 255))
        screen.blit(board, (box_w - (board.get_rect().width / 2),
                                 (str_start + (board.get_rect().height/len(score_dict)))))
        str_start += board.get_rect().height

    global score_time_comp
    score_time_comp += 3  # Compensates for the delay time
    pygame.display.flip()
    pygame.time.delay(3000)


def grass_background():
    """ Copy the grass tile all over the level area """
    for x in range(0, current_map.width):
        for y in range(0,  current_map.height):
            background.blit(images.grass,  (x*images.TILE_SIZE, y*images.TILE_SIZE))


def create_boxes():
    """ Create the boxes """
    for x in range(0, current_map.width):
        for y in range(0,  current_map.height):
            # Get the type of boxes
            box_type = current_map.boxAt(x, y)
            # If the box type is not 0 (aka grass tile), create a box
            if box_type != 0:
                # Create a "Box" using the box_type, aswell as the x,y coordinates,
                # and the pymunk space
                game_objects_list.append(gameobjects.get_box_with_type(x, y, box_type, space))


def create_tanks():
    """ Creates all tanks and puts them in their respective lists """

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
        base = gameobjects.GameVisibleObject(tanks_list[i].start_position.x,
        tanks_list[i].start_position.y, images.bases[i])
        game_objects_list.append(base)

        if (singleplayer and i > 0) or (multiplayer and i > 1):
            # Skapar ai-tanks
            tank_ai = ai.Ai(tank, game_objects_list, tanks_list, space, current_map)
            tank_ai.tank.bullet_speed *= 1.2
            tank_ai.tank.normal_max_speed *= 1.3
            ai_list.append(tank_ai)


def reset_game():
    """ Restarts game if a player acquires a point """

    sounds.victory_sound()

    for obj in game_objects_list[:]:
        if isinstance(obj, gameobjects.Tank):
            obj.reset_tank(current_map.flag_position)
        if isinstance(obj, gameobjects.Flag):
            obj.is_on_tank = False
            obj.x = current_map.flag_position[0]
            obj.y = current_map.flag_position[1]
        if isinstance(obj, gameobjects.Box):
            if obj.movable:
                space.remove(obj.body)
            space.remove(obj.shape)
            game_objects_list.remove(obj)
    for i in range(len(ai_list)):
        new_ai(i)

    create_boxes()

    for key, value in score_dict.items():
        print("Player", key, ' : ', value)
    score_board()


def collision_bullet_tank(arbiter, space, data):
    """ Handling collisions between tanks and bullets """
    tank = arbiter.shapes[0].parent
    bullet_shape = arbiter.shapes[1]
    if not tank.get_bullet() == bullet_shape.parent:  # Stops tank from shooting themselves
        if not tank.protection:
            if tank.hitpoints > 1:  # Changes the hitpoints of a tank when hit
                tank.hitpoints -= 1
            else:  # Removes the tank
                tank_explosion = gameobjects.Explosion(tank.body.position[0],
                tank.body.position[1],game_objects_list)
                game_objects_list.append(tank_explosion)
                sounds.explosion_sound()
                tank.alive = False
                tank.hitpoints = 2

            space.remove(bullet_shape, bullet_shape.body)

            if bullet_shape.parent in game_objects_list:  # Removes bullet from game_objects_list
                game_objects_list.remove(bullet_shape.parent)

    return False

def collision_bullet_box(arbiter, space, data):
    """ Handles collision between boxes and bullets """
    box = arbiter.shapes[1].parent
    bullet_shape = arbiter.shapes[0]
    if box.get_type():
        if box.hitpoints > 1:  # Changes the hitpoints of a box when hit
            box.hitpoints -= 1
        else:  # Removes the box
            space.remove(box.shape, box.body)
            game_objects_list.remove(box)
            box_explosion = gameobjects.Explosion(box.body.position[0],
                box.body.position[1], game_objects_list)
            game_objects_list.append(box_explosion)
            sounds.explosion_sound()

    space.remove(bullet_shape, bullet_shape.body)

    if bullet_shape.parent in game_objects_list:  # Removes bullet from game_objects_list
        game_objects_list.remove(bullet_shape.parent)

    return False


def event_handler():
    """ Handles keypresses and events """

    for event in pygame.event.get():

        # Closes game - ESC
        if event.type == QUIT or (event.type == KEYDOWN and event.key == K_ESCAPE):
            exit()

        # Player Controls
        if event.type == KEYDOWN:
            if singleplayer or multiplayer:
                if event.key == K_SPACE:
                    tanks_list[0].shoot(game_objects_list, pygame.time.get_ticks(), space)
                elif event.key in key_action:
                    key_action[event.key]()
                if event.key == K_RETURN:
                    tanks_list[1].shoot(game_objects_list, pygame.time.get_ticks(), space)

        if event.type == KEYUP:
            if event.key in key_action_up:
                key_action_up[event.key]()


def physics_update(skip_update):
    """Updating the physics"""
    if skip_update == 0:
        # Loop over all the game objects and update their speed in function of their
        # acceleration.
        for obj in game_objects_list:
            obj.update()
            if isinstance(obj, gameobjects.Tank):
                obj.try_grab_flag(flag)
                if obj.has_won():  # Checks if a tank has scored
                    global rounds_played
                    rounds_played += 1
                    obj.flag = None
                    obj.score += 1
                    score_dict[obj.player_number] = obj.score
                    reset_game()
                    win_conditions(obj)

        skip_update = 2
    else:
        skip_update -= 1


def win_conditions(obj = None):
    """Handles the win conditions score and rounds"""
    if (obj is not None and args.score_condition and obj.score == 5) \
       or (args.rounds_condition and rounds_played == 10):
        winning_screen()


def winning_screen():
    """Handles the displaying and calculating of the winning screen"""
    font = pygame.font.SysFont("Tahoma", 24)

    box_x = current_map.rect().size[0]/4 - 13
    box_y = current_map.rect().size[1]/4
    box_w = current_map.rect().size[0]/2 + 26
    box_h = current_map.rect().size[1]/2

    # Draws the base of the winning screen
    rect_outer = (box_x, box_y, box_w, box_h)
    pygame.draw.rect(screen, (255, 255, 255), rect_outer)
    rect_inner = (box_x+5, box_y+5, box_w-10, box_h-10)
    pygame.draw.rect(screen, (0, 0, 0), rect_inner)

    winning_player = 1
    winning_score = 0
    winning_list = []

    # Adds the highest scorer/scorers to a list
    for player in score_dict.items():
        if player[1] > winning_score:
            winning_player = player[0]
            winning_score = player[1]
            winning_list = []
        elif player[1] == winning_score:
            winning_list.append(player[0])
    if winning_player not in winning_list:
        winning_list.append(winning_player)

    # Handles if it is a win or a draw
    if len(winning_list) == 1:
        win_str = f"Player {winning_player} has won!"
    else:
        win_str = "It´s a draw!"

    # Adds the text on top of the winning screen
    win_board = font.render(f"{win_str}", False, (255, 255, 255))
    screen.blit(win_board, ((current_map.rect().size[0]/2 - win_board.get_rect().width / 2),
    (box_h - win_board.get_rect().height / 2)))

    pygame.display.flip()
    pygame.time.delay(5000)
    exit()


def show_clock():
    """
    Handles calculating and displaying the clock, as well as the
       time win_condition
    """
    font = pygame.font.SysFont("Tahoma", 24)
    time = (300000 - (pygame.time.get_ticks() - game_start_time)) // 1000 + score_time_comp
    mins = time // 60
    secs = time % 60

    # Checking if the time has reached 0, and then running the
    # winning screen
    if mins <= 0 and secs <= 0:
        winning_screen()
    if secs < 10:  # Adjusts the clock when the seconds reach single-digits
        secs = f"0{secs}"
    disp_clock = font.render(f"0{mins} : {secs}", False, (255, 255, 255))
    screen.blit(disp_clock, (current_map.rect().size[0] / 2 - (disp_clock.get_rect().width / 2), 0))

def new_ai(index):
    """Creates a new ai for a tank with a certain index"""
    ai_list[index] = ai.Ai(ai_list[index].tank, game_objects_list, tanks_list, space, current_map)

def object_update():
    """Updating the objects that depend on each other,
       as well as handling some ai functions"""
    # Check collisions and update the objects position
    space.step(1 / FRAMERATE)

    # Update object that depends on an other object position (for instance a flag)
    for obj in game_objects_list:
        obj.post_update(pygame.time.get_ticks())

    # Runs the decide function for every ai, as well as
    # handling the respawning of the tanks
    for i in enumerate(ai_list):
        if i[1].tank.respawn:
            i[1].tank.respawn = False
            new_ai(i[0])
        i[1].decide(game_objects_list, pygame.time.get_ticks(), space)

def display_update():
    """Updates display"""
    # Display the background on the screen
    screen.blit(background, (0, 0))
    # Update the display of the game objects on the screen
    for obj in game_objects_list:
        obj.update_screen(screen)
    if args.time_condition:  # Handles the time win-condition, as well as showing the clock
        show_clock()
    # Redisplay the entire screen (see double buffer technique)
    pygame.display.flip()


def __init__():
    """Initializing start-functions when starting the game"""
    global game_start_time
    game_start_time = pygame.time.get_ticks()  # Saving the time when the game starts

    # -- Create background, boxes and tanks
    grass_background()
    create_boxes()
    create_tanks()

    # Dictionaries for handling the inputs from the user
    global key_action
    global key_action_up
    key_action = {K_w: tanks_list[0].accelerate, K_s: tanks_list[0].decelerate,
                  K_a: tanks_list[0].turn_left, K_d: tanks_list[0].turn_right,
                  K_UP: tanks_list[1].accelerate, K_DOWN: tanks_list[1].decelerate,
                  K_LEFT: tanks_list[1].turn_left, K_RIGHT: tanks_list[1].turn_right}
    key_action_up = {K_w: tanks_list[0].stop_moving, K_s: tanks_list[0].stop_moving,
                     K_a: tanks_list[0].stop_turning, K_d: tanks_list[0].stop_turning,
                     K_UP: tanks_list[1].stop_moving, K_DOWN: tanks_list[1].stop_moving,
                     K_LEFT: tanks_list[1].stop_turning, K_RIGHT: tanks_list[1].stop_turning}

    # Method for splitting dictionary in half to prevent player 2 controls from controlling ai:
    if singleplayer:
        key_action = dict(list(key_action.items())[:len(key_action)//2:])
        key_action_up = dict(list(key_action_up.items())[:len(key_action_up)//2:])

    # -- Create the flag and the bases
    global flag
    flag = gameobjects.Flag(current_map.flag_position[0], current_map.flag_position[1])
    game_objects_list.append(flag)

    # -- Collision Handlers

    h_tank_bullet = space.add_collision_handler(1, 2)
    h_tank_bullet.pre_solve = collision_bullet_tank
    h_bullet_box = space.add_collision_handler(2, 3)
    h_bullet_box.pre_solve = collision_bullet_box
