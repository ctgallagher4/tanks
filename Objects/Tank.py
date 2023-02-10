import pygame
import numpy as np
from Utilities.Constants import *
from Objects.Bullet import Bullet
from threading import Thread, Lock
import time

class Tank(pygame.sprite.Sprite):

    def __init__(self, game, surface, bodyImage, turretImage, x, y, lightOn=False, target=None):\

        pygame.sprite.Sprite.__init__(self)

        self.surface = surface
        self.dir = 0
        self.turDir = 180
        self.x = x
        self.y = y
        self.prev = 0
        self.xVel = 0
        self.yVel = 0
        self.lightOn = lightOn
        self.target = target
        self.game = game
        self.rotating = False
        self.blitRect = pygame.Rect(self.x, self.y, WIDTH, HEIGHT)
        self.radarRadius = 500
        self.countTilNextMove = 0
        self.origin = None
        self.radDir = 0
        self.radLine = ((self.x, self.y), (self.x + self.radarRadius*np.sin(self.radDir),
                                          self.y + self.radarRadius*np.cos(self.radDir)))
        self.tagTime = 0

        if lightOn:
            self.lightImage = pygame.image.load("image4.png").convert_alpha()
            sizeX = self.lightImage.get_size()[0]
            sizeY = self.lightImage.get_size()[1]
            self.scaleLightImageSize = [sizeX * .60, sizeY * 2.5]
            self.lightImage = pygame.transform.scale(self.lightImage, self.scaleLightImageSize)
            self.lightImage = pygame.transform.rotate(self.lightImage, 180)
            self.filt = pygame.surface.Surface((WIDTH, HEIGHT), pygame.SRCALPHA)
        
        self.bodyImage = pygame.image.load(bodyImage).convert_alpha()
        self.scaleBodyImageSize = [i/WIDTH * 300 for i in self.bodyImage.get_size()]
        self.bodyImage = pygame.transform.scale(self.bodyImage, self.scaleBodyImageSize)
        self.turretImage = pygame.image.load(turretImage).convert_alpha()
        self.scaleTurretImageSize = [i/WIDTH * 300 for i in self.turretImage.get_size()]
        self.turretImage = pygame.transform.scale(self.turretImage, self.scaleTurretImageSize)
        self.bodyRect = self.bodyImage.get_rect(center = (self.x, self.y))
        self.turretRect = self.turretImage.get_rect(center = (self.x, self.y))

    def drawRadar(self):
        rect = pygame.Rect(self.x - self.radarRadius, 
                           self.y - self.radarRadius, 
                           self.radarRadius * 2,
                           self.radarRadius * 2)
        # pygame.draw.rect(self.surface, GREEN, rect, 2)
        pygame.draw.arc(self.surface, GREEN, rect, 
                        self.radDir - np.pi/10 - 1.02*np.pi/2, 
                        self.radDir - 1.02*np.pi/2,
                        width = 2)
        points = [*self.radLine, (self.x + self.radarRadius*np.sin(self.radDir - np.pi/16),
                                         self.y + self.radarRadius*np.cos(self.radDir - np.pi/16)),
                                        (self.x + self.radarRadius*np.sin(self.radDir - 2*np.pi/16),
                                         self.y + self.radarRadius*np.cos(self.radDir - 2*np.pi/16))
                                          ]
        pygame.draw.polygon(self.surface, GREEN, points)
        pygame.draw.line(self.surface, GREEN, *self.radLine)
        for item in self.game.objects:
            if type(item) == Bullet and item.origin != self:
                if item.rect.clipline(*self.radLine):
                    item.tagTime += 5

                else:
                    dist = ((item.x - self.x) ** 2 + (item.y - self.y) ** 2) ** .5
                    if item.tagTime >= 0 and self.radarRadius >= dist:
                        rect = item.rect.copy()
                        rect.height = 4 * item.rect.height
                        rect.width = 4 * item.rect.width
                        rect.center = item.rect.center
                        pygame.draw.rect(self.surface, RED, rect, 2)
                    if item.tagTime > 0:
                        item.tagTime -= 1

            if type(item) == Tank:
                if item.bodyRect.clipline(*self.radLine):
                    item.tagTime += 5
                else:
                    dist = ((item.x - self.x) ** 2 + (item.y - self.y) ** 2)**(1/2)
                    if item.tagTime >= 0 and self.radarRadius >= dist:
                        rect = item.bodyRect.copy()
                        rect.height = 2 * item.bodyRect.height
                        rect.width = 2 * item.bodyRect.width
                        rect.center = item.bodyRect.center
                        pygame.draw.rect(self.surface, RED, rect, 2)
                    if item.tagTime > 0:
                        item.tagTime -= 1
        

    def rotateBodyCC(self):
        self.dir -= BODY_ROT_ANGLE
        self.dir = self.dir % 360
        self.turDir -= BODY_ROT_ANGLE
        self.rotating = True
        
    def rotateBodyC(self):
        self.dir += BODY_ROT_ANGLE 
        self.dir = self.dir % 360
        self.turDir += BODY_ROT_ANGLE
        self.rotating = True

    def drawAndHitBox(self):

        if self.lightOn:
            img_copy = pygame.transform.rotate(self.lightImage, self.dir)
            x = self.x - 600*np.sin((self.dir)/360*2*np.pi) - \
                img_copy.get_width() / 2 
            y = self.y - 600*np.cos((self.dir)/360*2*np.pi) - \
                img_copy.get_height() / 2 
                
            self.filt.fill(BLACK)
            self.filt.blit(img_copy, (x, y), special_flags=pygame.BLEND_RGBA_SUB)
            self.surface.blit(self.filt, (0, 0))
            pygame.draw.circle(self.surface, GREEN, (self.x, self.y), self.radarRadius, 1)
            
            self.radDir -= np.pi/25
            self.radDir = self.radDir % (2 * np.pi)
            self.radLine = ((self.x, self.y), (self.x + self.radarRadius*np.sin(self.radDir),
                                          self.y + self.radarRadius*np.cos(self.radDir)))

        if self == self.game.player:
            self.drawRadar()

        img_copy = pygame.transform.rotate(self.bodyImage, self.dir)
        self.surface.blit(img_copy, (self.x - img_copy.get_width() / 2,
                                    self.y - img_copy.get_height() / 2))
        self.bodyRect = img_copy.get_rect(center = (self.x, self.y))
        img_copy = pygame.transform.rotate(self.turretImage, self.turDir)
        self.surface.blit(img_copy, (self.x - img_copy.get_width() / 2,
                                    self.y - img_copy.get_height() / 2))
        self.turretRect = img_copy.get_rect(center = (self.x, self.y))

    def rotateTurret(self):
        if self.target:
            mx, my = self.target.x, self.target.y
        else:
            mx, my = pygame.mouse.get_pos()
        x = mx - self.x
        if x == 0:
            x += .001
        y = my - self.y
        angle = np.arctan(y / x) / (2 * np.pi) * 360 - 270
        if mx < self.x:
            mouseAngle = -1 * (angle + 180)
        else:
            mouseAngle = -1 * angle
        speed = (mouseAngle - self.turDir) / 5
        if np.fabs(speed) >= 30:
            speed = -1 * speed / 10
        self.turDir += speed
        self.turDir = self.turDir % 360
        self.game.fuel -= np.fabs(speed) * .005

    def calcEnemySpeed(self):
        return (1 + self.game.score * .02) * ENEMY_MOVEMENT_SPEED

    def forward(self):
        if self.lightOn:
            speed = MOVEMENT_SPEED
        else:
            speed = self.calcEnemySpeed()
        self.y -= speed * np.cos(self.dir * 2 * np.pi / (360))
        self.x -= speed * np.sin(self.dir * 2 * np.pi / (360))
        self.yVel = -1 *  speed * np.cos(self.dir * 2 * np.pi / (360))
        self.xVel = -1 * speed * np.sin(self.dir * 2 * np.pi / (360))

    def reverse(self):
        if self.lightOn:
            speed = MOVEMENT_SPEED
        else:
            speed = self.calcEnemySpeed()
        self.y += speed * np.cos(self.dir * 2 * np.pi / (360))
        self.x += speed * np.sin(self.dir * 2 * np.pi / (360))
        self.yVel = speed * np.cos(self.dir * 2 * np.pi / (360))
        self.xVel = speed * np.sin(self.dir * 2 * np.pi / (360))

    def stop(self):
        self.countTilNextMove = STOP_FRAME_COUNT
        self.yVel = 0
        self.xVel = 0


    def update(self):
        if self.lightOn:
            keys = pygame.key.get_pressed()
            
            self.rotateTurret()
            
            if keys[pygame.K_a]:
                self.rotateBodyC()
            if keys[pygame.K_d]:
                self.rotateBodyCC()
            if keys[pygame.K_w]:
                self.forward()
            if keys[pygame.K_s]:
                self.reverse()

            if self.yVel != 0 or self.xVel != 0 or self.rotating:
                self.game.fuel -= FUEL_PER_SECOND / FRAME_RATE

            self.xVel = 0
            self.yVel = 0
            self.rotating = False

        else:
            self.rotateTurret()

            if self.countTilNextMove == 0:

                if -10 < self.x < WIDTH + 10 and -10 < self.y < HEIGHT + 10:
                    self.forward()

                else: 
                    self.dir = (self.dir + 180) % 360
                    self.forward()

            else:
                self.countTilNextMove -= 1

        self.drawAndHitBox()
                                    
