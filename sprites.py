import json
import os.path
import random

import pygame as pg

with open('settings.json') as data:
    settings = json.load(data)

CARD_SIZE = settings['CARDSIZE']
WIDTH = settings['WIDTH']
HEIGHT = settings['HEIGHT']
GREEN = (0, 255, 0)
curCard = 10
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
layers = pg.sprite.LayeredUpdates()
with open(f'{settings["gameType"]}.json') as data:
    cards = json.load(data)

cards_keys = [str(i) for i in range(1, settings['cardsAmount'] + 1)]
random.shuffle(cards_keys)


class CollideError(Exception):
    pass


class AnswerError(Exception):
    pass


class Card(pg.sprite.Sprite):
    def __init__(self, x, y, isplaced, number, layer=1):
        pg.sprite.Sprite.__init__(self)
        self.card = cards[number]
        self.source = pg.image.load(os.path.join(f'img/{settings["gameType"]}', self.card[0]))
        self.inspect = pg.image.load(os.path.join(f'img/{settings["gameType"]}', 'card' + self.card[0][3:]))
        self._layer = layer
        self.image = self.source
        self.isClicked = False
        self.isInspect = False
        self.angle = 0
        self.rect = self.image.get_rect()
        self.rect.center = (x, HEIGHT - y)
        self.isplaced = isplaced
        self.sides = self.card[1:5]
        self.saved_centre = (0, 0)

    def update(self):
        if self.isInspect:
            self.image = self.inspect
            self.rect = self.image.get_rect()
            if self.rect.x + 250 <= WIDTH:
                self.rect.x += 250
            else:
                self.rect.x -= 250

            if self.rect.y + 250 <= HEIGHT:
                self.rect.y += 250
            else:
                self.rect.y -= 250
        if self.isClicked:
            self.rect.center = pg.mouse.get_pos()

    def flip(self):
        self.angle = (self.angle - 90) % 360
        self.image = pg.transform.rotate(self.image, -90)
        self.sides[0], self.sides[1], self.sides[2], self.sides[3] =\
            self.sides[3], self.sides[0], self.sides[1], self.sides[2]


class Player(pg.sprite.Sprite):
    def __init__(self, cards):
        pg.sprite.Sprite.__init__(self)
        self.score = 0
        self.cardsLeft = 8
        self.cards = []
        for i in range(1, 9):
            temp = Card((CARD_SIZE + 5) * i, CARD_SIZE // 2 + 50, False, cards[i-1])
            self.cards.append(temp)
            layers.add(self.cards[-1])

    def placeCard(self, holding, collision, card):
        self.cards[holding].isClicked = False
        x, y = self.cards[holding].rect.center
        card2 = self.cards[holding]
        first = collision[0] == "LEFT" and card.sides[0] == card2.sides[2]
        second = collision[0] == "RIGHT" and card.sides[2] == card2.sides[0]
        third = collision[1] == "UP" and card.sides[1] == card2.sides[3]
        forth = collision[1] == "DOWN" and card.sides[3] == card2.sides[1]
        if first or second or third or forth:  # check for right answer
            if collision[0] == "LEFT":
                x = card.rect.center[0] - CARD_SIZE
            elif collision[0] == "RIGHT":
                x = card.rect.center[0] + CARD_SIZE
            else:
                x = card.rect.center[0]

            if collision[1] == "UP":
                y = card.rect.center[1] - CARD_SIZE
            elif collision[1] == "DOWN":
                y = card.rect.center[1] + CARD_SIZE
            else:
                y = card.rect.center[1]

            self.cards[holding].rect.center = (x, y)
        else:
            raise AnswerError

    def isCollide(self, board_card, player_card):
        a = board_card.rect.center
        b = player_card.rect.center
        x = ''
        y = ''
        if CARD_SIZE + 10 >= b[0] - a[0] > 0:
            x = "RIGHT"
        elif b[0] == a[0]:
            x = "EQUAL"
        elif CARD_SIZE + 10 >= a[0] - b[0] > 0:
            x = "LEFT"
        else:
            return False, ()

        if CARD_SIZE + 10 >= b[1] - a[1] > 0:
            y = "DOWN"
        elif b[1] == a[1]:
            y = "EQUAL"
        elif CARD_SIZE + 10 >= a[1] - b[1] > 0:
            y = "UP"
        else:
            return False, ()

        if y == "EQUAL":
            if x == "EQUAL":
                raise CollideError
        elif x != "EQUAL":
            if abs(a[0] - b[0]) > abs(a[1] - b[1]):
                y = "EQUAL"
            elif abs(a[0] - b[0]) < abs(a[1] - b[1]):
                x = "EQUAL"
            else:
                return False, ()

        if CARD_SIZE * 2 - CARD_SIZE // 2 < abs(a[0] - b[0]) + abs(a[1] - b[1]):
            return False, ()

        return True, (x, y)


class Desk(pg.sprite.Sprite):
    def __init__(self, start_card):
        pg.sprite.Sprite.__init__(self)
        self.cardsLeft = 1
        self.cards = [Card(650, 350, True, start_card, layer=0)]
        layers.add(self.cards[-1])


class Button(pg.sprite.Sprite):
    def __init__(self, path):
        pg.sprite.Sprite.__init__(self)
        IMAGE = pg.image.load(os.path.join('img/buttons', path))
        self.image = IMAGE
        self._layer = 0
        self.rect = self.image.get_rect()
        self.rect.center = (100, 100)
        layers.add(self)
