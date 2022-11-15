import pygame as pg
import json
import os.path

with open('settings.json') as data:
    settings = json.load(data)

CARD_SIZE = settings['CARDSIZE']
WIDTH = settings['WIDTH']
HEIGHT = settings['HEIGHT']
GREEN = (0, 255, 0)
screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)
IMAGE = pg.image.load(os.path.join('img', 'img1.png'))


class CollideError(Exception):
    pass


class AnswerError(Exception):
    pass


class Card(pg.sprite.Sprite):
    def __init__(self, x, y, isplaced, sides):
        pg.sprite.Sprite.__init__(self)
        # self.image = pg.Surface((CARD_SIZE, CARD_SIZE))
        # self.image.fill(GREEN)
        self.image = IMAGE
        self.isClicked = False
        self.rect = self.image.get_rect()
        self.rect.center = (x, HEIGHT - y)
        self.isplaced = isplaced
        self.sides = sides

    def update(self):
        if self.isClicked:
            self.rect.center = pg.mouse.get_pos()

    def flip(self):
        print("faff")
        self.image = pg.transform.rotate(self.image, -90)
        self.sides['LEFT'], self.sides['UP'], self.sides['RIGHT'], self.sides['DOWN'], =\
            self.sides['UP'], self.sides['RIGHT'], self.sides['DOWN'], self.sides['LEFT'],
        print(self.sides)


class Player(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.score = 0
        self.cardsLeft = 10
        self.cards = []
        for i in range(1, 11):
            self.cards.append(
                Card((CARD_SIZE + 10) * i, CARD_SIZE // 2 + 50, False, {'LEFT': 1, 'UP': 2, 'RIGHT': 3, "DOWN": 4}))

    def placeCard(self, holding, collision, card):
        self.cards[holding].isClicked = False
        x, y = self.cards[holding].rect.center
        print(collision, card)

        if True:  # check for right asnwer
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
            self.score += 100
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
        return True, (x, y)


class Desk(pg.sprite.Sprite):
    def __init__(self):
        pg.sprite.Sprite.__init__(self)
        self.cardsLeft = 1
        self.cards = [Card(WIDTH // 2, HEIGHT // 2, True, {'LEFT': 1, 'UP': 2, 'RIGHT': 3, "DOWN": 4})]
