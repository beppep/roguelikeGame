import pygame
import time
import random
import os
clock = pygame.time.Clock()
filepath="roguelikeGameFiles"
SOUND_PATH = os.path.join(filepath, "sounds")

def initSound():
    volume = 1
    pygame.font.init() # you have to call this at the start, 
                           # if you want to use this module.
    pygame.mixer.init(buffer=32)
    #Player.gameSound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "game.wav"))
    #Player.gameSound.set_volume(volume*0.5)
    
    #pygame.mixer.music.load(os.path.join(filepath, "music.wav")) #must be wav 16bit and stuff?
    #pygame.mixer.music.set_volume(volume*0.1)
    #pygame.mixer.music.play(-1)

def loadTexture(name, w,h=None, mirror=False):
    if not h:
        h=w
    image = pygame.image.load(os.path.join(filepath, "textures", name))
    image = pygame.transform.scale(image, (w, h))
    if mirror:
        return (pygame.transform.flip(image, True, False), image)
    else:
        return image

class Game():

    def __init__(self):
        self.player = Player(100,100)
        self.enemies = [Animus(500,200)]

    def update(self):
        for enemy in self.enemies:
            enemy.update()
        self.player.update()

    def findEnemies(self, x,y, r): #hitdetection (idk if aoe is necessary or wathever)
        targets = []
        for enemy in self.enemies:
            r = r+enemy.radius
            if (enemy.x-x)**2 + (enemy.y-y)**2 < r**2:
                targets.append(enemy)
        return targets


    def draw(self):
        gameDisplay.fill((100,100,100))
        for enemy in self.enemies:
            enemy.draw()
        self.player.draw()

class Player():

    radius = 20
    imageSize = 128
    idleImage = loadTexture("player/player.png", imageSize)
    walkImages = [loadTexture("player/walk1.png", imageSize), loadTexture("player/walk2.png", imageSize)]
    attackImage = loadTexture("player/strike.png", imageSize)
    rollImages = [loadTexture("player/roll1.png", imageSize), loadTexture("player/roll2.png", imageSize)]

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xdir = 0 #senaste man tittade
        self.ydir = 0
        self.state = 0 #0:idle, 1:atak, 2:roll, (hitstun??)
        self.stateTimer = 0
        self.image = self.idleImage
        self.movementspeed = 1


    def update(self):
        pressed = pygame.key.get_pressed()

        # IDLE
        if self.state == 0:
            dx = pressed[pygame.K_d] - pressed[pygame.K_a]
            dy = pressed[pygame.K_s] - pressed[pygame.K_w]
            if dx or dy:
                self.x += dx*self.movementspeed
                self.y += dy*self.movementspeed
                self.xdir = dx
                self.ydir = dy
                self.image = random.choice(self.walkImages+[self.idleImage])
            else:
                self.image = self.idleImage
            if pressed[pygame.K_SPACE]:
                self.state = 1
                self.stateTimer = 0
            if pressed[pygame.K_LSHIFT]:
                self.state = 2
                self.stateTimer = 0

        # ATAKK
        if self.state == 1:
            self.image = self.attackImage
            if self.stateTimer == 2:
                targets = game.findEnemies(self.x+self.xdir*10, self.y+self.ydir*10, 20)
                for target in targets:
                    target.hurt()

            self.stateTimer+=1
            if self.stateTimer>=40:
                self.state = 0

        # ROLL
        if self.state == 2:
            if self.stateTimer<20:
                self.image = random.choice(self.rollImages)
                self.x+=self.xdir*self.movementspeed*2
                self.y+=self.ydir*self.movementspeed*2
            else:
                self.image = self.rollImages[1]
            self.stateTimer+=1
            if self.stateTimer>=40:
                self.state = 0

    def draw(self):
        gameDisplay.blit(self.image, (int(self.x) - self.imageSize//2, int(self.y) - self.imageSize//2))
        pygame.draw.circle(gameDisplay, (100,100,200), (self.x, self.y), self.radius)
        pygame.draw.circle(gameDisplay, (200,100,100), (self.x+self.xdir*20, self.y+self.ydir*20), 20)
        


class Enemy():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = 0
        self.movementspeed = 1

    def update(self):
        if self.state == 0:
            dx = (self.x<game.player.x)*2 -1
            dy = (self.y<game.player.y)*2 -1
            if dx or dy:
                self.x += dx*self.movementspeed
                self.y += dy*self.movementspeed
                #self.image = random.choice(self.walkImages+[self.idleImage])
            else:
                pass
                #self.image = self.idleImage

    def draw(self):
        gameDisplay.blit(self.image, (int(self.x) - self.imageSize//2, int(self.y) - self.imageSize//2))
        pygame.draw.circle(gameDisplay, (100,100,200), (self.x, self.y), self.radius)

class Animus(Enemy):

    radius = 30
    imageSize = 64
    idleImage = loadTexture("enemies/animus.png", imageSize)

    def __init__(self, x, y):
        super(Animus, self).__init__(x,y)
        self.image = self.idleImage

    def hurt(self):
        game.enemies.remove(self)

gameDisplay = pygame.display.set_mode((1600, 900),)# pygame.FULLSCREEN)
pygame.display.set_caption("Roguelike Game")
#pygame.display.set_icon(pygame.image.load(os.path.join(filepath, "textures", "puncher", "idle.png")))

initSound()

game = Game()

jump_out = False
while jump_out == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jump_out = True

    game.update()
    game.draw()

    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
quit()
