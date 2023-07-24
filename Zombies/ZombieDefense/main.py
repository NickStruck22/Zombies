import pygame, sys, math
from random import *
from pygame.locals import *

pygame.init()
FPS = 30 
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
SIRINAEKRANA = 800
VISINAEKRANA = 600

FONT = pygame.font.Font('freesansbold.ttf', 16)
scoreText = FONT.render('Score: ', True, RED)
scoreRect = scoreText.get_rect()
scoreRect.topleft = (SIRINAEKRANA - 150, 25)

bangSound = pygame.mixer.Sound('bang.ogg')
punchSound = pygame.mixer.Sound('punch.ogg')
zDeathSound = pygame.mixer.Sound('zDeath.ogg')
gameOverSound = pygame.mixer.Sound('gameOver.ogg')
winSound = pygame.mixer.Sound('win.ogg')
lvlUpSound = pygame.mixer.Sound('lvlup.ogg')

ramboImg = pygame.image.load('rambo.png')
ramboRect = ramboImg.get_rect()
ramboRect.center = (SIRINAEKRANA/2, VISINAEKRANA/2)

pistolImg = pygame.image.load('pistol.png')
shotgunImg = pygame.image.load('shotgun.png')
rifleImg = pygame.image.load('rifle.png')

crosshairImg = pygame.image.load('crosshair.png')
crosshairRect = crosshairImg.get_rect()

basicZombieImg = pygame.transform.scale(pygame.image.load('basicZombie.png'), [55, 90])
shieldZombieImg = pygame.transform.scale(pygame.image.load('shieldZombie.png'), [70, 105])
bossZombieImg = pygame.transform.scale(pygame.image.load('zombieBoss.png'), [100, 120])

blackBarImg = pygame.transform.scale(pygame.image.load('hpbarBlack.png'), [50, 5])
greenBarImg = pygame.transform.scale(pygame.image.load('hpbarGreen.png'), [50, 5])
redBarImg = pygame.transform.scale(pygame.image.load('hpbarRed.png'), [50, 5])

bulletImg = pygame.image.load('bullet.png')

bgd1 = pygame.image.load('zBackground.jpg')

ramboDirection = 'right'
ramboMSpeed = 5

lastShootTime = 0
lastHitTime = 0

pressed = False
soundPlayed = False

class Weapon:

    def __init__(self) -> None:
        self.angle = 0, False
        
    def drawWeapon(self, screen, mousepos):
        global ramboRect
        self.rect.center = ramboRect.center
        # formula za nalazenje ugla izmedju pistolja i nisana, da bi znali za kolko da rotiramo pistolj, tako da gleda u nisan
        angle = 360 - math.atan2(mousepos[1]-self.rect.centery, mousepos[0]-self.rect.centerx)*180/math.pi
        # print(angle) ovo smo koristili da bi nasli izmedju kojih uglova treba da flipujemo sliku
        if (angle > 180 and angle < 270) or (angle <= 540 and angle > 450): # ovime flipujemo po y-osi pistolj i menjamo ugao
            rotImg = pygame.transform.rotate(self.img, 360 - angle)        # ako je pistolj okrenut ulevo, da ne bi bio naopacke
            rotRect = rotImg.get_rect(center = (self.rect.center))
            rotImg = pygame.transform.flip(rotImg, False, True)
            self.angle = 360 - angle, True
        else:
            rotImg = pygame.transform.rotate(self.img, angle)
            rotRect = rotImg.get_rect(center = (self.rect.center))
            self.angle = angle, False
        screen.blit(rotImg, rotRect)

class Pistol(Weapon):

    def __init__(self) -> None:
        super().__init__()
        self.damage = 30
        self.cooldown = 600
        self.img = pistolImg
        self.rect = self.img.get_rect()

class Shotgun(Weapon):

    def __init__(self) -> None:
        super().__init__()
        self.damage = 35
        self.cooldown = 1000
        self.img = shotgunImg
        self.rect = self.img.get_rect()

class Rifle(Weapon):

    def __init__(self) -> None:
        super().__init__()
        self.damage = 20
        self.cooldown = 200
        self.img = rifleImg
        self.rect = self.img.get_rect()

weapon = Pistol()

class GameManager:

    def __init__(self) -> None:
        self.zombies1 = []
        self.zombies2 = []
        self.zombies3 = []
        self.zombies = []
        self.bullets = []
        self.nextLevel = False
        self.levelRunning = False
        self.level = 0
    
    def setupLevels(self):
        self.zombies1.append(BasicZombie())
        self.zombies1.append(ShieldZombie())
        self.zombies1.append(BasicZombie())
        self.zombies1.append(BasicZombie())
        self.zombies1.append(BasicZombie())

        self.zombies2.append(BasicZombie())
        self.zombies2.append(BasicZombie())
        self.zombies2.append(ShieldZombie())
        self.zombies2.append(ShieldZombie())
        self.zombies2.append(ShieldZombie())

        self.zombies3.append(BasicZombie())
        self.zombies3.append(ShieldZombie())
        self.zombies3.append(ShieldZombie())
        self.zombies3.append(ShieldZombie())
        self.zombies3.append(BossZombie())
    
    def play(self, screen):
        global pressed, weapon, soundPlayed
        if self.level == 0:
            instructionText = FONT.render('PRESS ENTER TO START', True, RED)
            instructionRect = instructionText.get_rect()
            instructionRect.center = (SIRINAEKRANA/2, VISINAEKRANA/2)
            screen.blit(instructionText, instructionRect)
            
            if pressed:
                pygame.time.wait(500)
                self.level = 1
                self.bullets.clear()
        elif not self.levelRunning and self.level == 1:
            self.zombies = self.zombies1
            self.levelRunning = True
            self.nextLevel = False
        elif not self.levelRunning and  self.level == 2:
            self.zombies = self.zombies2
            weapon = Shotgun()
            self.levelRunning = True
            self.nextLevel = False
        elif not self.levelRunning and  self.level == 3:
            self.zombies = self.zombies3
            weapon = Rifle()
            self.levelRunning = True
            self.nextLevel = False
        elif not self.levelRunning and  self.level == 4:
            if not soundPlayed:
                winSound.play()
                soundPlayed = True
            instructionText = FONT.render('YOU WON!!!', True, RED)
            instructionRect = instructionText.get_rect()
            instructionRect.center = (SIRINAEKRANA/2, VISINAEKRANA/2)
            screen.blit(instructionText, instructionRect)
        elif self.levelRunning and not self.nextLevel:
            self.checkEnemies()
            self.draw(screen)
        elif self.levelRunning and self.nextLevel:
            self.draw(screen)
            if ramboRect.left > SIRINAEKRANA:
                self.levelRunning = False
                ramboRect.center = (SIRINAEKRANA/2, VISINAEKRANA/2)
                self.bullets.clear()
                self.level += 1

    def checkEnemies(self):
        if len(self.zombies) == 0:
            lvlUpSound.play()
            self.nextLevel = True

    def draw(self, screen):
        for bullet in self.bullets:
            bullet.move(screen)
            bullet.drawBullet(screen)

        if len(self.zombies) != 0:
            for zombie in self.zombies:
                zombie.move()
                zombie.drawZombie(screen)

            for bullet in self.bullets:
                for zombie in self.zombies:
                    if zombie.imgRect.colliderect(bullet.rect):
                        self.bullets.remove(bullet)
                        zombie.hpBar.removeHp(weapon.damage)
                        zombie.checkDead()
                        break
        
        instructionText = FONT.render('Round ' + str(self.level), True, RED)
        instructionRect = instructionText.get_rect()
        instructionRect.center = (50, 20)
        screen.blit(instructionText, instructionRect)

game = GameManager()

class HpBar:

    def __init__(self, bar) -> None:
        self.maxHP = 100
        self.hp = 100
        self.black = blackBarImg
        self.bar = bar
        self.pos = (ramboRect.topleft[0], ramboRect.topleft[1] - 6)

    def changeHP(self, damage):
        global lastHitTime
        if pygame.time.get_ticks() - lastHitTime >= 500:
            lastHitTime = pygame.time.get_ticks()
            punchSound.play()
            self.hp -= damage
            self.bar = pygame.transform.scale(self.bar, [max(0, self.hp/self.maxHP * 50), 5])
            if self.hp <= 0:
                gameOverAnimation()
            print(str(self.hp) + '/' + str(self.maxHP))

    def removeHp(self, damage):
        #global game
        self.hp -= damage
        self.bar = pygame.transform.scale(self.bar, [max(0, self.hp/self.maxHP * 50), 5])

    def drawHp(self, screen):
        screen.blit(self.black, self.pos)
        screen.blit(self.bar, self.pos)

ramboHpBar = HpBar(greenBarImg)

def main():
    screen = pygame.display.set_mode((SIRINAEKRANA, VISINAEKRANA))
    pygame.display.set_caption('Zombie Defense')
    fpsClock = pygame.time.Clock() 
    
    pygame.mouse.set_visible(False)

    game.setupLevels()

    while True:
        screen.blit(bgd1, (0, 0))       
        
        checkInput()
        ramboHpBar.pos = checkMove()

        screen.blit(ramboImg, ramboRect)
        ramboHpBar.drawHp(screen)

        mousepos = pygame.mouse.get_pos()
        
        weapon.drawWeapon(screen, mousepos)

        game.play(screen)
        
        crosshairRect.center = mousepos
        screen.blit(crosshairImg, crosshairRect)

        pygame.display.update()
        fpsClock.tick(FPS)


def gameOverAnimation():
    gameOverSound.play()
    pygame.time.wait(5000)
    terminate()


def checkMove():
    global ramboImg, ramboDirection

    keys = pygame.key.get_pressed()

    if keys[pygame.K_a]:
        if ramboRect.left > 0:                          # ogranicenje sleva
            ramboRect.centerx -= ramboMSpeed
        
        if ramboDirection == 'right':                   # rotiramo ramba ako je promenio stranu u koju gleda
            ramboImg = pygame.transform.flip(ramboImg, True, False)
            ramboDirection = 'left'
    
    elif keys[pygame.K_d]:
        if ramboRect.right < SIRINAEKRANA:              # ogranicenje zdesna
            ramboRect.centerx += ramboMSpeed
        elif game.nextLevel:                             # ako je goToNextLevel True, onda mozemo da idemo
            ramboRect.centerx += ramboMSpeed          # kroz desnu ivicu
        
        if ramboDirection == 'left':                    # rotiramo ramba ako je promenio stranu u koju gleda
            ramboImg = pygame.transform.flip(ramboImg, True, False)
            ramboDirection = 'right'
    
    if keys[pygame.K_w]:
        if ramboRect.bottom > VISINAEKRANA / 3 + 50:    # ogranicenje odozgo
            ramboRect.centery -= ramboMSpeed
    
    elif keys[pygame.K_s]:
        if ramboRect.bottom < VISINAEKRANA:             # ogranicenje odozdo
            ramboRect.centery += ramboMSpeed
    
    return (ramboRect.topleft[0], ramboRect.topleft[1] - 6)

def shoot():
    global game
    angle_radians = math.atan2((crosshairRect.centery - weapon.rect.centery), (crosshairRect.centerx - weapon.rect.centerx))
    if type(weapon) != Shotgun:
        game.bullets.append(Bullet(weapon.rect.centerx, weapon.rect.centery, angle_radians))
    else:
        game.bullets.append(Bullet(weapon.rect.centerx, weapon.rect.centery, angle_radians-0.175))
        game.bullets.append(Bullet(weapon.rect.centerx, weapon.rect.centery, angle_radians))
        game.bullets.append(Bullet(weapon.rect.centerx, weapon.rect.centery, angle_radians+0.175))
    bangSound.play()

def terminate():
    pygame.quit()
    sys.exit()

def checkInput():
    global lastShootTime, pressed
    for event in pygame.event.get(QUIT): 
        terminate()
    for event in pygame.event.get(KEYUP):
        if event.key == K_RETURN:
            pressed = True
        if event.key == K_ESCAPE:
            terminate()
        pygame.event.post(event)

    if pygame.mouse.get_pressed()[0]:
        if pygame.time.get_ticks() - lastShootTime >= weapon.cooldown:
            lastShootTime = pygame.time.get_ticks()
            shoot()

class Zombie:

    def __init__(self) -> None:
        self.x = choice([0, SIRINAEKRANA])
        self.y = randrange(250, VISINAEKRANA)
        self.direction = 'left'
        self.hpBar = HpBar(redBarImg)

    def move(self):
        distance = math.sqrt((ramboRect.centerx - self.imgRect.centerx)**2 + (ramboRect.centery - self.imgRect.centery)**2)
        angle_radians = math.atan2((ramboRect.centery - self.y), (ramboRect.centerx - self.x))

        if distance > 45:
            self.y += self.speed * math.sin(angle_radians)
            self.x += self.speed * math.cos(angle_radians)

            self.imgRect.centerx = self.x
            self.imgRect.centery = self.y

            self.hpBar.pos = (self.imgRect.topleft[0], self.imgRect.topleft[1] - 6)

            if self.direction == 'left' and ramboRect.centerx > self.x:
                self.direction = 'right'
                self.image = pygame.transform.flip(self.image, True, False)
            elif self.direction == 'right' and ramboRect.centerx < self.x:
                self.direction = 'left'
                self.image = pygame.transform.flip(self.image, True, False)
        else:
            ramboHpBar.changeHP(self.damage)

    def checkDead(self):
        if self.hpBar.hp <= 0:
            zDeathSound.play()
            game.zombies.remove(self)

    def drawZombie(self, screen):
        screen.blit(self.image, self.imgRect)
        self.hpBar.drawHp(screen)

class BasicZombie(Zombie):

    def __init__(self) -> None:
        super().__init__()
        self.image = basicZombieImg
        self.imgRect = self.image.get_rect()
        self.speed = 3
        self.damage = 10
        self.hpBar.maxHP = 60
        self.hpBar.hp = 60
        
class ShieldZombie(Zombie):

    def __init__(self) -> None:
        super().__init__()
        self.image = shieldZombieImg
        self.imgRect = self.image.get_rect()
        self.speed = 2
        self.damage = 20
        self.hpBar.maxHP = 120
        self.hpBar.hp = 120
        
class BossZombie(Zombie):

    def __init__(self) -> None:
        super().__init__()
        self.image = bossZombieImg
        self.imgRect = self.image.get_rect()
        self.speed = 1
        self.damage = 35
        self.hpBar.maxHP = 300
        self.hpBar.hp = 300
        

class Bullet:

    def __init__(self, x, y, angle) -> None:
        self.x = x
        self.y = y
        self.speed = 10
        self.angle = angle
        self.image = pygame.transform.rotate(bulletImg, weapon.angle[0])
        self.rect = self.image.get_rect()
        if weapon.angle[1]:
            self.image = pygame.transform.flip(self.image, False, True)

    def move(self, screen):
        global game
        self.y += self.speed * math.sin(self.angle)
        self.x += self.speed * math.cos(self.angle)
        self.rect.center = (self.x, self.y)
        if not screen.get_rect().collidepoint(self.x, self.y):
            game.bullets.remove(self)
    
    def drawBullet(self, screen):
        screen.blit(self.image, (self.x, self.y))

if __name__ == '__main__':
    main()