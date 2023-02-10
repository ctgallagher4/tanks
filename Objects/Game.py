import pygame
import pygame
import numpy as np
from Utilities.Constants import *
from Objects.Tank import Tank
from Objects.Bullet import Bullet
from Objects.Target import Target
from Objects.Explosion import Explosion

class Game():

    '''A class to handle the Game'''

    def __init__(self):
        self.surface = pygame.display.set_mode((WIDTH, HEIGHT))
        pygame.display.set_caption('shadowTanks')
        self.clock = pygame.time.Clock()
        self.fontEnd = pygame.font.SysFont('timesnewroman', 300)
        self.fontLife = pygame.font.SysFont('timesnewroman', 100)
        self.fontDuring = pygame.font.SysFont('timesnewroman', 100)
        self.fontfps = pygame.font.SysFont('timesnewroman', 50)
        self.score = 0
        self.objects = []
        self.bulletThresh = 0
        self.bullets = []
        self.fuel = 100
        self.health = 100
        pygame.mouse.set_cursor(*pygame.cursors.diamond)

    def eventListener(self):
        '''A method to listen for events, specifically quit'''
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                return False
        else:
            return True

    def displayScore(self):
        '''A method to display the score to the screen'''
        score = self.fontDuring.render(str(self.score), False, WHITE)
        self.surface.blit(score, (100,100))

    def setup(self):
        '''A method to setup the game sprites'''
        self.target = Target(self.surface)
        self.objects.append(self.target)
        self.player = Tank(self, self.surface, "tank_body.png", "turret.png", WIDTH/2, 
                           HEIGHT/2, lightOn = True)
        self.adversary1 = Tank(self, self.surface, "tank_body_red.png", "turret_red.png",
                              0, HEIGHT/2, target = self.player)
        self.adversary2 = Tank(self, self.surface, "tank_body_red.png", "turret_red.png",
                              WIDTH/2, 0, target=self.player)
        self.adversary3 = Tank(self, self.surface, "tank_body_red.png", "turret_red.png",
                              WIDTH, HEIGHT/2, target=self.player)
        self.adversary4 = Tank(self, self.surface, "tank_body_red.png", "turret_red.png",
                              WIDTH/2, HEIGHT, target=self.player)
        self.objects.append(self.adversary1)
        self.objects.append(self.adversary2)
        self.objects.append(self.adversary3)
        self.objects.append(self.adversary4)
        #self.objects.append(self.player)

    def reset(self):
        '''A method to reset the game sprites'''
        self.objects = [] 
        self.setup()
        self.score = 0
        self.fuel = 100
        self.health = 100

    def pause(self):
        '''A method to pause the game'''
        pygame.time.wait(500)
        while self.eventListener():
            self.displayScore()
            pause = self.fontLife.render("Press spacebar to continue...", 
                                            False, WHITE, BLACK)
            self.surface.blit(pause, (WIDTH/5, HEIGHT/3))
            pygame.display.flip()
            keys = pygame.key.get_pressed()
            if keys[pygame.K_SPACE] == 1:
                self.reset()
                break

    def display(self):
        self.surface.fill(WHITE)

    def handleFuel(self):
        background = pygame.Rect(WIDTH/25, 0, WIDTH / 10, 25)
        fuel = pygame.Rect(WIDTH/25, 0, self.fuel / 100 * WIDTH / 10, 25)
        pygame.draw.rect(self.surface, RED, background)
        pygame.draw.rect(self.surface, GREEN, fuel)
        if self.fuel <= 0:
            self.pause()
    
    def handleHealth(self):
        background = pygame.Rect(WIDTH/25, 25, WIDTH / 10, 25)
        fuel = pygame.Rect(WIDTH/25, 25, self.health / 100 * WIDTH / 10, 25)
        pygame.draw.rect(self.surface, WHITE, background)
        pygame.draw.rect(self.surface, BLUE, fuel)
        if self.health <= 0:
            self.pause()


    def tickFlip(self):
        self.clock.tick(FRAME_RATE)
        fps = self.fontfps.render(str(round(self.clock.get_fps(), 2)), False, GREEN)
        self.surface.blit(fps, (WIDTH - 150, HEIGHT - 100))
        pygame.display.update()


    def updateGameItems(self):
        to_be_removed = []
        explosionsAndSelfBullets = []
        for item in self.objects:
            if type(item) != Explosion:
                item.update()
            if type(item) == Bullet:
                if item.OOB:
                    to_be_removed.append(item)
            if type(item) == Explosion:
                if not item.OOB:
                    explosionsAndSelfBullets.append(item)
                else:
                    to_be_removed.append(item)
            if item.origin == self.player:
                explosionsAndSelfBullets.append(item)


        while to_be_removed != []:
            self.objects.remove(to_be_removed[0])
            to_be_removed.pop(0)


        self.player.update()


        for item in explosionsAndSelfBullets:
            if type(item) == Explosion:
                item.update()
            if type(item) == Bullet:
                pygame.draw.rect(self.surface, GREEN, item.rect, 1)

    def updateGame(self):
        self.checkAndLaunch()
        self.checkCollision()
        self.updateGameItems()
        self.handleFuel()
        self.handleHealth()

    def checkAdversaryLaunch(self):
        fireChance = (FIRE_CHANCE_PER_SECOND + DIFFICULTY_MOD * self.score) / FRAME_RATE
        speed = (1 + self.score * DIFFICULTY_MOD) * ENEMY_BULLET_SPEED
        if np.random.randint(0, 1000) / 1000 >= 1 - fireChance:
            xVel = -1 * speed * np.sin((self.adversary1.turDir / 360) * 2 * np.pi)
            yVel = -1 * speed * np.cos((self.adversary1.turDir / 360) * 2 * np.pi)
            turDir = self.adversary1.turDir / 360 * 2 * np.pi
            self.adversary1.stop()
            self.objects.append(Bullet(self.adversary1.x, self.adversary1.y, xVel,
                                       yVel, turDir, self.surface, self.adversary1))
            if np.random.randint(0, 1000) / 1000 >= 1 - TURN_CHANCE:
                self.adversary1.dir = np.random.randint(0, 360)
            self.adversary1.forward()

        if np.random.randint(0, 1000) / 1000 >= 1 - fireChance:
            xVel = -1 * speed * np.sin((self.adversary2.turDir / 360) * 2 * np.pi)
            yVel = -1 * speed * np.cos((self.adversary2.turDir / 360) * 2 * np.pi)
            turDir = self.adversary2.turDir / 360 * 2 * np.pi
            self.adversary2.stop()
            self.objects.append(Bullet(self.adversary2.x, self.adversary2.y, xVel,
                                       yVel, turDir, self.surface, self.adversary2))
            if np.random.randint(0, 1000) / 1000 >= 1 - TURN_CHANCE:
                self.adversary2.dir = np.random.randint(0, 360)
            self.adversary2.forward()

        if np.random.randint(0, 1000) / 1000 >= 1 - fireChance:
            xVel = -1 * speed * np.sin((self.adversary3.turDir / 360) * 2 * np.pi)
            yVel = -1 * speed * np.cos((self.adversary3.turDir / 360) * 2 * np.pi)
            turDir = self.adversary3.turDir / 360 * 2 * np.pi
            self.adversary3.stop()
            self.objects.append(Bullet(self.adversary3.x, self.adversary3.y, xVel,
                                       yVel, turDir, self.surface, self.adversary3))
            if np.random.randint(0, 1000) / 1000 >= 1 - TURN_CHANCE:
                self.adversary3.dir = np.random.randint(0, 360)
            self.adversary3.forward()
        
        if np.random.randint(0, 1000) / 1000 >= 1 - fireChance:
            xVel = -1 * speed * np.sin((self.adversary4.turDir / 360) * 2 * np.pi)
            yVel = -1 * speed * np.cos((self.adversary4.turDir / 360) * 2 * np.pi)
            turDir = self.adversary4.turDir / 360 * 2 * np.pi
            self.adversary4.stop()
            self.objects.append(Bullet(self.adversary4.x, self.adversary4.y, xVel,
                                       yVel, turDir, self.surface, self.adversary4))
            if np.random.randint(0, 1000) / 1000 >= 1 - TURN_CHANCE:
                self.adversary4.dir = np.random.randint(0, 360)
            self.adversary4.forward()
        
    def checkAndLaunch(self):
        keys = pygame.key.get_pressed()
        currTime = pygame.time.get_ticks()
        if keys[pygame.K_SPACE] and currTime > self.bulletThresh:
            self.bulletThresh = currTime + SHOOT_DELAY
            xVel = -1 * BULLET_SPEED * np.sin((self.player.turDir / 360) * 2 * np.pi)
            yVel = -1 * BULLET_SPEED * np.cos((self.player.turDir / 360) * 2 * np.pi)
            turDir = self.player.turDir / 360 * 2 * np.pi
            self.objects.append(Bullet(self.player.x, self.player.y, xVel, yVel, turDir, self.surface, self.player))

        self.checkAdversaryLaunch()

    def checkReachTarget(self):
        if self.target.rect.contains(self.player.bodyRect):
            self.target.setLoc()
            self.score += 1
            self.fuel = 100
            if self.health < 100:
                self.health += 10

    def resetAdversary(self, adversary):

        self.objects.append(Explosion(self.surface, adversary.x, adversary.y))
        adversary.tagTime = 0

        side = np.random.choice(["left", "top", "right", "bottom"])
        if side == "left":
            adversary.x = 0
            adversary.y = np.random.randint(0, HEIGHT)
        if side == "top":
            adversary.x = np.random.randint(0, WIDTH)
            adversary.y = 0
        if side == "bottom":
            adversary.x = np.random.randint(0, WIDTH)
            adversary.y = HEIGHT
        if side == "right":
            adversary.x = np.random.randint(0, WIDTH)
            adversary.y = 0

        self.score += 3

    def checkBulletHit(self):
        for item in self.objects:
            if (type(item) == Bullet and item.origin == self.player):
                if self.adversary1.bodyRect.contains(item):
                    item.OOB = True
                    self.resetAdversary(self.adversary1)
                if self.adversary2.bodyRect.contains(item):
                    item.OOB = True
                    self.resetAdversary(self.adversary2)
                if self.adversary3.bodyRect.contains(item):
                    item.OOB = True
                    self.resetAdversary(self.adversary3)
                if self.adversary4.bodyRect.contains(item):
                    item.OOB = True
                    self.resetAdversary(self.adversary4)

            elif (type(item) == Bullet and item.origin.lightOn == False):
                if self.player.bodyRect.contains(item):
                    self.health -= 10
                    item.OOB = True
            
    def checkCollision(self):
        self.checkReachTarget()
        self.checkBulletHit()
    
    def run(self):
        self.setup()
        gameOn = True
        while gameOn:
            self.display()
            self.updateGame()
            self.displayScore()
            self.tickFlip()
            gameOn = self.eventListener()