from network import Listener, Handler, poll

 
handlers = {}  # map client handler to user name
 
class MyHandler(Handler):
    
    def on_open(self):
        pass
     
    def on_close(self):
        gone = handlers.pop(self)
        names = ""
        for p in handlers.values():
            names = names + p + ","
        names = names[:-1]
 
        for h in handlers:
#             if msg['speak'] != handlers[h]:
            h.do_send({'quit': gone + ' has left the room. Users: ' + names})
     
    def on_msg(self, msg):
        if 'join' in msg:
            name = msg['join']
            handlers[self] = name
            for h in handlers:
                h.do_send({'join': name, 'list': handlers.values()})
        elif 'txt' in msg:
            if msg['txt'] != "":
                for h in handlers:
                    if msg['speak'] != handlers[h]:
                        h.do_send(msg)
        elif 'end' in msg:
            handlers.pop(self)
            names = ""
            for p in handlers:
                names = names + p + ","
            names = names[:-1]
            
            for h in handlers:
                if msg['speak'] != handlers[h]:
                    h.do_send(msg['speak'] + 'has left the room. Users: ' + names)            
 
port = 8888
server = Listener(port, MyHandler)
while 1:
    poll(timeout=0.05) # in seconds
    