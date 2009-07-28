import board
from options import *

class TraversalGraph:
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
                    self.board[row][column].has_dir(EAST) and \
                    self.board[row][column+1].has_dir(WEST):
                    vertex1 = (column, row)
                    vertex2 = (column+1, row)
                    self.addEdge(vertex1, vertex2)
                    self.addEdge(vertex2, vertex1)
                if row < self.totalRows-1 and \
                    self.board[row][column].has_dir(SOUTH) and \
                    self.board[row+1][column].has_dir(NORTH):
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

    def __init__(self, tiles):
        self.board = tiles.board
        self.totalRows = tiles.getTotalRows()
        self.totalColumns = tiles.getTotalColumns()
        self.t_graph = {}
        self.createVertices()
        self.createEdges()

if __name__ == "__main__":
    import board
    b = board.Board()
    x = TraversalGraph(b)

