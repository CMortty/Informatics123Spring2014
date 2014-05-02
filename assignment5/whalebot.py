from random import randint
from time import sleep
import math

################### MODEL #############################

from common import Model

################### CONTROLLER #############################

import pygame
from pygame.locals import KEYDOWN, QUIT, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT

class Controller():
    def __init__(self, m):
        self.m = m
        pygame.init()
    
    def poll(self):
        cmd = None
#         i = randint(0,3)
        closePellet = None;
        closeDistance = 99999999;
        myLocation = self.m.mybox;
        for pellet in self.m.pellets:
            distance = math.sqrt((math.pow((pellet[0] - myLocation[0]), 2) + math.pow((pellet[1] - myLocation[1]),2)))
            if distance < closeDistance:
                closeDistance = distance
                closePellet = pellet
        
        
        for event in pygame.event.get():  # inputs
            if event.type == QUIT:
                cmd = 'quit'
            if event.type == KEYDOWN:
                key = event.key
                if key == K_ESCAPE:
                    cmd = 'quit'
        if cmd != 'quit':
            if closePellet[0] < myLocation[0]:
                cmd = 'left'
            elif closePellet[0] > myLocation[0]:
                cmd = 'right'
            if closePellet[1] < myLocation[1]:
                cmd = 'up'
            elif closePellet[1] > myLocation[1]:
                cmd = 'down'
                
#             if i == 0:
#                 cmd = 'up'
#             elif i == 1:
#                 cmd = 'down'
#             elif i == 2:
#                 cmd =  'left'
#             else:
#                 cmd = 'right' 
        if cmd:
            self.m.do_cmd(cmd)

################### VIEW #############################

class View():
    def __init__(self, m):
        self.m = m
        self.frame_counter = 0
        pygame.init()
        self.screen = pygame.display.set_mode((400, 300))
        
    def display(self):
        self.frame_counter += 1
        if self.frame_counter >= 50:
            print("Position: " + str(self.m.mybox[0]) + " " + str(self.m.mybox[1]))
            self.frame_counter = 0
        screen = self.screen
#         borders = [pygame.Rect(b[0], b[1], b[2], b[3]) for b in self.m.borders]
#         pellets = [pygame.Rect(p[0], p[1], p[2], p[3]) for p in self.m.pellets]
#         b = self.m.mybox
#         myrect = pygame.Rect(b[0], b[1], b[2], b[3])
#         screen.fill((0, 0, 64))  # dark blue
#         pygame.draw.rect(screen, (0, 191, 255), myrect)  # Deep Sky Blue
#         [pygame.draw.rect(screen, (255, 192, 203), p) for p in pellets]  # pink
#         [pygame.draw.rect(screen, (0, 191, 255), b) for b in borders]  # red
#         pygame.display.update()
    
################### LOOP #############################

model = Model()
c = Controller(model)
v = View(model)

while not model.game_over:
    sleep(0.02)
    c.poll() 
    model.update()
    v.display()