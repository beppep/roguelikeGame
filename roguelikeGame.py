import pygame
import time
import random
import os
import math

# sacker man kan göra at göra
"""
boss
varierade floors
Shops
texturemark
ny content
bra AI movement
Klasser
"""

clock = pygame.time.Clock()
filepath="roguelikeGameFiles"
SOUND_PATH = os.path.join(filepath, "sounds")
display = (1200,700)
pygame.font.init()
myfont = pygame.font.Font(pygame.font.get_default_font(), 20)



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

def createF(names,x,y,occurance=1, lootTable=None,depth=1):
    def create():
        if(random.random()<occurance and depth<=game.depth):
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
        if game.depth==0:
            self.startRoom = Room([[createWallF(350,350,200,50),],[createF([Chest],350,250),],[]],[0,0]) # first room is empty
        else:
            self.startRoom = Room([[],[],[]],[0,0]) # first room is empty
        self.rooms=[self.startRoom]
        self.roomPosList=[[0,0]]
        numOfRooms=random.randint(5,9)
        for i in range(numOfRooms):
            roomPos=[0,0]
            while roomPos in self.roomPosList:
                connectedRoom = random.choice(self.rooms)
                while not None in connectedRoom.links:
                    connectedRoom = random.choice(self.rooms)
                connectionDirection = random.choice([i for i in range(4) if connectedRoom.links[i]==None ])
                roomPos=list(map(sum, zip(connectedRoom.floorPos[:],directionHash[connectionDirection]))) # Vector additon of two lists of integers
            self.roomPosList.append(roomPos)
            if(i == numOfRooms-1):
                room = Room([[],[],[createF([StairCase],250,250),]],roomPos) # Final room of floor
            else:
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
        self.roomSize=(500,500)
        self.links=[None,None,None,None] # Up, Right, Down, Left
        self.alreadyLoaded=False
        self.floorPos=floorPos
        self.wallWidth=50
        self.doorWidth=30
        
    def loadRoom(self):
        if(not self.alreadyLoaded):
            if(self.links[0]):
                self.walls.append(Wall(self.roomSize[0]/4-self.doorWidth,0,self.roomSize[0]/2-self.doorWidth*2,self.wallWidth))
                self.walls.append(Wall(self.roomSize[0]*3/4+self.doorWidth,0,self.roomSize[0]/2-self.doorWidth*2,self.wallWidth))
            else:
                self.walls.append(Wall(self.roomSize[0]/2,0,self.roomSize[0],self.wallWidth))
            if(self.links[1]):
                self.walls.append(Wall(self.roomSize[0],self.roomSize[1]/4-self.doorWidth,self.wallWidth,self.roomSize[1]/2-self.doorWidth*2))
                self.walls.append(Wall(self.roomSize[0],self.roomSize[1]*3/4+self.doorWidth,self.wallWidth,self.roomSize[1]/2-self.doorWidth*2))
            else:
                self.walls.append(Wall(self.roomSize[0],self.roomSize[1]/2,self.wallWidth,self.roomSize[1]))
            if(self.links[2]):
                self.walls.append(Wall(self.roomSize[0]/4-self.doorWidth,self.roomSize[1],self.roomSize[0]/2-self.doorWidth*2,self.wallWidth))
                self.walls.append(Wall(self.roomSize[0]*3/4+self.doorWidth,self.roomSize[1],self.roomSize[0]/2-self.doorWidth*2,self.wallWidth))
            else:
                self.walls.append(Wall(self.roomSize[0]/2,self.roomSize[1],self.roomSize[0],self.wallWidth))
            if(self.links[3]):
                self.walls.append(Wall(0,self.roomSize[1]/4-self.doorWidth,self.wallWidth,self.roomSize[1]/2-self.doorWidth*2))
                self.walls.append(Wall(0,self.roomSize[1]*3/4+self.doorWidth,self.wallWidth,self.roomSize[1]/2-self.doorWidth*2))
            else:
                self.walls.append(Wall(0,self.roomSize[1]/2,self.wallWidth,self.roomSize[1]))

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
        roomCorner=((display[0]-self.roomSize[0])/2,(display[1]-self.roomSize[1])/2)
        pygame.draw.rect(gameDisplay,[0,120,90],[*roomCorner,*self.roomSize])#self.roomSize[0],self.roomSize[1]])
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
        self.player = Ranger(250,250)
        self.room = None
        self.floor = None
        self.depth = 0

    def update(self):
        self.room.update()
        self.player.update()

    def enterFloor(self,floor):
        self.depth+=1
        self.floor=floor
        self.room=self.floor.startRoom
        self.room.loadRoom()
    def remove(self,thing,lst):
        if( thing in lst):
            lst.remove(thing)
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
        if self.player.invincibility:
            return 0
        r = r+self.player.radius
        if (self.player.x-x)**2 + (self.player.y-y)**2 < r**2:
            return self.player
        return 0

    def draw(self):
        gameDisplay.fill((100,100,100))
        self.room.draw()
        self.player.draw()
        self.player.drawPlayerUI()
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
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        pygame.draw.rect(gameDisplay, (50,50,50), (pos[0]-self.width//2, pos[1]-self.height//2, self.width, self.height),0)

class Player():

    radius = 20

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xdir = 1 #senaste man tittade
        self.ydir = 0
        self.hp = 3
        self.state = 0 #0:idle, 1:atak, 2:roll, (hitstun??)
        self.stateTimer = 0
        self.invincibility = 0
        self.image = self.idleImage

        self.movementSpeed = 1
        self.rollSpeed = 4
        self.fanRoll = 0 #3?
        self.swipeRange = 20
        self.icecrystal = 0
        self.crystal = 0
        self.projBounces = 0
        self.iceBody = 0
        self.freezeDamage=0
        self.freezeTime=60
        self.attackDamage=1
        self.fireSword=0

        self.shownItems = {}

    def update(self):
        pressed = pygame.key.get_pressed()

        if self.invincibility>0:
            self.invincibility-=1

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

        if(self.x>game.room.roomSize[0]):
            if(game.room.links[1]):
                game.room=game.room.links[1]
                game.room.loadRoom()
                self.x=10
            else:
                self.x=game.room.roomSize[0]
        elif(self.x<0):
            if(game.room.links[3]):
                game.room=game.room.links[3]
                game.room.loadRoom()
                self.x=game.room.roomSize[0]-10
            else:
                self.x=0
        elif(self.y>game.room.roomSize[1]):
            if(game.room.links[2]):
                game.room=game.room.links[2]
                game.room.loadRoom()
                self.y=10
            else:
                self.y=game.room.roomSize[1]
        elif(self.y<0):
            if(game.room.links[0]):
                game.room=game.room.links[0]
                game.room.loadRoom()
                self.y=game.room.roomSize[1]-10
            else:
                self.y=0
        for wall in game.room.walls:
            wall.adjust(self)

    def hurt(self):
        self.image = self.hurtImage
        self.hp-=1
        self.invincibility = 30
        self.state = -1
        self.stateTimer = 0
        if self.iceBody:
            targets = game.findEnemies(self.x, self.y, self.radius*self.iceBody*2)
            for target in targets:
                target.freeze()

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        #pygame.draw.circle(gameDisplay, (100,100,200), (self.x, self.y), self.radius)
        
        # YOU
        if self.stateTimer%2==0 or not self.invincibility:
            gameDisplay.blit(self.image, (pos[0] - self.imageSize//2, pos[1]-8 - self.imageSize//2))
        if self.iceBody:
            gameDisplay.blit(IceShield.image, (int(pos[0]-4) - IceShield.imageSize//2, int(pos[1]-4) - IceShield.imageSize//2))
    def drawPlayerUI(self):
        for i in range(self.hp):
            pygame.draw.rect(gameDisplay, (200,0,0),(50+20*i,30,16,16),0)
        for i in range(len(self.shownItems)):
            clss=list(self.shownItems.keys())[i]

            gameDisplay.blit(clss.image,(50-clss.imageSize/2,100+35*i-clss.imageSize/2))
            if(self.shownItems[clss]>1):
                textsurface = myfont.render("x"+str(self.shownItems[clss]) , False, (0, 0, 0))
                gameDisplay.blit(textsurface,(60,110+35*i))
        textsurface = myfont.render("floor: "+str(game.depth) , False, (0, 0, 0))
        gameDisplay.blit(textsurface,(1100,150))

class Warrior(Player):
    imageSize = 128
    idleImage = loadTexture("player/warrior/player.png", imageSize)
    hurtImage = loadTexture("player/warrior/hurt.png", imageSize)
    walkImages = [loadTexture("player/warrior/walk1.png", imageSize), loadTexture("player/warrior/walk2.png", imageSize)]
    attackImages = [loadTexture("player/warrior/strike1.png", imageSize), loadTexture("player/warrior/strike2.png", imageSize)]
    rollImages = [loadTexture("player/warrior/roll1.png", imageSize), loadTexture("player/warrior/roll2.png", imageSize)]

    swipeImage = loadTexture("player/warrior/swipe.png", imageSize)
    fireSwipeImage = loadTexture("player/warrior/fireswipe.png", imageSize)

    def update(self):
        super(Warrior, self).update()

        # ATAKK
        if self.state == 1:
            if self.stateTimer<20:
                self.image = self.attackImages[0]
            elif self.stateTimer == 20:
                attackX = self.x+self.xdir*self.swipeRange
                attackY = self.y+self.ydir*self.swipeRange
                targets = game.findEnemies(attackX, attackY, 30)
                for target in targets:
                    target.hurt()
                    target.fire(self.fireSword*30)
                """
                for i in range(self.icecrystal):
                    if random.random()<0.5:
                        game.room.projectiles.append(Sapphire(attackX,attackY,self.xdir*3+random.random()-0.5,self.ydir*3+random.random()-0.5))
                for i in range(self.crystal):
                    if random.random()<0.5:
                        game.room.projectiles.append(Ruby(attackX,attackY,self.xdir*3+random.random()-0.5,self.ydir*3+random.random()-0.5))
                """
            else:
                self.image = self.attackImages[1]

            self.stateTimer+=1
            if self.stateTimer>=30:
                self.state = 0

        # ROLL
        if self.state == 2:
            if self.stateTimer<20:
                self.invincibility=1
                self.image = random.choice(self.rollImages)
                self.x+=self.xdir*self.rollSpeed#*self.movementSpeed
                self.y+=self.ydir*self.rollSpeed#*self.movementSpeed
                # fanRoll
                targets = game.findEnemies(self.x,self.y,self.radius*self.fanRoll)
                for target in targets:
                    target.x-=self.xdir*self.fanRoll
                    target.y-=self.ydir*self.fanRoll
                targets = game.findProjectiles(self.x,self.y,self.radius*self.fanRoll)
                for target in targets:
                    target.xv=-self.xdir*self.fanRoll
                    target.yv=-self.ydir*self.fanRoll

            else:
                self.image = self.rollImages[0]
            self.stateTimer+=1
            if self.stateTimer>=40:
                self.state = 0

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        #pygame.draw.circle(gameDisplay, (200,100,100), (self.x+self.xdir*self.swipeRange, self.y+self.ydir*self.swipeRange), 30)

        # SWIPE
        if self.state == 1:
            if self.stateTimer == 20:
                x = int(pos[0]+self.xdir*self.swipeRange)
                y = int(pos[1]+self.ydir*self.swipeRange)
                if not self.fireSword:
                    image = self.swipeImage
                else:
                    image = self.fireSwipeImage
                blitRotate(gameDisplay, image, (x,y), (self.imageSize//2, self.imageSize//2), math.atan2(-self.ydir,-self.xdir))
        super(Warrior, self).draw()
class Ranger(Player):
    radius = 16
    imageSize = 128
    idleImage = loadTexture("player/ranger/idle.png", imageSize)
    hurtImage = loadTexture("player/ranger/hurt.png", imageSize)
    walkImages = [loadTexture("player/ranger/walk1.png", imageSize), loadTexture("player/ranger/walk2.png", imageSize)]
    attackImages = [loadTexture("player/ranger/fire.png", imageSize), loadTexture("player/ranger/reload0.png", imageSize)]
    reloadImages = [loadTexture("player/ranger/reload1.png", imageSize), loadTexture("player/ranger/reload2.png", imageSize)]
    def __init__(self, x, y):
        super().__init__(x,y)
        self.ammo=2
        self.movementSpeed=1.2
    def update(self):
        super(Ranger, self).update()

        # ATAKK
        if self.state == 1:
            if self.stateTimer==0:
                if(self.ammo>0):
                    self.image = self.attackImages[0]
                    game.room.projectiles.append(Bullet(self.x, self.y, self.xdir*8, self.ydir*8))
                    self.ammo-=1
                else:
                    self.state=0
        if self.state == 1:
            if self.stateTimer<3:
                self.image = self.attackImages[0]
            else:
                self.image = self.attackImages[1]

            self.stateTimer+=1
            if self.stateTimer>=30:
                self.state = 0

        # RELOAD
        if self.state == 2:
            if self.stateTimer<10:
                
                self.image = self.attackImages[1]
                # fanRoll
                targets = game.findEnemies(self.x,self.y,self.radius*self.fanRoll)
                for target in targets:
                    target.x+=self.xdir*self.fanRoll
                    target.y+=self.ydir*self.fanRoll
                targets = game.findProjectiles(self.x,self.y,self.radius*self.fanRoll)
                for target in targets:
                    target.xv=self.xdir*self.fanRoll
                    target.yv=self.ydir*self.fanRoll
            elif self.stateTimer<20:
                self.image = self.reloadImages[0]
            elif self.stateTimer<30:
                self.image = self.reloadImages[1]
                self.ammo=2
            elif self.stateTimer<40:
                self.image = self.reloadImages[0]
            elif self.stateTimer<50:
                self.image = self.idleImage

            self.stateTimer+=1
            if self.stateTimer>=50:
                self.state = 0


class Enemy():

    frozenImage = loadTexture("enemies/ice.png", 128)
    burningImage = loadTexture("enemies/fire.png", 128)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xdir = 1
        self.ydir = 0
        self.state = 0 # -2 frozen, -1:hurt, 0:idle
        self.stateTimer = 0
        self.movementSpeed = 1
        self.burning = 0
    def die(self):
        game.remove(self,game.room.enemies)
        for i in range(game.player.crystal):
            xv, yv = directionHash[random.randint(0,3)]
            game.room.projectiles.append(Ruby(game.player.x, game.player.y, xv*3+random.random()-0.5, yv*3+random.random()-0.5))
        for i in range(game.player.icecrystal):
            a = random.random()*6.28
            xv, yv = (math.cos(a),math.sin(a))
            game.room.projectiles.append(Sapphire(self.x, self.y, xv*3+random.random()-0.5, yv*3+random.random()-0.5))
    def freeze(self):
        if(self.hp>0):
            self.state=-2
            self.stateTimer = game.player.freezeTime
    def fire(self,duration):
        self.burning=duration
    def update(self):
        if(self.x>game.room.roomSize[0]):
            self.x=game.room.roomSize[0]
        elif(self.x<0):
            self.x=0
        elif(self.y>game.room.roomSize[1]):
            self.y=game.room.roomSize[1]
        elif(self.y<0):
            self.y=0

        for wall in game.room.walls:
            wall.adjust(self)
        
        if self.state == -2:
            self.burning=0
            self.image = self.idleImage
            self.stateTimer-=1
            if self.stateTimer <=0:
                self.state = 0
                self.hurt(game.player.freezeDamage)
        if(self.burning>0):
            self.hurt(0.02)
            self.burning-=1

    def basicMove(self):
        self.xdir = (self.x<game.player.x)*2 -1
        self.ydir = (self.y<game.player.y)*2 -1
        if self.xdir or self.ydir:
            self.x += self.xdir*self.movementSpeed
            self.y += self.ydir*self.movementSpeed
            #self.image = random.choice(self.walkImages+[self.idleImage])
        else:
            pass
            #self.image = self.idleImage

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        if self.state==-2:
            gameDisplay.blit(self.frozenImage, (int(pos[0]) - 128//2, int(pos[1]) - 128//2))
        if self.burning>0:
            gameDisplay.blit(self.burningImage, (int(pos[0]) - 128//2, int(pos[1]) - 128//2))
        gameDisplay.blit(self.image, (int(pos[0]) - self.imageSize//2, int(pos[1]) - self.imageSize//2))
        #pygame.draw.circle(gameDisplay, (100,100,200), (self.x, self.y), self.radius)
    def hurt(self,damage=None):
        if(damage==None):
            damage=game.player.attackDamage
        self.hp-=damage
        if self.hp<=0:
            self.die()
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
    def fire(*a):
        pass
    def freeze(*a):
        pass
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

                    game.remove(self,game.room.enemies)
                else:
                    self.state = 0
                    self.image = self.idleImage

    def hurt(self,damage=None):
        if(damage==None):
            damage=game.player.attackDamage
        self.hp-=damage
        self.state = -1
        self.stateTimer = 20
class Animus(Enemy):

    radius = 24
    imageSize = 64
    idleImage = loadTexture("enemies/animus.png", imageSize)

    def __init__(self, x, y):
        super(Animus, self).__init__(x,y)
        self.image = self.idleImage
        self.hp = 3

    def update(self):
        if self.state == 0:
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
            game.remove(self,game.room.enemies)
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
class Robot(Enemy):

    radius = 20
    imageSize = 64
    idleImage = loadTexture("enemies/robot/idle.png", imageSize)
    walkImage = loadTexture("enemies/robot/idleb.png", imageSize)
    hurtImage = loadTexture("enemies/robot/stunned.png", imageSize)
    fireImage = loadTexture("enemies/robot/fire.png", imageSize)

    def __init__(self, x, y, chief=True):
        super(Robot, self).__init__(x,y)
        self.image = self.idleImage
        self.hp = 3
        self.chief = chief
        if chief:
            self.friend = Robot(random.randint(100,game.room.roomSize[0]-100),random.randint(100,game.room.roomSize[1]-100), chief=False)
            game.room.enemies.append(self.friend)
            self.friend.friend = self

    def update(self):

        super(Robot, self).update()

        #IDLE
        if self.state == 0:
            self.x += random.randint(-2,2)
            self.y += random.randint(-2,2)
            self.image = random.choice([self.idleImage, self.walkImage])
            if self.friend and self.friend.state==0:
                #just beamin
                if self.chief: #unnecessary
                    randomPoint = random.random()
                    if game.findPlayer(self.x+10+(self.friend.x-self.x)*randomPoint, self.y+10+(self.friend.y-self.y)*randomPoint, 4):
                        game.player.hurt()
            elif random.random()<0.01:
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

    def hurt(self,damage=None):
        if(damage==None):
            damage=game.player.attackDamage
        self.hp-=damage
        if self.hp<=0:
            self.die()
            if self.friend:
                self.friend.friend = None

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        if self.state == 0 and self.friend and self.friend.state == 0 and self.chief:
            clonepos=(int((display[0]-game.room.roomSize[0])/2+self.friend.x),int((display[1]-game.room.roomSize[1])/2+self.friend.y))
            pygame.draw.line(gameDisplay, (200,200,200+random.random()*55), (pos[0]+10,pos[1]), (clonepos[0]+10, clonepos[1]), random.randint(1,8))
        super(Robot, self).draw()
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
        self.hp = 5
        self.movementSpeed = 0.5

    def update(self):
        super(SkuggVarg, self).update()

        #IDLE
        if self.state == 0:
            self.basicMove()
            if game.findPlayer(self.x, self.y, 24):
                self.state = 1
                self.stateTimer = 0

        #ATTACK
        if self.state == 1:
            if self.stateTimer<24:
                self.x+=self.xdir*2
                self.y+=self.ydir*2
                self.image = self.attackImages[self.stateTimer//6]
            if self.stateTimer==24:
                self.image = self.attackImages[4]
                target = game.findPlayer(self.x, self.y, 32)
                if target:
                    target.hurt()
            if self.stateTimer>30:
                self.image = self.attackImages[(62-self.stateTimer)//8]

            self.stateTimer+=1
            if self.stateTimer>=62:
                self.image = self.idleImage
                self.state = 0

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

        if(self.x>game.room.roomSize[0]):
            self.edge()
            self.xv*=-1
        elif(self.x<0):
            self.edge()
            self.xv*=-1
        elif(self.y>game.room.roomSize[1]):
            self.edge()
            self.yv*=-1
        elif(self.y<0):
            self.edge()
            self.yv*=-1

        for wall in game.room.walls:
            wall.adjust(self, proj=1)

    def edge(self):
        if self.bounces == 0:
            game.remove(self,game.room.projectiles)
        self.bounces-=1

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        gameDisplay.blit(self.image, (int(pos[0]) - self.imageSize//2, int(pos[1]) - self.imageSize//2))

class Missile(Projectile):

    radius = 4
    imageSize = 64
    image = loadTexture("enemies/robot/proj.png", imageSize)

    def update(self):
        super(Missile, self).update()

        # HIT PLAYER
        if game.findPlayer(self.x, self.y, self.radius):
            game.player.hurt()
            game.remove(self,game.room.projectiles)
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
            target.freeze()
        if targets:
            game.remove(self,game.room.projectiles)
class Ruby(Projectile):

    radius = 10
    imageSize = 64
    image = loadTexture("player/ruby.png", imageSize)

    def __init__(self, x, y, xv, yv):
        super(Ruby, self).__init__(x,y,xv,yv)
        self.bounces = game.player.projBounces

    def update(self):
        super(Ruby, self).update()

        # HIT ENEMIES
        targets =  game.findEnemies(self.x, self.y, self.radius)
        for target in targets:
            target.hurt()
        if targets:
            game.remove(self,game.room.projectiles)
class Bullet(Projectile):

    radius = 8
    imageSize = 128
    image = loadTexture("player/ranger/bullet.png", imageSize)

    def __init__(self, x, y, xv, yv):
        super(Bullet, self).__init__(x,y,xv,yv)
        self.bounces = game.player.projBounces

    def update(self):
        super(Bullet, self).update()

        # HIT ENEMIES
        targets =  game.findEnemies(self.x, self.y, self.radius)
        for target in targets:
            target.hurt()
            target.fire(game.player.fireSword*30)
        if targets:
            game.remove(self,game.room.projectiles)

class Item():

    radius = 20
    showItem=True
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.age=0


    def update(self):
        self.age+=1
        if self.age>20:
            if game.findPlayer(self.x,self.y, self.radius):
                if(self.showItem):
                    if (self.__class__ in game.player.shownItems):
                        game.player.shownItems[self.__class__]+=1
                    else:
                        game.player.shownItems[self.__class__]=1
                self.pickup()
                game.remove(self,game.room.items)

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        gameDisplay.blit(self.image, (int(pos[0]) - self.imageSize//2, int(pos[1]) - self.imageSize//2))

class Fruit(Item):

    imageSize = 128
    image = loadTexture("items/fruit.png", imageSize)

    def pickup(self):
        game.player.movementSpeed+=0.5
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
    showItem=False
    def pickup(self):
        game.player.hp+=1
class Icecrystal(Item):

    imageSize = 64
    image = loadTexture("items/icecrystal.png", imageSize)

    def pickup(self):
        game.player.icecrystal+=3
class Crystal(Item):

    imageSize = 64
    image = loadTexture("items/crystal.png", imageSize)

    def pickup(self):
        game.player.crystal+=1
class Bouncer(Item):
    imageSize = 128
    image = loadTexture("items/bouncer.png", imageSize)

    def pickup(self):
        game.player.projBounces+=1
class IceShield(Item):
    imageSize = 128
    image = loadTexture("items/iceShield.png", imageSize)

    def pickup(self):
        game.player.iceBody+=1
class StairCase(Item):
    imageSize = 128
    image = loadTexture("items/staircase.png", imageSize)
    showItem=False
    def pickup(self):
        game.enterFloor(Floor(roomPresets))
        game.room.items.append(self) # otherwise Item.update can't delete staircase after pickup
class ColdCore(Item):
    imageSize = 128
    image = loadTexture("items/coldcore.png", imageSize)

    def pickup(self):
        game.player.freezeDamage+=1
        game.player.freezeTime+=30
class FireSword(Item):
    imageSize = 128
    image = loadTexture("items/firesword.png", imageSize)

    def pickup(self):
        game.player.fireSword+=1    
    
directionHash={0:[0,-1],1:[1,0],2:[0,1],3:[-1,0]}
allItems=[Fruit,Stick,Fan,Icecrystal,Bouncer,IceShield,Crystal,ColdCore,FireSword]
roomPresets=[
    [[
    createWallF(300,300,200,50),
    createWallF(300,lambda :random.randint(1,200),lambda :random.randint(1,200),50),
    ],[
    createF([Chest],100,100, lootTable=[None,Fruit], occurance=0.2),
    createF([Animus,Pufferfish,Robot],150,50, depth=3),
    createF([SkuggVarg],lambda :random.randint(0,500),lambda :random.randint(0,500),occurance=0.5),
    ],[
    createF(allItems,200,400,occurance=0.1),
    ],], # Test Room using everything

    [[
    createWallF(100,200,120,20,occurance=0.2),
    createWallF(400,200,120,20,occurance=0.2),
    createWallF(150,300,20,220,occurance=0.3),
    createWallF(350,300,20,220,occurance=0.3),
    createWallF(250,400,220,20,occurance=0.2),
    createWallF(250,200,220,20,occurance=0.2),
    ],[
    createF([Animus],250,250),
    createF([Pufferfish],200,250,occurance=0.2),
    createF([Pufferfish],300,250,occurance=0.2),
    ],[
    createF([Fruit],250,350,occurance=0.3),
    ],], # Test Room
    
    [[
    createWallF(100,150,50,100),
    createWallF(300,lambda :random.randint(1,400),100,50),
    ],[
    createF([Robot],lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(100,game.room.roomSize[1]-100)),
    ],[
    createF(allItems,300,200, occurance=0.1, depth=3),
    ],], # Test Room

    [[
    ],[
    createF([Robot],lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(100,game.room.roomSize[1]-100)),
    createF([Animus],lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(100,game.room.roomSize[1]-100)),
    createF([Pufferfish],300,350),
    ],[
    createF([Fruit],200,300, occurance=0.1),
    createF([Stick],250,300, occurance=0.2),
    createF([Fan],300,300, occurance=0.1),
    ],], # Ellas Room

    [[
    ],[
    createF([Chest],250,250),
    createF([Animus,Pufferfish, SkuggVarg],150,200),
    createF([Animus,Pufferfish, SkuggVarg],350,200),
    createF([Animus,Pufferfish, SkuggVarg],250,150,depth=2),
    createF([Animus,Pufferfish, SkuggVarg],200,350,depth=2),
    createF([Animus,Pufferfish, SkuggVarg],300,350,depth=2),
    ],[
    #createF(allItems,600,350),
    ],], # Pentagon

    [[
    createWallF(lambda :random.randint(100,400),lambda :random.randint(100,400),lambda :random.randint(20,100),lambda :random.randint(20,200), occurance=0.5),
    createWallF(lambda :random.randint(100,400),lambda :random.randint(100,400),lambda :random.randint(20,200),lambda :random.randint(20,100), occurance=0.5),
    ],[
    createF([Chest],250,250)
    ]+[
    createF([Robot],lambda :random.randint(100,400),lambda :random.randint(100,400), occurance=0.8),
    ]*5,
    [
    #createF(allItems,600,350),
    ],], # Laser Room

    [[
    ],[
    createF([Pufferfish],250,250,occurance=0.5),
    ],[
    createF([Heart],lambda :random.randint(200,300),lambda :random.randint(200,300)),
    ],], # Heal

    [[
    createWallF(lambda :random.randint(200,300),lambda :random.randint(200,300),lambda :random.randint(20,100),lambda :random.randint(20,100), occurance=0.5),
    createWallF(250,250,100,100, occurance=0.5),
    ],[
    createF([Animus],lambda :random.randint(200,300),lambda :random.randint(200,300)),
    createF([Animus],lambda :random.randint(200,300),lambda :random.randint(200,300), depth=2),
    createF([Animus],lambda :random.randint(200,300),lambda :random.randint(200,300), occurance=0.8),
    ],[
    ],], # Animals

    [[
    createWallF(lambda :random.randint(1,4)*100,lambda :random.randint(0,4)*100+50,20,120),
    ]*4+[
    createWallF(lambda :random.randint(0,4)*100+50,lambda :random.randint(1,4)*100,120,20),
    ]*4,[
    createF([SkuggVarg],200,250, depth=5),
    createF([SkuggVarg],250,250),
    createF([SkuggVarg],300,250, depth=5),
    createF([Chest],250,250, occurance=0.5),
    ],[
    createF([Heart],350,250, occurance=0.5),
    ],], # Minotaur
]


gameDisplay = pygame.display.set_mode(display,)# pygame.FULLSCREEN)
pygame.display.set_caption("Roguelike Game")
pygame.display.set_icon(pygame.image.load(os.path.join(filepath, "textures", "player/warrior", "player.png")))

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

#ddddddddd