"""
Style: main and subroutines
Components: main program and subroutines
Connectors: procedure calls
Constraints: components can't communicate using shared memory (e.g. global 
variables) 
Gains: change the implementation of a subroutine without affecting the main 
program.  
"""

from random import randint

import pygame
from pygame.locals import KEYDOWN, QUIT, K_ESCAPE, K_w, K_a, K_s, K_d, K_SPACE

############################################################

def process_input(game_status, prev_direction):
    prev_game_status, direction = 1, prev_direction
    for event in pygame.event.get():
        if event.type == QUIT:
            game_status = 0 # 0 for game over, 1 for play
        if event.type == KEYDOWN:
            key = event.key
            if key == K_ESCAPE:
                game_status = 0
            elif key == K_SPACE:
                if game_status == -1:
                    game_status = 1
                else:
                    game_status = -1
            elif key == K_w: # was K_UP
                direction = (0, -1)
            elif key == K_s: # was K_DOWN
                direction = (0, 1)
            elif key == K_a: # was K_LEFT
                direction = (-1, 0)
            elif key == K_d: # was K_RIGHT
                direction = (1, 0)
    return game_status, direction

############################################################

def draw_everything(screen, mybox, pellets, borders):
    screen.fill((139, 19, 244))  # dark blue - now purple
    [pygame.draw.rect(screen, (255, 191, 5), b) for b in borders]  # # Deep Sky Blue - now orangeish 
    [pygame.draw.rect(screen, (5, 94, 3), p) for p in pellets]  # pink - now dark green
    pygame.draw.rect(screen, (222, 19, 55), mybox)  # Deep Sky Blue - now a redish color
    pygame.display.update()

############################################################

def create_box(dims):
    w, h = dims
    box = pygame.Rect(w / 2, h / 2, 10, 10)  # start in middle of the screen
    direction = 0, 1  # start direction: down
    return box, direction

############################################################

def collide(box, boxes):
    # return True if box collides with any entity in boxes
    return box.collidelist(boxes) != -1
    
############################################################

def move(box, direction): 
    return box.move(direction[0] * 2, direction[1] * 2) 

############################################################

def create_borders(dims, thickness=2):
    w, h = dims
    return [pygame.Rect(0, 0, thickness, h),
            pygame.Rect(0, 0, w, thickness),
            pygame.Rect(w - thickness, 0, thickness, h),
            pygame.Rect(0, h - thickness, w, thickness),
            pygame.Rect(100, 50, thickness, 100),
            pygame.Rect(200, 50, 100, thickness)]
    
############################################################

def create_pellet(dims, offset):
    w, h = dims
    return pygame.Rect(randint(offset, w - offset),
                       randint(offset, h - offset), 5, 5)

def create_pellets(dims, qty, offset=10): 
    # this is the only subroutine independent of Pygame
    return [create_pellet(dims, offset) for _ in range(qty)]
    
def eat_and_replace_colliding_pellet(box, pellets, dims, offset=10):
    p_index = box.collidelist(pellets)
    if p_index != -1:  # ate a pellet: grow, and replace a pellet
        pellets[p_index] = create_pellet(dims, offset)
        box.size = box.width * 1.2, box.height * 1.2
    return box, pellets
    
############################################################

pygame.init()
clock = pygame.time.Clock()

# display
dims = 400, 300
screen = pygame.display.set_mode(dims)

# game objects
borders = create_borders(dims)
pellets = create_pellets(dims, 4)
mybox, direction = create_box(dims)

# game loop
game_status = 1  # 0 for game over, 1 for play
while game_status == 1 or game_status == -1:

    game_status, direction = process_input(game_status, direction)
    
    while game_status == -1:
        game_status, direction = process_input(game_status, direction)
                        
    mybox = move(mybox, direction)
    if collide(mybox, borders):
        mybox, direction = create_box(dims)
    mybox, pellets = eat_and_replace_colliding_pellet(mybox, pellets, dims)
    
    draw_everything(screen, mybox, pellets, borders)
    
    clock.tick(50)  # or sleep(.02) to have the loop Pygame-independent