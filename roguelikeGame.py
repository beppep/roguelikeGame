import pygame
import time
import random
import os
import math

EZ = 1

# sacker man kan göra at göra
"""
bättre boss?
varierade floors?
ny content
health bars?

#halvsvåra sacker

olika stora rum, skärmstorlek, screenshake etc
att rendera allt pixelperfect?
att man inte får bara firestars/pinnar
kvadratiska väggblock?
menu
flera filer?

enemies:
healer
"""

clock = pygame.time.Clock()
filepath="roguelikeGameFiles"
SOUND_PATH = os.path.join(filepath, "sounds")
pygame.init()
info = pygame.display.Info() # You have to call this before pygame.display.set_mode()
display = (info.current_w,info.current_h)
gameDisplay = pygame.display.set_mode(display,)# pygame.FULLSCREEN)
gameDisplay.blit(pygame.transform.scale(pygame.image.load(os.path.join(filepath, "textures", "loading.png")),display),(0,0))
pygame.display.update()
pygame.display.set_caption("Roguelike Game")
pygame.display.set_icon(pygame.image.load(os.path.join(filepath, "textures", "player", "warrior", "player.png")))
pygame.font.init()
#myfont = pygame.font.SysFont('Calibri', 20) #for pyinstaller
myfont = pygame.font.Font(pygame.font.get_default_font(), 20)

boost = 5

class Sound():
    volume = 1
    SOUND_PATH=os.path.join(filepath, "sounds")
    pygame.font.init() # you have to call this at the start, 
                           # if you want to use this module.
    pygame.mixer.init(buffer=256) # important to change?
    hitSounds=[]
    hitSounds.append(pygame.mixer.Sound(os.path.join(SOUND_PATH, "hit1.wav")))
    hitSounds[0].set_volume(volume*0.4)

    reloadSound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "reload.wav"))
    reloadSound.set_volume(volume*0.2)
    shotSound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "shot.wav"))
    shotSound.set_volume(volume*0.2)
    coinSound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "coin2.wav"))
    coinSound.set_volume(volume*0.5)
    pickpocketSound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "coin.wav"))
    pickpocketSound.set_volume(volume*0.5)
    cashSound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "cash.wav"))
    cashSound.set_volume(volume*0.2)
    glassSound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "glass.wav"))
    glassSound.set_volume(volume*0.2)
    playedHorrorSound = False
    horrorSound = pygame.mixer.Sound(os.path.join(SOUND_PATH, "panic.wav"))
    horrorSound.set_volume(volume*0.5)
    
    pygame.mixer.music.load(os.path.join(SOUND_PATH, "junglemusic.wav")) #must be wav 16bit and stuff?
    pygame.mixer.music.set_volume(volume*0.25)
    time.sleep(0.1)
    pygame.mixer.music.play(-1)

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
    image = pygame.image.load(os.path.join(filepath, "textures", name)).convert_alpha()
    image = pygame.transform.scale(image, (w, h))
    if mirror:
        return (pygame.transform.flip(image, True, False), image)
    else:
        return image

def createF(names,x,y,occurance=1, lootTable=None,depth=1,shop=False):
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
            if(shop):
                thing = random.choice(names)(posX,posY,shopItem=True)
            else:
                thing = random.choice(names)(posX,posY)
            if lootTable:
                thing.lootTable = lootTable
            return thing
        return None
    return create
def createWallF(x,y,w,h,occurance=1, depth=1):
    def createWall():
        if(random.random()<occurance and depth<=game.depth):
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

    groundImage = loadTexture(f"ground{random.randint(1,3)}.png",16*32,16*32).convert()
    tutorialGroundImage = loadTexture("tutorialGround.png",16*32,16*32).convert()

    def __init__(self,presets):
        self.shopPosition = (0,0)
        if game.depth==0:
            self.startRoom = Room([
                [createWallF(350,350,150,50),],
            [createF([Chest],350,300),], # ,lootTable=[ProjectileEnlarger]
            [],
            ],[0,0]) # first room is empty
            self.startRoom.tutorialRoom = True
        else:
            self.startRoom = Room([[],[],[]],[0,0]) # first room is empty
        for i in range(boost): #boost
            self.startRoom.items.append(random.choice(allItems)(250,250))
        self.rooms=[self.startRoom]
        self.roomPosList=[[0,0]]
        if game.depth==5:  # boss rooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooooom!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!
            bossRoom = Room([[],[createF([Boss,Boss2],250,150)],[]],[0,-1])
            self.startRoom.links[0]=bossRoom
            bossRoom.links[2]=self.startRoom
            self.rooms.append(bossRoom)
            self.roomPosList.append([-1,0])
            return
        numOfRooms=random.randint(4+game.depth,6+game.depth)
        for i in range(numOfRooms):
            roomPos=[0,0]
            while roomPos in self.roomPosList:
                connectedRoom = random.choice(self.rooms)
                while not None in connectedRoom.links:
                    connectedRoom = random.choice(self.rooms)
                connectionDirection = random.choice([i for i in range(4) if connectedRoom.links[i]==None])
                roomPos=list(map(sum, zip(connectedRoom.floorPos[:],directionHash[connectionDirection]))) # Vector additon of two lists of integers #lol gotta style right
            self.roomPosList.append(roomPos)
            if(i == numOfRooms-1):
                room = Room([[],[],[createF([StairCase],250,250),]],roomPos) # Final room of floor
            elif(i == numOfRooms-2) and game.depth>0:
                self.shopPosition = roomPos
                room = Room([[],[createF([Statue],250,150)],[createF(allItems,400,250,shop=True),createF(allItems,300,250,shop=True),createF(allItems,200,250,shop=True),createF([Heart],100,250,shop=True),],],roomPos)
            else:
                room = Room(random.choice(presets[0::]),roomPos)
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
            if self.shopPosition:
                pos = self.shopPosition
                pygame.draw.circle(gameDisplay, (200,150,0),[display[0]-100+pos[0]*20+5,100+pos[1]*20+5],3)

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
        self.locked = 0
        self.harmlessRoom = False
        self.tutorialRoom = False
        
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
        if self.enemies:
            self.locked = 300
    def update(self):
        self.harmlessRoom = True
        for enemy in self.enemies:
            if not enemy.harmless:
                self.harmlessRoom=False
                break

        if self.locked:
            self.locked-=1
            if self.harmlessRoom:
                    self.locked = 0
        for item in self.items:
            item.update()
        for proj in self.projectiles:
            proj.update()
        for enemy in self.enemies:
            enemy.update()
    def draw(self):
        roomCorner=((display[0]-self.roomSize[0])/2,(display[1]-self.roomSize[1])/2)
        pygame.draw.rect(gameDisplay,[100,80,50],[*roomCorner,*self.roomSize])#self.roomSize[0],self.roomSize[1]])
        #
        if self.tutorialRoom:
            gameDisplay.blit(game.floor.tutorialGroundImage,roomCorner)
        else:
            gameDisplay.blit(game.floor.groundImage,roomCorner)
        for wall in self.walls:
            wall.draw()
        for item in self.items:
            item.draw()
        for ally in game.allies:
            ally.draw()
        for enemy in self.enemies:
            enemy.draw()
        for proj in self.projectiles:
            proj.draw()
    def drawRoomUI(self):
        for e in self.enemies:
            if isinstance(e,Boss) or isinstance(e,Boss2): #bad code? yes
                e.drawUI()
class Game():

    def __init__(self, player_class):
        self.player = player_class(250,250)#random.choice(allClasses)(250,250)
        self.allies = []
        self.room = None
        self.floor = None
        self.depth = 0+boost #0
        self.drawFunctionQ=[] # fill it with [drawFunction, frameCountDown]
        Sound.playedHorrorSound = False
        
    def update(self):
        self.room.update()
        self.player.update()
        for ally in self.allies:
            ally.update()

    def gameOver(self, lose = False):
        if not lose:
            if isinstance(self.player, Warrior):
                Ranger.unlocked = True
            elif isinstance(self.player, Ranger):
                Thief.unlocked = True
            elif isinstance(self.player, Thief):
                Mage.unlocked = True
            save_save_file()

        Game.playing_a_run = False
        for projCls in [Sapphire,Ruby,Emerald,Bullet,FireBullet,Orb,FireOrb]:
            projCls.changeSize(1)
        winAnimation(lose = lose)

    def gatherAllies(self):
        for ally in self.allies:
            ally.x = self.player.x + random.randint(-32,32)
            ally.y = self.player.y + random.randint(-32,32)

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
                if not enemy.invincibility:
                    targets.append(enemy)
        return targets

    def findProjectiles(self, x,y, r):
        targets = []
        for proj in self.room.projectiles:
            d = r+proj.radius
            if (proj.x-x)**2 + (proj.y-y)**2 < d**2:
                targets.append(proj)
        return targets

    def findPlayer(self, x,y, r, fool=False):
        if self.player.invincibility:
            return 0
        r = r+self.player.radius
        if fool:
            playerX = self.player.fakeX
            playerY = self.player.fakeY
        else:
            playerX = self.player.x
            playerY = self.player.y
        if (playerX-x)**2 + (playerY-y)**2 < r**2:
            return self.player
        return 0

    def draw(self):
        #gameDisplay.fill((100,100,100))
        self.room.draw()
        self.player.draw()
        color = (80,80,75)
        pygame.draw.rect(gameDisplay, color, (0,0,(display[0]-game.room.roomSize[0])/2,display[1]))
        pygame.draw.rect(gameDisplay, color, (0,0,display[0],(display[1]-game.room.roomSize[1])/2))
        pygame.draw.rect(gameDisplay, color, ((display[0]+game.room.roomSize[0])/2,0,(display[0]-game.room.roomSize[0])/2,display[1]))
        pygame.draw.rect(gameDisplay, color, (0,(display[1]+game.room.roomSize[1])/2,display[0],(display[1]-game.room.roomSize[1])/2))
        self.player.drawPlayerUI()
        self.room.drawRoomUI()
        self.floor.drawMinimap()
        for drawFunction in self.drawFunctionQ:
            drawFunction[0]()
            drawFunction[1]-=1
            if(drawFunction[1]<=0):
                self.drawFunctionQ.remove(drawFunction) 

class Wall():

    def __init__(self, x, y, width, height):
        self.x = x
        self.y = y
        self.width = width
        self.height = height

    def adjust(self, other):#, proj=0):
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

                if dx*dx<dy*dy: # (abs slow?)
                    other.x-=dx
                    other.edge(verticalWall=True)
                    return "x"
                else:
                    other.y-=dy
                    other.edge(verticalWall=False)
                    return "y"

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        pygame.draw.rect(gameDisplay, (30,30,30), (pos[0]-self.width//2, pos[1]-self.height//2, self.width, self.height),0)

class Player():

    radius = 20
    hiteffectImage = loadTexture("player/hiteffect.png",128)
    fireHiteffectImage = loadTexture("player/firehiteffect.png",128)

    burningImage = loadTexture("enemies/fire.png", 128)
    frozenImage = loadTexture("enemies/ice.png", 128)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xv = 0 #for carpet
        self.yv = 0
        self.xdir = 1 #senaste man tittade
        self.ydir = 0
        self.dx = 0
        self.dy = 0
        self.fakeX = x #det de tror
        self.fakeY = y
        self.maxhp = 3+7*EZ
        self.hp = 3+7*EZ
        self.state = 0 #0:idle, 1:atak, 2:roll, (hitstun??)
        self.stateTimer = 0
        self.invincibility = 0
        self.invisibility = 0
        self.burning = 0
        self.image = self.idleImage
        self.imageDir = 1

        self.coins = 0
        self.movementSpeed = 1.5
        self.rollSpeed = 4
        self.fanRoll = 0 #3?
        self.swipeRange = 20
        self.lifeSteal = 0
        self.icecrystal = 0
        self.crystal = 0
        self.mosscrystal = 0
        self.projBounces = 0
        self.iceBody = 0
        self.freezeDamage=0
        self.freezeTime=60
        self.attackDamage=1
        self.fireSword = 0
        self.magicWand = 0
        self.magnet = 0
        self.piggyBank = 0
        self.fireStar = 0
        self.shockLink = 0
        self.spirality = 0
        self.carpet = 0
        self.library = 0
        self.projectileSize = 1

        self.furyBuff=0 # Only Warrior
        self.furyTime=0 # Only Warrior

        self.shownItems = {} # fill it with Class:num

    def getKill(self,enemy):
        for i in range(self.crystal):
            a = random.random()*6.28
            xv, yv = (math.cos(a),math.sin(a))
            game.room.projectiles.append(Ruby(self.x, self.y, xv*3, yv*3))

    def edge(self, verticalWall=False):
        pass

    def fire(self,duration=30):
        self.burning = max(self.burning, duration)

    def update(self):
        pressed = pygame.key.get_pressed()

        if self.invincibility>0:
            self.invincibility-=1
        if(self.burning>0):
            self.hurt(0.02)
            self.burning-=1
        elif self.invisibility:
            if random.random()<0.02:
                self.fakeX = random.randint(100, game.room.roomSize[0])
                self.fakeY = random.randint(100, game.room.roomSize[1])
        else:
            self.fakeX = self.x
            self.fakeY = self.y

        # IDLE
        if self.state == 0:
            self.stateTimer+=1
            self.basicMove()
            if (pressed[pygame.K_SPACE] or pressed[pygame.K_j]) and not self.invisibility:
                self.state = 1
                self.stateTimer = 0
            if pressed[pygame.K_LSHIFT] or pressed[pygame.K_k]:
                self.state = 2
                self.stateTimer = 0
            if pressed[pygame.K_e] or pressed[pygame.K_l]:
                self.state = 3
                self.stateTimer = 0

        # HURT
        if self.hp <= 0:
            self.state = -1
            if not Sound.playedHorrorSound:
                Sound.horrorSound.play()
                Sound.playedHorrorSound = True
                self.deathTimer = 0
            self.deathTimer += 1
            if self.deathTimer>122:
                game.gameOver(lose=True)

        if self.state == -1:
            self.stateTimer+=1
            if self.stateTimer>=20:
                if self.hp <= 0:
                    pass
                else:
                    self.image = self.idleImage
                    self.state = 0

        self.xv *=0.9
        self.yv *=0.9
        self.x += self.xv
        self.y += self.yv

        # WALLS
        if(self.x>game.room.roomSize[0]):
            if(game.room.links[1] and not game.room.locked):
                game.room=game.room.links[1]
                game.room.loadRoom()
                self.x=10
                game.gatherAllies()
            else:
                self.x=game.room.roomSize[0]
        elif(self.x<0):
            if(game.room.links[3] and not game.room.locked):
                game.room=game.room.links[3]
                game.room.loadRoom()
                self.x=game.room.roomSize[0]-10
                game.gatherAllies()
            else:
                self.x=0
        elif(self.y>game.room.roomSize[1]):
            if(game.room.links[2] and not game.room.locked):
                game.room=game.room.links[2]
                game.room.loadRoom()
                self.y=10
                game.gatherAllies()
            else:
                self.y=game.room.roomSize[1]
        elif(self.y<0):
            if(game.room.links[0] and not game.room.locked):
                game.room=game.room.links[0]
                game.room.loadRoom()
                self.y=game.room.roomSize[1]-10
                game.gatherAllies()
            else:
                self.y=0

        for wall in game.room.walls:
            wall.adjust(self)

    def basicMove(self, spdMult=1):
        speed = self.movementSpeed+self.furyBuff
        if game.room.harmlessRoom:
            speed = max(2.2, speed) #speed in empty rooms
            
        pressed = pygame.key.get_pressed()
        dx = (pressed[pygame.K_d] or pressed[pygame.K_RIGHT]) - (pressed[pygame.K_a] or pressed[pygame.K_LEFT])
        dy = (pressed[pygame.K_s] or pressed[pygame.K_DOWN]) - (pressed[pygame.K_w] or pressed[pygame.K_UP])
        if dx or dy: #do movement in direction and anim
            if dx and self.state==0:
                self.imageDir = (dx+1)//2
            if dx and dy:
                dx, dy = dx*0.707, dy*0.707
            if not self.carpet:
                self.x += dx*speed*spdMult
                self.y += dy*speed*spdMult
                self.image = [self.idleImage,self.walkImages[0],self.idleImage,self.walkImages[1]][int(self.stateTimer*speed//8)%4]
            else: #carpet
                self.xv += dx*speed *(0.05*(self.carpet+2))
                self.yv += dy*speed *(0.05*(self.carpet+2))
                self.image = self.walkImages[0]
            if self.state==0:
                self.xdir = dx
                self.ydir = dy
        else:
            self.image = self.idleImage
        self.dx = dx
        self.dy = dy

    def applyAttackEffects(self, targets):
        alreadyHit=[]
        for target in targets:
            alreadyHit.append(target)
            if(target.burning>0):
                damage = (self.attackDamage+self.furyBuff)*(1+self.fireStar)
            else:
                damage = self.attackDamage+self.furyBuff
            target.hurt(damage)
            if self.lifeSteal>0:
                self.heal(damage*self.lifeSteal)
            if self.fireSword:
                target.fire(self.fireSword*30)
        if(len(targets)>0):
            target=random.choice(targets)
            for i in range(self.shockLink):
                targets = game.findEnemies(target.x, target.y, 80)
                targets=[target for target in targets if (target not in alreadyHit)]
                if(len(targets)>0):
                    oldPos=((display[0]-game.room.roomSize[0])/2+target.x, (display[1]-game.room.roomSize[1])/2+target.y)
                    target=random.choice(targets)
                    newPos=((display[0]-game.room.roomSize[0])/2+target.x, (display[1]-game.room.roomSize[1])/2+target.y)
                    target.hurt()
                    alreadyHit.append(target)
                    def createDrawShock(oldPos,newPos):
                        def drawShock():
                            pygame.draw.line(gameDisplay, (250+random.random()*5,250+random.random()*5,0), oldPos, newPos, random.randint(8,9))
                        return drawShock
                    game.drawFunctionQ.append([createDrawShock(oldPos,newPos),10])

                else:
                    break

        """
        for i in range(self.icecrystal):
            if random.random()<0.5:
                game.room.projectiles.append(Sapphire(attackX,attackY,self.xdir*3+random.random()-0.5,self.ydir*3+random.random()-0.5))
        for i in range(self.crystal):
            if random.random()<0.5:
                game.room.projectiles.append(Ruby(attackX,attackY,self.xdir*3+random.random()-0.5,self.ydir*3+random.random()-0.5))
        """

    def heal(self, damage):
        self.hp = min(self.hp+damage, self.maxhp)

    def hurt(self, damage=1):
        self.hp-=damage
        if damage>0.1:
            self.image = self.hurtImage
            self.invincibility = 60
            self.state = -1
            self.stateTimer = 0
            if self.iceBody:
                targets = game.findEnemies(self.x, self.y, self.radius*self.iceBody*2)
                for target in targets:
                    target.freeze()

    def draw(self):
        shakeX = random.randint(-int(2*self.furyBuff),int(2*self.furyBuff))
        shakeY = random.randint(-int(2*self.furyBuff),int(2*self.furyBuff))
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x+shakeX),int((display[1]-game.room.roomSize[1])/2+self.y+shakeY))
        #pygame.draw.circle(gameDisplay, (100,100,200), (self.x, self.y), self.radius)
        
        # YOU
        if self.burning>0:
            gameDisplay.blit(self.burningImage, (int(pos[0]) - 128//2, int(pos[1]) - 128//2))
        for i in range(self.carpet):
            gameDisplay.blit(Carpet.images[random.randint(0,1)], (int(pos[0]) - Carpet.imageSize//2, int(pos[1]+16+8*(self.carpet-i-1)) - Carpet.imageSize//2))
        if self.freezeDamage:
            gameDisplay.blit(ColdCore.image, (int(pos[0]) - ColdCore.imageSize//2, int(pos[1]) - ColdCore.imageSize//2))
        if self.stateTimer%2==0 or not (self.invincibility or self.invisibility):
            gameDisplay.blit(self.image[self.imageDir], (pos[0] - self.imageSize//2, pos[1]-8 - self.imageSize//2))
        if self.iceBody:
            gameDisplay.blit(IceShield.image, (int(pos[0]+8-16*self.imageDir) - IceShield.imageSize//2, int(pos[1]+8) - IceShield.imageSize//2))
        if JesterHat in self.shownItems:
            gameDisplay.blit(JesterHat.image, (int(pos[0]) - JesterHat.imageSize//2, int(pos[1]-32) - JesterHat.imageSize//2))
    def drawPlayerUI(self):
        #hp
        pygame.draw.rect(gameDisplay, (200,0,0),(30,30,150,30))
        if self.hp>0:
            pygame.draw.rect(gameDisplay, (0,200,0),(30,30,150*(self.hp/self.maxhp)**1.1, 30))
        #items
        item_vertical_spacing = 50
        item_horizontal_spacing = 20
        for i in range(len(self.shownItems)):
            clss=list(self.shownItems.keys())[i]
            number_of_copies = self.shownItems[clss]
            for j in range(number_of_copies):
                gameDisplay.blit(clss.image,(50+item_horizontal_spacing*j-clss.imageSize/2,100+item_vertical_spacing*i-clss.imageSize/2))
            
            if self.library>0:#(self.shownItems[clss]>0):
                textsurface = myfont.render(clss.libraryString, False, (0, 0, 0))
                gameDisplay.blit(textsurface,(90+j*item_horizontal_spacing,90+item_vertical_spacing*i))
            
        #text
        textsurface = myfont.render("floor: "+str(game.depth) , False, (0, 0, 0))
        gameDisplay.blit(textsurface,(display[0]-150,200))
        textsurface = myfont.render("coins: "+str(self.coins) , False, (0, 0, 0))
        gameDisplay.blit(textsurface,(200,30))

class Warrior(Player):
    unlocked = True
    unlock_description = "This character should always be unlocked. Please contact Bror Persson 0709419442 to fix your save-file."
    description = ["The Warriors are sword-wielding brawlers that often venture into the dungeon.",
        "",
        "Abilities:",
        " J : A classic sword attack.",
        " K : A combat roll that can dodge attacks.",
        " L : Powerful spinning attack that you can charge.",
        "",
        "Passive ability:",
        " Warriors build up rage when killing multiple enemies in quick succession,",
        " allowing them to run faster and hit harder.",
    ]
    imageSize = 128
    idleImage = loadTexture("player/warrior/player.png", imageSize, mirror=True)
    hurtImage = loadTexture("player/warrior/hurt.png", imageSize, mirror=True)
    walkImages = [loadTexture("player/warrior/walk1.png", imageSize, mirror=True), loadTexture("player/warrior/walk2.png", imageSize, mirror=True)]
    attackImages = [loadTexture("player/warrior/strike1.png", imageSize, mirror=True), loadTexture("player/warrior/strike2.png", imageSize, mirror=True)]
    rollImages = [loadTexture("player/warrior/roll1.png", imageSize, mirror=True), loadTexture("player/warrior/roll2.png", imageSize, mirror=True),loadTexture("player/warrior/roll3.png", imageSize, mirror=True)]

    swipeImage = loadTexture("player/warrior/swipe.png", imageSize)
    fireSwipeImage = loadTexture("player/warrior/fireswipe.png", imageSize)
    def update(self):
        super().update()

        # ATAKK
        if self.state == 1:
            self.basicMove(spdMult=0)
            self.stateTimer+=1
            if self.stateTimer<15:
                self.image = self.attackImages[0]
            elif self.stateTimer == 15:
                attackX = self.x+self.xdir*self.swipeRange
                attackY = self.y+self.ydir*self.swipeRange
                targets = game.findEnemies(attackX, attackY, 30)
                self.applyAttackEffects(targets)
            elif self.stateTimer<25:
                self.image = self.attackImages[1]
            elif self.stateTimer>=25:
                self.state = 0

        # ROLL
        if self.state == 2:
            self.stateTimer+=1
            if self.stateTimer<20:
                self.invincibility=1
                self.image = self.rollImages[self.stateTimer//8]
                self.x+=self.xdir*self.rollSpeed#*self.movementSpeed
                self.y+=self.ydir*self.rollSpeed#*self.movementSpeed
                # fanRoll
                if self.fanRoll:
                    targets = game.findEnemies(self.x,self.y,self.radius*self.fanRoll)
                    for target in targets:
                        target.x-=self.xdir*self.fanRoll
                        target.y-=self.ydir*self.fanRoll
                    targets = game.findProjectiles(self.x,self.y,self.radius*self.fanRoll)
                    for target in targets:
                        target.xv=-self.xdir*self.fanRoll
                        target.yv=-self.ydir*self.fanRoll

            elif self.stateTimer<24:
                self.image = self.rollImages[2]
                self.fakeX = self.x
                self.fakeY = self.y
            elif self.stateTimer<30:
                self.image = self.walkImages[1]
            else:
                self.state = 0

        # ???
        if self.state == 3:
            self.basicMove(spdMult=0)
            self.stateTimer+=1
            if self.stateTimer<15:
                pressed = pygame.key.get_pressed()
                if pressed[pygame.K_e] or pressed[pygame.K_l]:
                    self.stateTimer-=1
                self.image = self.attackImages[0]
            elif self.stateTimer < 35:
                self.image = self.attackImages[1]
                if self.stateTimer % 5 == 0:
                    self.xdir, self.ydir = self.ydir, -self.xdir
                    attackX = self.x+self.xdir*(self.swipeRange+30)*0.5
                    attackY = self.y+self.ydir*(self.swipeRange+30)*0.5
                    targets = game.findEnemies(attackX, attackY, 20)#+self.swipeRange*0.6)
                    self.applyAttackEffects(targets)
            elif self.stateTimer<60:
                self.image = self.attackImages[1]
            elif self.stateTimer>=60:
                self.state = 0

        if(self.furyTime>0):
            self.furyTime-=1
        else:
            self.furyBuff=0


    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        #pygame.draw.circle(gameDisplay, (200,100,100), (self.x+self.xdir*self.swipeRange, self.y+self.ydir*self.swipeRange), 30)

        # SWIPE
        if self.state == 1:
            if 15<=self.stateTimer<=20:
                x = int(pos[0]+self.xdir*self.swipeRange)
                y = int(pos[1]+self.ydir*self.swipeRange)
                if not self.fireSword:
                    image = self.swipeImage
                else:
                    image = self.fireSwipeImage
                blitRotate(gameDisplay, image, (x,y), (self.imageSize//2, self.imageSize//2), math.atan2(-self.ydir,-self.xdir))
        # SPIN
        if self.state == 3:
            if 15<=self.stateTimer<=35:
                x = int(pos[0]+self.xdir*(self.swipeRange+30)*0.5)
                y = int(pos[1]+self.ydir*(self.swipeRange+30)*0.5)
                if not self.fireSword:
                    image = self.swipeImage
                else:
                    image = self.fireSwipeImage
                blitRotate(gameDisplay, image, (x,y), (self.imageSize//2, self.imageSize//2), math.atan2(-self.ydir,-self.xdir))
        super().draw()
    def getKill(self,enemy):
        super().getKill(enemy)
        if(self.furyTime>0):
            self.furyBuff+=0.5
        self.furyTime=180
class Ranger(Player):
    unlocked = False
    unlock_description = "Complete the game as a Warrior to unlock."
    description = ["The Rangers use rifles to keep the distance to their foes.",
        "",
        "Abilities:",
        " J : Fire the rifle.",
        " K : Reload the rifle.",
        " L : Jump into the air and stomp to push enemies away.",
        "",
        "Passive ability:",
        " The Rifle has three bullets.",
        " Once they run out you must reload the rifle to fire again.",
    ]
    radius = 16
    imageSize = 128
    blackImage = loadTexture("player/ranger/black.png", imageSize, mirror=True)
    idleImage = loadTexture("player/ranger/idle.png", imageSize, mirror=True)
    hurtImage = loadTexture("player/ranger/hurt.png", imageSize, mirror=True)
    walkImages = [loadTexture("player/ranger/walk1.png", imageSize, mirror=True), loadTexture("player/ranger/walk2.png", imageSize, mirror=True)]
    attackImages = [loadTexture("player/ranger/fire.png", imageSize, mirror=True), loadTexture("player/ranger/reload0.png", imageSize, mirror=True)]
    reloadImages = [loadTexture("player/ranger/reload1.png", imageSize, mirror=True), loadTexture("player/ranger/reload2.png", imageSize, mirror=True)]
    jumpImages = [loadTexture("player/ranger/jump.png", imageSize, mirror=True)]
    def __init__(self, x, y):
        super().__init__(x,y)
        self.maxAmmo = 3
        self.ammo=self.maxAmmo
        self.movementSpeed=1.5
        self.fastReload=False
    def update(self):
        super().update()
        pressed = pygame.key.get_pressed()

        # ATAKK
        if self.state == 1:
            self.basicMove(spdMult=0)
            if self.stateTimer==0:
                if(self.ammo>0):
                    Sound.shotSound.play()
                    self.image = self.attackImages[0]
                    if self.fireSword:
                        game.room.projectiles.append(FireBullet(self.x, self.y, self.xdir*8, self.ydir*8))
                    else:
                        game.room.projectiles.append(Bullet(self.x, self.y, self.xdir*8, self.ydir*8))
                    self.ammo-=1
                else:
                    self.state=0
        if self.state == 1:
            self.stateTimer+=1
            if self.stateTimer<3:
                self.image = self.attackImages[0]
            elif self.stateTimer<25:
                self.image = self.attackImages[1]
            elif self.stateTimer>=25:
                self.state = 0

        # RELOAD
        if self.state == 2:
            self.stateTimer+=1
            self.basicMove(0.1)
            if self.stateTimer==1:
                Sound.reloadSound.play()
            if self.stateTimer<10:
                
                self.image = self.attackImages[1]
                # fanRoll
                if self.fanRoll:
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
                self.ammo=self.maxAmmo
            elif self.stateTimer<38:
                self.image = self.reloadImages[0]
                if(pressed[pygame.K_LSHIFT] or pressed[pygame.K_k]):
                    self.fastReload=True
                else:
                    self.fastReload=False
            elif self.stateTimer<50:
                if((not (pressed[pygame.K_LSHIFT] or pressed[pygame.K_k])) and self.fastReload):
                    self.state = 0
                    self.fastReload=False
                self.image = self.idleImage
            elif self.stateTimer>=50:
                self.state = 0

        # STOMP
        if self.state == 3:
            self.stateTimer+=1
            self.basicMove(spdMult=0)
            if self.stateTimer<20:
                self.image = self.jumpImages[0]
                self.invincibility = 1
            elif self.stateTimer<30:
                self.image = self.idleImage
                targets = game.findEnemies(self.x,self.y,100)
                for target in targets:
                    hyp = math.sqrt((target.x-self.x)**2+(target.y-self.y)**2+1) #add 1 for fun #also to not divide by 0
                    ang = math.atan2((target.y-self.y),(target.x-self.x))
                    target.knockback = 4+self.fanRoll*4
                    target.knockbackAngle = ang
                    target.a = ang
                    target.xv = (target.x-self.x)/hyp*(self.fanRoll+1)
                    target.yv = (target.y-self.y)/hyp*(self.fanRoll+1)
                    target.xdir = (target.x-self.x)/hyp
                    target.ydir = (target.y-self.y)/hyp
                targets = game.findProjectiles(self.x,self.y,100)
                for target in targets:
                    hyp = math.sqrt((target.x-self.x)**2+(target.y-self.y)**2+1)
                    target.xv = (target.x-self.x)/hyp*(self.fanRoll+1)
                    target.yv = (target.y-self.y)/hyp*(self.fanRoll+1)
            elif self.stateTimer>=40:
                self.state = 0

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        if random.random()<0.5 and self.ammo and self.state==0:
            pygame.draw.line(gameDisplay, (255,0,0), pos,(pos[0]+self.xdir*500,pos[1]+self.ydir*500), 1)
        super().draw()
class Thief(Player):
    unlocked = False
    unlock_description = "Complete the game as a Ranger to unlock."
    description = ["The Thieves use stealth to avoid combat, and pick-pocket money from enemies without killing them.",
        "",
        "Abilities:",
        " J : Performs a basic knife stab.",
        " K : Toggles stealth mode.",
        " L : Pick-pocket an enemy. This makes the enemy drop their coin on the ground.",
        "",
        "Passive ability:",
        " While in stealth mode you cannot be seen by enemies, but they can still hit you.",
        " You cannot attack while in stealth mode, but you can still pick-pocket.",
    ]
    imageSize = 128
    blackImage = loadTexture("player/thief/black.png", imageSize, mirror=True)
    idleImage = loadTexture("player/thief/idle.png", imageSize, mirror=True)
    hurtImage = loadTexture("player/thief/hurt.png", imageSize, mirror=True)
    walkImages = [loadTexture("player/thief/walk1.png", imageSize, mirror=True), loadTexture("player/thief/walk2.png", imageSize, mirror=True)]
    attackImages = [loadTexture("player/thief/attack1.png", imageSize, mirror=True), loadTexture("player/thief/attack2.png", imageSize, mirror=True)]
    hideImages = [loadTexture("player/thief/hide.png", imageSize, mirror=True)]
    stealImages = [loadTexture("player/thief/steal1.png", imageSize, mirror=True),loadTexture("player/thief/steal2.png", imageSize, mirror=True)]

    swipeImage = loadTexture("player/thief/swipe.png", imageSize)
    fireSwipeImage = loadTexture("player/thief/fireswipe.png", imageSize)
    def update(self):
        super().update()
        pressed = pygame.key.get_pressed()

        # ATAKK
        if self.state == 1:
            self.stateTimer+=1
            self.basicMove(spdMult=0)
            if self.stateTimer<5:
                self.image = self.attackImages[0]
            elif self.stateTimer == 5:
                attackX = self.x+self.xdir*self.swipeRange
                attackY = self.y+self.ydir*self.swipeRange
                targets = game.findEnemies(attackX, attackY, 30)
                self.applyAttackEffects(targets)
            elif self.stateTimer<15:
                self.image = self.attackImages[1]
            elif self.stateTimer<20:
                self.image = self.attackImages[0]
            elif self.stateTimer<25:
                self.image = self.idleImage
            else:
                self.state = 0

        # HIDE
        if self.state == 2:
            self.stateTimer+=1
            if self.stateTimer<30:
                self.basicMove(spdMult=0.1)
                self.image = self.hideImages[0]
                # fanRoll
                if self.fanRoll:
                    targets = game.findEnemies(self.x,self.y,self.radius*self.fanRoll)
                    for target in targets:
                        target.x+=self.xdir*self.fanRoll
                        target.y+=self.ydir*self.fanRoll
                    targets = game.findProjectiles(self.x,self.y,self.radius*self.fanRoll)
                    for target in targets:
                        target.xv=self.xdir*self.fanRoll
                        target.yv=self.ydir*self.fanRoll
            elif self.stateTimer>=30:
                self.invisibility = not self.invisibility
                self.fakeX = self.x
                self.fakeY = self.y
                self.state = 0
                self.stateTimer = 0

        # STEAL
        if self.state == 3:
            self.stateTimer+=1
            self.basicMove(spdMult=0)
            if self.stateTimer<6:
                self.image = self.stealImages[0]
            elif self.stateTimer==6:
                attackX = self.x+self.xdir*20
                attackY = self.y+self.ydir*20
                targets = game.findEnemies(attackX, attackY, 30)
                #target = random.choice(targets)
                for target in targets:
                    if target.coins:
                        target.coins-=1
                        game.room.items.append(Coin(target.x+random.randint(-8,8),target.y+random.randint(-8,8),))
                        Sound.pickpocketSound.play()
            elif self.stateTimer<11:
                self.image = self.stealImages[1]
            elif self.stateTimer<15:
                self.image = self.idleImage
            elif self.stateTimer>=15:
                self.state = 0

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        #pygame.draw.circle(gameDisplay, (200,100,100), (self.x+self.xdir*self.swipeRange, self.y+self.ydir*self.swipeRange), 30)

        # SWIPE
        if self.state == 1:
            if 5<=self.stateTimer<=10:
                x = int(pos[0]+self.xdir*self.swipeRange)
                y = int(pos[1]+self.ydir*self.swipeRange)
                if not self.fireSword:
                    image = self.swipeImage
                else:
                    image = self.fireSwipeImage
                blitRotate(gameDisplay, image, (x,y), (self.imageSize//2, self.imageSize//2), math.atan2(-self.ydir,-self.xdir))
        super().draw()
class Mage(Player):
    unlocked = False
    unlock_description = "Complete the game as a Thief to unlock."
    description = ["The Mages use powerful magic to overcome their foes.",
        "",
        "Abilities:",
        " J : Fire a slow-moving bolt of water.",
        " K : Teleport a short distance.",
        " L : Waive your arms and chant to make your enemies run away in fear.",
        "",
        "Passive ability:",
        " You can walk slowly while using your abilities, instead of completely stopping.",
    ]
    imageSize = 128
    blackImage = loadTexture("player/mage/black.png", imageSize, mirror=True)
    idleImage = loadTexture("player/mage/player.png", imageSize, mirror=True)
    hurtImage = loadTexture("player/mage/hurt.png", imageSize, mirror=True)
    walkImages = [loadTexture("player/mage/walk1.png", imageSize, mirror=True), loadTexture("player/mage/walk2.png", imageSize, mirror=True)]
    attackImages = [loadTexture("player/mage/attack1.png", imageSize, mirror=True), loadTexture("player/mage/attack2.png", imageSize, mirror=True)]
    tpImages = [loadTexture("player/mage/teleport1.png", imageSize, mirror=True),loadTexture("player/mage/teleport2.png", imageSize, mirror=True)]
    magicImages = [loadTexture("player/mage/magic.png", imageSize, mirror=True),loadTexture("player/mage/magic2.png", imageSize, mirror=True)]

    def __init__(self, x,y):
        super().__init__(x,y)
        self.mana = 0
        self.maxmana = 10
        self.MANAMECHANIC = False

    def update(self):
        super().update()
        pressed = pygame.key.get_pressed()
        if self.MANAMECHANIC:
            if game.room.harmlessRoom:
                self.mana += 0.05
            else:
                self.mana += 0.02
            self.mana = min(self.mana, self.maxmana)
        

        # ATTACK
        if self.state == 1:
            self.stateTimer+=1
            if self.stateTimer==1 and self.MANAMECHANIC:
                if self.mana < 2:
                    self.state = 0
                else:
                    self.mana -= 2
            else:
                self.basicMove(spdMult=0.5)
                if self.stateTimer<10:
                    self.image = self.attackImages[0]
                elif self.stateTimer == 10:
                    self.image = self.attackImages[1]
                    attackX = self.x+self.xdir*self.swipeRange
                    attackY = self.y+self.ydir*self.swipeRange
                    if self.fireSword:
                        game.room.projectiles.append(FireOrb(self.x, self.y - 8, self.xdir*3+self.xv, self.ydir*3+self.yv))
                    else:
                        game.room.projectiles.append(Orb(self.x, self.y - 8, self.xdir*3+self.xv, self.ydir*3+self.yv))

                elif self.stateTimer<40:
                    self.image = self.attackImages[1]
                elif self.stateTimer<45:
                    self.image = self.attackImages[0]
                elif self.stateTimer<50:
                    self.image = self.idleImage
                else:
                    self.state = 0

        # TELEPORT
        if self.state == 2:
            self.stateTimer+=1
            if self.stateTimer==1 and self.MANAMECHANIC:
                if self.mana < 5:
                    self.state = 0
                else:
                    self.mana -= 5
            else:
                if self.stateTimer<10:
                    self.basicMove(spdMult=0.5)
                    self.image = self.tpImages[0]
                elif self.stateTimer<20:
                    self.image = self.tpImages[1]
                elif self.stateTimer==20:
                    self.image = self.tpImages[1]
                    tp_distance = 100
                    safe_guard = 40
                    self.x += self.xdir*tp_distance
                    self.y += self.ydir*tp_distance
                    self.x = max(self.x, safe_guard)
                    self.y = max(self.y, safe_guard)
                    self.x = min(self.x, game.room.roomSize[0]-safe_guard)
                    self.y = min(self.y, game.room.roomSize[1]-safe_guard)
                elif self.stateTimer<30:
                    self.image = self.tpImages[1]
                elif self.stateTimer<40:
                    self.basicMove(spdMult=0.5)
                    self.image = self.tpImages[0]
                elif self.stateTimer<45:
                    self.basicMove(spdMult=0.5)
                    self.image = self.idleImage
                elif self.stateTimer>=45:
                    self.state = 0

        # SCARE
        if self.state == 3:
            self.stateTimer+=1
            if self.stateTimer==1 and self.MANAMECHANIC:
                if self.mana < 5:
                    self.state = 0
                else:
                    self.mana -= 5
            else:
                self.basicMove(spdMult=0.5)
                if self.stateTimer==10:
                    targets = game.findEnemies(self.x, self.y, 300)
                    #target = random.choice(targets)
                    for target in targets:
                        target.scared = 40
                if self.stateTimer<5:
                    self.image = self.attackImages[0]
                elif self.stateTimer<55:
                    self.image = self.magicImages[(self.stateTimer//10)%2]

                    # fanRoll
                    if self.fanRoll:
                        targets = game.findEnemies(self.x,self.y,self.radius*self.fanRoll)
                        for target in targets:
                            target.x+=self.xdir*self.fanRoll
                            target.y+=self.ydir*self.fanRoll
                        targets = game.findProjectiles(self.x,self.y,self.radius*self.fanRoll)
                        for target in targets:
                            target.xv=self.xdir*self.fanRoll
                            target.yv=self.ydir*self.fanRoll
                elif self.stateTimer<60:
                    self.image = self.attackImages[0]
                elif self.stateTimer>=60:
                    self.state = 0

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        #pygame.draw.circle(gameDisplay, (200,100,100), (self.x+self.xdir*self.swipeRange, self.y+self.ydir*self.swipeRange), 30)
        super().draw()

    def drawPlayerUI(self):
        super().drawPlayerUI()
        if self.MANAMECHANIC:
            w = 150
            pygame.draw.rect(gameDisplay, (0,100,100),((display[0]-w)//2, 30, w, 30))
            pygame.draw.rect(gameDisplay, (0,200,200),((display[0]-w)//2, 30, w*(self.mana/self.maxmana), 30))

def load_save_file():
    try:
        with open(os.path.join("roguelikeGameFiles","savefile.txt"), "r") as save_file:
            for i in range(4):
                line = save_file.readline()
                if "1" in line:
                    [Warrior,Ranger,Thief,Mage][i].unlocked = True
                if len(unlockedClasses())>3:
                    badItems.append(ClassChange)
    except Exception as e:
        print("no savefile")
def save_save_file():
    with open(os.path.join("roguelikeGameFiles","savefile.txt"), "w") as save_file:
        for c in allClasses:
            save_file.write(c.__name__ + ": " + str(int(c.unlocked)) + "\n")

allClasses = [Warrior, Ranger, Thief, Mage]

def unlockedClasses():
    r = []
    for i in allClasses:
        if i.unlocked:
            r.append(i)
    return r


class Ally():

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xdir=1
        self.ydir=0
        self.facing=1
        self.state = 0
        self.stateTimer = 0
        self.movementSpeed = 1.5
    
    def update(self):
        if(self.x>game.room.roomSize[0]):
            self.x=game.room.roomSize[0]
            self.xdir*=-1
        elif(self.x<0):
            self.x=0
            self.xdir*=-1
        elif(self.y>game.room.roomSize[1]):
            self.y=game.room.roomSize[1]
            self.ydir*=-1
        elif(self.y<0):
            self.y=0
            self.ydir*=-1

        for wall in game.room.walls:
            wall.adjust(self)

    def edge(self,verticalWall=False):
        if verticalWall:
            self.xdir*=-1
        else:
            self.ydir*=-1

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        gameDisplay.blit(self.image[self.facing],(pos[0] - self.imageSize//2, pos[1] - self.imageSize//2))

class WaterSpirit(Ally):

    radius = 16
    imageSize = 128
    image = loadTexture("allies/waterspirit.png",imageSize,mirror=True)

    def update(self):
        if random.random()<0.8:
            self.xdir = game.player.xdir
            self.x+=self.xdir*self.movementSpeed
            self.ydir = game.player.ydir
            self.y+=self.ydir*self.movementSpeed
            if self.xdir<0:
                self.facing=0
            if self.xdir>0:
                self.facing=1

        super().update()

        self.stateTimer+=1
        if self.stateTimer>=90:
            game.room.projectiles.append(Sapphire(self.x,self.y,self.xdir*3,self.ydir*3))
            self.stateTimer=0
class Jester(Ally):

    radius = 24
    imageSize = 128
    image = loadTexture("allies/jester.png",imageSize,mirror=True)

    def update(self):
        if random.random()<0.4:
            x, y = game.player.x, game.player.y
            hyp = math.sqrt((x-self.x)**2+(y-self.y)**2)
            if hyp == 0:
                return
            self.xdir = (x-self.x)/hyp
            self.ydir = (y-self.y)/hyp
            self.x += self.xdir*self.movementSpeed
            self.y += self.ydir*self.movementSpeed
            if self.xdir<0:
                self.facing=0
            if self.xdir>0:
                self.facing=1

        game.player.fakeX = self.x
        game.player.fakeY = self.y

        super().update()
class FireSpirit(Ally):

    radius = 16
    imageSize = 128
    images = [loadTexture("allies/fire.png",imageSize,mirror=True),loadTexture("allies/fire2.png",imageSize,mirror=True)]
    image = random.choice(images)

    def update(self):
        if random.random()<0.5:
            self.facing = random.randint(0,1)
            self.image = random.choice(self.images)

            hyp = math.sqrt((game.player.x-self.x)**2+(game.player.y-self.y)**2)
            if hyp>0:
                self.xdir += (game.player.x-self.x)/hyp *0.1
                self.ydir += (game.player.y-self.y)/hyp *0.1
            self.xdir*=0.99
            self.ydir*=0.99
        self.x+=self.xdir*self.movementSpeed
        self.y+=self.ydir*self.movementSpeed

        super().update()

        if random.random()<0.5:
            for enemy in game.findEnemies(self.x,self.y,self.radius):
                enemy.fire(30)

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        pos2=(int((display[0]-game.room.roomSize[0])/2+game.player.x),int((display[1]-game.room.roomSize[1])/2+game.player.y))
        pygame.draw.line(gameDisplay, (150,100,50), pos, pos2, 4)
        super().draw()

class Enemy():

    frozenImage = loadTexture("enemies/ice.png", 128)
    burningImage = loadTexture("enemies/fire.png", 128)

    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.xdir = 1
        self.ydir = 0
        self.knockback = 0
        self.knockbackAngle = 0
        self.state = 0 # -2 frozen, -1:hurt, 0:idle
        self.stateTimer = 0
        self.movementSpeed = 1
        self.invincibility= 0
        self.burning = 0
        self.harmless = False
        self.scared = 0
        self.coins = 1
    def die(self):
        game.player.getKill(self)
        game.remove(self,game.room.enemies)
        for i in range(self.coins):
            game.room.items.append(Coin(self.x+random.randint(-8,8),self.y+random.randint(-8,8)))
        for i in range(game.player.icecrystal):
            a = random.random()*6.28
            xv, yv = (math.cos(a),math.sin(a))
            game.room.projectiles.append(Sapphire(self.x, self.y, xv*3, yv*3))
    def freeze(self):
        if(self.hp>0):
            self.state=-2
            self.stateTimer = max(self.stateTimer, game.player.freezeTime)
    def fire(self,duration=30):
        self.burning = max(self.burning, duration)
    def edge(self, verticalWall=False):
        pass
    def update(self):


        if self.scared>0:
            self.scared-=1

        if self.knockback>0:
            self.x += math.cos(self.knockbackAngle)*self.knockback
            self.y += math.sin(self.knockbackAngle)*self.knockback
            self.knockback -= 1

        if(self.x>game.room.roomSize[0]):
            self.x=game.room.roomSize[0]
            self.xdir*=-1
        elif(self.x<0):
            self.x=0
            self.xdir*=-1
        elif(self.y>game.room.roomSize[1]):
            self.y=game.room.roomSize[1]
            self.ydir*=-1
        elif(self.y<0):
            self.y=0
            self.ydir*=-1

        for wall in game.room.walls:
            wall.adjust(self)
        
        if self.state == -2:
            self.burning=0
            self.image = self.idleImage
            self.stateTimer-=1
            if self.stateTimer <=0:
                self.state = 0
                if game.player.freezeDamage:
                    Sound.glassSound.play()
                    self.hurt(game.player.freezeDamage)
        if(self.burning>0):
            self.hurt(0.02)
            self.burning-=1
        if self.invincibility:
            self.invincibility-=1

    def basicMove(self,spdMult=1,target=None):
        if self.scared:
            spdMult=-1
        if target==None:
            target=game.player
        if target == game.player:
            x = target.fakeX
            y = target.fakeY
        else:
            x = target.x
            y = target.y
        hyp = math.sqrt((x-self.x)**2+(y-self.y)**2)
        if hyp == 0:
            return #to not set xdir and ydir to 0 because then they shoot projs that are still
        else:
            self.xdir = (x-self.x)/hyp
            self.ydir = (y-self.y)/hyp
            self.x += self.xdir*self.movementSpeed*spdMult
            self.y += self.ydir*self.movementSpeed*spdMult

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        if self.state==-2:
            gameDisplay.blit(self.frozenImage, (int(pos[0]) - 128//2, int(pos[1]) - 128//2))
        if self.burning>0:
            gameDisplay.blit(self.burningImage, (int(pos[0]) - 128//2, int(pos[1]) - 128//2))
        gameDisplay.blit(self.image, (int(pos[0]) - self.imageSize//2, int(pos[1]) - self.imageSize//2))
        #pygame.draw.circle(gameDisplay, (100,100,200), (self.x, self.y), self.radius)

    def heal(self, damage):
        self.hp = min(self.hp+damage, self.maxhp)
    def hurt(self,damage=None,knockback=None,attacker=None):
        if(damage==None):
            damage=game.player.attackDamage
        if knockback==None:
            self.knockback = damage*8
            if attacker==None:
                attacker = game.player
            self.knockbackAngle = math.atan2(self.y - attacker.y, self.x - attacker.x)
        if damage>0.3:
            random.choice(Sound.hitSounds).play()
            pos=((display[0]-game.room.roomSize[0])/2+self.x-64, (display[1]-game.room.roomSize[1])/2+self.y-64)           
            def createDrawHit(pos):
                if self.burning and game.player.fireStar:
                    def drawHit():
                        gameDisplay.blit(Player.fireHiteffectImage,pos)
                else:
                    def drawHit():
                        gameDisplay.blit(Player.hiteffectImage,pos)
                return drawHit
            game.drawFunctionQ.append([createDrawHit(pos),2])

        self.hp-=damage
        if self.hp<=0:
            self.die()

class Chest(Enemy):

    radius = 48
    imageSize = 128
    idleImage = loadTexture("enemies/chest1.png", imageSize)
    hurtImage = loadTexture("enemies/chest2.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.hp = 1
        self.coins = 0
        self.lootTable = allItems
        self.harmless = True
    #def fire(*a):
     #   pass
    def freeze(*a):
        pass
    def update(self):
        super().update()
        #HURT
        if self.state == -1:
            self.image = self.hurtImage
            self.stateTimer-=1 #här går den neråt
            if self.stateTimer<=0:
                if self.hp<=0:
                    loot = random.choice(self.lootTable)
                    if loot:
                        if issubclass(loot,Enemy):
                            game.room.enemies.append(loot(self.x,self.y))
                        else:
                            game.room.items.append(loot(self.x,self.y))
                    elif random.random()<0.2:
                        game.room.projectiles.append(Explosion(self.x,self.y))
                    game.remove(self,game.room.enemies)
                else:
                    self.state = 0
                    self.image = self.idleImage
        
    def die(self):
        self.state = -1
        self.stateTimer = 20
class Animus(Enemy):

    radius = 24
    imageSize = 64
    idleImage = loadTexture("enemies/animus.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 2
        self.hp = 2
        self.transformationCharger = 0 # for less variance in time

    def update(self):
        if self.state == 0:
            if self.hp==2:
                self.basicMove()
            else:
                self.basicMove(spdMult=-0.5)
            self.x += random.randint(-1,1)
            self.y += random.randint(-1,1)

        super().update()

        #if random.random()<0.001:
         #   game.room.enemies.append(Animus(self.x,self.y))

        #ATTACK
        if self.state == 0:
            if self.hp<2 and random.random()<0.01:
                self.transformationCharger+=1
                if self.transformationCharger>5:
                    game.remove(self,game.room.enemies)
                    port = Portal(self.x,self.y)
                    game.room.enemies.append(port)
                    port.coins = self.coins
                    port.state = 2
            else:
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
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 2
        self.hp = 2
        self.movementSpeed = 0.8

    def update(self):
        super().update()
        
        #IDLE
        if self.state == 0:
            self.basicMove()
            if game.findPlayer(self.x, self.y, 16, fool=True):
                self.state = 1
                self.stateTimer = 0

        #ATTACK
        if self.state == 1:
            self.stateTimer+=1
            self.basicMove(spdMult=0.5)
            if self.stateTimer==1:
                self.image = self.attackImages[0]
            elif self.stateTimer==10:
                self.image = self.attackImages[1]
            elif self.stateTimer==20:
                self.image = self.attackImages[2]
                target = game.findPlayer(self.x, self.y, 12)
                if target:
                    target.hurt(0.7)
            elif self.stateTimer==35:
                self.image = self.attackImages[1]
            elif self.stateTimer==50:
                self.image = self.attackImages[0]
            elif self.stateTimer>70:
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
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 3
        self.hp = 3
        self.chief = chief
        if chief:
            self.friend = Robot(random.randint(100,game.room.roomSize[0]-100),random.randint(100,game.room.roomSize[1]-100), chief=False)
            game.room.enemies.append(self.friend)
            self.friend.friend = self

    def update(self):

        super().update()

        #IDLE
        if self.state == 0:
            #self.x += random.randint(-2,2)
            #self.y += random.randint(-2,2)
            self.image = random.choice([self.idleImage, self.walkImage])
            if self.friend and self.friend.state==0:
                self.basicMove(spdMult=0.5)
                self.basicMove(spdMult=-0.5, target=self.friend)
                #just beamin
                if self.chief: #unnecessary
                    randomPoint = random.random()
                    if game.findPlayer(self.x+10+(self.friend.x-self.x)*randomPoint, self.y+10+(self.friend.y-self.y)*randomPoint, 4):
                        game.player.hurt()
            else:
                self.basicMove(spdMult=-1)
                #just shootin
                if random.random()<0.05:
                    self.state = 1
                    self.stateTimer = 0

        # SHOOT
        if self.state == 1:
            self.stateTimer+=1
            if self.stateTimer==1:
                self.image = self.idleImage
            elif self.stateTimer==30:
                self.image = self.hurtImage
            elif self.stateTimer==70:
                self.image = self.fireImage
                hyp = math.sqrt((self.x-game.player.fakeX)**2 + (self.y-game.player.fakeY)**2)
                dx = (game.player.fakeX-self.x)/hyp
                dy = (game.player.fakeY-self.y)/hyp
                game.room.projectiles.append(Missile(self.x, self.y, dx*3, dy*3))
            elif self.stateTimer==80:
                self.image = self.idleImage
            elif self.stateTimer>100:
                self.state = 0

    def die(self):
        super().die()
        if self.friend:
            self.friend.friend = None

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        if self.state == 0 and self.friend and self.friend.state == 0 and self.chief:
            clonepos=(int((display[0]-game.room.roomSize[0])/2+self.friend.x),int((display[1]-game.room.roomSize[1])/2+self.friend.y))
            pygame.draw.line(gameDisplay, (200,200,200+random.random()*55), (pos[0]+10,pos[1]), (clonepos[0]+10, clonepos[1]), random.randint(1,8))
        super().draw()
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
        self.maxhp = 4
        self.hp = 4
        self.coins = 2
        self.movementSpeed = 0.5

    def update(self):
        super(SkuggVarg, self).update()

        #IDLE
        if self.state == 0:
            self.basicMove()
            if game.findPlayer(self.x, self.y, 64, fool=True):
                self.state = 1
                self.stateTimer = 0

        #ATTACK
        if self.state == 1:
            self.stateTimer+=1
            if self.stateTimer<32:
                self.x+=self.xdir*2
                self.y+=self.ydir*2
                self.image = self.attackImages[self.stateTimer//8]
            elif self.stateTimer==32:
                self.image = self.attackImages[4]
                target = game.findPlayer(self.x, self.y, 32)
                if target:
                    target.hurt()
            elif 32<self.stateTimer<80:
                self.image = self.attackImages[(80-self.stateTimer)//12]
            elif self.stateTimer>=80:
                self.image = self.idleImage
                self.state = 0
class Schmitt(Enemy):

    radius = 32
    imageSize = 256
    idleImage = loadTexture("enemies/axereaper/idle.png", imageSize)
    attackImages = [loadTexture("enemies/axereaper/attack"+str(i)+".png", 256) for i in (1,2)]

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 5
        self.hp = 5
        self.movementSpeed = 0.8
        self.coins = 2

    def update(self):
        super().update()

        #IDLE
        if self.state == 0:
            self.basicMove()
            if game.findPlayer(self.x, self.y, 64, fool=True):
                self.state = 1
                self.stateTimer = 0

        #ATTACK
        if self.state == 1:
            self.stateTimer+=1
            if self.stateTimer==1:
                self.basicMove()
                self.image = self.attackImages[0]
            elif self.stateTimer==35:
                self.image = self.attackImages[1]
                target = game.findPlayer(self.x+self.xdir*16, self.y+self.xdir*16, 64)
                if target:
                    target.hurt()
            elif self.stateTimer==40:
                self.image = self.idleImage
            elif self.stateTimer>=80:
                self.image = self.idleImage
                self.state = 0

    def die(self):
        super().die()
        myHead = Skull(self.x,self.y-20)
        myHead.xv = math.cos(self.knockbackAngle)*self.knockback*0.1
        myHead.yv = math.sin(self.knockbackAngle)*self.knockback*0.1
        game.room.enemies.append(myHead)

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        # SWIPE
        if self.state == 1:
            if 35<=self.stateTimer<40:
                x = int(pos[0]+self.xdir*16)
                y = int(pos[1]+self.ydir*16)
                #blitRotate(gameDisplay, image, (x,y), (self.imageSize//2, self.imageSize//2), math.atan2(-self.ydir,-self.xdir))
                pygame.draw.circle(gameDisplay, (200,200,200), (x,y), 64)
        super().draw()
class Skull(Enemy):

    radius = 16
    imageSize = 256
    idleImage = loadTexture("enemies/axereaper/skull.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 1
        self.hp = 1
        self.xv = 0
        self.yv = 0
        self.invincibility = 20
    
    def edge(self, verticalWall=False):
        if verticalWall:
            self.xv = 0
        else:
            self.yv = 0
    def update(self):
        if self.state == 0:
            target = game.player
            x = target.fakeX
            y = target.fakeY
            hyp = math.sqrt((x-self.x)**2+(y-self.y)**2)
            if hyp>0:
                if self.scared:
                    hyp = -hyp
                self.xdir = (x-self.x)/hyp
                self.ydir = (y-self.y)/hyp
                self.xv+=0.03*self.xdir*self.movementSpeed
                self.yv+=0.03*self.ydir*self.movementSpeed
                self.x+=self.xv
                self.y+=self.yv
            self.xv*=0.99
            self.yv*=0.99

        super().update()

        #ATTACK
        if not self.invincibility and self.state==0:
            target = game.findPlayer(self.x, self.y, 8)
            if target:
                target.hurt(0.8)
                game.remove(self,game.room.enemies)
class Saw(Enemy):

    radius = 24
    spinRadius = 100
    imageSize = 128
    idleImage = loadTexture("enemies/sledger/saw1.png", imageSize)
    spinImage = loadTexture("enemies/sledger/saw2.png", imageSize)

    def __init__(self, x, y, friend=None):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 1
        self.hp = 1
        self.movementSpeed = 2
        self.a = random.random()*6.28
        self.xdir = math.cos(self.a)
        self.ydir = math.sin(self.a)
        self.friend = friend
        if self.friend:
            self.spindir = random.choice((1,-1))

    def edge(self, verticalWall=False):
        if self.friend:
            self.spindir*=-1
            self.a+=self.movementSpeed*self.spindir/self.spinRadius*3
        else:
            if verticalWall:
                self.xdir*=-1
            else:
                self.ydir*=-1

    def update(self):
        r = self.spinRadius
        if self.state == 0:
            self.image = random.choice((self.idleImage, self.spinImage))
            if self.friend:
                self.a+=self.movementSpeed*self.spindir/r
                self.xdir = -math.sin(self.a)*self.spindir
                self.ydir = math.cos(self.a)*self.spindir
            else:
                self.x+=self.xdir*self.movementSpeed
                self.y+=self.ydir*self.movementSpeed
        if self.friend:
            self.x=self.friend.x+math.cos(self.a)*r
            self.y=self.friend.y+math.sin(self.a)*r


        while True in [wall.adjust(self) for wall in game.room.walls]: 
            self.a += 0.03

        super().update()

        #ATTACK
        if self.state == 0:
            target = game.findPlayer(self.x, self.y, 24)
            if target:
                target.hurt()

    def hurt(self,damage=None):
        if self.friend:
            self.spindir*=-1
        else:
            super().hurt(damage)
class Sledger(Enemy):

    radius = 24
    imageSize = 128
    idleImage = loadTexture("enemies/sledger/idle.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 3
        self.hp = 3
        self.coins = 2
        self.movementSpeed = 0.5
        self.friend = Saw(self.x+50,self.y,friend=self)
        game.room.enemies.append(self.friend)

    def edge(self, verticalWall=False):
        if verticalWall:
            self.xdir*=-1
        else:
            self.ydir*=-1

    def update(self):
        if self.state == 0:
            self.image = self.idleImage
            if game.findPlayer(self.x,self.y,100, fool=True):
                self.basicMove(spdMult=-1)
            else:
                self.basicMove()

        super().update()

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        if 1:
            clonepos=(int((display[0]-game.room.roomSize[0])/2+self.friend.x),int((display[1]-game.room.roomSize[1])/2+self.friend.y))
            pygame.draw.line(gameDisplay, (200,100,25), (pos[0],pos[1]), (clonepos[0], clonepos[1]), 8)
        super().draw()


    def die(self):
        super().die()
        if self.friend:
            self.friend.friend = None
class Svamp(Enemy):

    radius = 32
    imageSize = 128
    idleImage = loadTexture("enemies/svamp/svamp.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 2
        self.hp = 2

    def update(self):

        super().update()

        #IDLE
        if self.state == 0:
            self.image = self.idleImage
            if random.random()<0.02:
                self.state = 1
                self.stateTimer = 0

        # SHOOT
        if self.state == 1:
            self.stateTimer+=1
            if self.stateTimer==1:
                a = random.random()*6.28
                dx = math.cos(a)
                dy = math.sin(a)
                game.room.projectiles.append(Spore(self.x, self.y, dx, dy, self))
            elif self.stateTimer>30:
                self.state = 0
class BlazeSpitter(Enemy):

    radius = 24
    imageSize = 128
    idleImage = loadTexture("enemies/blazespitter/blazespitter.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 2
        self.hp = 2
        self.coins = 1
        self.transformationCharger = 0

    def update(self):
        super().update()

        #IDLE
        if self.state == 0:
            self.image = self.idleImage
            if random.random()<0.05:
                self.state = 1
                self.stateTimer = 0
                self.transformationCharger += 1
            if random.random()<0.05 and self.transformationCharger>5:
                game.remove(self,game.room.enemies)
                plant = Hjuldjurplant(self.x,self.y)
                game.room.enemies.append(plant)
                plant.state = 2

        # SHOOT
        if self.state == 1:
            self.stateTimer+=1
            if self.stateTimer==1:
                a = random.random()*6.28
                dx = math.cos(a)*2
                dy = math.sin(a)*2
                game.room.projectiles.append(Firering(self.x, self.y, dx, dy))
            elif self.stateTimer>30:
                self.state = 0

    def die(self):
        super().die()
        #game.room.enemies.append(Hjuldjurplant(self.x,self.y-8))
class Hjuldjurplant(Enemy):

    radius = 24
    imageSize = 64
    idleImage = loadTexture("enemies/hjuldjur/hjuldjurplant.png", imageSize)
    transform1Image = loadTexture("enemies/hjuldjur/transform1.png", imageSize)
    transform2Image = loadTexture("enemies/hjuldjur/transform2.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 2
        self.hp = 2
        self.coins = 0
        self.harmless = True
        self.transformationCharger = 0

    def update(self):
        super().update()

        # IDLE
        if self.state == 0:
            if random.random()<0.01:
                self.transformationCharger+=1
                if self.transformationCharger>5:
                    self.state = 1
                    self.stateTimer = 0

        #TRANSFORM
        if self.state == 1:
            self.stateTimer+=1
            if self.stateTimer<20:
                self.image = self.transform1Image
            elif self.stateTimer<40:
                self.image = self.transform2Image
            elif self.stateTimer==40:
                game.remove(self,game.room.enemies)
                blaze = BlazeSpitter(self.x,self.y)
                game.room.enemies.append(blaze)

        #TRANSFORM BACK
        if self.state == 2:
            self.stateTimer+=1
            if self.stateTimer<20:
                self.image = self.transform2Image
            elif self.stateTimer<40:
                self.image = self.transform1Image
            elif self.stateTimer==40:
                self.image = self.idleImage
                self.state = 0

    def die(self):
        super().die()
        game.room.enemies.append(Hjuldjur(self.x,self.y-8))
class Hjuldjur(Enemy):
    radius = 16
    imageSize = 64
    idleImage = loadTexture("enemies/hjuldjur/hjuldjur.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 2
        self.hp = 2
        self.movementSpeed=1.5
        self.invincibility = 20
        self.scared = 60

    def hurt(self,damage=None):
        super().hurt(damage)
        self.scared = 60

    def update(self):
        if self.state==0:
            if self.hp<=1:
                self.basicMove(spdMult=-1)
            else:
                self.basicMove()
            self.x += random.randint(-1,1)
            self.y += random.randint(-1,1)

        super().update()

        #ATTACK
        if not self.invincibility and self.state==0:
            target = game.findPlayer(self.x, self.y, 16)
            if target:
                target.hurt()
                game.remove(self,game.room.enemies)
                game.room.enemies.append(Hjuldjurplant(self.x,self.y))
class Statue(Enemy):
    radius = 24
    imageSize = 128
    idleImage = loadTexture("enemies/rockgolem.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 8
        self.hp = 8
        self.coins = 0
        self.harmless = True

    def update(self):
        super().update()

        # IDLE

    def die(self):
        super().die()
        for i in range(5):
            game.room.enemies.append(Saw(self.x,self.y))
class Mercenary(Enemy):
    #mediocre name
    radius = 24
    imageSize = 128
    idleImage = loadTexture("player/warrior/player.png", imageSize)
    walkImages = [loadTexture("player/warrior/walk1.png", imageSize), loadTexture("player/warrior/walk2.png", imageSize)]
    attackImages = [loadTexture("player/warrior/strike1.png", imageSize), loadTexture("player/warrior/strike2.png", imageSize)]
    rollImages = [loadTexture("player/warrior/roll1.png", imageSize), loadTexture("player/warrior/roll2.png", imageSize)]

    swipeImage = loadTexture("player/warrior/swipe.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 3
        self.hp = 3
        self.movementSpeed = 1.5
        self.coins = 0

    def update(self):
        super().update()

        #IDLE
        if self.state == 0:
            self.image = random.choice([self.idleImage]+self.walkImages)
            self.basicMove()
            if game.player.state==1 and random.random()<0.05:
                self.state = 2
                self.stateTimer = 0
            if game.findPlayer(self.x, self.y, 32, fool=True):
                self.state = 1
                self.stateTimer = 0

        # ATAKK
        if self.state == 1:
            self.stateTimer+=1
            if self.stateTimer<15:
                self.image = self.attackImages[0]
            elif self.stateTimer == 15:
                self.image = self.attackImages[1]
                if game.findPlayer(self.x, self.y, 30):
                    game.player.hurt()
                for enemy in game.findEnemies(self.x, self.y, 30):
                    if not self==enemy:
                        enemy.hurt()
            elif self.stateTimer>=25:
                self.state = 0

        # ROLL
        if self.state == 2:
            self.stateTimer+=1
            if self.stateTimer<20:
                self.invincibility=1
                self.image = random.choice(self.rollImages)
                self.x+=self.xdir*4
                self.y+=self.ydir*4
            elif self.stateTimer==20:
                self.image = self.rollImages[0]
            elif self.stateTimer>=30:
                self.state = 0

    def die(self):
        super().die()
        kista = Chest(self.x,self.y)
        game.room.enemies.append(kista)
        kista.lootTable=goodItems
class fungusArm(Enemy):

    radius = 16
    imageSize = 128
    idleImage = loadTexture("enemies/lord fungus/arm2.png", imageSize)
    attackImages = [loadTexture("enemies/lord fungus/arm"+str(i)+".png", 128) for i in (1,2,3)]

    def __init__(self, x, y, owner):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 2
        self.hp = 2
        self.owner = owner
        self.state = 1

    def update(self):
        super().update()
        
        #bite
        if self.state == 1:
            self.stateTimer+=1
            if self.stateTimer==1:
                self.image = self.attackImages[0]
            elif self.stateTimer==20:
                self.image = self.attackImages[1]
            elif self.stateTimer>=50:
                self.image = self.attackImages[2]
                target = game.findPlayer(self.x, self.y, 16)
                if target:
                    target.hurt()
                self.state=0
                self.stateTimer=0

        #chillin and leavin
        if self.state == 0:
            self.stateTimer+=1
            if self.stateTimer==1:
                self.image = self.attackImages[2]
            if self.stateTimer==60:
                self.image = self.attackImages[0]
            elif self.stateTimer>70:
                game.remove(self, game.room.enemies)

    def hurt(self,damage=None):
        super().hurt(damage)
        self.owner.hurt(damage)
    def die(self):
        super().die()
        self.owner.arms-=1
class Portal(Enemy):

    radius = 32
    imageSize = 128
    idleImage = loadTexture("enemies/portal/portal.png", imageSize)
    spawnImage = loadTexture("enemies/portal/portal2.png", imageSize)
    transform1Image = loadTexture("enemies/portal/preportal1.png", imageSize)
    transform2Image = loadTexture("enemies/portal/preportal2.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 4
        self.hp = 4
        self.coins = 3
        self.transformationCharger = 0 # for tranformation back to animus

    def update(self):
        super().update()
        
        #IDLE
        if self.state == 0:
            if random.random()<0.05:
                self.state = 1
                self.stateTimer = 0
            elif random.random()<0.5 and self.transformationCharger>5:
                self.state = 3
                self.stateTimer = 0

        #SPAWN
        if self.state == 1:
            self.stateTimer+=1
            if 60<self.stateTimer<150:
                self.image = random.choice((self.idleImage, self.spawnImage))
            elif self.stateTimer==150:
                self.transformationCharger += 1
                self.image = self.idleImage
                enemy = random.choice([Animus, Pufferfish, Svamp, Skull, Hjuldjur])(self.x,self.y)
                game.room.enemies.append(enemy)
                if self.coins>=enemy.coins: #transfer coins
                    self.coins-=enemy.coins
                else:
                    enemy.coins = self.coins
                    self.coins = 0


            elif self.stateTimer>300:
                self.image = self.idleImage
                self.state = 0

        #TRANSFORM
        if self.state == 2:
            self.stateTimer+=1
            if self.stateTimer<50:
                self.image = self.transform1Image
            elif self.stateTimer<100:
                self.image = self.transform2Image
            elif self.stateTimer==100:
                self.state = 0
                self.image = self.idleImage

        #TRANSFORM BACK
        if self.state == 3:
            self.stateTimer+=1
            if self.stateTimer<30:
                self.image = self.transform2Image
            elif self.stateTimer<60:
                self.image = self.transform1Image
            elif self.stateTimer==60:
                game.remove(self, game.room.enemies)
                mus = Animus(self.x,self.y)
                game.room.enemies.append(mus)
                mus.coins = self.coins
                mus.state = 0
class Tnt(Enemy):

    radius = 32
    imageSize = 128
    idleImage = loadTexture("enemies/tnt.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 1
        self.hp = 1
        self.coins = 0
        self.harmless = True

    def fire(self,*a):
        self.die()
    def freeze(*a):
        pass
    def die(self):
        game.room.projectiles.append(Explosion(self.x,self.y))
        game.remove(self,game.room.enemies)

class Boss(Enemy):
    
    radius = 64
    imageSize = 512
    idleImage = loadTexture("enemies/lord fungus/boss2.png", imageSize)
    screamImage = loadTexture("enemies/lord fungus/boss3.png", imageSize)
    sleepImage = loadTexture("enemies/lord fungus/boss0.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 50
        self.hp = 50
        self.movementSpeed = 0.2
        self.coins = 10
        self.arms = 8
        self.firstMoveSpores = 1

        pygame.mixer.music.stop()  # Stop the current song
        pygame.mixer.music.load(os.path.join(SOUND_PATH, "bosstheme.wav"))  # Load the new song
        pygame.mixer.music.play(-1)  # Play the new song in a loop

    def freeze(self):
        if game.player.freezeDamage:
            Sound.glassSound.play()
            self.hurt(game.player.freezeDamage)

    def update(self):
        super().update()

        #IDLE
        if self.state == 0:
            self.image = self.idleImage
            self.basicMove()
            if random.random()<0.02 or self.firstMoveSpores>0:
                self.firstMoveSpores -= 1
                self.state = 2
                self.stateTimer = 0
            if random.random()<0.06:
                self.state = 3
                self.stateTimer = 0
            if random.random()<0.02:
                self.state = 4
                self.stateTimer = 0

        #SPORES
        if self.state == 2:
            self.stateTimer+=1
            if self.stateTimer in [10,30,50]: #summon spores
                self.image = self.screamImage
                dx = (game.player.fakeX - self.x + random.randint(-60,60))*0.8/120
                dy = (game.player.fakeY - self.y + random.randint(-60,60))*0.8/120
                spore = Spore(self.x,self.y, dx, dy)
                spore.createOwner=True
                game.room.projectiles.append(spore)
            if self.stateTimer==60:
                self.image = self.idleImage
            if self.stateTimer>=200:
                self.state = 0

        #ARMS
        if self.state == 3:
            self.stateTimer+=1
            if self.stateTimer==20: #summon arms
                self.image = self.screamImage
                #additional arm at u which cant die
                arm = fungusArm(game.player.fakeX+random.randint(-16,16), game.player.fakeY+random.randint(-16,16), owner=self)
                game.room.enemies.append(arm)
                #many arms
                for i in range(self.arms):
                    arm = fungusArm(random.randint(100,game.room.roomSize[0]-100),random.randint(100,game.room.roomSize[1]-100), owner=self)
                    game.room.enemies.append(arm)
            if self.stateTimer==60:
                self.image = self.idleImage
            if self.stateTimer>=200:
                self.state = 0

        #SLEEP
        if self.state == 4:
            self.heal(0.01)
            self.stateTimer+=1
            if self.stateTimer==20:
                self.image = self.sleepImage
            if self.stateTimer>=200:
                self.state = 0
    
    def drawUI(self):
        scale = 20
        pygame.draw.rect(gameDisplay, (200,0,0), (display[0]//2 - self.maxhp//2*scale, display[1]-50-32, scale*self.hp, 32))
        
    def die(self):
        super().die()
        game.room.enemies = []
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_b]:
            game.room.items.append(StairCase(self.x,self.y))
            game.depth = 0
        else:
            game.room.items.append(StairCase2(self.x,self.y))
        print("you win")

class Boss2(Enemy):
    
    radius = 48
    imageSize = 128
    idleImage = loadTexture("enemies/lord wurm/head.png", imageSize)
    screamImage = loadTexture("enemies/lord wurm/bite1.png", imageSize)
    biteImage = loadTexture("enemies/lord wurm/bite2.png", imageSize)

    def __init__(self, x, y):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 50
        self.hp = 50
        self.movementSpeed = 1
        self.coins = 5
        self.tail = Boss2_tail(x, y-10, more_tail = 9)
        self.tail.head = self
        self.a = 0
        self.xv = 0
        self.yv = 1
        game.room.enemies.append(self.tail)


        pygame.mixer.music.stop()  # Stop the current song
        pygame.mixer.music.load(os.path.join(SOUND_PATH, "bosstheme.wav"))  # Load the new song
        pygame.mixer.music.play(-1)  # Play the new song in a loop

    def freeze(self):
        if game.player.freezeDamage:
            Sound.glassSound.play()
            self.hurt(game.player.freezeDamage)

    def basicMove(self, spdMult = 1, target = None):
        target = game.player
        x = target.fakeX
        y = target.fakeY
        hyp = math.sqrt((x-self.x)**2+(y-self.y)**2)
        if hyp>0:
            if self.scared:
                hyp = -hyp
            self.xdir = (x-self.x)/hyp
            self.ydir = (y-self.y)/hyp
            self.xv+=0.03*self.xdir*self.movementSpeed*spdMult
            self.yv+=0.03*self.ydir*self.movementSpeed*spdMult

    def update(self):
        super().update()

        #IDLE
        if self.state == 0:
            self.image = self.idleImage
            self.basicMove()
            if random.random()<0.06:
                self.state = 2
                self.stateTimer = 0
            if random.random()<0.02:
                self.state = 3
                self.stateTimer = 0
            if random.random()<0.02:
                self.state = 4
                self.stateTimer = 0

        self.x+=self.xv
        self.y+=self.yv
        self.a = math.atan2(-self.yv,-self.xv)
        self.xv*=0.99
        self.yv*=0.99

        # BITE
        if self.state == 2:
            self.basicMove(spdMult = 0.8)
            self.stateTimer+=1
            if self.stateTimer < 20: # prebite
                # face correctly
                #self.moveToTarget()
                if random.random()<0.02:
                    pass # collateral damage?
                self.image = self.screamImage
            elif self.stateTimer == 20: # bite
                self.image = self.biteImage
                displacement = -40
                target = game.findPlayer(self.x + math.cos(self.a)*displacement, self.y + math.sin(self.a)*displacement, 32)
                if target:
                    target.hurt()
            elif self.stateTimer < 40: # ending lag
                self.image = self.biteImage
            else:
                self.state = 0

        # SHOOT
        if self.state == 3:
            self.stateTimer+=1
            if self.stateTimer<100:
                self.image = self.idleImage
                self.basicMove(spdMult = -1)
            #if self.stateTimer==2:
             #   Sound.horrorSound.play()
            elif self.stateTimer<170:
                self.image = self.idleImage
                self.basicMove(spdMult = 1)
            elif self.stateTimer<240: # summon projs
                self.basicMove(spdMult = 0.5)
                self.image = self.screamImage
                #additional arm at u which cant die
                if random.random()<0.3:
                    displacement = -40
                    proj = Firering(self.x+ math.cos(self.a)*displacement, self.y+ math.sin(self.a)*displacement, -math.cos(self.a+random.randint(-2,2)*0.2)*2, -math.sin(self.a+random.randint(-2,2)*0.2)*2)               
                    game.room.projectiles.append(proj)
            elif self.stateTimer<250:
                self.image = self.idleImage
            else:
                self.state = 0

        # SAW
        if self.state == 4:
            self.stateTimer+=1
            if self.stateTimer<30:
                self.image = self.idleImage
                self.basicMove(spdMult = -0.5)
            #if self.stateTimer==2:
             #   Sound.horrorSound.play()
            elif self.stateTimer==55:# summon saw
                self.image = self.screamImage
                displacement = -40
                saw = Saw(self.x+ math.cos(self.a)*displacement, self.y+ math.sin(self.a)*displacement)
                game.room.enemies.append(saw)
                saw.a = self.a + math.pi
                saw.xdir = math.cos(saw.a)
                saw.ydir = math.sin(saw.a)
            elif self.stateTimer<70: 
                self.basicMove(spdMult = 1)
                self.image = self.screamImage
            elif self.stateTimer<100:
                self.image = self.idleImage
            else:
                self.state = 0

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        if self.burning>0:
            gameDisplay.blit(self.burningImage, (int(pos[0]) - 128//2, int(pos[1]) - 128//2))
        blitRotate(gameDisplay, self.image, (int(pos[0]), int(pos[1])), (self.imageSize//2, self.imageSize//2), self.a)
    
    def drawUI(self):
        scale = 20
        pygame.draw.rect(gameDisplay, (200,0,0), (display[0]//2 - self.maxhp//2*scale, display[1]-50-32, scale*self.hp, 32))
        
    def die(self):
        super().die()
        game.room.enemies = []
        pressed = pygame.key.get_pressed()
        if pressed[pygame.K_b]:
            game.room.items.append(StairCase(self.x,self.y))
            game.depth = 0
        else:
            game.room.items.append(StairCase2(self.x,self.y))
        print("you win")
class Boss2_tail(Enemy):
    
    radius = 32
    imageSize = 128
    idleImage = loadTexture("enemies/lord wurm/tail.png", imageSize)

    def __init__(self, x, y, more_tail):
        super().__init__(x,y)
        self.image = self.idleImage
        self.maxhp = 50
        self.hp = 50
        self.movementSpeed = 0.8
        self.coins = 1
        self.a = 0
        if more_tail:
            self.tail = Boss2_tail(x, y-10, more_tail = more_tail-1)
            self.tail.head = self
            game.room.enemies.append(self.tail)

    def follow(self, other):
        pos_diff = (self.x - other.x, self.y - other.y)
        dist_to_other2 = (pos_diff[0]**2 + pos_diff[1]**2)**0.5
        angle_to_other = math.atan2(pos_diff[1], pos_diff[0])
        follow_dist = 20
        if dist_to_other2 > follow_dist:
            shorten_factor = follow_dist / dist_to_other2
            self.x = other.x + pos_diff[0]*shorten_factor
            self.y = other.y + pos_diff[1]*shorten_factor
        self.a = angle_to_other

    def freeze(self):
        if game.player.freezeDamage:
            Sound.glassSound.play()
            self.hurt(game.player.freezeDamage)

    def update(self):
        super().update()

        #IDLE
        self.follow(self.head)
        displacement = -10
        target = game.findPlayer(self.x + math.cos(self.a)*displacement, self.y + math.sin(self.a)*displacement, 32)
        if target:
            target.hurt(0.4)

    def hurt(self, val=1):
        self.head.hurt(val*0.8)

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        if self.burning>0:
            gameDisplay.blit(self.burningImage, (int(pos[0]) - 128//2, int(pos[1]) - 128//2))
        blitRotate(gameDisplay, self.image, (int(pos[0]), int(pos[1])), (self.imageSize//2, self.imageSize//2), self.a)

class Projectile():

    drawAngled = False
    magicglowImage = loadTexture("projectiles/magicglow.png", 64)

    def __init__(self, x, y, xv, yv):
        self.x = x
        self.y = y
        self.xv = xv
        self.yv = yv
        self.bounces = 0
        self.magicglow = 0
        if not self.evil:
            self.bounces = game.player.projBounces
    @classmethod
    def changeSize(cls,multiplier):
        if not hasattr(cls, 'original_radius'):
            cls.original_radius = cls.radius
            cls.original_imageSize = cls.imageSize
        cls.radius = int(cls.original_radius*multiplier)
        cls.imageSize = int(cls.original_imageSize*multiplier)
        cls.image = loadTexture(cls.imagePath, cls.original_imageSize*multiplier)
        #print("enlarged",cls, cls.imageSize*multiplier)

    def update(self):
        self.x+=self.xv
        self.y+=self.yv

        if not self.evil and False:
            if game.player.magnet:
                targets = game.findEnemies(self.x,self.y,50+20*game.player.magnet)
                if targets:
                    target=random.choice(targets)
                    hyp = math.sqrt((target.x-self.x)**2+(target.y-self.y)**2)
                    self.xv += (target.x-self.x)/hyp*game.player.magnet
                    self.yv += (target.y-self.y)/hyp*game.player.magnet

        if game.player.spirality:
            hyp = math.sqrt(self.xv**2+self.yv**2)
            self.a = math.atan2(self.yv,self.xv)
            self.a+=0.02*game.player.spirality
            self.xv = math.cos(self.a)*hyp
            self.yv = math.sin(self.a)*hyp

        if game.player.magicWand and not self.evil:
            self.xv += game.player.magicWand * game.player.dx * 0.05
            self.yv += game.player.magicWand * game.player.dy * 0.05
            self.xv *= 0.99
            self.yv *= 0.99

        if(self.x>game.room.roomSize[0]):
            self.edge(verticalWall=True)
        elif(self.x<0):
            self.edge(verticalWall=True)
        elif(self.y>game.room.roomSize[1]):
            self.edge(verticalWall=False)
        elif(self.y<0):
            self.edge(verticalWall=False)

        for wall in game.room.walls:
            wall.adjust(self)

    def edge(self, verticalWall=False):
        if verticalWall:
            self.xv*=-1
        else:
            self.yv*=-1
        if self.bounces == 0:
            game.remove(self,game.room.projectiles)
        self.bounces-=1

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        if game.player.magicWand and not self.evil:
            gameDisplay.blit(self.magicglowImage, (int(pos[0]) - 64//2, int(pos[1]) - 64//2))
        if self.drawAngled:
            blitRotate(gameDisplay, self.image, (int(pos[0]),int(pos[1])), (self.imageSize//2, self.imageSize//2), math.atan2(-self.yv,-self.xv))
        else:
            gameDisplay.blit(self.image, (int(pos[0]) - self.imageSize//2, int(pos[1]) - self.imageSize//2))

class Firering(Projectile):

    evil = True
    radius = 16
    imageSize = 128
    imagePath="enemies/blazespitter/firering.png"
    image = loadTexture("enemies/blazespitter/firering.png", imageSize)

    def update(self):
        super().update()

        # HIT PLAYER
        if game.findPlayer(self.x, self.y, self.radius):
            #game.player.hurt()
            game.player.fire(30)
            game.remove(self,game.room.projectiles)
class Missile(Projectile):

    drawAngled = True
    evil = True
    radius = 4
    imageSize = 64
    image = loadTexture("enemies/robot/proj.png", imageSize)
    drawAngled = True

    """
    def update(self):
        super().update()

        # HIT PLAYER
        if game.findPlayer(self.x, self.y, self.radius):
            game.player.hurt()
            game.remove(self,game.room.projectiles)
    """

    def edge(self, verticalWall=False):
        game.room.projectiles.append(Explosion(self.x,self.y))
        game.remove(self, game.room.projectiles)

class Sapphire(Projectile):

    evil = False
    radius = 10
    imageSize = 64
    imagePath="projectiles/sapphire.png"
    image = loadTexture("projectiles/sapphire.png", imageSize)

    def update(self):
        super().update()

        # HIT ENEMIES
        targets =  game.findEnemies(self.x, self.y, self.radius)
        for target in targets:
            target.freeze()
        if targets:
            game.remove(self,game.room.projectiles)
class Ruby(Projectile):

    evil = False
    radius = 10
    imageSize = 64
    imagePath="projectiles/ruby.png"
    image = loadTexture("projectiles/ruby.png", imageSize)

    def update(self):
        super().update()

        # HIT ENEMIES
        targets =  game.findEnemies(self.x, self.y, self.radius)
        for target in targets:
            target.fire(30)
        if targets:
            game.remove(self,game.room.projectiles)
class Emerald(Projectile):

    evil = False
    radius = 10
    imageSize = 64
    imagePath="projectiles/emerald.png"
    image = loadTexture("projectiles/emerald.png", imageSize)

    def update(self):
        super().update()

        # HIT ENEMIES
        targets =  game.findEnemies(self.x, self.y, self.radius)
        for target in targets:
            if hasattr(target, "movementSpeed"):
                target.movementSpeed *= 0.3
        if targets:
            game.remove(self,game.room.projectiles)
class Bullet(Projectile):

    drawAngled = True
    evil = False
    radius = 4
    imageSize = 128
    imagePath="player/ranger/bullet.png"
    image = loadTexture("player/ranger/bullet.png", imageSize)

    def update(self):
        super().update()

        # HIT ENEMIES
        targets =  game.findEnemies(self.x, self.y, self.radius)
        if targets:
            game.remove(self,game.room.projectiles)
        game.player.applyAttackEffects(targets)
class FireBullet(Projectile):

    drawAngled = True
    evil = False
    radius = 4
    imageSize = 128
    imagePath="player/ranger/firebullet.png"
    image = loadTexture("player/ranger/firebullet.png", imageSize)

    def update(self):
        super().update()

        # HIT ENEMIES
        targets =  game.findEnemies(self.x, self.y, self.radius)
        if targets:
            game.remove(self,game.room.projectiles)
        game.player.applyAttackEffects(targets)
class Orb(Projectile):

    drawAngled = True
    evil = False
    radius = 8
    imageSize = 128
    imagePath="player/mage/bullet.png"
    image = loadTexture("player/mage/bullet.png", imageSize)

    def update(self):
        super().update()

        # HIT ENEMIES
        targets =  game.findEnemies(self.x, self.y, self.radius)
        if targets:
            game.remove(self,game.room.projectiles)
        game.player.applyAttackEffects(targets)
class FireOrb(Projectile):

    drawAngled = True
    evil = False
    radius = 8
    imageSize = 128
    imagePath="player/mage/firebullet.png"
    image = loadTexture("player/mage/firebullet.png", imageSize)

    def update(self):
        super().update()

        # HIT ENEMIES
        targets =  game.findEnemies(self.x, self.y, self.radius)
        if targets:
            game.remove(self,game.room.projectiles)
        game.player.applyAttackEffects(targets)
class Spore(Projectile):

    evil = True
    radius = 8
    imageSize = 128
    image = loadTexture("enemies/svamp/spore.png", imageSize)
    puffImage = loadTexture("enemies/svamp/sporepuff.png", imageSize)

    def __init__(self, x, y, xv, yv, owner=None):
        super().__init__(x,y,xv,yv)
        self.age = 0
        self.owner= owner
        self.bounces=16
        self.createOwner = False #for boss spores

    def update(self):
        super().update()

        self.age+=1

        if self.age == 110:
            self.xv=0
            self.yv=0
            self.image = self.puffImage
            if game.findPlayer(self.x, self.y, 24):
                game.player.hurt()
        if self.age == 120:
            if self.owner and not self.owner.state==-1:
                self.owner.x = self.x
                self.owner.y = self.y
            elif self.createOwner:
                game.room.enemies.append(Svamp(self.x,self.y))
                self.createOwner=False
            game.remove(self,game.room.projectiles)
class Explosion(Projectile):

    evil=1
    radius = 48
    imageSize = 128
    imagePath="projectiles/explosion.png"
    image = loadTexture("projectiles/bigexplosion1.png", imageSize)
    image2 = loadTexture("projectiles/bigexplosion2.png", imageSize)

    def __init__(self, x, y, xv=0, yv=0):
        super().__init__(x,y,xv,yv)
        self.age = 0

    def update(self):
        #super().update()

        # HIT ENEMIES
        self.age+=1
        if self.age==1:
            Sound.hitSounds[0].play()

            targets =  game.findEnemies(self.x, self.y, self.radius)
            for target in targets:
                target.hurt(2.5)
            if game.findPlayer(self.x, self.y, self.radius-10):
                game.player.hurt(2)
        if self.age==5:
            self.image=self.image2
        if self.age==10:
            game.remove(self,game.room.projectiles)

class Item():

    radius = 20
    showItem=True
    def __init__(self, x, y,shopItem=False):
        self.x = x
        self.y = y
        self.age=0
        self.shopItem=shopItem

    def update(self):
        self.age+=1
        if self.age>20 and (not self.shopItem or game.player.coins>=self.price):
            if game.findPlayer(self.x,self.y, self.radius) and game.player.hp>0:
                if self.shopItem:
                    game.player.coins-=self.price
                    Sound.cashSound.play()
                if(self.showItem):
                    if (self.__class__ in game.player.shownItems):
                        game.player.shownItems[self.__class__]+=1
                    else:
                        game.player.shownItems[self.__class__]=1
                game.remove(self,game.room.items)
                self.pickup()

    def draw(self):
        pos=(int((display[0]-game.room.roomSize[0])/2+self.x),int((display[1]-game.room.roomSize[1])/2+self.y))
        gameDisplay.blit(self.image, (int(pos[0]) - self.imageSize//2, int(pos[1]) - self.imageSize//2))
        if(self.shopItem):
            textsurface = myfont.render(str(self.price)+" coins" , False, (0, 0, 0))
            gameDisplay.blit(textsurface,(pos[0]-20,pos[1]+25))

class StairCase(Item):
    imageSize = 128
    image = loadTexture("items/staircase.png", imageSize)
    showItem=False
    def pickup(self):
        game.enterFloor(Floor(roomPresets))
        game.player.x = self.x
        game.player.y = self.y
        game.gatherAllies()
        for i in range(min(50, game.player.coins*game.player.piggyBank//2)):
            game.room.items.append(Coin(random.randint(100,400),random.randint(100,400)))
class StairCase2(Item):
    imageSize = 128
    image = loadTexture("items/staircase.png", imageSize)
    showItem=False
    def pickup(self):
        game.gameOver()
        
class Coin(Item):

    imageSize = 128
    image = loadTexture("items/coin.png", imageSize)
    showItem = False
    def pickup(self):
        game.player.coins+=1
        Sound.coinSound.play()
        if game.player.mosscrystal:
            for i in range(game.player.mosscrystal):
                a = random.random()*6.28
                dx = math.cos(a)
                dy = math.sin(a)
                game.room.projectiles.append(Emerald(self.x,self.y, dx*3, dy*3))
    def update(self):
        super().update()
        if game.player.magnet and game.findPlayer(self.x,self.y,100*game.player.magnet):
            target = game.player
            hyp = math.sqrt((target.x-self.x)**2+(target.y-self.y)**2)
            self.x += (target.x-self.x)/hyp*game.player.magnet
            self.y += (target.y-self.y)/hyp*game.player.magnet
class Fruit(Item):
    libraryString = "Hasty Snack"
    price=8
    imageSize = 128
    image = loadTexture("items/fruit.png", imageSize)
    
    def pickup(self):
        game.player.movementSpeed+=0.8
class Stick(Item):
    libraryString = "Long Stick"
    price=11
    imageSize = 128
    image = loadTexture("items/stick.png", imageSize)

    def pickup(self):
        game.player.swipeRange+=30
        if hasattr(game.player, "maxAmmo"):
            game.player.maxAmmo+=1
            game.player.ammo+=1
class Fan(Item):
    libraryString = "Windy Fan Thingy"
    price=6
    imageSize = 128
    image = loadTexture("items/fan.png", imageSize)

    def pickup(self):
        game.player.fanRoll+=2
class Heart(Item):
    price=5
    imageSize = 128
    image = loadTexture("items/heart.png", imageSize)
    showItem=False
    def pickup(self):
        game.player.heal(1+1*EZ)
class Icecrystal(Item):
    libraryString = "Frost Crystal"
    price=15
    imageSize = 64
    image = loadTexture("items/icecrystal.png", imageSize)

    def pickup(self):
        game.player.icecrystal+=3
class Crystal(Item):
    libraryString = "Fire Crystal"
    price=12
    imageSize = 64
    image = loadTexture("items/crystal.png", imageSize)

    def pickup(self):
        game.player.crystal+=3
class Mosscrystal(Item):
    libraryString = "Moss Crystal"
    price=10
    imageSize = 64
    image = loadTexture("items/mosscrystal.png", imageSize)

    def pickup(self):
        game.player.mosscrystal+=3
class Bouncer(Item):
    libraryString = "Bounce"
    price=13
    imageSize = 128
    image = loadTexture("items/bouncer.png", imageSize)

    def pickup(self):
        game.player.projBounces+=1
class IceShield(Item):
    libraryString = "Ice Shield"
    price=6
    imageSize = 128
    image = loadTexture("items/iceShield.png", imageSize)

    def pickup(self):
        game.player.iceBody+=2
class ColdCore(Item):
    libraryString = "Shattering Ice"
    price=16
    imageSize = 128
    image = loadTexture("items/coldcore.png", imageSize)

    def pickup(self):
        game.player.freezeDamage+=1
        game.player.freezeTime+=30
class FireSword(Item):
    libraryString = "Fire Sword"
    price=13
    imageSize = 128
    image = loadTexture("items/firesword.png", imageSize)

    def pickup(self):
        game.player.fireSword+=1    
class MagicWand(Item):
    libraryString = "Magic Wand"
    price=15
    imageSize = 128
    image = loadTexture("items/magicwand.png", imageSize)

    def pickup(self):
        game.player.magicWand+=1    
class Magnet(Item):
    libraryString = "Coin Magnet"
    price=5
    imageSize = 128
    image = loadTexture("items/magnet.png", imageSize)

    def pickup(self):
        game.player.magnet+=1
class PiggyBank(Item):
    libraryString = "Life Savings"
    price=14
    imageSize = 128
    image = loadTexture("items/piggybank.png", imageSize)

    def pickup(self):
        game.player.piggyBank+=1
class FireStar(Item):
    libraryString = "Intense Fire"
    price=15
    imageSize = 128
    image = loadTexture("items/firestar.png", imageSize)

    def pickup(self):
        game.player.fireStar+=1
class ShockLink(Item):
    libraryString = "Shock Link"
    price=20
    imageSize = 128
    image = loadTexture("items/shocklink.png", imageSize)

    def pickup(self):
        game.player.shockLink+=1
class WaterFace(Item):
    libraryString = "the Water Spirit"
    price=16
    imageSize = 128
    image = loadTexture("items/waterspirit.png", imageSize)

    def pickup(self):
        game.allies.append(WaterSpirit(self.x,self.y))
class VampireBite(Item):
    libraryString = "Vampire"
    price=17
    imageSize = 128
    image = loadTexture("items/vampirebite.png", imageSize)

    def pickup(self):
        game.player.lifeSteal+=0.1
class ClassChange(Item):
    libraryString = "Class Change"
    price=10
    imageSize = 128
    image = loadTexture("items/classchange.png", imageSize)

    def pickup(self):
        oldPlayer = game.player
        classes = unlockedClasses()#.copy()
        classes.remove(oldPlayer.__class__)
        game.player = random.choice(classes)(oldPlayer.x,oldPlayer.y)
        game.player.coins = oldPlayer.coins
        game.player.hp = oldPlayer.hp#maxhp
        game.allies = []
        for i in range(len(oldPlayer.shownItems)):
            clss=list(oldPlayer.shownItems.keys())[i]
            for j in range(oldPlayer.shownItems[clss]):
                if not (clss == ClassChange or clss == ProjectileEnlarger):
                    clss(game.player.x,game.player.y).pickup()
                if(clss.showItem):
                    if (clss in game.player.shownItems):
                        game.player.shownItems[clss]+=1
                    else:
                        game.player.shownItems[clss]=1
class Spirality(Item):
    libraryString = "Spirality"
    price=4
    imageSize = 128
    image = loadTexture("items/spirality.png", imageSize)

    def pickup(self):
        game.player.spirality+=1
class JesterHat(Item):
    libraryString = "the Jester"
    price=16
    imageSize = 128
    image = loadTexture("items/jesterhat.png", imageSize)

    def pickup(self):
        game.allies.append(Jester(self.x,self.y))
class FireRope(Item):
    libraryString = "the Eternal Flame"
    price=12
    imageSize = 128
    image = loadTexture("items/firerope.png", imageSize)

    def pickup(self):
        game.allies.append(FireSpirit(self.x,self.y))
class Carpet(Item):
    libraryString = "Magic Carpet"
    price=19
    imageSize = 128
    image = loadTexture("items/carpet.png", imageSize)
    images = loadTexture("items/carpet.png", imageSize, mirror=True)

    def pickup(self):
        game.player.carpet+=1
class Library(Item):
    libraryString = "the Little Library"
    price=3
    imageSize = 128
    image = loadTexture("items/library.png", imageSize)

    def pickup(self):
        game.player.library+=1
class ProjectileEnlarger(Item):
    libraryString = "Projectile Enlarger"
    price=10
    imageSize = 128
    image = loadTexture("items/projectilehologram.png", imageSize)

    def pickup(self):
        game.player.projectileSize += 1
        for projCls in [Sapphire,Ruby,Emerald,Bullet,FireBullet,Orb,FireOrb]:
            projCls.changeSize(game.player.projectileSize)

directionHash={0:[0,-1],1:[1,0],2:[0,1],3:[-1,0]}
goodItems=[PiggyBank,Bouncer,ShockLink,FireSword,MagicWand,ColdCore,Icecrystal,WaterFace,VampireBite,JesterHat,Carpet,ProjectileEnlarger]
badItems=[Fruit,Stick,FireStar,Fan,IceShield,Mosscrystal,Crystal,Magnet,FireRope,Library]
allItems=goodItems+badItems
roomPresets=[
    [[
    createWallF(100,100,190,160, occurance=0.3),
    createWallF(400,100,190,190, occurance=0.3),
    createWallF(100,400,160,180, occurance=0.3),
    createWallF(400,400,190,190, occurance=0.3),
    ],[
    createF([Chest],100,100, lootTable=[Spirality,Saw,Svamp,Tnt], occurance=0.5),
    createF([Animus,Pufferfish,Skull,Saw,Svamp],250,250),
    createF([Animus,Pufferfish,Skull,Saw,Sledger],250,250, depth=3),
    createF([Animus,Pufferfish,Robot,Skull,Saw,Schmitt],250,250, depth=5),
    createF([Animus,Pufferfish,Robot,Skull,Saw,Hjuldjur],lambda :random.randint(200,300),lambda :random.randint(200,300),occurance=0.5),
    ],[
    createF(allItems,200,400,occurance=0.2),
    ],], # Test Room using everything

    [[
    createWallF(400,200,120,20,occurance=0.2),
    createWallF(150,300,20,220,occurance=0.3),
    createWallF(350,300,20,220,occurance=0.3),
    createWallF(250,400,220,20,occurance=0.2),
    createWallF(250,200,220,20,occurance=0.2),
    ],[
    createF([Animus],250,250),
    createF([Sledger,Schmitt],250,200,depth=3),
    createF([Pufferfish,Tnt],200,250,occurance=0.4),
    createF([Pufferfish,Tnt],300,250,occurance=0.4),
    createF([Hjuldjurplant,BlazeSpitter,Svamp],300,350,occurance=0.3, depth=4),
    createF([Hjuldjurplant,BlazeSpitter,Svamp],200,350,occurance=0.3, depth=4),
    ],[
    createF([Fruit],250,350,occurance=0.3),
    ],], # Test Room

    # [[
    # ],[
    # ],[
    # createF(allItems,400,250,shop=True),
    # createF(allItems,300,250,shop=True),
    # createF(allItems,200,250,shop=True),
    # createF([Heart],100,250,shop=True),
    # ],], # Shop
    
    [[
    createWallF(100,100,200,200, occurance=0.5),
    createWallF(300,lambda :random.randint(1,400),100,50),
    ],[
    createF([Robot],lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(100,game.room.roomSize[1]-100)),
    createF([Svamp],lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(100,game.room.roomSize[1]-100)),
    createF([Sledger],lambda :random.randint(200,game.room.roomSize[0]-200),lambda :random.randint(200,game.room.roomSize[1]-200),depth=3),
    createF([Tnt],lambda :random.randint(200,game.room.roomSize[0]-200),lambda :random.randint(200,game.room.roomSize[1]-200),depth=5),
    createF([Tnt],lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(100,game.room.roomSize[1]-100),depth=5),
    ],[
    createF(allItems,300,200, occurance=0.1, depth=3),
    ],], # Test Room

    [[
    createWallF(lambda :random.randint(200,game.room.roomSize[0]-200),lambda :random.randint(100,game.room.roomSize[1]-100),60,90, occurance=0.3),
    createWallF(lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(200,game.room.roomSize[1]-200),lambda :random.randint(60,200),60, occurance=0.3),
    ],[
    createF([Robot],400,400,depth=2),
    createF([Animus],200,lambda :random.randint(200,game.room.roomSize[1]-200)),
    createF([Pufferfish],100,100),
    createF([Sledger],250,250, depth=4),
    ],[
    createF([Fruit],200,300, occurance=0.1),
    createF([Stick],250,300, occurance=0.2),
    createF([Fan],300,300, occurance=0.1),
    ],], # Ellas Room

    [[
    createWallF(50,40,90,60, occurance=0.3),
    createWallF(400,50,90,90, occurance=0.3),
    createWallF(30,470,60,80, occurance=0.3),
    createWallF(450,450,90,90, occurance=0.3),
    ],[
    createF([Chest],250,250),
    createF([Schmitt,Sledger],250,250,depth=4),
    createF([Animus,Pufferfish, Skull],150,200),
    createF([Animus,Pufferfish, Skull],350,200),
    createF([Animus,Pufferfish, Skull],250,150,depth=2),
    createF([Animus,Pufferfish, Skull],200,350,depth=2),
    createF([Animus,Pufferfish, Skull],300,350,depth=2),
    ],[
    ],], # Pentagon

    [[
    createWallF(lambda :random.randint(100,400),lambda :random.randint(100,400),lambda :random.randint(20,100),lambda :random.randint(20,200), occurance=0.5),
    createWallF(lambda :random.randint(100,400),lambda :random.randint(100,400),lambda :random.randint(20,200),lambda :random.randint(20,100), occurance=0.5),
    ],[
    createF([Chest],250,250),
    createF([Robot],lambda :random.randint(100,400),lambda :random.randint(100,400), depth = 2),
    createF([Robot],lambda :random.randint(100,400),lambda :random.randint(100,400), depth = 3),
    createF([Saw],lambda :random.randint(100,400),lambda :random.randint(100,400), depth = 5),
    ]+[
    createF([Robot],lambda :random.randint(100,400),lambda :random.randint(100,400), occurance=0.5),
    ]*2,
    [
    ],], # Laser Room

    [[
    createWallF(lambda :random.randint(100,400),lambda :random.randint(100,400),lambda :random.randint(20,100),lambda :random.randint(20,100), occurance=0.5),
    createWallF(lambda :random.randint(100,400),lambda :random.randint(100,400),lambda :random.randint(20,100),lambda :random.randint(20,100), occurance=0.5),
    createWallF(lambda :random.randint(100,400),lambda :random.randint(100,400),lambda :random.randint(20,100),lambda :random.randint(20,100), occurance=0.5),
    createWallF(lambda :random.randint(100,400),lambda :random.randint(100,400),lambda :random.randint(20,100),lambda :random.randint(20,100), occurance=0.5),
    ],[
    createF([Skull,Tnt],250,250,occurance=0.5),
    createF([Saw],50,50, depth=2),
    createF([Saw],50,450, depth=4),
    createF([Saw],450,50, depth=4),
    createF([Saw],450,450, depth=3),
    ],[
    createF([Heart],lambda :random.randint(200,300),lambda :random.randint(200,300)),
    ],], # Heal

    [[
    createWallF(100,100,180,180, occurance=0.3),
    createWallF(lambda :random.randint(200,300),lambda :random.randint(200,300),lambda :random.randint(20,100),lambda :random.randint(20,100), occurance=0.5),
    createWallF(250,250,100,100, occurance=0.5),
    ],[
    createF([Animus],lambda :random.randint(200,300),lambda :random.randint(200,300)),
    createF([Animus],lambda :random.randint(200,300),lambda :random.randint(200,300), depth=2),
    createF([Animus],lambda :random.randint(200,300),lambda :random.randint(200,300), occurance=0.8),
    createF([Sledger],lambda :random.randint(200,300),lambda :random.randint(200,300), depth=3),
    createF([Sledger],lambda :random.randint(200,300),lambda :random.randint(200,300), occurance=0.8, depth=5),
    ],[
    ],], # Animals

    [[
    createWallF(lambda :random.randint(1,4)*100,lambda :random.randint(1,3)*100+50,20,120),
    ]*4+[
    createWallF(lambda :random.randint(1,3)*100+50,lambda :random.randint(1,4)*100,120,20),
    ]*4,[
    createF([SkuggVarg,Sledger,Schmitt],200,250, depth=4),
    createF([SkuggVarg],250,250),
    createF([SkuggVarg,Sledger,Schmitt],300,250, depth=5),
    createF([Chest],250,250, occurance=0.5, lootTable=badItems),
    ],[
    createF([Heart],350,250, occurance=0.5),
    createF([Coin],350,350, occurance=0.6),
    createF([Coin, Spirality],150,150, occurance=0.6),
    ],], # Minotaur

    [[
    createWallF(300,250,20,120,occurance=0.9),
    createWallF(200,250,20,120),
    createWallF(250,300,120,20),
    createWallF(250,200,120,20),
    ],[
    createF([Saw],50,450),
    createF([Schmitt,Sledger],50,50, depth=3),
    createF([Schmitt],50,450, depth=5),
    createF([Skull],450,50, depth=5),
    createF([Schmitt],450,450, depth=4),
    ],[
    createF(badItems,250,250, occurance=0.1),
    ],], # Schmitts' housing

    [[
    ],[
    createF([Svamp],lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(100,game.room.roomSize[1]-100)),
    ]*2+[
    createF([Tnt],lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(100,game.room.roomSize[1]-100),occurance=0.5),
    ]*4+[
    createF([Svamp,Hjuldjurplant,BlazeSpitter],lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(100,game.room.roomSize[1]-100),depth=2),
    createF([Svamp],lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(100,game.room.roomSize[1]-100),depth=3),
    createF([Svamp],lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(100,game.room.roomSize[1]-100),depth=4),
    createF([Svamp],lambda :random.randint(100,game.room.roomSize[0]-100),lambda :random.randint(100,game.room.roomSize[1]-100),depth=5),
    ],[
    createF([Coin],250,250),
    ],], # Fungii

    [[
    createWallF(200,140,400,40),
    createWallF(300,360,400,40),
    createWallF(120,300,40,140, occurance=0.5),
    createWallF(380,200,40,140, occurance=0.5),
    ],[
    createF([Hjuldjurplant,BlazeSpitter],140,70),
    createF([Hjuldjur],70,70, depth=5, occurance=0.5),
    createF([Svamp],lambda :random.randint(100,game.room.roomSize[0]-100),70, depth=2, occurance=0.5),
    createF([Schmitt, Sledger, SkuggVarg],250,250, depth = 4),
    createF([Svamp],lambda :random.randint(100,game.room.roomSize[0]-100),430, depth=2, occurance=0.5),
    createF([Hjuldjur],430,430, depth=5, occurance=0.5),
    createF([Hjuldjurplant,BlazeSpitter],360,430),
    ],[
    createF([Coin],70,70),
    createF([Coin],430,430),
    ],], # Plants

    [[
    ],[
    createF([Statue,Tnt],80,80, occurance=0.6),
    createF([Statue,Tnt,BlazeSpitter],420,80, depth=5, occurance=0.6),
    createF([Statue,Tnt,BlazeSpitter],80,420, depth=5, occurance=0.6),
    createF([Statue,Tnt],420,420, occurance=0.6),
    createF([Mercenary],250,250, depth = 3),
    ],[
    ],], # 12: Duel

    [[
    createWallF(260,140,300,40),
    createWallF(lambda :random.randint(150,350),360,300,40),
    createWallF(130,250,40,260, occurance=0.5),
    ],[
    createF([Hjuldjurplant,BlazeSpitter],420,80, depth=4),
    createF([Portal],250,250, depth=2),
    createF([Portal],80,420, depth=4),
    createF([Tnt],80,80, occurance=0.4),
    ],[
    createF([Coin],430,430),
    ],], # Portals

    [[
    createWallF(250,200,120,20),
    createWallF(200,250,20,120),
    createWallF(300,300,220,20, depth=2),
    createWallF(400,200,20,220, depth=2),
    createWallF(250,100,320,20, depth=3),
    createWallF(100,250,20,320, depth=4),
    createWallF(300,400,420,20, depth=5),
    ],[
    createF([Portal],250,250),
    createF([Tnt],lambda :random.randint(100,400),lambda :random.randint(100,400), occurance=0.5),
    createF([Tnt],lambda :random.randint(100,400),lambda :random.randint(100,400), occurance=0.5),
    createF([Hjuldjurplant],lambda :random.randint(100,400),lambda :random.randint(100,400), occurance=0.5),
    ],[
    createF([Coin],430,430, depth=5),
    ],], # Portal spiral

]

class CharacterSelect():

    def __init__(self):
        load_save_file()
        self.cursor = 0

    def update(self):
        pass

    def draw(self):
        gameDisplay.fill((100,80,50))
        allClasses_draw_anchor = (200,600)
        for i in range(len(allClasses)):
            da_class = (allClasses)[i]
            if i == self.cursor:
                pygame.draw.rect(gameDisplay, (120,100,50), (allClasses_draw_anchor[0]+i*120, allClasses_draw_anchor[1],128,128))
            if da_class.unlocked:
                img = da_class.idleImage[0]
            else:
                img = da_class.blackImage[0]
            gameDisplay.blit(img, (allClasses_draw_anchor[0]+i*120, allClasses_draw_anchor[1]))

        class_draw_anchor = (200,200)
        selected_class = allClasses[self.cursor]
        pygame.draw.rect(gameDisplay, (120,100,50), (*class_draw_anchor,256,256))
        if selected_class.unlocked:
            img = selected_class.idleImage[1]
        else:
            img = selected_class.blackImage[1]
        gameDisplay.blit(pygame.transform.scale_by(img, 2), class_draw_anchor)


        myfont_big = pygame.font.Font(pygame.font.get_default_font(), 50)
        if selected_class.unlocked:
            classname_text = selected_class.__name__
            info_text = selected_class.description
        else:
            classname_text = "LOCKED"
            info_text = [selected_class.unlock_description] # LOL

        classname_text_surf = myfont_big.render(classname_text, False, (0, 0, 0))
        gameDisplay.blit(classname_text_surf,(class_draw_anchor[0] + 20, class_draw_anchor[1]+256 + 40))
        for row in range(len(info_text)):
            info_text_surf = myfont.render(info_text[row], False, (0, 0, 0))
            gameDisplay.blit(info_text_surf,(class_draw_anchor[0]+256 + 40 , class_draw_anchor[1] + 20 + 22*row))

def winAnimation(lose = False):
    myfont_big = pygame.font.Font(pygame.font.get_default_font(), 100)
    pressed = pygame.key.get_pressed()
    da_player_that_won = game.player
    

    #text
    if lose:
        gameDisplay.fill((100,80,50))
        text = da_player_that_won.__class__.__name__.upper() + " SLAIN!"
    else:
        gameDisplay.fill((120,100,50))
        text = da_player_that_won.__class__.__name__.upper() + " WINS!"
    textsurface = myfont_big.render(text, True, (0, 0, 0))
    img = da_player_that_won.idleImage[0]

    for i in range(122):# and not pressed[pygame.K_q]:
        pygame.event.get()
        #for event in pygame.event.get():
         #   if event.type == pygame.QUIT:
          #      State.jump_out = True
        
        gameDisplay.blit(pygame.transform.scale_by(img, 4),(430,110))
        gameDisplay.blit(textsurface,(330,600))

        pygame.display.update()
        clock.tick(60)

characterSelect = CharacterSelect()

Game.playing_a_run = False
jump_out = False
while jump_out == False:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            jump_out = True
        if event.type == pygame.KEYDOWN and not Game.playing_a_run:
            if event.key in [pygame.K_RIGHT, pygame.K_d]:
                characterSelect.cursor = min( characterSelect.cursor +1 , len(allClasses)-1)
            if event.key in [pygame.K_LEFT, pygame.K_a]:
                characterSelect.cursor = max( characterSelect.cursor -1 , 0)
            if event.key in [pygame.K_SPACE, pygame.K_RETURN]:
                if allClasses[characterSelect.cursor].unlocked:
                    Game.playing_a_run = True
                    game = Game(allClasses[characterSelect.cursor])
                    game.enterFloor(Floor(roomPresets))
            if event.key in [pygame.K_q, pygame.K_ESCAPE]:
                jump_out = True


    if Game.playing_a_run:
        game.update()
        game.draw()
    else:
        characterSelect.update()
        characterSelect.draw()

    pygame.display.flip()
    clock.tick(60)
    
pygame.quit()
#quit() #remove for pyinstaller

#ddddddddd         ddddddddd            aa  bssssss  
#aasssddddddSSSSSSDDDDDddddddddddddADDDDDDDDDDDDD