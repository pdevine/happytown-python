from gamelib import new_board
import xmlrpclib

proxy = xmlrpclib.ServerProxy("http://localhost:8000")

print proxy.getBoard()
proxy.moveRow(1, new_board.EAST)
print proxy.getBoard()
proxy.moveColumn(2, new_board.SOUTH)
print proxy.getBoard()
