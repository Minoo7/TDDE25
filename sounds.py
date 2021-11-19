import pygame

def background_music():
    pygame.mixer.music.load("background_music.mp3")
    pygame.mixer.music.play(-1, 0.0)

def victory_sound():
    victory_sound = pygame.mixer.Sound("victory_sound.wav")
    victory_sound.play()

def explosion_sound():
    explosion_sound = pygame.mixer.Sound("explosion_sound.wav")
    explosion_sound.play()

def flag_sound():
    flag_sound = pygame.mixer.Sound("flag_sound.mp3")
    flag_sound.play()

def shoot_sound():
    shoot_sound = pygame.mixer.Sound("shoot_sound.mp3")
    shoot_sound.play()