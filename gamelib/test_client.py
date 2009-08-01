import board
import xmlrpclib

proxy = xmlrpclib.ServerProxy("http://localhost:8000")

print proxy.getBoard()
#proxy.moveRow(1, board.EAST)
#print proxy.getBoard()
#proxy.moveColumn(2, board.SOUTH)
#print proxy.getBoard()

print proxy.findPath(0,0,0,2)
