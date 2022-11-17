import pygame
import pygame as pg
import random
from sprites import *
import json


FPS = 60
running = True
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
takeButton = TakeButton(settings["takeCard"])
all_sprites.add(takeButton)
holding = 0


while running:
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if takeButton.rect.collidepoint(event.pos):
                player.cards.append(Card((CARD_SIZE + 5) * 2, CARD_SIZE // 2 + 150, False, cards_keys[curCard]))
                layers.add(player.cards[-1])
                player.cardsLeft += 1
                curCard += 1
                all_sprites.add(player.cards[-1])
                continue
            for i, card in enumerate(player.cards):
                if card.rect.collidepoint(event.pos):
                    card.isClicked = True
                    holding = i
                    break
        elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
            happen = False
            answer = True
            try:
                if player.cards[holding].isClicked:
                    for card in desk.cards:
                        flag, collision = player.isCollide(card, player.cards[holding]) # if no cards
                        if flag:
                            happen = True
                            collision_list.append((collision, card))
                try:
                    for collision, card in collision_list:
                        player.placeCard(holding, collision, card)
                except AnswerError:
                    answer = False
                for card in desk.cards:
                    if card.rect.center == player.cards[holding].rect.center:
                        happen = False
                        break
            except CollideError:
                happen = False

            if happen and answer:
                desk.cards.append(player.cards[holding])
                pg.sprite.LayeredUpdates.change_layer(layers, desk.cards[-1], 0)
                player.cards.pop(holding)
                player.cardsLeft -= 1
                player.score += len(collision_list) * 100
            elif happen and not answer:
                player.score -= len(collision_list) * 100
                player.cards[holding].rect.center = (CARD_SIZE + 5, HEIGHT - (CARD_SIZE // 2 + 160))
            else:
                player.cards[holding].isClicked = False
            print(player.score)
            holding = 0
            collision_list.clear()
            player.update()
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            for i, card in enumerate(player.cards):
                if card.rect.collidepoint(event.pos):
                    card.flip()
                    break
        if event.type == pg.QUIT:
            running = False

    all_sprites.update()
    screen.fill((0, 0, 0))
    layers.draw(screen)
    pg.display.flip()

pg.quit()
