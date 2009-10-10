#
# ai.py
# (c) 2009 pdevine@sonic.net
# Bombitron - www.bombitron.com
#
#

import sys

import socket
import server

MSGLEN = 4096

def debug(exceptType, value, tb):
    import traceback, pdb
    traceback.print_exception(exceptType, value, tb)
    print

    pdb.pm()

class AISocketHandler(object):
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def connect(self, host, port):
        self.sock.connect((host, port))

    def send(self, msg):
        totalSent = 0
        while totalSent < len(msg):
            sent = self.sock.send(msg[totalSent:])
            if sent == 0:
                raise RuntimeError, "socket connection broken"

            totalSent += sent

    def receive(self):
        msg = ''
        msgLen = ''
 
        while len(msgLen) < 4:
            msgLenChunk = self.sock.recv(4)
            if msgLenChunk == '':
                raise RuntimeError, "socket connection broken"

            msgLen += msgLenChunk

        while len(msg) < int(msgLen):
            chunk = self.sock.recv(int(msgLen))
            msg += chunk
            
        return msg

class AIBaseClass(AISocketHandler):
    def __init__(self, host='localhost', port=server.port, nick='foobar'):
        AISocketHandler.__init__(self)

        self.connect(host, port)
        self.setNick(nick)

    def waitForMessage(self, waitMsg):
        while True:
            msg = self.receive()
            if msg == waitMsg:
                return

    def setNick(self, nick):
        self.send('/nick %s' % nick)

        self.waitForMessage(server.TEXT_SET_NICK % nick)
        print "Nick set to %s" % nick

    def joinGame(self, gameKey):
        self.send('/join %s' % gameKey)

        self.waitForMessage(server.TEXT_JOIN_GAME % gameKey)
        print "Joined game %s" % gameKey

sys.excepthook = debug

ai = AIBaseClass()
ai.joinGame('a707882654e2505250d58ae7630469ae')
ai.sock.close()

