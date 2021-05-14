# Class for characters in the game (anything that moves)
# Contains methods for moving in maze (each character will always be at a grid position)

# How moving in this game is implemented is similar to the original Pacman game
# To ensure Characters are always displayed in the center of a cell, the end position of each movement will be a cell
# This means each Character is always completely in one grid cell or another, never in between
# Moving the Character will display an animation but the Character will be treated as being in a new grid position instantaneously
# Each iteration of the event loop is referred to as a "frame"
# Each time all Characters are done their animation is referred to as another "cycle"
# While each animation occurs, events will not be processed until the next cycle
# When the direction is changed mid-cycle, the change will be stored (to enhance UX) but not processed until next cycle
import pygame
import random
from configs import *

# Not an abstract class since Python has ugly abstract class implementation
class Character(pygame.sprite.Sprite):
    def __init__(self, x, y, game_grid, images, frames_per_cycle): # game_grid should be valid game grid, image should be Surface object
        super().__init__()

        # Grid coordinates
        self.gc = [x, y]

        # Vector representing character movement direction in terms of grid coordinates
        self.movement = (0, 0)

        # Store a reference to the game grid (necessary for move() to work)
        # It's more OOP-like to have the moving implemented in itself rather than from the main loop
        # Overhead should be minimal since object references don't take up much memory
        self.game_grid = game_grid

        # Pass images up the constructor
        self.images = images
        self.image = self.images[0]
        self.rect = self.image.get_rect()

        # Frames per cycle for particular character
        self.fpc = frames_per_cycle
    
    def change_image(self, idx):
        self.image = self.images[idx]
    
    # Whether a move in a direction is valid
    def valid_move(self, direction): # Direction should be a vector
        new_gc = (self.gc[0]+direction[0], self.gc[1]+direction[1])
        return 0 <= new_gc[0] < COL and 0 <= new_gc[1] < ROW and self.game_grid[new_gc[1]][new_gc[0]]
    
    # Change direction
    def turn(self, direction):
        if self.valid_move(direction):
            self.movement = direction

    # Move in the specified direction
    def move(self):
        if self.valid_move(self.movement):
            self.gc[0] += self.movement[0]
            self.gc[1] += self.movement[1]
        else:
            self.movement = (0, 0)

    # Align in the center of grid
    def align(self):
        self.rect.center = ((self.gc[0] + 0.5) * GRIDWIDTH/COL, (self.gc[1] + 0.5) * GRIDHEIGHT/ROW)
    
    # Update position for each frame
    def update(self):
        self.rect.center = (self.rect.center[0] + self.movement[0] * GRIDWIDTH/COL / self.fpc, self.rect.center[1] + self.movement[1] * GRIDHEIGHT/ROW / self.fpc)


# Class for player sprite
class Player(Character):
    def __init__(self, game_grid, images):
        super().__init__(0, ROW-1, game_grid, images, PLAYER_FRAMES_PER_CYCLE)

        # Number of dots eaten
        self.points = 0

        # Number of lives
        self.lives = 3

        self.align()
    

# Class for ghost sprite
class Ghost(Character):
    def __init__(self, game_grid, images, target=None):
        super().__init__(COL-1, 0, game_grid, images, GHOST_FRAMES_PER_CYCLE)
        
        self.image_num = 0 # Current image
        self.image_delta = 1 # Direction of animation loading

        # Function stored as member (since functions are first class) that picks a target point to move towards
        # Default target will always be where the player is
        # target can be overridden to provide individuality
        if not target:
            target = lambda player: player.gc
        self.target = target

        self.align()

    # Ghost AI (also depends on Character.target())
    def plan(self, player):
        # Count degrees of freedom and find valid moves
        dof = 0
        valid_moves = []
        for move in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
            if self.valid_move(move):
                dof += 1
                valid_moves.append(move)
        
        # Ghost cannot backtrack unless stuck with 1 degree of freedom
        backtrack = (-self.movement[0], -self.movement[1])
        
        if dof == 0: # This situation should NOT be happening
            return (0, 0)
        elif dof == 1: # Backing out of corner
            return valid_moves[0]
        elif dof >= 3:
            target = self.target(player)
            # Find shortest euclidean distance
            valid_moves.sort(key=lambda mv: (self.gc[0]+mv[0]-target[0])**2 + (self.gc[1]+mv[1]-target[1])**2)
        
        for move in valid_moves:
            if move != backtrack:
                return move
