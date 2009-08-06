import board
import xmlrpclib

proxy = xmlrpclib.ServerProxy("http://localhost:8000")

gameKey = proxy.newGame()
print gameKey
print proxy.getBoard(gameKey)
#proxy.moveRow(1, board.EAST)
#print proxy.getBoard()
#proxy.moveColumn(2, board.SOUTH)
#print proxy.getBoard()

print proxy.listGames()
#print proxy.findPath(gameKey,0,0,0,2)
