import pygame
import pygame as pg
from sprites import *
import json

with open('settings.json') as data:
    settings = json.load(data)

FPS = 60
running = True
WIDTH = settings['WIDTH']
HEIGHT = settings['HEIGHT']
collision_list = []
pg.init()
pg.mixer.init()
pg.display.set_caption("My Game")
clock = pg.time.Clock()
all_sprites = pg.sprite.Group()
player = Player()
for card in player.cards:
    all_sprites.add(card)
desk = Desk()
all_sprites.add(desk.cards[0])

holding = 0
# Цикл игры
while running:
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN:
            for i, card in enumerate(player.cards):
                if card.rect.collidepoint(event.pos):
                    card.isClicked = True
                    holding = i
                    break
        elif event.type == pg.MOUSEBUTTONUP:
            happen = False
            try:
                if player.cards[holding].isClicked:
                    for card in desk.cards:
                        flag, collision = player.isCollide(card, player.cards[holding]) # if no cards
                        if flag:
                            happen = True
                            collision_list.append((collision, card))
                for collision, card in collision_list:
                    player.placeCard(holding, collision, card)
                for card in desk.cards:
                    if card.rect.center == player.cards[holding].rect.center:
                        happen = False
                        break
            except CollideError:
                happen = False

            if happen:
                desk.cards.append(player.cards[holding])
                player.cards.pop(holding)
                player.cardsLeft -= 1
            else:
                player.cards[holding].isClicked = False
            holding = 0
            collision_list.clear()
            player.update()

        if event.type == pg.QUIT:
            running = False

    all_sprites.update()
    screen.fill((0, 0, 0))
    all_sprites.draw(screen)
    pg.display.flip()

pg.quit()
