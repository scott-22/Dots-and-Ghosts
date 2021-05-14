# Classes for grid sprites
import pygame
from configs import *

# Cell of maze
class Cell(pygame.sprite.Sprite):
    def __init__(self, x, y, color):
        super().__init__()

        # Grid coordinates (starting from top left corner, like Pygame)
        self.gc = [x, y]

        self.color = color


# Wall of maze
class Wall(Cell):
    def __init__(self, x, y):
        super().__init__(x, y, GREY)
    
        self.image = pygame.Surface((GRIDWIDTH/COL + 2, GRIDHEIGHT/ROW + 2))
        self.image.fill(self.color)

        self.rect = self.image.get_rect()
        self.rect.center = ((self.gc[0] + 0.5) * GRIDWIDTH/COL, (self.gc[1] + 0.5) * GRIDHEIGHT/ROW)


# Empty cell of maze ("Way" as in "hallway")
class Way(Cell):
    def __init__(self, x, y, dot=True):
        super().__init__(x, y, WHITE)

        # True if player can get a point from this cell (i.e., dot inside is uneaten)
        # Spawn points for player and ghosts should not have dots
        self.dot = dot

        self.image = pygame.Surface((GRIDWIDTH/COL + 8, GRIDHEIGHT/ROW + 8))
        self.image.fill(self.color)

        self.rect = self.image.get_rect()
        self.rect.center = ((self.gc[0] + 0.5) * GRIDWIDTH/COL, (self.gc[1] + 0.5) * GRIDHEIGHT/ROW)

        if self.dot:
            pygame.draw.circle(self.image, TEAL, (self.rect.width/2, self.rect.height/2), 4)
