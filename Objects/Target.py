import pygame
import numpy as np
from Utilities.Constants import *
from Utilities.__init__ import *

class Target(pygame.sprite.Sprite):

    def __init__(self, surface):
        pygame.sprite.Sprite.__init__(self)
        self.radius = 100
        self.setLoc()
        self.surface = surface
        self.origin = None
    
    def setLoc(self):
        self.x = np.random.randint(0 + self.radius, WIDTH - self.radius)
        self.y = np.random.randint(0 + self.radius, HEIGHT - self.radius)
        self.rect = pygame.Rect([self.x - self.radius, self.y - self.radius,
                                 2 * self.radius, 2 * self.radius])
        
    def draw(self):
        pygame.draw.circle(self.surface, RED, (self.x, self.y), self.radius, 0)
        pygame.draw.circle(self.surface, WHITE, (self.x, self.y), self.radius/2, 0)
        pygame.draw.circle(self.surface, RED, (self.x, self.y), self.radius/4, 0)

    def update(self):
        self.draw()