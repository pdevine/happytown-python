import sys
import pyglet
import random

from tiles import Tile
from tiles import SNAP_SPEED, FLOATINGTILE_LOCATION_X, FLOATINGTILE_LOCATION_Y
from tiles import CLOCKWISE, ANTICLOCKWISE

sys.path.append('..')
import board
import events
import settings
import character
import traverse

from pyglet.window import key

from math import sqrt, sin, cos, atan2, log

TOKEN_IMAGES = []

for i in range(1, 13):
    TOKEN_IMAGES.append(pyglet.image.load('../../data/%d.png' % i))

for img in TOKEN_IMAGES:
    if img:
        img.anchor_x = int(img.width / 2)
        img.anchor_y = int(img.height / 2)

OFFSET_X = 65
OFFSET_Y = 55

BOARD_OFFSET_X = 140
BOARD_OFFSET_Y = 140

ROWS = 9
COLUMNS = 12

class PlayerBox(object):
    def __init__(self, playerNum):
        self.tokenBatch = pyglet.graphics.Batch()
        self.tokens = []

        self.x = 780
        self.y = 560 - playerNum * 110

        #self.addToken(0)
        #self.addToken(1)
        #self.addToken(2)

    def addToken(self, number):
        self.tokens.append(
            Token(number,
                self.x + 70 * len(self.tokens),
                self.y,
                batch=self.tokenBatch))

        self.tokens[-1].setHighlight(False)

    def update(self, dt):
        pass

    def draw(self):
        self.tokenBatch.draw()

class Token(pyglet.sprite.Sprite):
    def __init__(self, number, x, y, column=-1, row=-1, batch=None,
                 highlight=True):
        print "number = %d" % number
        print TOKEN_IMAGES[number]
        self.tokenId = number

        pyglet.sprite.Sprite.__init__(self, TOKEN_IMAGES[number], batch=batch)

        self.x = x
        self.y = y

        self.column = column
        self.row = row

        self.setHighlight(highlight)

    def setHighlight(self, val):
        if not val:
            self.color = (255, 255, 255)
        else:
            self.color = (255, 170, 170)


class AnimateBoard(object):
    def slideIn(self):
        self.moving = True
        print "start moving"
        count = 0
        for tile in self.tiles:
            tile.x = 1024 + tile.x
            tile.moveSpeed = SNAP_SPEED
            self.movingTiles.append(tile)

    def pourIn(self):
        self.moving = True
        for tile in self.tiles:
            tile.y = 768 + tile.y + (self.rows - tile.row) * 60
            tile.moveSpeed = SNAP_SPEED
            self.movingTiles.append(tile)

    def fallOut(self):
        self.Moving = True
        for tile in self.tiles:
            tile.moveToY = -300
            tile.moveSpeed = SNAP_SPEED
            self.movingTiles.append(tile)

    def snapbackFloatingTile(self):
        self.dragTile = True
        self.floatingTile.moveToX = FLOATINGTILE_LOCATION_X
        self.floatingTile.moveToY = FLOATINGTILE_LOCATION_Y
        self.floatingTile.moveSpeed = SNAP_SPEED
        self.moving = True
        self.movingTiles.append(self.floatingTile)


class Board(AnimateBoard):
    def __init__(self, columns=COLUMNS, rows=ROWS, demo=False,
                 fadeColor=(100, 100, 100)):
        self.tileBatch = pyglet.graphics.Batch()
        self.tokenBatch = pyglet.graphics.Batch()

        self.tiles = []
        self.tokens = []
        self.people = []

        self.playerBoxes = []

        self.dragTile = False

        self.moving = False
        self.movingTiles = []

        self.columns = columns
        self.rows = rows

        self.ourTurn = False

        # make the colour dimmer if we're not running in a real game
        self.started = False
        self.demo = demo
        self.color = (255, 255, 255)
        self.fadeColor = fadeColor

        self.settings = settings.GameSettings()

        # XXX - fix me with something dynamic

        offset_x = OFFSET_X
        if columns == 7:
            offset_x = BOARD_OFFSET_X

        offset_y = OFFSET_Y
        if rows == 7:
            offset_y = BOARD_OFFSET_Y

        for y in range(rows):
            for x in range(columns):
                self.tiles.append(Tile(x * 81 + offset_x,
                                         768 - (y * 81) - offset_y,
                                         x, y,
                                         color=self.color,
                                         tileType=random.randint(1, 3),
                                         tileRotation=random.randint(0, 3),
                                         batch=self.tileBatch))


        self.floatingTile = Tile(-100, -100, -1, -1,
                                 color=self.color,
                                 tileType=random.randint(1, 3),
                                 tileRotation=random.randint(0, 3),
                                 batch=self.tileBatch)

        events.addListener(self)

        pyglet.clock.schedule(self.update)

    def getTile(self, column, row):
        for tile in self.tiles:
            if tile.column == column and tile.row == row:
                return tile

    def boardToSprites(self):
        gameBoard = self.settings.board

        self.rows = gameBoard.rows
        self.columns = gameBoard.columns

        # is this going to gc correctly?
        self.tiles = []
        self.tokens = []

        for y in range(gameBoard.rows):
            for x in range(gameBoard.columns):
                tile = gameBoard.board[y][x]
                self.tiles.append(
                    Tile(x * 81 + BOARD_OFFSET_X,
                         768 - (y * 81) - BOARD_OFFSET_Y,
                         x, y,
                         color=(255, 255, 255),
                         tileType=tile.tileType,
                         tileRotation=tile.tileRotation,
                         batch=self.tileBatch))

                if tile.boardItem and not tile.boardItem.found:
                    self.tokens.append(
                        Token(int(tile.boardItem.itemNumber),
                              self.tiles[-1].x,
                              self.tiles[-1].y,
                              x, y,
                              batch=self.tokenBatch))

        self.floatingTile = \
            Tile(FLOATINGTILE_LOCATION_X,
                 FLOATINGTILE_LOCATION_Y,
                 -1, -1,
                 color=(255, 255, 255),
                 tileType=gameBoard.floatingTile.tileType,
                 tileRotation=gameBoard.floatingTile.tileRotation,
                 batch=self.tileBatch)

        for player in self.settings.board.players:
            column, row = player.getLocation()
            playerSprite = character.Character(column, row)
            tile = self.getTile(column, row)

            playerSprite.x, playerSprite.y = tile.xy
 
            self.people.append(playerSprite)

            self.playerBoxes.append(PlayerBox(player.playerNumber))

            for item in player.boardItems:
                self.playerBoxes[-1].addToken(item.itemNumber)
                pass


    # XXX - remove this later
    def placePeople(self):
        positions = [(0, 0), (self.columns-1, self.rows-1),
                     (0, self.rows-1), (self.columns-1, 0)]

        for count, person in enumerate(self.people):
            pos = positions[count]
            for tile in self.tiles:
                if tile.row == pos[1] and tile.column == pos[0]:
                    person.x = tile.x
                    person.y = tile.y

    def on_mousePress(self, args):
        print "!!! button pressed"
        x, y, button, modifiers = args
        #self.checkTileClicked(x, y)
        if self.ourTurn:
            self.pickupFloatingTile(x, y)

    def on_mouseRelease(self, args):
        print "!!! button released"
        x, y, button, modifiers = args
        if self.ourTurn:
            self.checkTileClicked(x, y)
            if self.dragTile:
                self.dropFloatingTile(x, y)

    def on_mouseDrag(self, args):
        x, y, dx, dy, buttons, modifiers = args
        if self.dragTile:
            self.dragFloatingTile(x, y)

    def on_keyPress(self, args):
        print "!!! key pressed"
        symbol, modifiers = args
        if symbol == key.RIGHT:
            self.settings.client.send('/rotate clockwise')
        elif symbol == key.LEFT:
            self.settings.client.send('/rotate counterclockwise')
        elif symbol == key.SPACE:
            if self.ourTurn:
                self.ourTurn = False
                self.settings.client.send('/end')

    def on_tileRotated(self, args):
        print "!!! tile rotated"
        print args

        self.floatingTile.rotate(int(args[0]))

    def on_playerSetup(self, args):
        print "!!! player setup"
        print args

    def on_turnChanged(self, args):
        print "!!! player turn changed"
        print args

        self.settings.board.playerTurn = int(args[1])

        print "player turn = %d" % self.settings.board.playerTurn


    def on_playerTookObject(self, args):
        print "!!! player took object"
        print args
        playerNum = self.settings.board.playerTurn - 1

        player = self.people[playerNum]

        for token in self.tokens:
            if token.column == player.column and \
               token.row == player.row:
                tokenId = token.tokenId
                for player in self.playerBoxes:
                    for playerToken in player.tokens:
                        if playerToken.tokenId == tokenId:
                            playerToken.setHighlight(True)
                self.tokens.remove(token)
                break

    def on_boardData(self, args):
        boardData = args[0]
        print "!!! board data = %s" % args[0]

        self.settings.board.deserialize(boardData)
        if not self.started:
            self.boardToSprites()
            self.started = True

        print "player turn = %d" % self.settings.board.playerTurn

    def on_startGame(self, args):
        print "!!! start game"
        self.demo = False
        #self.fallOut()

        #self.settings.fallingTiles = True

    def on_tilePushed(self, args):
        nick, pos, direction = args
        self.moveTiles(int(pos), int(direction))
        self.settings.client.send('/data')

    def on_playerTurn(self, args):
        print "!!! your turn"
        self.ourTurn = True
        self.tilePushed = False

    def on_playerMoved(self, args):
        nick, column, row = args
        print "!!! player moved"
        print args
        column = int(column)
        row = int(row)

        traverseGraph = traverse.TraversalGraph(self.settings.board)

        playerNum = self.settings.board.playerTurn - 1
        startLocation = self.settings.board.players[playerNum].location

        print [x.location for x in self.settings.board.players]

        print "start: " + str(startLocation)
        print "end: (%d, %d)" % (column, row)

        movePath = traverseGraph.findPath(startLocation, (column, row))
        print movePath

        self.people[playerNum].column = column
        self.people[playerNum].row = row

        self.movePlayer(playerNum, self.pathToCoords(movePath))

    def on_endTurn(self, args):
        # get the new board layout
        self.settings.client.send('/data')

    def checkTileAtPoint(self, tile, x, y):
        if x >= tile.x - tile.width / 2 and \
           x <= tile.x + tile.width / 2 and \
           y >= tile.y - tile.height / 2 and \
           y <= tile.y + tile.height / 2:
            return True
        return False

    def pathToCoords(self, movePath):
        moveCoords = []
        for column, row in movePath:
            tile = self.getTile(column, row)
            moveCoords.append((tile.x, tile.y))

        return moveCoords

    def checkTileClicked(self, x, y):
        for tile in self.tiles:
            if self.checkTileAtPoint(tile, x, y):
                print "Clicked on %d, %d" % (tile.column, tile.row)

                traverseGraph = traverse.TraversalGraph(self.settings.board)
                playerNum = self.settings.board.playerTurn - 1
                startLocation = self.settings.board.players[playerNum].location

                movePath = traverseGraph.findPath(startLocation,
                                          (tile.column, tile.row))
                if movePath:
                    # XXX - remove
                    #self.movePlayer(0, self.pathToCoords(movePath))
                    self.settings.client.send('/move %d %d' % (tile.column,
                                                               tile.row))
                    print "Found path!"

    def movePlayer(self, playerNum, moveSegments):
        player = self.people[playerNum]
        self.people[playerNum].walk(moveSegments)

    def pickupFloatingTile(self, x, y):
        if not self.ourTurn:
            return

        if self.tilePushed:
            return

        if self.checkTileAtPoint(self.floatingTile, x, y):
            self.dragTile = True

    def dropFloatingTile(self, x, y):
        for tile in self.tiles:
            if tile.column == 0:
                if tile.row > 0 and tile.row < self.rows - 1:
                    if self.checkTileAtPoint(tile, x + 81, y):
                        self.settings.client.send('/pushrow %d %d' %
                                                  (tile.row, board.EAST))
                        self.dragTile = False 
                        return
            elif tile.column == self.columns - 1:
                if tile.row > 0 and tile.row < self.rows - 1:
                    if self.checkTileAtPoint(tile, x - 81, y):
                        self.settings.client.send('/pushrow %d %d' %
                                                  (tile.row, board.WEST))
                        self.dragTile = False 
                        return
            elif tile.row == 0:
                if tile.column > 0 and tile.column < self.columns - 1:
                    if self.checkTileAtPoint(tile, x, y - 81):
                        self.settings.client.send('/pushcolumn %d %d' %
                                                  (tile.column, board.SOUTH))
                        self.dragTile = False 
                        return
            elif tile.row == self.rows - 1:
                if tile.column > 0 and tile.column < self.columns - 1:
                    if self.checkTileAtPoint(tile, x, y + 81):
                        self.settings.client.send('/pushcolumn %d %d' %
                                                  (tile.column, board.NORTH))
                        self.dragTile = False 
                        return

        self.snapbackFloatingTile()


    def dragFloatingTile(self, x, y):
        if self.dragTile:
            self.floatingTile.x = x
            self.floatingTile.y = y

    def rotateTiles(self, direction=CLOCKWISE):
        for tile in self.tiles:
            #pyglet.clock.schedule(tile.update)
            tile.rotate(direction)

    def moveTiles(self, pos, direction):
        assert direction in [board.NORTH, board.EAST, board.SOUTH, board.WEST]
        assert self.moving == False

        self.moving = True
        self.movingTiles = []
        self.tilePushed = True

        if direction in [board.EAST, board.WEST]:
            for tile in self.tiles:
                if tile.row != pos:
                    continue
                self.movingTiles.append(tile)

            # this is important for getting the floating tile correct
            self.movingTiles.sort(lambda x, y: cmp(x.column, y.column))

            if direction == board.EAST:
                tile = self.movingTiles[0]
                self.floatingTile.x = tile.x - 81
                self.floatingTile.y = tile.y
                self.floatingTile.moveToY = tile.y
                self.floatingTile.moveToX = tile.x
                self.floatingTile.row = pos
                self.floatingTile.column = -1

                self.movingTiles.insert(0, self.floatingTile)
                self.tiles.append(self.floatingTile)

                self.floatingTile = self.movingTiles[-1]
                self.tiles.remove(self.floatingTile)

                for item in self.movingTiles + self.people + self.tokens:
                    if item.row == pos:
                        item.column += 1
                        if hasattr(item, 'moveToX'):
                            item.moveToX = item.x + 81

            elif direction == board.WEST:
                tile = self.movingTiles[-1]
                self.floatingTile.x = tile.x + 81
                self.floatingTile.y = tile.y
                self.floatingTile.moveToX = tile.x
                self.floatingTile.moveToY = tile.y
                self.floatingTile.row = pos
                self.floatingTile.column = self.columns

                self.movingTiles.append(self.floatingTile)
                self.tiles.append(self.floatingTile)

                self.floatingTile = self.movingTiles[0]
                self.tiles.remove(self.floatingTile)

                for item in self.movingTiles + self.people + self.tokens:
                    if item.row == pos:
                        item.column -= 1
                        if hasattr(item, 'moveToX'):
                            item.moveToX = item.x - 81

        elif direction in [board.NORTH, board.SOUTH]:
            for tile in self.tiles:
                if tile.column != pos:
                    continue
                self.movingTiles.append(tile)

            self.movingTiles.sort(lambda x, y: cmp(x.row, y.row))

            if direction == board.NORTH:
                tile = self.movingTiles[-1]
                self.floatingTile.x = tile.x
                self.floatingTile.y = tile.y - 81
                self.floatingTile.moveToX = tile.x
                self.floatingTile.moveToY = tile.y
                self.floatingTile.column = pos
                self.floatingTile.row = self.rows

                self.movingTiles.append(self.floatingTile)
                self.tiles.append(self.floatingTile)

                self.floatingTile = self.movingTiles[0]
                self.tiles.remove(self.floatingTile)

                for item in self.movingTiles + self.people + self.tokens:
                    if item.column == pos:
                        item.row -= 1
                        if hasattr(item, 'moveToY'):
                            item.moveToY = item.y + 81

            elif direction == board.SOUTH:
                tile = self.movingTiles[0]
                self.floatingTile.x = tile.x
                self.floatingTile.y = tile.y + 81
                self.floatingTile.moveToX = tile.x
                self.floatingTile.moveToY = tile.y
                self.floatingTile.column = pos
                self.floatingTile.row = -1

                self.movingTiles.insert(0, self.floatingTile)
                self.tiles.append(self.floatingTile)

                self.floatingTile = self.movingTiles[-1]
                self.tiles.remove(self.floatingTile)

                for item in self.movingTiles + self.people + self.tokens:
                    if item.column == pos:
                        item.row += 1
                        if hasattr(item, 'moveToY'):
                            item.moveToY = item.y - 81

    def setItemOnTile(self, item):
        if item.row == -1:
            item.row = self.rows - 1
        elif item.row == self.rows:
            item.row = 0
        elif item.column == -1:
            item.column = self.columns - 1
        elif item.column == self.columns:
            item.column = 0
        else:
            pass

        tile = self.getTile(item.column, item.row)
        item.x = tile.x
        item.y = tile.y

    def update(self, dt):
        #if not self.movingTiles and self.color != self.fadeColor:
        #    colors = []
        #    for count, val in enumerate(self.color):
        #        if val > self.fadeColor[count]:
        #            colors.append(
        #                max(self.fadeColor[count], int(val - 10 * dt)))
        #        else:
        #            colors.append(self.fadeColor[count])
        #    self.color = tuple(colors)
        #
        #    for tile in self.tiles:
        #        tile.color = self.color
        #
        #    self.floatingTile.color = self.color

        if self.moving:
            for tile in self.movingTiles:
                opp = tile.moveToX - tile.x
                adj = tile.moveToY - tile.y

                rad = atan2(opp, adj)

                tile.velocityX = tile.moveSpeed * dt * sin(rad)
                tile.velocityY = tile.moveSpeed * dt * cos(rad)

                distance = sqrt(pow(tile.moveToX - tile.x, 2) + \
                                pow(tile.moveToY - tile.y, 2))

                if distance < 1:
                    if tile == self.floatingTile:
                        if self.dragTile:
                            self.dragTile = False
                        else:
                            tile.falling = True
                            print "ft: c=%d r=%d" % (tile.column, tile.row)
                            for item in self.tokens + self.people:
                                print "c=%d r=%d" % (item.column, item.row)
                                if item.row == tile.row and \
                                   item.column == tile.column:
                                    self.setItemOnTile(item)
                    tile.reset()
                    self.movingTiles.remove(tile)
                    continue
                elif distance < 100:
                    braking = log(distance+10, 10) - 1
                    tile.velocityX *= braking
                    tile.velocityY *= braking

                tile.x += tile.velocityX
                tile.y += tile.velocityY

                for item in self.people + self.tokens:
                    if tile.row == item.row and \
                       tile.column == item.column:
                        item.x = tile.x
                        item.y = tile.y

        # make the floating tile fall
        if self.floatingTile.falling:
            self.floatingTile.scale -= dt
            if self.floatingTile.scale <= 0:
                self.floatingTile.resetFloatingTile()

        if not self.movingTiles:
            self.moving = False

        if self.demo and not self.movingTiles and self.color == self.fadeColor:
            self.moving = False
            direction = random.choice([board.NORTH,
                                       board.EAST,
                                       board.SOUTH,
                                       board.WEST])
            if direction in [board.NORTH, board.SOUTH]:
                self.moveTiles(random.randint(0, self.columns-1), direction)
            else:
                self.moveTiles(random.randint(0, self.rows-1), direction)

    def draw(self):
        self.tileBatch.draw()
        self.tokenBatch.draw()

        for player in self.people:
            player.draw()

        for playerBox in self.playerBoxes:
            playerBox.draw()

        if self.dragTile:
            self.floatingTile.draw()

if __name__ == '__main__':
    from pyglet.window import key

    window = pyglet.window.Window(1024, 768)

    fps_display = pyglet.clock.ClockDisplay()

    b = Board(7, 7)
    #b.pourIn()
    b.floatingTile.x = 800
    b.floatingTile.y = 650
    b.ourTurn = True

    b.settings.board = board.Board()
    b.settings.board.createBoard(2)
    b.people.append(character.Character())
    b.people.append(character.Character())

    b.boardToSprites()

    b.placePeople()

    @window.event
    def on_draw():
        window.clear()
        b.draw()
        fps_display.draw()

    @window.event
    def on_mouse_press(x, y, button, modifiers):
        print "(%d,%d)" % (x, y)
        b.pickupFloatingTile(x, y)

    @window.event
    def on_mouse_release(x, y, button, modifiers):
        b.checkTileClicked(x, y)
        b.dropFloatingTile(x, y)

    @window.event
    def on_mouse_drag(x, y, dx, dy, buttons, modifiers):
        b.dragFloatingTile(x, y)
        pass

    @window.event
    def on_key_release(symbol, modifiers):
        if symbol == key.RIGHT:
            b.rotateTiles(CLOCKWISE)
            print "right"
        elif symbol == key.LEFT:
            b.rotateTiles(ANTICLOCKWISE)
            print "left"
        elif symbol == key.SPACE:
            #b.demo = not b.demo
            b.placePeople()

    @window.event
    def on_key_press(symbol, modifiers):
        pass

    pyglet.app.run()

