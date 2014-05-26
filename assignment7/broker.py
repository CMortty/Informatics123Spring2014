from network import Listener, Handler, poll

handlers = {}  # map client handler to user name
names = {} # map name to handler
subs = {} # map tag to handlers

def broadcast(msg):
    for h in handlers.keys():
        h.do_send(msg)


class MyHandler(Handler):
    
    def on_open(self):
        handlers[self] = None
        
    def on_close(self):
        name = handlers[self]
        del handlers[self]
        broadcast({'leave': name, 'users': handlers.values()})
        
    def on_msg(self, msg):
        if 'join' in msg:
            name = msg['join']
            handlers[self] = name
            broadcast({'join': name, 'users': handlers.values()})
        elif 'speak' in msg:
            name, txt = msg['speak'], msg['txt']
            text = txt.split()
            if '+' in txt or '#' in txt or '-' in txt or '@' in txt:
                sent = []
                for s in text:
                    if '+' in s:
                        print s[1:]
                        if subs.has_key(self):
                            subs[self].append(s[1:])
                        else:
                            subs[self] = [s[1:]]
                    if '#' in s:
                        print s[1:]
                        for k,l in subs.items():
                            for v in l:
                                if v in s[1:]:
                                    if k not in sent:
                                        k.do_send({'speak': name, 'txt': txt})
                                        sent.append(k)
                    if '-' in s:
                        print s[1:]
                        if subs.has_key(self):
                            l = subs[self]
                            for v in l:
                                if v == s[1:]:
                                    subs[self].remove(v)
                                    print 'removed ' + v
                    if '@' in s:
                        print s[1:]
                        for k,l in handlers.items():
                            for v in l:
                                if v in s[1:]:
                                    if k not in sent:
                                        k.do_send({'speak': name, 'txt': txt})
                                        sent.append(k)
#             if '#' in txt:
#                 for h in text:
#                     if '#' in h:
#                         print h[1:]
#                         for k,v in subs.items():
#                             if v in h[1:]:
#                                 k.do_send({'speak': name, 'txt': txt})
            else:
                broadcast({'speak': name, 'txt': txt})


Listener(8888, MyHandler)
while 1:
    poll(0.05)