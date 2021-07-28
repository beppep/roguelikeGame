import pygame
import time
import random
import os
clock = pygame.time.Clock()
filepath="roguelikeGameFiles"
SOUND_PATH = os.path.join(filepath, "sounds")
SCALE

def initSound():
    State.volume = 1
    v=State.volume
    pygame.font.init() # you have to call this at the start, 
                           # if you want to use this module.
    pygame.mixer.init(buffer=32)
    #Player.gameSound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "game.wav"))
    #Player.gameSound.set_volume(v*0.5)
    
    #pygame.mixer.music.load(os.path.join(filepath, "music.wav")) #must be wav 16bit and stuff?
    #pygame.mixer.music.set_volume(v*0.1)
    #pygame.mixer.music.play(-1)

class Game():

    def __init__(self):
        self.player = Player()

class Player():

    def __init__(self, x, y, facingRight, controls, joystick=None):
        self.x = x
        self.y = y
        self.pressed = {"w":False,"a":False,"S":False,"d":False,}

    def getPressed(self, pressed):
        for i in ["w","a","s","d"]:
            self.pressed[i] = pressed[self.controls[i]]

    def load(playerName, textureName):
        image = pygame.image.load(os.path.join(filepath, "textures", playerName, textureName))
        image = pygame.transform.scale(image, (Player.SCALE*32, Player.SCALE*32))
        return (pygame.transform.flip(image, True, False), image)

    def draw(self):
        gameDisplay.blit(image, (int(self.x), int(self.y)))

gameDisplay = pygame.display.set_mode((1600, 900),)# pygame.FULLSCREEN)
pygame.display.set_caption("Roguelike Game")
#pygame.display.set_icon(pygame.image.load(os.path.join(filepath, "textures", "puncher", "idle.png")))

initSound()

jump_out = False
while State.jump_out == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            State.jump_out = True

    pygame.display.update()
    clock.tick(State.frameRate)
    
    
pygame.quit()
quit()
