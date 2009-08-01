import random
import string

import tile

class Card:
    def __init__(self, value):
        self.value = value

class Person:
    def __init__(self, name="Player", cards=[]):
        self.name = name
        self.cards = cards

class GameEngine:
    def createCards(self):
        self.cards = []
        for x in range(M_OBJECTS):
            self.cards.append(Card(x))

    def createPeople(self):
        self.people = []

        for x in range(4):
            name = "Player %d" % (x+1,)
            self.people.append(Person(name=name))

    def __init__(self):
        self.createCards()
        self.createPeople()
    

if __name__ == "__main__":
    pass

