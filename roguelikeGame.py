import pygame
import time
import random
import os
import math

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

def blitRotate(surf,image, pos, originPos, angle):

    #ifx rad ddeg
    angle = -angle*180/math.pi

    # calcaulate the axis aligned bounding box of the rotated image
    w, h       = image.get_size()
    box        = [pygame.math.Vector2(p) for p in [(0, 0), (w, 0), (w, -h), (0, -h)]]
    box_rotate = [p.rotate(angle) for p in box]
    min_box    = (min(box_rotate, key=lambda p: p[0])[0], min(box_rotate, key=lambda p: p[1])[1])
    max_box    = (max(box_rotate, key=lambda p: p[0])[0], max(box_rotate, key=lambda p: p[1])[1])

    # calculate the translation of the pivot 
    pivot        = pygame.math.Vector2(originPos[0], -originPos[1])
    pivot_rotate = pivot.rotate(angle)
    pivot_move   = pivot_rotate - pivot

    # calculate the upper left origin of the rotated image
    origin = (int(pos[0] - originPos[0] + min_box[0] - pivot_move[0]), int(pos[1] - originPos[1] - max_box[1] + pivot_move[1]))

    # get a rotated image
    rotated_image = pygame.transform.rotate(image, angle+180)
    surf.blit(rotated_image, origin)

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
        self.enemies = []#Animus(500,200)]
        self.items = []

    def update(self):
        for item in self.items:
            item.update()
        for enemy in self.enemies:
            enemy.update()
        self.player.update()
        if random.random()<0.005:
            self.enemies.append(random.choice([Animus,Pufferfish,Robot])(random.random()*1000, 700))
        if random.random()<0.002:
            self.items.append(random.choice([Fruit,Stick,Fan,Heart])(random.random()*1000, 500))

    def findEnemies(self, x,y, r): #hitdetection (idk if aoe is necessary or wathever)
        targets = []
        for enemy in self.enemies:
            d = r+enemy.radius
            if (enemy.x-x)**2 + (enemy.y-y)**2 < d**2:
                targets.append(enemy)
        return targets

    def findPlayer(self, x,y, r):
        if (self.player.state==2 and self.player.stateTimer<20):
            return 0
        r = r+self.player.radius
        if (self.player.x-x)**2 + (self.player.y-y)**2 < r**2:
            return self.player
        return 0

    def draw(self):
        gameDisplay.fill((100,100,100))
        for i in range(self.player.hp):
            pygame.draw.rect(gameDisplay, (200,0,0),(50+20*i,30,16,16),0)
        for item in self.items:
            item.draw()
        for enemy in self.enemies:
            enemy.draw()
        self.player.draw()

class Player():

    radius = 20
    imageSize = 128
    idleImage = loadTexture("player/player.png", imageSize)
    hurtImage = loadTexture("player/hurt.png", imageSize)
    walkImages = [loadTexture("player/walk1.png", imageSize), loadTexture("player/walk2.png", imageSize)]
    attackImages = [loadTexture("player/strike1.png", imageSize), loadTexture("player/strike2.png", imageSize)]
    rollImages = [loadTexture("player/roll1.png", imageSize), loadTexture("player/roll2.png", imageSize)]

    swipeImage = loadTexture("player/swipe.png", imageSize)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xdir = 0 #senaste man tittade
        self.ydir = 0
        self.hp = 3
        self.state = 0 #0:idle, 1:atak, 2:roll, (hitstun??)
        self.stateTimer = 0
        self.image = self.idleImage
        self.movementSpeed = 1
        self.rollSpeed = 4
        self.fanRoll = 0 #3?
        self.swipeRange = 20

    def update(self):
        pressed = pygame.key.get_pressed()

        # IDLE
        if self.state == 0:
            dx = pressed[pygame.K_d] - pressed[pygame.K_a]
            dy = pressed[pygame.K_s] - pressed[pygame.K_w]
            if dx or dy:
                self.x += dx*self.movementSpeed
                self.y += dy*self.movementSpeed
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

        # HURT
        if self.state == -1:
            self.stateTimer+=1
            if self.stateTimer>=10:
                if self.hp <= 0:
                    global jump_out
                    jump_out = True
                else:
                    self.image = self.idleImage
                    self.state = 0

        # ATAKK
        if self.state == 1:
            if self.stateTimer<10:
                self.image = self.attackImages[0]
            elif self.stateTimer == 10:
                targets = game.findEnemies(self.x+self.xdir*self.swipeRange, self.y+self.ydir*self.swipeRange, 30)
                for target in targets:
                    target.hurt()
            else:
                self.image = self.attackImages[1]

            self.stateTimer+=1
            if self.stateTimer>=30:
                self.state = 0

        # ROLL
        if self.state == 2:
            if self.stateTimer<20:
                self.image = random.choice(self.rollImages)
                self.x+=self.xdir*self.rollSpeed#*self.movementSpeed
                self.y+=self.ydir*self.rollSpeed#*self.movementSpeed
                # fanRoll
                targets = game.findEnemies(self.x,self.y,self.radius)
                for target in targets:
                    target.x+=self.xdir*self.fanRoll
                    target.y+=self.ydir*self.fanRoll
            else:
                self.image = self.rollImages[0]
            self.stateTimer+=1
            if self.stateTimer>=40:
                self.state = 0

    def hurt(self):
        self.image = self.hurtImage
        self.hp-=1
        self.state = -1
        self.stateTimer = 0

    def draw(self):

        #pygame.draw.circle(gameDisplay, (100,100,200), (self.x, self.y), self.radius)
        #pygame.draw.circle(gameDisplay, (200,100,100), (self.x+self.xdir*self.swipeRange, self.y+self.ydir*self.swipeRange), 30)

        # SWIPE
        if self.state == 1:
            if self.stateTimer == 10:
                x = int(self.x+self.xdir*self.swipeRange)
                y = int(self.y+self.ydir*self.swipeRange)
                blitRotate(gameDisplay, self.swipeImage, (x,y), (self.imageSize//2, self.imageSize//2), math.atan2(-self.ydir,-self.xdir))

        # YOU
        gameDisplay.blit(self.image, (int(self.x) - self.imageSize//2, int(self.y-8) - self.imageSize//2))


class Enemy():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.state = 0
        self.stateTimer = 0
        self.movementSpeed = 1

    def update(self):
        if self.state == 0:
            dx = (self.x<game.player.x)*2 -1
            dy = (self.y<game.player.y)*2 -1
            if dx or dy:
                self.x += dx*self.movementSpeed
                self.y += dy*self.movementSpeed
                #self.image = random.choice(self.walkImages+[self.idleImage])
            else:
                pass
                #self.image = self.idleImage

    def draw(self):
        gameDisplay.blit(self.image, (int(self.x) - self.imageSize//2, int(self.y) - self.imageSize//2))
        #pygame.draw.circle(gameDisplay, (100,100,200), (self.x, self.y), self.radius)

class Animus(Enemy):

    radius = 30
    imageSize = 64
    idleImage = loadTexture("enemies/animus.png", imageSize)

    def __init__(self, x, y):
        super(Animus, self).__init__(x,y)
        self.image = self.idleImage
        self.hp = 1

    def update(self):
        super(Animus, self).update()

        #ATTACK
        target = game.findPlayer(self.x, self.y, 20)
        if target:
            target.hurt()
            game.enemies.remove(self)

    def hurt(self):
        self.hp-=1
        if self.hp<=0:
            game.enemies.remove(self)
class Pufferfish(Enemy):

    radius = 20
    imageSize = 64
    idleImage = loadTexture("enemies/pufferfish/idle.png", imageSize)
    hurtImage = loadTexture("enemies/pufferfish/stunned.png", imageSize)
    attackImages = [loadTexture("enemies/pufferfish/attack"+str(i)+".png", Animus.imageSize) for i in (1,2,3)]

    def __init__(self, x, y):
        super(Pufferfish, self).__init__(x,y)
        self.image = self.idleImage
        self.hp = 2

    def update(self):
        super(Pufferfish, self).update()

        #HURT
        if self.state == -1:
            self.image = self.hurtImage

            self.stateTimer-=1 #här går den neråt
            if self.stateTimer<=0:
                if self.hp<=0:
                    game.enemies.remove(self)
                else:
                    self.state = 0
                    self.image = self.idleImage

        #IDLE
        if self.state == 0:
            if game.findPlayer(self.x, self.y, 20):
                self.state = 1
                self.stateTimer = 0

        #ATTACK
        if self.state == 1:
            if self.stateTimer==0:
                self.image = self.attackImages[0]
            if self.stateTimer==10:
                self.image = self.attackImages[1]
            if self.stateTimer==20:
                self.image = self.attackImages[2]
                target = game.findPlayer(self.x, self.y, 20)
                if target:
                    target.hurt()
            if self.stateTimer==50:
                self.image = self.attackImages[1]
            if self.stateTimer==70:
                self.image = self.attackImages[0]

            self.stateTimer+=1
            if self.stateTimer>=90:
                self.image = self.idleImage
                self.state = 0

    def hurt(self):
        self.hp-=1
        self.state = -1
        self.stateTimer = 20
class Robot(Enemy):

    radius = 20
    imageSize = 64
    idleImages = [loadTexture("enemies/robot/idle.png", imageSize), loadTexture("enemies/robot/idleb.png", imageSize)]
    hurtImage = loadTexture("enemies/robot/stunned.png", imageSize)

    def __init__(self, x, y, hasClone=True):
        super(Robot, self).__init__(x,y)
        self.image = self.idleImages[0]
        self.hp = 3
        self.hasClone = hasClone
        if hasClone:
            self.clone = Robot(x+200,y, hasClone=False)
            game.enemies.append(self.clone)

    def update(self):
        self.x += random.randint(-2,2)
        self.y += random.randint(-2,2)

        if self.hasClone:
            if self.clone.hp <= 0:
                self.hasClone = 0

        #HURT
        if self.state == -1:
            self.image = self.hurtImage

            self.stateTimer-=1
            if self.stateTimer<=0:
                if self.hp<=0:
                    game.enemies.remove(self)
                else:
                    self.state = 0

        #IDLE
        if self.state == 0:
            self.image = random.choice(self.idleImages)
            if self.hasClone:
                randomPoint = random.random()
                if game.findPlayer(self.x+(self.clone.x-self.x)*randomPoint, self.y+(self.clone.y-self.y)*randomPoint, 4):
                    game.player.hurt()

    def hurt(self):
        self.hp-=1
        self.state = -1
        self.stateTimer = 20

    def draw(self):
        if self.hasClone and self.state == 0 and self.clone.state == 0:
            pygame.draw.line(gameDisplay, (200,200,200+random.random()*55), (self.x+10,self.y), (self.clone.x+10, self.clone.y), random.randint(1,8))
        gameDisplay.blit(self.image, (int(self.x) - self.imageSize//2, int(self.y) - self.imageSize//2))

class Item():

    radius = 20

    def __init__(self, x, y):
        self.x = x
        self.y = y

    def update(self):
        if game.findPlayer(self.x,self.y, self.radius):
            self.pickup()
            game.items.remove(self)

    def draw(self):
        gameDisplay.blit(self.image, (int(self.x) - self.imageSize//2, int(self.y) - self.imageSize//2))

class Fruit(Item):

    imageSize = 128
    image = loadTexture("items/fruit.png", imageSize)

    def pickup(self):
        game.player.movementSpeed+=1
class Stick(Item):

    imageSize = 128
    image = loadTexture("items/stick.png", imageSize)

    def pickup(self):
        game.player.swipeRange+=16
class Fan(Item):

    imageSize = 128
    image = loadTexture("items/fan.png", imageSize)

    def pickup(self):
        game.player.fanRoll-=3
class Heart(Item):

    imageSize = 128
    image = loadTexture("items/heart.png", imageSize)

    def pickup(self):
        game.player.hp+=1

gameDisplay = pygame.display.set_mode((1600, 900),)# pygame.FULLSCREEN)
pygame.display.set_caption("Roguelike Game")
pygame.display.set_icon(pygame.image.load(os.path.join(filepath, "textures", "player", "player.png")))

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
