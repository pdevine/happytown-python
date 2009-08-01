import xmlrpclib
from SimpleXMLRPCServer import SimpleXMLRPCServer

import board
import traverse

b = board.Board()

def getBoard():
    return b.asciiBoard()

def moveRow(row, direction):
    b.moveRow(row, direction)
    return True

def moveColumn(column, direction):
    b.moveColumn(column, direction)
    return True
    
def findPath(start_column, start_row, end_column, end_row):
    tGraph = traverse.TraversalGraph(b)
    return str(tGraph.findPath(
        (start_column, start_row), (end_column, end_row)))

server = SimpleXMLRPCServer(('localhost', 8000))
print "Listening on port 8000"

server.register_function(getBoard, "getBoard")
server.register_function(moveRow, "moveRow")
server.register_function(moveColumn, "moveColumn")
server.register_function(findPath, "findPath")
server.serve_forever()
