import pygame
from pygame.locals import *
import math

#--------------------------------<VARIABLES>------------------------------------------------------------------------

BLACK = (0,0,0)
WHITE = (255,255,255)
GRAY = (217,217,217)
RED = (255,0,0)
BROWN = (160,82,45)     
WIDTH = 50
HEALTH = 70
FUEL = 60
GROUND_HEIGHT = 110
TIMING = 2

#--------------------------------</VARIABLES>------------------------------------------------------------------------

#--------------------<CLASS>----------------------------------------------------------
class Player(pygame.sprite.Sprite):

    def __init__(self,x,y,img):
        self.chimg = img
        super().__init__()
        self.image = pygame.image.load(img).convert_alpha()

        self.step = 5
        self.width = 50
        self.height = 50

        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.plusHeight = self.height/3 # 정가운데 포가 위치하면 이상하니까 위로 높여주는 상수

        if x < scrWidth/2:
            self.cannonAngle = math.pi /4
        else:
            self.cannonAngle = math.pi - math.pi/4
        
        self.cannonAngleDif = math.pi / 60      
        self.cannonLength = self.width * math.sqrt(2)

        self.reverse()


        self.missileRadius = 5
        self.missile_x = 0
        self.missile_y = 0
        self.missileDx = 10
        self.missileDy = 0
        self.missilePower = 0
        self.Gravity_Acceleration =  0.3

        self.playerDir = 0
        self.cannonDir = 0
        self.isCharging = False
        self.isFired = False
        self.health = HEALTH
        self.have_shoot = False

        self.fuel = FUEL
        self.canMove = True

        #Gauge
        self.gaugeAngle = math.pi
        self.gaugeDif = math.pi/60
        self.gaugeBarRadius = 30 * 2
        self.gaugeRect = pygame.Rect(self.rect.centerx,self.rect.centery - self.cannonLength ,self.gaugeBarRadius, self.gaugeBarRadius)


    def drawGauge(self):
        pygame.draw.arc(screen,RED,self.gaugeRect,0,self.gaugeAngle,width = 7)

    def drawCannon(self):
        if self.health > 0:
            line_x = self.rect.centerx + self.cannonLength * math.cos(self.cannonAngle)
            line_y = self.rect.centery - self.plusHeight - self.cannonLength * math.sin(self.cannonAngle)
            pygame.draw.line(screen ,WHITE,[self.rect.centerx,self.rect.centery - self.plusHeight],(line_x,line_y),width = 6)

    def reverse(self):
        if self.cannonAngle > math.pi/2:
            self.image = pygame.image.load(self.chimg[0:-4] + "_reverse.png").convert_alpha()
        else:
            self.image = pygame.image.load(self.chimg).convert_alpha()


    def update(self):
        self.gaugeRect = pygame.Rect(self.rect.centerx - self.width/2,self.rect.centery - self.cannonLength,self.gaugeBarRadius, self.gaugeBarRadius)


        #위치, 포 각도 조건
        if self.rect.x < 0:  
            self.rect.x = 0
        elif self.rect.x > (scrWidth - self.rect.width):
            self.rect.x = scrWidth - self.rect.width
        if self.cannonAngle > math.pi:
            self.cannonAngle = math.pi
        elif self.cannonAngle < 0:    
            self.cannonAngle = 0

        #실시간으로 변하는 값들
        if self.canMove:
            self.rect.x += self.playerDir * self.step
        self.cannonAngle += self.cannonDir * self.cannonAngleDif

        #연료 감소
        if self.canMove:
            if self.fuel <=0:
                turnOver()
                changeTurn(turn)
            if self.playerDir != 0:
                self.fuel -=1


        #게이지 설정
        if self.isCharging and not(self.isFired) and not(self.have_shoot):
            if self.gaugeAngle > 0.1:
                self.gaugeAngle -= self.gaugeDif
            self.drawGauge()

        self.reverse()

        if self.isFired:
            playerShoot(self.missilePower)

class Missile(pygame.sprite.Sprite):
    
    def __init__(self,power):
        super().__init__()
        self.image = pygame.image.load('missile_small.png').convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = (mainPlayer.rect.centerx + mainPlayer.cannonLength * math.cos(mainPlayer.cannonAngle),mainPlayer.rect.centery - mainPlayer.plusHeight - mainPlayer.cannonLength * math.sin(mainPlayer.cannonAngle) )
        self.power = power
        self.missileDx = mainPlayer.missileDx
        self.missileDy = mainPlayer.missileDy
        self.Gravity_Acceleration = 0.3


    def update(self):
        global turn
        global missileV 
        self.missileDy -= self.Gravity_Acceleration
        self.rect.centerx += self.missileDx
        self.rect.centery -= self.missileDy
        

        missileV = math.sqrt(abs(self.missileDx * self.missileDy)) *2.5
        if self.rect.y > scrHeight - GROUND_HEIGHT -20:
            explosionFx.play()
            self.kill()  # if ammo has left screen, kill it
            playerExplo.setPosition(self.rect.center)
            playerExplo.setVisible(True)
            turnOver()

        if self.rect.x < 0 or self.rect.x > scrWidth:
            self.kill()
            turnOver()

class Box(pygame.sprite.Sprite):
    def __init__(self):
        super().__init__()
        self.image = pygame.image.load('box.png').convert_alpha()
        self.rect = self.image.get_rect()



class AnimSprite(pygame.sprite.Sprite):

    def __init__(self, fnm, numPics):
        # assume that sheet in fnm is a single column of numPics pics
        super().__init__()
        self.frames = []
        for frameNum in range(1,13):
            self.frames.append(pygame.image.load("tank_explosion"+ str(frameNum)+'.png').convert_alpha())

        self.numPics = numPics
        self.isVisible = False
        self.isRepeating = False
        self.frameNo = 0
        self.image = self.frames[self.frameNo]
        self.rect = self.image.get_rect()
        self.rect.topleft = (scrWidth/2,scrHeight/2)


    def setVisible(self, isVisible):
        self.isVisible = isVisible

    def setRepeating(self, isRepeating):
        self.isRepeating = isRepeating

    def setPosition(self, pos):
        self.rect.center = pos

    def draw(self, screen):
        global timing
        if self.isVisible:
            if timing == TIMING:
                timing = 0
                self.frameNo = (self.frameNo + 1) % self.numPics
                self.image = self.frames[self.frameNo]
            screen.blit(self.image, (self.rect.centerx - self.image.get_width() // 2, self.rect.centery - self.image.get_height() // 2)) # 가운데에 blit하는법
            if self.frameNo == 0 and not self.isRepeating:
                self.isVisible = False




#--------------------------------</CLASS>--------------------------------------------------------------------


#--------------------------------<FUNCTION>------------------------------------------------------------------
def playerShoot(power):
    global mainBullet
    if mainPlayer.isFired and not(mainPlayer.have_shoot):
        mainPlayer.canMove = False
        tank_fireFx.play()
        bullet = Missile(power)
        mainBullet = bullet
        sprites.add(bullet)
        missiles.add(bullet)

        mainPlayer.isFired = False
        mainPlayer.have_shoot = True

def changeTurn(turn):
    global mainPlayer
    if turn == 1:
        mainPlayer = player1
    else:
        mainPlayer = player2
        

def isGameOver(p1, p2):
    global finalMSG
    if p1.health <=0: 
        finalMSG = "Player2 WIN!!!"
        return True
    elif p2.health <=0:
        finalMSG = "Player1 WIN!!!"
        return True
    else:
        return False
        
def checkCollisions():
    global turn

    if pygame.sprite.groupcollide(missiles, walls, True, True):
        explosionFx.play()
        playerExplo.setPosition(mainBullet.rect.center)
        playerExplo.setVisible(True)
        turnOver()

    
    for target in pygame.sprite.groupcollide(players, missiles, False, True):
        explosionFx.play()
        playerExplo.setPosition(mainBullet.rect.center)
        playerExplo.setVisible(True)
        target.health -= missileV
        turnOver()
      
def turnOver():
    global turn 
    global missileV
    mainPlayer.playerDir = 0
    mainPlayer.isFired = False
    mainPlayer.have_shoot = False
    mainPlayer.gaugeAngle = math.pi
    mainPlayer.missilePower  = 0
    mainPlayer.fuel = FUEL
    mainPlayer.canMove = True
    turn *=-1
    missileV = 0

def drawUI():

    player1H_rect = pygame.Rect(50, 50,player1.health * 5,50)
    player2H_rect = pygame.Rect(scrWidth/2 + 400, 50,player2.health * 5,50)

    player1F_rect = pygame.Rect(50, 130,player1.fuel * 5,30)
    player2F_rect = pygame.Rect(scrWidth/2 + 400, 130,player2.fuel * 5,30)

    #체력바
    pygame.draw.rect(screen,RED,player1H_rect, width = 0)
    pygame.draw.rect(screen,RED,player2H_rect, width = 0)


    #연료바
    pygame.draw.rect(screen,BROWN,player1F_rect, width = 0)
    pygame.draw.rect(screen,BROWN,player2F_rect, width = 0)

    #턴 사인 그리기
    if mainPlayer == player1:
        screen.blit(lightbulb, (0,0))
    if mainPlayer == player2:
        screen.blit(lightbulb, (scrWidth - 200, 50))


def createWall(height):
    for r in range(height):
        box = Box()
        box.rect.x = (scrWidth - box.rect.width) // 2 
        box.rect.y = box.rect.height + r * box.rect.height
        walls.add(box)
        sprites.add(box)


#---

#------------------------------</FUNCTION>------------------------------------------------------------------
        

#--------------------------------<MAIN>------------------------------------------------------------------------
# create sprite groups
sprites = pygame.sprite.Group()
missiles = pygame.sprite.Group()
players = pygame.sprite.Group()
walls = pygame.sprite.Group()

pygame.init()
screen = pygame.display.set_mode([1600,800])
pygame.display.set_caption('Fortress')
scrWidth, scrHeight = screen.get_size()

# game fonts
pygame.font.init()
gameFont = pygame.font.Font('RETRO_SPACE.ttf', 28)
splashFont = pygame.font.Font('RETRO_SPACE.ttf', 72)


#image
background = pygame.image.load('game_background.jpg').convert_alpha()
playerExplo = AnimSprite('explosive_animated.png', 9)
lightbulb = pygame.image.load('lightBulb.png')
startScreen = pygame.image.load('game_startScreen.png')

#sound
engine_soundFx= pygame.mixer.Sound('engineLoop.wav')
tank_fireFx = pygame.mixer.Sound('fire.wav')
explosionFx = pygame.mixer.Sound('explosion.wav')
winFx = pygame.mixer.Sound('win_sound.wav')
pygame.mixer.music.load('background.wav')
pygame.mixer.music.play(-1)
pygame.mixer.music.set_volume(0.25)



turn = 1
finalMSG= ""
clock  = pygame.time.Clock()
gameOver = False
missileV = 0
timing = 0
mainBullet = None
showStartScreen = True
#main


player1 = Player(0,scrHeight - WIDTH - GROUND_HEIGHT ,"tanks_tankGreen_body1.png")
player2 = Player(scrWidth - WIDTH,  scrHeight - WIDTH - GROUND_HEIGHT,"tanks_tankNavy_body1.png")
players.add(player1,player2)

mainPlayer = player1

sprites.add(player1,player2)
createWall(13)
engine_soundFx.set_volume(0.3)
engine_soundFx.play(loops=-1)


running = True

while running:
    if timing <TIMING:
        timing +=1

    #턴 정하기 
    changeTurn(turn)

    if isGameOver(player1,player2):
        gameOver = True

    clock.tick(60) 

    for event in pygame.event.get():
        if event.type == QUIT:
            running = False
        if event.type == KEYDOWN:
            if event.key == K_ESCAPE:
                running = False
            elif event.key == K_a:
                engine_soundFx.set_volume(0.8)
                mainPlayer.playerDir = -1
            elif event.key == K_d:
                engine_soundFx.set_volume(0.8)
                mainPlayer.playerDir = 1
            elif event.key == K_UP:
                mainPlayer.cannonDir = 1
            elif event.key == K_DOWN:
                mainPlayer.cannonDir = -1
            elif event.key == K_SPACE:
                mainPlayer.isCharging = True
            showStartScreen = False
                

        if event.type == KEYUP:
            engine_soundFx.set_volume(0.3)
            if event.key == K_a or event.key == K_d:
                mainPlayer.playerDir = 0
            elif event.key == K_UP or event.key == K_DOWN:
                mainPlayer.cannonDir = 0
            elif event.key == K_SPACE:
                mainPlayer.isCharging = False
                mainPlayer.isFired = True
                mainPlayer.missilePower = (math.pi - mainPlayer.gaugeAngle) * 10
                mainPlayer.missileDx = mainPlayer.missilePower * math.cos(mainPlayer.cannonAngle)
                mainPlayer.missileDy = mainPlayer.missilePower * math.sin(mainPlayer.cannonAngle)
                mainPlayer.gaugeAngle = math.pi


    #update the game
    if not(gameOver):
        checkCollisions()
        sprites.update()

    if gameOver:
        winFx.play()
        pygame.mixer.music.stop()
        screen.blit(splashFont.render(finalMSG,  1, RED), (scrWidth/2 - 300,scrHeight/2-300))
        screen.blit(splashFont.render('Press Esc to Exit',  1, BLACK), (scrWidth/2 - 400 ,scrHeight/2-200))

    pygame.display.update()

    #redraw the 
    if showStartScreen:
        screen.blit(startScreen, [0,0])
    else:
        screen.blit(background, [0, 0])
        drawUI()
        sprites.draw(screen)
        player1.drawCannon()
        player2.drawCannon()
        playerExplo.draw(screen)


pygame.quit()

#--------------------------------</MAIN>------------------------------------------------------------------------



