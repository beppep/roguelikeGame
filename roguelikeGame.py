import pygame
import time
import random
import os
import math

# sacker man kan göra at göra
"""
boss
flera floors
texturemark
små rum
visa items
ny content
"""

clock = pygame.time.Clock()
filepath="roguelikeGameFiles"
SOUND_PATH = os.path.join(filepath, "sounds")
display = (1200,700)

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

def createF(names,x,y,occurance=1, lootTable=None):
    def create():
        if(random.random()<occurance):
            if(callable(x)):
                posX=x()
            else:
                posX=x
            if(callable(y)):
                posY=y()
            else:
                posY=y
            thing = random.choice(names)(posX,posY)
            if lootTable:
                thing.lootTable = lootTable
            return thing
        return None
    return create
def createWallF(x,y,w,h,occurance=1):
    def createWall():
        if(random.random()<occurance):
            if(callable(x)):
                posX=x()
            else:
                posX=x
            if(callable(y)):
                posY=y()
            else:
                posY=y
            if(callable(w)):
                width=w()
            else:
                width=w
            if(callable(h)):
                height=h()
            else:
                height=h 
            return Wall(posX,posY,width,height)
        return None
    return createWall

class Floor():
    def __init__(self,presets):
        self.startRoom = Room([[createWallF(500,400,200,100),],[],[]],[0,0]) # first room is empty
        self.rooms=[self.startRoom]
        self.roomPosList=[[0,0]]
        for i in range(random.randint(5,19)):
            roomPos=[0,0]
            while roomPos in self.roomPosList:
                connectedRoom = random.choice(self.rooms)
                while not None in connectedRoom.links:
                    connectedRoom = random.choice(self.rooms)
                connectionDirection = random.choice([i for i in range(4) if connectedRoom.links[i]==None ])
                roomPos=list(map(sum, zip(connectedRoom.floorPos[:],directionHash[connectionDirection]))) # Vector additon of two lists of integers
            self.roomPosList.append(roomPos)
            room = Room(random.choice(presets),roomPos)
            #room = Room(presets[-1],roomPos)
            self.rooms.append(room)
            connectedRoom.links[connectionDirection]=room
            room.links[(connectionDirection+2)%4]=connectedRoom
    def drawMinimap(self):
        for room in self.rooms:
            pos=room.floorPos
            pygame.draw.rect(gameDisplay, (200,200,200),[display[0]-100+pos[0]*20,100+pos[1]*20,10,10],0)
            for link in room.links:
                if link:
                    pos2=link.floorPos
                    pygame.draw.line(gameDisplay,(200,200,200),[display[0]-100+pos[0]*20+5,100+pos[1]*20+5],[display[0]-100+pos2[0]*20+5,100+pos2[1]*20+5],3)
            pos=game.room.floorPos
            pygame.draw.circle(gameDisplay, (200,0,0),[display[0]-100+pos[0]*20+5,100+pos[1]*20+5],3)

class Room():
    def __init__(self,preset,floorPos):
        self.enemies = []
        self.items = []
        self.walls = []
        self.projectiles = []
        self.preset=preset
        self.links=[None,None,None,None] # Up, Right, Down, Left
        self.alreadyLoaded=False
        self.floorPos=floorPos
        
    def loadRoom(self):
        if(not self.alreadyLoaded):
            for f in self.preset[0]:
                wall = f()
                if(wall):
                    self.walls.append(wall)
            for f in self.preset[1]:
                enemy = f()
                if(enemy):
                    self.enemies.append(enemy)
            for f in self.preset[2]:
                item = f()
                if(item):
                    self.items.append(item)
            self.alreadyLoaded=True
    def update(self):
        for item in self.items:
            item.update()
        for proj in self.projectiles:
            proj.update()
        for enemy in self.enemies:
            enemy.update()
    def draw(self):
        for wall in self.walls:
            wall.draw()
        for item in self.items:
            item.draw()
        for proj in self.projectiles:
            proj.draw()
        for enemy in self.enemies:
            enemy.draw()
class Game():

    def __init__(self):
        self.player = Player(display[0]//2,display[1]//2)
        self.room = None
        self.floor = None

    def update(self):
        self.room.update()
        self.player.update()

    def enterFloor(self,floor):
        self.floor=floor
        self.room=self.floor.startRoom
        self.room.loadRoom()

    def findEnemies(self, x,y, r): #hitdetection
        targets = []
        for enemy in self.room.enemies:
            d = r+enemy.radius
            if (enemy.x-x)**2 + (enemy.y-y)**2 < d**2:
                targets.append(enemy)
        return targets

    def findProjectiles(self, x,y, r):
        targets = []
        for proj in self.room.projectiles:
            d = r+proj.radius
            if (proj.x-x)**2 + (proj.y-y)**2 < d**2:
                targets.append(proj)
        return targets

    def findPlayer(self, x,y, r):
        if self.player.state==2 and self.player.stateTimer<20:
            return 0
        r = r+self.player.radius
        if (self.player.x-x)**2 + (self.player.y-y)**2 < r**2:
            return self.player
        return 0

    def draw(self):
        gameDisplay.fill((100,100,100))
        self.room.draw()
        self.player.draw()
        for i in range(self.player.hp):
            pygame.draw.rect(gameDisplay, (200,0,0),(50+20*i,30,16,16),0)
        self.floor.drawMinimap()

class Wall():

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def adjust(self, other, proj=0):
        dx = self.width//2+other.radius
        dy = self.height//2+other.radius
        if self.x-dx < other.x < self.x+dx:
            if self.y-dy < other.y < self.y+dy: #is inside?

                if other.x - (self.x-dx) < (self.x+dx) - other.x: #find closest side
                    dx = other.x - (self.x-dx)
                else:
                    dx = other.x - (self.x+dx)
                if other.y - (self.y-dy) < (self.y+dy) - other.y:
                    dy = other.y - (self.y-dy)
                else:
                    dy = other.y - (self.y+dy)

                if proj: # handle projs (man kan flytta dem också dx ut från väggen om man vill i guess)
                    if abs(dx)<abs(dy): # (abs slow?)
                        other.xv*=-1
                        other.edge()
                    else:
                        other.yv*=-1
                        other.edge()
                else:
                    if abs(dx)<abs(dy):
                        other.x-=dx
                    else:
                        other.y-=dy

    def draw(self):
        pygame.draw.rect(gameDisplay, (50,50,50), (self.x-self.width//2, self.y-self.height//2, self.width, self.height),0)

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
        self.icecrystal = 0
        self.projBounces = 0

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
                attackX = self.x+self.xdir*self.swipeRange
                attackY = self.y+self.ydir*self.swipeRange
                targets = game.findEnemies(attackX, attackY, 30)
                for target in targets:
                    target.hurt()
                for i in range(self.icecrystal):
                    game.room.projectiles.append(Sapphire(attackX,attackY,self.xdir*3+random.random()-0.5,self.ydir*3+random.random()-0.5))
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
                targets = game.findEnemies(self.x,self.y,self.radius*self.fanRoll)
                for target in targets:
                    target.x+=self.xdir*self.fanRoll
                    target.y+=self.ydir*self.fanRoll
                targets = game.findProjectiles(self.x,self.y,self.radius*self.fanRoll)
                for target in targets:
                    target.xv=self.xdir*self.fanRoll
                    target.yv=self.ydir*self.fanRoll

            else:
                self.image = self.rollImages[0]
            self.stateTimer+=1
            if self.stateTimer>=40:
                self.state = 0

        if(self.x>display[0]):
            if(game.room.links[1]):
                game.room=game.room.links[1]
                game.room.loadRoom()
                self.x=10
            else:
                self.x=display[0]
        elif(self.x<0):
            if(game.room.links[3]):
                game.room=game.room.links[3]
                game.room.loadRoom()
                self.x=display[0]-10
            else:
                self.x=0
        elif(self.y>display[1]):
            if(game.room.links[2]):
                game.room=game.room.links[2]
                game.room.loadRoom()
                self.y=10
            else:
                self.y=display[1]
        elif(self.y<0):
            if(game.room.links[0]):
                game.room=game.room.links[0]
                game.room.loadRoom()
                self.y=display[1]-10
            else:
                self.y=0
        for wall in game.room.walls:
            wall.adjust(self)

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
        if(self.x>display[0]):
            self.x=display[0]
        elif(self.x<0):
            self.x=0
        elif(self.y>display[1]):
            self.y=display[1]
        elif(self.y<0):
            self.y=0

        for wall in game.room.walls:
            wall.adjust(self)

    def basicMove(self):
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

class Chest(Enemy):

    radius = 48
    imageSize = 128
    idleImage = loadTexture("enemies/chest1.png", imageSize)
    hurtImage = loadTexture("enemies/chest2.png", imageSize)

    def __init__(self, x, y):
        super(Chest, self).__init__(x,y)
        self.image = self.idleImage
        self.hp = 1
        self.lootTable = allItems

    def update(self):
        super(Chest, self).update()

        #if random.random()<0.001:
         #   game.room.enemies.append(Animus(self.x,self.y))
        
        #HURT
        if self.state == -1:
            self.image = self.hurtImage

            self.stateTimer-=1 #här går den neråt
            if self.stateTimer<=0:
                if self.hp<=0:
                    loot = random.choice(self.lootTable)
                    if loot:
                        game.room.items.append(loot(self.x,self.y))
                    game.room.enemies.remove(self)
                else:
                    self.state = 0
                    self.image = self.idleImage

    def hurt(self):
        self.hp-=1
        self.state = -1
        self.stateTimer = 20
class Animus(Enemy):

    radius = 24
    imageSize = 64
    idleImage = loadTexture("enemies/animus.png", imageSize)

    def __init__(self, x, y):
        super(Animus, self).__init__(x,y)
        self.image = self.idleImage
        self.hp = 1

    def update(self):
        self.basicMove()
        self.x += random.randint(-1,1)
        self.y += random.randint(-1,1)

        super(Animus, self).update()

        if random.random()<0.001:
            game.room.enemies.append(Animus(self.x,self.y))

        #ATTACK
        target = game.findPlayer(self.x, self.y, 16)
        if target:
            target.hurt()
            game.room.enemies.remove(self)

    def hurt(self):
        self.hp-=1
        if self.hp<=0:
            game.room.enemies.remove(self)
class Pufferfish(Enemy):

    radius = 8
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
                    game.room.enemies.remove(self)
                else:
                    self.state = 0
                    self.image = self.idleImage

        #IDLE
        if self.state == 0:
            self.basicMove()
            if game.findPlayer(self.x, self.y, 16):
                self.state = 1
                self.stateTimer = 0

        #ATTACK
        if self.state == 1:
            if self.stateTimer==0:
                self.image = self.attackImages[0]
            if self.stateTimer==7:
                self.image = self.attackImages[1]
            if self.stateTimer==14:
                self.image = self.attackImages[2]
                target = game.findPlayer(self.x, self.y, 16)
                if target:
                    target.hurt()
            if self.stateTimer==30:
                self.image = self.attackImages[1]
            if self.stateTimer==45:
                self.image = self.attackImages[0]

            self.stateTimer+=1
            if self.stateTimer>=60:
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
    fireImage = loadTexture("enemies/robot/fire.png", imageSize)

    def __init__(self, x, y, hasClone=True):
        super(Robot, self).__init__(x,y)
        self.image = self.idleImages[0]
        self.hp = 3
        self.hasClone = hasClone
        self.alone = False
        if hasClone:
            self.clone = Robot(random.randint(100,display[0]-100),random.randint(100,display[1]-100), hasClone=False)
            game.room.enemies.append(self.clone)

    def update(self):
        self.x += random.randint(-2,2)
        self.y += random.randint(-2,2)

        super(Robot, self).update()

        if self.hasClone:
            if self.clone.hp <= 0:
                self.hasClone = False
                self.alone = True

        #HURT
        if self.state == -1:
            self.image = self.hurtImage

            self.stateTimer-=1
            if self.stateTimer<=0:
                if self.hp<=0:
                    game.room.enemies.remove(self)
                    if self.hasClone:
                        self.clone.alone = True
                else:
                    self.state = 0

        #IDLE
        if self.state == 0:
            self.image = random.choice(self.idleImages)
            if self.hasClone:
                randomPoint = random.random()
                if game.findPlayer(self.x+10+(self.clone.x-self.x)*randomPoint, self.y+10+(self.clone.y-self.y)*randomPoint, 4):
                    game.player.hurt()
            if self.alone:
                if random.random()<0.01:
                    self.state = 1
                    self.stateTimer = 0

        # SHOOT
        if self.state == 1:
            self.image = self.fireImage
            self.stateTimer+=1
            if self.stateTimer==10:
                d = math.sqrt((self.x-game.player.x)**2 + (self.y-game.player.y)**2)
                dx = (game.player.x-self.x)/d
                dy = (game.player.y-self.y)/d
                game.room.projectiles.append(Missile(self.x, self.y, dx*3, dy*3))
            if self.stateTimer>=30:
                self.state = 0

    def hurt(self):
        self.hp-=1
        self.state = -1
        self.stateTimer = 20

    def draw(self):
        if self.hasClone and self.state == 0 and self.clone.state == 0:
            pygame.draw.line(gameDisplay, (200,200,200+random.random()*55), (self.x+10,self.y), (self.clone.x+10, self.clone.y), random.randint(1,8))
        gameDisplay.blit(self.image, (int(self.x) - self.imageSize//2, int(self.y) - self.imageSize//2))
class SkuggVarg(Enemy): 
    # "kolmården"

    radius = 16
    imageSize = 64
    idleImage = loadTexture("enemies/skugg/idle.png", imageSize)
    attackImages = [loadTexture("enemies/skugg/SkuggVarg_"+str(i+38)+".png", Animus.imageSize) for i in range(5)]
    hurtImage = loadTexture("enemies/skugg/SkuggVarg_68.png", imageSize)

    def __init__(self, x, y):
        super(SkuggVarg, self).__init__(x,y)
        self.image = self.idleImage
        self.hp = 2

    def update(self):
        super(SkuggVarg, self).update()

        #HURT
        if self.state == -1:
            self.image = self.hurtImage

            self.stateTimer-=1 #här går den neråt
            if self.stateTimer<=0:
                if self.hp<=0:
                    game.room.enemies.remove(self)
                else:
                    self.state = 0
                    self.image = self.idleImage

        #IDLE
        if self.state == 0:
            self.basicMove()
            if game.findPlayer(self.x, self.y, 16):
                self.state = 1
                self.stateTimer = 0

        #ATTACK
        if self.state == 1:
            if self.stateTimer<24:
                self.image = self.attackImages[self.stateTimer//6]
            if self.stateTimer==24:
                self.image = self.attackImages[4]
                target = game.findPlayer(self.x, self.y, 16)
                if target:
                    target.hurt()
            if self.stateTimer>30:
                self.image = self.attackImages[(62-self.stateTimer)//8]

            self.stateTimer+=1
            if self.stateTimer>=62:
                self.image = self.idleImage
                self.state = 0

    def hurt(self):
        self.hp-=1
        self.state = -1
        self.stateTimer = 20

class Projectile():
    def __init__(self, x, y, xv, yv):
        self.x = x
        self.y = y
        self.xv = xv
        self.yv = yv
        self.bounces = 0
    
    def update(self):
        self.x+=self.xv
        self.y+=self.yv

        if(self.x>display[0]):
            self.edge()
            self.xv*=-1
        elif(self.x<0):
            self.edge()
            self.xv*=-1
        elif(self.y>display[1]):
            self.edge()
            self.yv*=-1
        elif(self.y<0):
            self.edge()
            self.yv*=-1

        for wall in game.room.walls:
            wall.adjust(self, proj=1)

    def edge(self):
        if self.bounces == 0:
            game.room.projectiles.remove(self)
        self.bounces-=1

    def draw(self):
        gameDisplay.blit(self.image, (int(self.x) - self.imageSize//2, int(self.y) - self.imageSize//2))

class Missile(Projectile):

    radius = 4
    imageSize = 64
    image = loadTexture("enemies/robot/proj.png", imageSize)

    def update(self):
        super(Missile, self).update()

        # HIT PLAYER
        if game.findPlayer(self.x, self.y, self.radius):
            game.player.hurt()
            game.room.projectiles.remove(self)
class Sapphire(Projectile):

    radius = 10
    imageSize = 64
    image = loadTexture("player/sapphire.png", imageSize)

    def __init__(self, x, y, xv, yv):
        super(Sapphire, self).__init__(x,y,xv,yv)
        self.bounces = game.player.projBounces

    def update(self):
        super(Sapphire, self).update()

        # HIT ENEMIES
        targets =  game.findEnemies(self.x, self.y, self.radius)
        for target in targets:
            target.hurt()
        if targets:
            game.room.projectiles.remove(self)

class Item():

    radius = 20

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.age=0

    def update(self):
        self.age+=1
        if self.age>20:
            if game.findPlayer(self.x,self.y, self.radius):
                self.pickup()
                game.room.items.remove(self)

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
        game.player.swipeRange+=20
class Fan(Item):

    imageSize = 128
    image = loadTexture("items/fan.png", imageSize)

    def pickup(self):
        game.player.fanRoll+=3
class Heart(Item):

    imageSize = 128
    image = loadTexture("items/heart.png", imageSize)

    def pickup(self):
        game.player.hp+=1
class Icecrystal(Item):

    imageSize = 64
    image = loadTexture("items/icecrystal.png", imageSize)

    def pickup(self):
        game.player.icecrystal+=1
class Bouncer(Item):
    imageSize = 64
    image = loadTexture("items/bouncer.png", imageSize)

    def pickup(self):
        game.player.projBounces+=1

directionHash={0:[0,-1],1:[1,0],2:[0,1],3:[-1,0]}
allItems=[Fruit,Stick,Fan,Heart,Icecrystal,Bouncer]
roomPresets=[
    [[
    createWallF(100,100,200,100),
    createWallF(800,lambda :random.randint(1,600),lambda :random.randint(1,600),50),
    ],[
    createF([Chest],100,100, lootTable=[None,Fruit]),
    createF([Animus,Pufferfish,Robot],150,50),
    createF([SkuggVarg],lambda :random.randint(0,1200),lambda :random.randint(0,700),occurance=0.5),
    ],[
    createF([Fruit],10,150),
    createF(allItems,10,150),
    createF(allItems+[None],200,400,occurance=0.5),
    ],], # Test Room using everything

    [[
    createWallF(400,300,120,20,occurance=0.2),
    createWallF(800,300,120,20,occurance=0.2),
    createWallF(450,400,20,220,occurance=0.3),
    createWallF(750,400,20,220,occurance=0.3),
    createWallF(600,500,320,20,occurance=0.2),
    createWallF(600,300,320,20,occurance=0.2),
    ],[
    createF([Animus],600,350),
    createF([Pufferfish],400,350,occurance=0.2),
    createF([Pufferfish],800,350,occurance=0.2),
    ],[
    createF([Fruit],600,500,occurance=0.5),
    ],], # Test Room
    
    [[
    createWallF(100,100,200,100),
    createWallF(800,lambda :random.randint(1,600),150,50),
    ],[
    createF([Robot],lambda :random.randint(100,display[0]-100),lambda :random.randint(100,display[1]-100)),
    ],[
    createF(allItems,600,500, occurance=0.1),
    ],], # Test Room

    [[
    ],[
    createF([Robot],lambda :random.randint(100,display[0]-100),lambda :random.randint(100,display[1]-100)),
    createF([Animus],lambda :random.randint(100,display[0]-100),lambda :random.randint(100,display[1]-100)),
    createF([Pufferfish],600,350),
    ],[
    createF([Fruit],550,350, occurance=0.3),
    createF([Stick],600,350, occurance=0.4),
    createF([Fan],650,350, occurance=0.3),
    ],], # Ellas Room

    [[
    ],[
    createF([Chest],600,350),
    createF([Animus,Pufferfish, SkuggVarg],500,300),
    createF([Animus,Pufferfish, SkuggVarg],700,300),
    createF([Animus,Pufferfish, SkuggVarg],600,250),
    createF([Animus,Pufferfish, SkuggVarg],550,450),
    createF([Animus,Pufferfish, SkuggVarg],650,450),
    ],[
    #createF(allItems,600,350),
    ],], # Pentagon

    [[
    createWallF(lambda :random.randint(200,1000),lambda :random.randint(200,500),lambda :random.randint(200,1000),lambda :random.randint(200,500), occurance=0.5),
    createWallF(lambda :random.randint(200,1000),lambda :random.randint(200,500),lambda :random.randint(200,1000),lambda :random.randint(200,500), occurance=0.5),
    ],[
    createF([Chest],600,350)
    ]+[
    createF([Robot],lambda :random.randint(100,1100),lambda :random.randint(100,600), occurance=0.8),
    ]*5,
    [
    #createF(allItems,600,350),
    ],], # Laser Room

    [[
    ],[
    ],[
    createF([Heart],lambda :random.randint(500,700),lambda :random.randint(300,400)),
    ],], # Heal

    [[
    createWallF(lambda :random.randint(200,1000),lambda :random.randint(200,500),lambda :random.randint(200,1000),lambda :random.randint(200,500), occurance=0.5),
    createWallF(600,350,100,100, occurance=0.5),
    ],[
    createF([Animus],lambda :random.randint(200,1000),lambda :random.randint(200,500)),
    createF([Animus],lambda :random.randint(200,1000),lambda :random.randint(200,500)),
    createF([Animus],lambda :random.randint(200,1000),lambda :random.randint(200,500), occurance=0.8),
    ],[
    ],], # Animals

    [[
    createWallF(lambda :random.randint(2,10)*100,lambda :random.randint(2,5)*100,220,20),
    ]*8+[
    createWallF(lambda :random.randint(2,10)*100,lambda :random.randint(2,5)*100,20,220),
    ]*8,[
    createF([SkuggVarg],600,350),
    ],[
    createF([Heart],600,350),
    ],], # Minotaur
]


gameDisplay = pygame.display.set_mode(display,)# pygame.FULLSCREEN)
pygame.display.set_caption("Roguelike Game")
pygame.display.set_icon(pygame.image.load(os.path.join(filepath, "textures", "player", "player.png")))

initSound()

game = Game()
game.enterFloor(Floor(roomPresets))

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