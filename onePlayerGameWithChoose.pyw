import sys
from spritesForChoose import *
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QApplication
app = QApplication(sys.argv)
FPS = 60
running = True
pg.init()
pg.mixer.init()
pg.display.set_caption("My Game")
clock = pg.time.Clock()

collision_list = []

all_sprites = pg.sprite.Group()


class changeSettings(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("changeSettingsDesign.ui", self)
        self.pushButton2.clicked.connect(lambda x: self.change('stones'))
        self.pushButton.clicked.connect(lambda x: self.change('geographic'))

    def change(self, gameType:str):
        change_settings(gameType)
        self.close()


ex = changeSettings()
ex.show()
app.exec_()
from spritesForChoose import cards_keys, cards, curCard
player = Player(cards_keys[0:curCard])

for card in player.cards:
    all_sprites.add(card)

f1 = pg.font.Font(None, 40)
f2 = pg.font.Font(None, 20)

desk = Desk(cards_keys[-1])
all_sprites.add(desk.cards[0])

takeButton = Button(settings["takeCard"])
all_sprites.add(takeButton)
hintButton = Button(settings["helpCard"])
hintButton.rect.center = (100, 250)
all_sprites.add(hintButton)

holding = 0

while running:
    clock.tick(FPS)
    for event in pg.event.get():
        if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
            if hintButton.rect.collidepoint(event.pos):
                command = "img/buttons/helpTable.PNG"
                os.system(command)
            elif takeButton.rect.collidepoint(event.pos):
                if curCard < len(cards_keys):
                    player.cards.append(Card((CARD_SIZE + 5) * 2, CARD_SIZE // 2 + 150, False, cards_keys[curCard]))
                    layers.add(player.cards[-1])
                    player.cardsLeft += 1
                    curCard += 1
                    all_sprites.add(player.cards[-1])
                    continue
            else:
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
                        flag, collision = player.isCollide(card, player.cards[holding])  # if no cards
                        if flag:
                            happen = True
                            collision_list.append((collision, card))
                try:

                    for collision, card in collision_list:
                        print(collision, card.sides)
                        print(player.cards[holding].sides)
                        print(player)
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
            holding = 0
            collision_list.clear()
            player.update()
        elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
            for i, card in enumerate(player.cards):
                if card.rect.collidepoint(event.pos):
                    card.flip()
                    break
        elif (event.type == pg.MOUSEBUTTONDOWN and event.button == 2) or \
                (event.type == pg.KEYDOWN and event.key == pg.K_t):
            for card in all_sprites.sprites():
                if card.rect.collidepoint(pg.mouse.get_pos()) and type(card) != Button:
                    pg.sprite.LayeredUpdates.change_layer(layers, card, 2)
                    card.isInspect = True
                    if card not in desk.cards:
                        card.isClicked = True
                    else:
                        card.saved_centre = card.rect.center
                    break
        elif (event.type == pg.MOUSEBUTTONUP and event.button == 2) or (event.type == pg.KEYUP and event.key == pg.K_t):
            for card in all_sprites.sprites():
                if type(card) != Button and card.isInspect:
                    card.isInspect = False
                    card.isClicked = False
                    card.image = card.source
                    card.rect = card.image.get_rect()
                    if card in desk.cards:
                        card.rect.center = card.saved_centre
                        pg.sprite.LayeredUpdates.change_layer(layers, card, 0)
                    else:
                        card.rect.center = pg.mouse.get_pos()
                        pg.sprite.LayeredUpdates.change_layer(layers, card, 1)
                    card.image = pg.transform.rotate(card.image, card.angle)
        elif event.type == pg.KEYDOWN and event.key == pg.K_RIGHT:
            for card in desk.cards:
                card.rect.x += 100
        elif event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
            for card in desk.cards:
                card.rect.x -= 100
        elif event.type == pg.KEYDOWN and event.key == pg.K_UP:
            for card in desk.cards:
                card.rect.y -= 100
        elif event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
            for card in desk.cards:
                card.rect.y += 100
        elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:

            for i, card in enumerate(player.cards):
                if card.rect.collidepoint(pg.mouse.get_pos()):
                    save = card.rect.center
                    temp = card.rect.x // 100 * 100
                    a = temp + 100 - card.rect.x
                    b = card.rect.x - temp
                    if a < b:
                        card.rect.x = temp + 100
                    else:
                        card.rect.x = temp

                    temp = card.rect.y // 100 * 100
                    a = temp + 100 - card.rect.y
                    b = card.rect.y - temp
                    if a < b:
                        card.rect.y = temp + 100
                    else:
                        card.rect.y = temp
                    flagx = True
                    flagy = True
                    for board_card in desk.cards:
                        if board_card.rect.x == card.rect.x or board_card.rect.x == card.rect.x - 100 or \
                                board_card.rect.x == card.rect.x + 100:
                            flagx = False

                        if board_card.rect.y == card.rect.y or board_card.rect.y == card.rect.y - 100 or \
                                board_card.rect.y == card.rect.y + 100:
                            flagy = False

                    if flagx or flagy:
                        player.cards.pop(i)
                        desk.cards.append(card)
                        break
                    else:
                        card.rect.center = save
                        break
        elif event.type == pg.QUIT:
            running = False

    all_sprites.update()
    screen.fill((0, 0, 0))
    layers.draw(screen)
    text = f1.render(f"????????: {player.score}", True, (255, 153, 51))
    screen.blit(text, (WIDTH - 150, 20))

    text = ["?????? - ?????????????????? ???????????????? ????????????", "?????? - ?????????????? ????????????????", "?????????????????? - ?????????????????????? ???????????????? ???? ????????",
            "???????????? ?? - ?????????????????? ????????????????", "???????????? - ???????????? ?????????? ?????????? ????????????????"]
    for i, text in enumerate(text):
        rend = f2.render(text, True, (255, 255, 255))
        screen.blit(rend, (WIDTH - 300, 80 + i * 20))

    pg.display.flip()

pg.quit()
