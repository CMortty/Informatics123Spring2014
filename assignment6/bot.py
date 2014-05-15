"""
The Client is slave: 
- it sends only the player inputs to the server.
- every frame, it displays the server's last received data
Pros: the server is the only component with game logic, 
so all clients see the same game at the same time (consistency, no rollbacks).
Cons: lag between player input and screen display (one round-trip).
But the client can smooth the lag by interpolating the position of the boxes. 
"""
import asynchat
import asyncore
import socket
import json
from time import sleep

from pygame import Rect, init as init_pygame
from pygame.display import set_mode, update as update_pygame_display
from pygame.draw import rect as draw_rect
from pygame.event import get as get_pygame_events
from pygame.locals import KEYDOWN, QUIT, K_ESCAPE, K_UP, K_DOWN, K_LEFT, K_RIGHT
from pygame.time import Clock

##################### NETWORK ##############################

class Handler(asynchat.async_chat):
    
    def __init__(self, host, port, sock=None):
        if sock:  # passive side: Handler automatically created by a Listener
            asynchat.async_chat.__init__(self, sock)
        else:  # active side: Handler created manually
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # TCP
            asynchat.async_chat.__init__(self, sock)
            self.connect((host, port))  # asynchronous and non-blocking
        self.set_terminator('\0')
        self._buffer = []
        
    def collect_incoming_data(self, data):
        self._buffer.append(data)

    def found_terminator(self):
        msg = json.loads(''.join(self._buffer))
        self._buffer = []
        self.on_msg(msg)
    
    def handle_close(self):
        self.close()
        self.on_close()

    def handle_connect(self):  # called on the active side
        self.on_open()
        
    # API you can use
    def do_send(self, msg):
        self.push(json.dumps(msg) + '\0')
        
    def do_close(self):
        self.handle_close()  # will call self.on_close
    
    # callbacks you should override
    def on_open(self):
        pass
        
    def on_close(self):
        pass
        
    def on_msg(self, data):
        pass
    
def poll(timeout=0):
    asyncore.loop(timeout=timeout, count=1) # return right away

###################### MODEL ###############################
        

def make_rect(quad):  # make a pygame.Rect from a list of 4 integers
    x, y, w, h = quad
    return Rect(x, y, w, h)

class Client(Handler):
    
    def on_open(self):
        print "Connected to Server"
        
    def on_close(self):
        print "Disconnected from Server"
    
    def __init__(self, *args):
        Handler.__init__(self, *args)
        self.borders = []
        self.pellets = []
        self.players = {}  # map player name to rectangle
        self.myname = None
        self.current_pellets = ""
                    
    def on_msg(self, data):
#         global borders, pellets, players, myname
        self.borders = [make_rect(b) for b in data['borders']]
        self.pellets = [make_rect(p) for p in data['pellets']]
        self.players = {name: make_rect(p) for name, p in data['players'].items()}
        self.myname = data['myname']

valid_inputs = {K_UP: 'up', K_DOWN: 'down', K_LEFT: 'left', K_RIGHT: 'right'}

###################### VIEW ################################

class ConsoleView():
    def __init__(self, m):
        init_pygame()
        self.model = m
        
    def display(self):
        if self.model.current_pellets == "":
            self.model.current_pellets = self.model.pellets
        elif self.model.current_pellets != self.model.pellets:
            print "Ate Pellet"
            self.model.current_pellets = self.model.pellets

class PygameView():
    def __init__(self, model):
        init_pygame()
        self.screen = set_mode((400, 300))
        self.clock = Clock()
        self.model = model
         
    def display(self):
        self.screen.fill((0, 0, 64))  # dark blue
        [draw_rect(self.screen, (0, 191, 255), b) for b in model.borders]  # deep sky blue 
        [draw_rect(self.screen, (255, 192, 203), p) for p in model.pellets]  # shrimp
        for name, p in model.players.items():
            if name != model.myname:
                draw_rect(self.screen, (255, 0, 0), p)  # red
        if model.myname:
            draw_rect(self.screen, (0, 191, 255), model.players[model.myname])  # deep sky blue
           
        update_pygame_display()
           
        self.clock.tick(50)  # frames per second, independent of server frame rate
        


################### CONTROLLER #############################

class Controller():
    def __init__(self, model):
        self.model = model
        
    def poll(self):
        p = self.model.pellets[0] # always target the first pellet
        b = self.model.players[self.model.myname]
        for event in get_pygame_events():  
            if event.type == QUIT:
                self.model.do_close()
                exit()
            if event.type == KEYDOWN:
                key = event.key
                if key == K_ESCAPE:
                    self.model.do_close()
                    exit()
        
        if p[0] > b[0]:
            cmd = 'right'
        elif p[0] + p[2] <= b[0]: # p[2] to avoid stuttering left-right movement
            cmd = 'left'
        elif p[1] > b[1]:
            cmd = 'down'
        else:
            cmd = 'up'
        msg = {'input': cmd}
        self.model.do_send(msg)
###################### LOOP ################################ 

model = Client('localhost', 8888)  # connect asynchronously
c = Controller(model)
v = ConsoleView(model)
while 1:
    poll()  # push and pull network messages
    c.poll()
    v.display()
