import pygame
import random, sys

from configs import *
import Grid, Character, CellSet


def generate_grid():
    # Generate a random grid using a randomized Kruskal's
    game_grid = [[0 for j in range(COL)] for i in range(ROW)]

    # Disjoint Set to store grid cells
    cell_set = CellSet.CellSet()
    
    # Edge list
    edges = []
    for r in range(0, ROW, 2):
        edges.extend(((r, c), (r, c+2)) for c in range(COL-1) if c%2 == 0)
    for c in range(0, COL, 2):
        edges.extend(((r, c), (r+2, c)) for r in range(ROW-1) if r%2 == 0)
    random.shuffle(edges)
    while edges:
        x, y = edges.pop()
        # Give random chance to add edge so that the maze is more "loopy"
        if cell_set.dhashfind(x) != cell_set.dhashfind(y) or random.randint(1, 8) == 1:
            cell_set.dmerge(x, y)
            game_grid[x[0]][x[1]] = 1
            game_grid[y[0]][y[1]] = 1
            game_grid[(x[0]+y[0])//2][(x[1]+y[1])//2] = 1

    game_grid[ROW-1][0] = 1
    game_grid[0][COL-1] = 1
    return game_grid



def menu(screen):
    # Clear screen
    screen.fill(BLACK)

    # Set clock
    clock = pygame.time.Clock()

    # Using a ghost as background
    background_ghost_sprite_images = [pygame.image.load("resources/ghost/0" + str(j) + ".png") for j in range(ANIMATION_FRAMES)]
    for j in range(ANIMATION_FRAMES):
        background_ghost_sprite_images[j].convert_alpha()
        background_ghost_sprite_images[j] = pygame.transform.scale(background_ghost_sprite_images[j], (min(WIDTH, HEIGHT), min(WIDTH, HEIGHT)))
    background_ghost = Character.Ghost([[]], background_ghost_sprite_images)
    background_ghost.rect.center = (WIDTH/2, HEIGHT/2)

    # Add text slightly larger than usual
    courier_prime = pygame.font.Font("resources/text/courier.ttf", int(FONT_SIZE*1.5))

    default_grid_image = pygame.transform.scale(pygame.image.load("resources/grid/defaultgrid.png"), (min(WIDTH, HEIGHT)//3, min(WIDTH, HEIGHT)//3))
    default_grid_image_rect = default_grid_image.get_rect()
    default_grid_image_rect.bottomleft = (WIDTH/9, HEIGHT*8/9)

    default_grid_text = courier_prime.render("Default", True, WHITE, GREY)
    default_grid_text_rect = default_grid_text.get_rect()
    default_grid_text_rect.center = (default_grid_image_rect.centerx, default_grid_image_rect.top - FONT_SIZE*2)

    random_grid_image = pygame.transform.scale(pygame.image.load("resources/grid/randomgrid.png"), (min(WIDTH, HEIGHT)//3, min(WIDTH, HEIGHT)//3))
    random_grid_image_rect = random_grid_image.get_rect()
    random_grid_image_rect.bottomright = (WIDTH*8/9, HEIGHT*8/9)

    random_grid_text = courier_prime.render("Random", True, WHITE, GREY)
    random_grid_text_rect = random_grid_text.get_rect()
    random_grid_text_rect.center = (random_grid_image_rect.centerx, random_grid_image_rect.top - FONT_SIZE*2)

    ghost_frame_num = 0

    screen.blit(background_ghost.image, background_ghost.rect)
    screen.blit(default_grid_image, default_grid_image_rect)
    screen.blit(default_grid_text, default_grid_text_rect)
    screen.blit(random_grid_image, random_grid_image_rect)
    screen.blit(random_grid_text, random_grid_text_rect)

    while True:
        ghost_frame_num = (ghost_frame_num+1) % GHOST_FRAMES_PER_CYCLE

        # Process animation
        if ghost_frame_num % FRAMES_PER_ANIMATION_CYCLE == 0:
            background_ghost.image_num += background_ghost.image_delta
            if not (0 <= background_ghost.image_num < ANIMATION_FRAMES):
                background_ghost.image_delta *= -1
                background_ghost.image_num += background_ghost.image_delta
            background_ghost.image = background_ghost.images[background_ghost.image_num]

            screen.fill(BLACK)
            screen.blit(background_ghost.image, background_ghost.rect)
            screen.blit(default_grid_image, default_grid_image_rect)
            screen.blit(default_grid_text, default_grid_text_rect)
            screen.blit(random_grid_image, random_grid_image_rect)
            screen.blit(random_grid_text, random_grid_text_rect)

            pygame.display.update()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                if default_grid_image_rect.collidepoint(event.pos) or default_grid_text_rect.collidepoint(event.pos):
                    return DEFAULT_GAME_GRID
                if random_grid_image_rect.collidepoint(event.pos) or random_grid_text_rect.collidepoint(event.pos):
                    return generate_grid()
        
        clock.tick(100)



def play(screen, game_grid):
    # Game variables
    obj_grid = game_grid # Grid containing each Way object
    num_dots = 0
    clock = pygame.time.Clock()

    # Game resources
    courier_prime = pygame.font.Font("resources/text/courier.ttf", FONT_SIZE)

    player_sprite_images = [pygame.image.load("resources/player/player.png")]
    player_sprite_images[0].convert_alpha()
    player_sprite_images[0] = pygame.transform.scale(player_sprite_images[0], (GRIDWIDTH//COL, GRIDHEIGHT//ROW))

    ghost_sprite_images = [[pygame.image.load("resources/ghost/" + str(i) + str(j) + ".png") for j in range(ANIMATION_FRAMES)] for i in range(GHOSTS)]
    for i in range(GHOSTS):
        for j in range(ANIMATION_FRAMES):
            ghost_sprite_images[i][j].convert_alpha()
            ghost_sprite_images[i][j] = pygame.transform.scale(ghost_sprite_images[i][j], (GRIDWIDTH//COL+4, GRIDHEIGHT//ROW+4))
    
    # Ghost target functions
    ghost_sprite_target_functions = [
        None, # Target straight on player
        lambda player: (player.gc[0] + 8*player.movement[0] + random.randint(-5, 5), player.gc[1] + 8*player.movement[1] + random.randint(-5, 5)), # Target somewhere in front of player
        lambda player: (player.gc[0] - 4*player.movement[0] + random.randint(-5, 5), player.gc[1] - 4*player.movement[1] + random.randint(-5, 5)), # Target somewhere behind player
        lambda player: (player.gc[0] + random.randint(-15, 15), player.gc[1] + random.randint(-15, 15)), # Target randomly near player
        lambda player: (player.gc[0] + random.randint(-15, 15), player.gc[1] + random.randint(-15, 15)) # Target randomly near player
    ]

    # Sprite groups
    walls = pygame.sprite.Group()
    ways = pygame.sprite.Group()
    ghosts = pygame.sprite.Group()
    player = Character.Player(game_grid, player_sprite_images)

    for i in range(GHOSTS):
        ghosts.add(Character.Ghost(game_grid, ghost_sprite_images[i], target=ghost_sprite_target_functions[i]))

    # For consistency, the coordinate system also starts from top left corner
    for r in range(ROW):
        for c in range(COL):
            if game_grid[r][c]:
                if (r, c) in [(0, ROW-1), (COL-1, 0)]:
                    cell = Grid.Way(c, r, dot=False)
                else:
                    cell = Grid.Way(c, r)
                    num_dots += 1
                obj_grid[r][c] = cell
                ways.add(cell)
            else:
                walls.add(Grid.Wall(c, r))
    
    # For score keeping purposes
    total_dots = num_dots

    # How movement is represented in this game is explained in the Character class
    # Frame number
    player_frame_num = 0
    ghost_frame_num = 0

    # Store player's next direction
    next_dir = (0, 0)

    screen.fill(BLACK)
    
    walls.draw(screen)
    ways.draw(screen)

    screen.blit(player.image, player.rect)
    ghosts.draw(screen)
    
    pygame.display.update()

    # Previous character locations to keep track of areas for updating screen
    prev_player_locations = [obj_grid[0][ROW-1].rect, obj_grid[COL-1][0].rect]
    prev_ghost_locations = [obj_grid[0][ROW-1].rect, obj_grid[COL-1][0].rect]

    # Align ghosts
    for ghost in ghosts:
        ghost.turn(ghost.plan(player))
        ghost.move()

    while player.lives:
        player_frame_num = (player_frame_num+1) % PLAYER_FRAMES_PER_CYCLE
        ghost_frame_num = (ghost_frame_num+1) % GHOST_FRAMES_PER_CYCLE
        dirty = [] # Parts of screen that need updating

        # Load only necessary areas
        dirty.extend(prev_player_locations)
        dirty.extend(prev_ghost_locations)
        dirty.append(obj_grid[player.gc[1]][player.gc[0]].rect)
        for ghost in ghosts:
            dirty.append(obj_grid[ghost.gc[1]][ghost.gc[0]].rect)
        
        # Process animation
        if ghost_frame_num % FRAMES_PER_ANIMATION_CYCLE == 0:
            for ghost in ghosts:
                ghost.image_num += ghost.image_delta
                if not (0 <= ghost.image_num < ANIMATION_FRAMES):
                    ghost.image_delta *= -1
                    ghost.image_num += ghost.image_delta
                ghost.image = ghost.images[ghost.image_num]
        
        # Process player events
        if player_frame_num == 0:
            # Eat dot event
            if obj_grid[player.gc[1]][player.gc[0]].dot:
                player.points += 1
                num_dots -= 1
                obj_grid[player.gc[1]][player.gc[0]].dot = False
                obj_grid[player.gc[1]][player.gc[0]].image.fill(obj_grid[player.gc[1]][player.gc[0]].color)
        
            # Kill event
            kill = False
            for ghost in ghosts:
                if ghost.gc == player.gc:
                    kill = True
                    break
            if kill:
                player.lives -= 1
                player.gc = [0, ROW-1]
                player.movement = (0, 0)
                for ghost in ghosts:
                    ghost.gc = [COL-1, 0]
                pygame.time.wait(1000)
        
            # Win event
            if num_dots == 0:
                return (True, player.points, total_dots)

            # Align player in current cell
            player.align()

            # Current cells become previous cells
            prev_player_locations.clear()
            prev_player_locations.append(obj_grid[player.gc[1]][player.gc[0]].rect)
            
            # Move player to new direction if possible
            player.turn(next_dir)
            player.move()
            
        # Process ghost events
        if ghost_frame_num == 0:
            # Kill event
            kill = False
            for ghost in ghosts:
                if ghost.gc == player.gc:
                    kill = True
                    break
            if kill:
                player.lives -= 1
                player.gc = [0, ROW-1]
                player.movement = (0, 0)
                for ghost in ghosts:
                    ghost.gc = [COL-1, 0]
                pygame.time.wait(1000)

            # Align ghosts in current cell
            for ghost in ghosts:
                ghost.align()

            # Current cells become previous cells
            prev_ghost_locations.clear()
            for ghost in ghosts:
                prev_ghost_locations.append(obj_grid[ghost.gc[1]][ghost.gc[0]].rect)

            # Move ghosts
            for ghost in ghosts:
                ghost.turn(ghost.plan(player))
                ghost.move()
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_UP:
                    if player.movement != (0, -1):
                        next_dir = (0, -1)
                elif event.key == pygame.K_DOWN:
                    if player.movement != (0, 1):
                        next_dir = (0, 1)
                elif event.key == pygame.K_LEFT:
                    if player.movement != (-1, 0):
                        next_dir = (-1, 0)
                elif event.key == pygame.K_RIGHT:
                    if player.movement != (1, 0):
                        next_dir = (1, 0)

        player.update()
        ghosts.update()

        ways.draw(screen)
        screen.blit(player.image, player.rect)
        ghosts.draw(screen)

        points_text = courier_prime.render("Points: " + str(player.points), True, WHITE, BLACK)
        points_text_rect = points_text.get_rect()
        points_text_rect.center = (GRIDWIDTH+(WIDTH-GRIDWIDTH)/2, HEIGHT/3)
        dirty.append(screen.blit(points_text, points_text_rect))

        lives_text = courier_prime.render("Lives: " + str(player.lives), True, WHITE, BLACK)
        lives_text_rect = lives_text.get_rect()
        lives_text_rect.center = (GRIDWIDTH+(WIDTH-GRIDWIDTH)/2, HEIGHT*2/3)
        dirty.append(screen.blit(lives_text, lives_text_rect))

        pygame.display.update(dirty)

        clock.tick(100)
    
    return (False, player.points, total_dots)



def end(screen, res): # res should be tuple with Win (bool), Points (int), Total points (int)
    # Clear screen
    screen.fill(BLACK)

    # Different text sizes
    courier_prime_large = pygame.font.Font("resources/text/courier.ttf", FONT_SIZE*2)
    courier_prime_small = pygame.font.Font("resources/text/courier.ttf", FONT_SIZE)

    message_text = courier_prime_large.render("You won!" if res[0] else "You lost!", True, WHITE, GREY)
    message_text_rect = message_text.get_rect()
    message_text_rect.center = (WIDTH/2, HEIGHT/3)

    instruction_text = courier_prime_small.render("Click anywhere to continue.", True, WHITE, GREY)
    instruction_text_rect = instruction_text.get_rect()
    instruction_text_rect.center = (WIDTH/2, HEIGHT*2/3)

    points_text = courier_prime_small.render("You got " + str(res[1]) + "/" + str(res[2]) + " points.", True, WHITE, GREY)
    points_text_rect = points_text.get_rect()
    points_text_rect.centerx = WIDTH/2
    points_text_rect.top = instruction_text_rect.bottom + 5

    screen.blit(message_text, message_text_rect)
    screen.blit(instruction_text, instruction_text_rect)
    screen.blit(points_text, points_text_rect)
    pygame.display.update()

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                sys.exit()
            elif event.type == pygame.MOUSEBUTTONUP:
                return
        
    

def main():

    # Initialize Pygame stuff
    pygame.init()
    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    while True:
        end(screen, play(screen, menu(screen)))

main()
