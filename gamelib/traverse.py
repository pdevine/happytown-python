import board
from board import NORTH, EAST, SOUTH, WEST

class TraversalGraph:
    def __init__(self, board):
        self.board = board.board
        self.totalRows = board.rows
        self.totalColumns = board.columns
        self.t_graph = {}
        self.createVertices()
        self.createEdges()

    def addVertex(self, v):
        self.t_graph[v] = []

    def addEdge(self, v1, v2):
        self.t_graph[v1].append(v2)

    def createVertices(self):
        for row in range(self.totalRows):
            for column in range(self.totalColumns):
                vertex = (column, row)
                self.addVertex(vertex)

    def createEdges(self):
        for row in range(self.totalRows):
            for column in range(self.totalColumns):
                if column < self.totalColumns-1 and \
                    self.board[row][column].hasDir(EAST) and \
                    self.board[row][column+1].hasDir(WEST):
                    vertex1 = (column, row)
                    vertex2 = (column+1, row)
                    self.addEdge(vertex1, vertex2)
                    self.addEdge(vertex2, vertex1)
                if row < self.totalRows-1 and \
                    self.board[row][column].hasDir(SOUTH) and \
                    self.board[row+1][column].hasDir(NORTH):
                    vertex1 = (column, row)
                    vertex2 = (column, row+1)
                    self.addEdge(vertex1, vertex2)
                    self.addEdge(vertex2, vertex1)

    def findPath(self, start, end):
        return self.findShortestPath(self.t_graph, start, end)

    def findShortestPath(self, graph, start, end, path=[]):
        path = path + [start]
        if start == end:
            return path
        if not graph.has_key(start):
            return None
        shortest = None
        for vertex in graph[start]:
            if vertex not in path:
                newpath = self.findShortestPath(graph, vertex, end, path)
                if newpath:
                    if not shortest or len(newpath) < len(shortest):
                        shortest = newpath
        return shortest


if __name__ == "__main__":
    import board
    b = board.Board()
    x = TraversalGraph(b)

