from network import Handler, poll
import sys
from threading import Thread
from time import sleep


myname = raw_input('What is your name? ')

class Client(Handler):
    
    def on_close(self):
        print '**** Disconnected from server ****'
    
    def on_msg(self, msg):
        if 'join' in msg:
            names = ""
            for p in msg['list']:
                names = names + p + ","
            names = names[:-1]
            print msg['join'] + " joined. Users: " + names         
        elif 'speak' in msg:
            print msg['speak'] + ": " + msg['txt']
        elif 'quit' in msg:
            print msg['quit']

        
host, port = 'localhost', 8888
client = Client(host, port)
client.do_send({'join': myname})

def periodic_poll():
    while 1:
        poll()
        sleep(0.05)  # seconds
                            
thread = Thread(target=periodic_poll)
thread.daemon = True  # die when the main thread dies 
thread.start()

while 1:
    mytxt = sys.stdin.readline().rstrip()
    if mytxt == 'quit':
        client.do_close()
        break
    client.do_send({'speak': myname, 'txt': mytxt})
