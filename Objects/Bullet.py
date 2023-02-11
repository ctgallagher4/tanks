import numpy as np
import pygame
from Utilities.Constants import *
from Utilities import *

class Bullet(pygame.sprite.Sprite):

    '''A class to work with missiles'''
    RADIUS = 1

    def __init__(self, x, y, xVel, yVel, tip, surface, origin, target=None):
        '''A class to initialize the missile object'''
        pygame.sprite.Sprite.__init__(self)
        self.xVel = xVel + origin.xVel
        self.yVel = yVel + origin.yVel
        self.tip = tip
        self.surface = surface
        self.origin = origin
        self.target = target
        self.OOB = False
        self.image = pygame.Surface([10, 10], pygame.SRCALPHA)
        if self.origin.lightOn == True:
            self.image.fill(BLUE)
        else:
            self.image.fill(RED)
        self.rect = self.image.get_rect()
        self.x = x - 75 * np.sin(self.tip)
        self.y = y - 75 * np.cos(self.tip)
        self.tagTime = 0
        
    def draw(self):
        '''A class to draw a missile'''
        img_copy = pygame.transform.rotate(self.image, self.tip * 360 / (2 * np.pi))
        self.surface.blit(img_copy, self.rect.center)

    def update(self):
        '''A method to update a missile on the screen'''
        self.rect.center = (self.x, self.y)
        if self.target:
            selfVec = np.array([self.x, self.y])
            rocketVec = np.array([self.target.x, self.target.y])
            dist = rocketVec - selfVec
            nDist = dist / np.linalg.norm(dist) * BULLET_SPEED
            self.x += nDist[0]
            self.y += nDist[1]
        else:
            self.x += self.xVel
            self.y += self.yVel

        if 0 < self.x < WIDTH and 0 < self.y < HEIGHT:
            pass
        else:
            self.OOB = True

        self.draw()

