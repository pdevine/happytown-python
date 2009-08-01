import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

import new_board

b = new_board.Board()

def getBoard():
    return b.asciiBoard()

def moveRow(row, direction):
    b.moveRow(row, direction)
    return True

def moveColumn(column, direction):
    b.moveColumn(column, direction)
    return True
    

server = SimpleXMLRPCServer(('localhost', 8000))
print "Listening on port 8000"

server.register_function(getBoard, "getBoard")
server.register_function(moveRow, "moveRow")
server.register_function(moveColumn, "moveColumn")
server.serve_forever()
