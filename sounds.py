import pygame

def background_music():
    pygame.mixer.music.load("data/audio/background_music.wav")
    pygame.mixer.music.play(-1, 0.0)

def victory_sound():
    victory_sound = pygame.mixer.Sound("data/audio/victory_sound.wav")
    victory_sound.play()

def explosion_sound():
    explosion_sound = pygame.mixer.Sound("data/audio/explosion_sound.wav")
    explosion_sound.play()

def flag_sound():
    flag_sound = pygame.mixer.Sound("data/audio/flag_sound.wav")
    flag_sound.play()

def shoot_sound():
    shoot_sound = pygame.mixer.Sound("data/audio/shoot_sound.wav")
    shoot_sound.play()