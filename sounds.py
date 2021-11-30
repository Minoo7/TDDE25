import pygame

def background_music():
    return
    pygame.mixer.music.load("data/audio/background_music.mp3")
    pygame.mixer.music.play(-1, 0.0)

def victory_sound():
    return
    victory_sound = pygame.mixer.Sound("data/audio/victory_sound.wav")
    victory_sound.play()

def explosion_sound():
    return
    explosion_sound = pygame.mixer.Sound("data/audio/explosion_sound.wav")
    explosion_sound.play()

def flag_sound():
    return
    flag_sound = pygame.mixer.Sound("data/audio/flag_sound.mp3")
    flag_sound.play()

def shoot_sound():
    return
    shoot_sound = pygame.mixer.Sound("data/audio/shoot_sound.mp3")
    shoot_sound.play()