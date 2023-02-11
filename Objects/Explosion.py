from Utilities.Constants import *
from Utilities import *

class Explosion(pygame.sprite.Sprite):

    def __init__(self, surface, x, y):
        self.surface = surface
        self.x = x
        self.y = y
        self.OOB = False
        self.img1 = pygame.image.load("assets/exp1.png").convert_alpha()
        self.img2 = pygame.image.load("assets/exp2.png").convert_alpha()
        self.img3 = pygame.image.load("assets/exp3.png").convert_alpha()
        self.img4 = pygame.image.load("assets/exp4.png").convert_alpha()
        self.img5 = pygame.image.load("assets/exp5.png").convert_alpha()
        sizeX = self.img1.get_size()[0]
        sizeY = self.img2.get_size()[1]
        self.scaleImageSize = [WIDTH * .035, HEIGHT * .053]
        self.img1 = pygame.transform.scale(self.img1, self.scaleImageSize)
        self.img2 = pygame.transform.scale(self.img2, self.scaleImageSize)
        self.img3 = pygame.transform.scale(self.img3, self.scaleImageSize)
        self.img4 = pygame.transform.scale(self.img4, self.scaleImageSize)
        self.img5 = pygame.transform.scale(self.img5, self.scaleImageSize)
        self.images = [self.img1, self.img2, self.img3, self.img4, self.img5, 0]
        self.imagesGen = (i for i in self.images)
        self.origin = None

    def update(self):
        self.draw()

    def draw(self):
        image = next(self.imagesGen)
        if image == 0:
            self.OOB = True
        else:
            self.surface.blit(image, (self.x - image.get_width() / 2,
                                        self.y - image.get_height() / 2))