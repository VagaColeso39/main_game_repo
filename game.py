import threading
import uuid

import requests

from sprites import *

cur_turn = 0


class ExitError(Exception):
    pass


class Game:
    def __init__(self, cards, name, start_card):
        global screen
        screen = pg.display.set_mode((WIDTH, HEIGHT), pg.RESIZABLE)

        self.FPS = 60
        self.running = True
        self.name = name
        self.x_move = 0
        self.y_move = 0

        pg.init()
        pg.mixer.init()
        pg.display.set_caption("Геомино")
        self.clock = pg.time.Clock()

        self.collision_list = []

        self.all_sprites = pg.sprite.Group()
        self.card_sprites = pg.sprite.Group()

        self.player = Player(cards)

        for card in self.player.cards:
            self.all_sprites.add(card)

        self.f1 = pg.font.Font(None, 40)
        self.f2 = pg.font.Font(None, 20)

        self.desk = Desk(start_card)
        self.all_sprites.add(self.desk.cards[0])

        self.takeButton = Button(settings["takeCard"])
        self.all_sprites.add(self.takeButton)
        self.hintButton = Button(settings["helpCard"])
        self.hintButton.rect.center = (100, 250)
        self.all_sprites.add(self.hintButton)
        self.url = 'https://vagacoleso.pythonanywhere.com'
        self.url = 'http://127.0.0.1:5000'
        self.user_id = str(uuid.UUID(int=uuid.getnode()))
        self.holding = 0

    def check_desk(self):
        data = {"user_id": self.user_id, "command": "get_desk", "name": self.name}
        global cur_turn
        req = requests.post(self.url + "/game", json=data)
        data["command"] = "is_my_turn"
        check = requests.post(self.url + "/game", json=data)
        if req and not check:
            cur_turn = req.json()['turn']

            cards_on_desk = [req.json()['cards'][key] for key in req.json()['cards'].keys()]
            for i, temp in enumerate(
                    cards_on_desk):
                cards_on_desk[i] = Card(temp[0][0] + self.x_move, HEIGHT - temp[0][1] - self.y_move, isplaced=True,
                                        number=str(temp[1]), angle=temp[2], layer=0)
                self.desk.cards = cards_on_desk
            self.card_sprites.empty()
            for card in cards_on_desk:
                self.card_sprites.add(card)
                if not layers.has(card):
                    layers.add(card)
        desk_check = threading.Timer(1, self.check_desk)
        desk_check.start()

    def run(self):
        global curCard
        user_id = str(uuid.UUID(int=uuid.getnode()))
        url = 'https://vagacoleso.pythonanywhere.com'
        url = 'http://127.0.0.1:5000'
        desk_check = threading.Timer(1, self.check_desk)
        desk_check.start()

        while self.running:
            self.clock.tick(self.FPS)
            for event in pg.event.get():
                if event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                    if self.hintButton.rect.collidepoint(event.pos):
                        command = "img\helpTable.PNG"
                        os.system(command)
                    elif self.takeButton.rect.collidepoint(event.pos):
                        data = {"user_id": user_id, "command": "is_my_turn", "name": self.name}
                        check = requests.post(url + "/game", json=data)
                        if check:
                            if check.text == "YES":
                                data["command"] = "get_card"
                                req = requests.post(url + "/game", json=data)
                                if req:
                                    card_key = req.text
                                    if card_key != "NO":
                                        self.player.cards.append(
                                            Card((CARD_SIZE + 5) * 2, CARD_SIZE // 2 + 150, False, card_key))
                                        layers.add(self.player.cards[-1])
                                        self.player.cardsLeft += 1
                                        curCard += 1
                                        self.all_sprites.add(self.player.cards[-1])
                                    else:
                                        print("No cards")
                    else:
                        for i, card in enumerate(self.player.cards):
                            if card.rect.collidepoint(event.pos):
                                card.isClicked = True
                                self.holding = i
                                break
                elif event.type == pg.MOUSEBUTTONUP and event.button == 1:
                    happen = False
                    answer = True
                    try:
                        if self.player.cards[self.holding].isClicked:
                            for card in self.desk.cards:
                                flag, collision = self.player.isCollide(card,
                                                                        self.player.cards[self.holding])  # if no cards
                                if flag:
                                    happen = True
                                    self.collision_list.append((collision, card))
                        try:
                            for collision, card in self.collision_list:
                                self.player.placeCard(self.holding, collision, card)
                        except AnswerError:
                            answer = False
                        for card in self.desk.cards:
                            if card.rect.center == self.player.cards[self.holding].rect.center:
                                happen = False
                                break
                    except CollideError:
                        happen = False

                    if happen and answer:
                        data = {"user_id": user_id, "command": "is_my_turn", "name": self.name}
                        check = requests.post(url + "/game", json=data)
                        if check:
                            if check.text == "YES":
                                data["command"] = "put_card"
                                data['card_id'] = int(self.player.cards[self.holding].card[0][3:5].replace('.', ''))
                                data['angle'] = self.player.cards[self.holding].angle
                                data['rect'] = (self.player.cards[self.holding].rect.x - self.x_move + 50,
                                                self.player.cards[self.holding].rect.y - self.y_move + 50)
                                self.desk.cards.append(self.player.cards[self.holding])
                                pg.sprite.LayeredUpdates.change_layer(layers, self.desk.cards[-1], 0)
                                self.player.cards.pop(self.holding)
                                self.player.cardsLeft -= 1
                                self.player.score += len(self.collision_list) * 100
                                data['score'] = self.player.score
                                requests.post(url + "/game", json=data)

                    elif happen and not answer:
                        data = {"user_id": user_id, "command": "is_my_turn", "name": self.name}
                        check = requests.post(url + "/game", json=data)
                        if check:
                            if check.text == "YES":
                                self.player.score -= len(self.collision_list) * 100
                                self.player.cards[self.holding].rect.center = (
                                    CARD_SIZE + 5, HEIGHT - (CARD_SIZE // 2 + 160))
                                data['command'] = 'change_score'
                                data['score'] = self.player.score

                    else:
                        self.player.cards[self.holding].isClicked = False
                    self.holding = 0
                    self.collision_list.clear()
                    self.player.update()
                elif event.type == pg.MOUSEBUTTONDOWN and event.button == 3:
                    for i, card in enumerate(self.player.cards):
                        if card.rect.collidepoint(event.pos):
                            card.flip()
                            break
                elif (event.type == pg.MOUSEBUTTONDOWN and event.button == 2) or \
                        (event.type == pg.KEYDOWN and event.key == pg.K_t):
                    for card in self.all_sprites.sprites():
                        if card.rect.collidepoint(pg.mouse.get_pos()) and type(card) != Button:
                            pg.sprite.LayeredUpdates.change_layer(layers, card, 2)
                            card.isInspect = True
                            if card not in self.desk.cards:
                                card.isClicked = True
                            else:
                                card.saved_centre = card.rect.center
                            break
                elif (event.type == pg.MOUSEBUTTONUP and event.button == 2) or (
                        event.type == pg.KEYUP and event.key == pg.K_t):
                    for card in self.all_sprites.sprites():
                        if type(card) != Button and card.isInspect:
                            card.isInspect = False
                            card.isClicked = False
                            card.image = card.source
                            card.rect = card.image.get_rect()
                            if card in self.desk.cards:
                                card.rect.center = card.saved_centre
                                pg.sprite.LayeredUpdates.change_layer(layers, card, 0)
                            else:
                                card.rect.center = pg.mouse.get_pos()
                                pg.sprite.LayeredUpdates.change_layer(layers, card, 1)
                            card.image = pg.transform.rotate(card.image, card.angle)
                elif event.type == pg.KEYDOWN and event.key == pg.K_RIGHT:
                    for card in self.desk.cards:
                        card.rect.x += 100
                        self.x_move += 100
                elif event.type == pg.KEYDOWN and event.key == pg.K_LEFT:
                    for card in self.desk.cards:
                        card.rect.x -= 100
                        self.x_move -= 100
                elif event.type == pg.KEYDOWN and event.key == pg.K_UP:
                    for card in self.desk.cards:
                        card.rect.y -= 100
                        self.y_move -= 100
                elif event.type == pg.KEYDOWN and event.key == pg.K_DOWN:
                    for card in self.desk.cards:
                        card.rect.y += 100
                        self.y_move += 100
                elif event.type == pg.KEYDOWN and event.key == pg.K_SPACE:

                    for i, card in enumerate(self.player.cards):
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

                            for board_card in self.desk.cards:
                                if type(board_card) == list:
                                    board_card = Card(board_card[0][0], board_card[0][1], True, str(board_card[1]), 0, board_card[2])
                                if board_card.rect.x == card.rect.x or board_card.rect.x == card.rect.x - 100 or \
                                        board_card.rect.x == card.rect.x + 100:
                                    flagx = False

                                if board_card.rect.y == card.rect.y or board_card.rect.y == card.rect.y - 100 or \
                                        board_card.rect.y == card.rect.y + 100:
                                    flagy = False

                            if flagx or flagy:
                                data = {"user_id": user_id, "command": "is_my_turn", "name": self.name}
                                check = requests.post(url + "/game", json=data)
                                if check:
                                    if check.text == "YES":
                                        data["command"] = "put_card"
                                        for i, card in enumerate(self.player.cards):
                                            if card.rect.collidepoint(pg.mouse.get_pos()):
                                                self.holding = i
                                                break
                                        data['card_id'] = int(
                                            self.player.cards[self.holding].card[0][3:5].replace(".", ""))
                                        data['angle'] = self.player.cards[self.holding].angle
                                        data['rect'] = (self.player.cards[self.holding].rect.x + self.x_move + 50,
                                                        self.player.cards[self.holding].rect.y + self.y_move + 50)
                                        data['score'] = self.player.score
                                        requests.post(url + "/game", json=data)
                                        self.desk.cards.append(self.player.cards[self.holding])
                                        self.player.cards.pop(self.holding)
                                        pg.sprite.LayeredUpdates.change_layer(layers, self.desk.cards[-1], 0)
                                        break
                            else:
                                card.rect.center = save
                                break
                elif event.type == pg.QUIT:
                    raise ExitError

            self.all_sprites.update()

            text = self.f1.render(f"Счет: {self.player.score}", True, (255, 153, 51))

            text2 = ["ЛКМ - установка карточек игрока", "ПКМ - поворот карточки",
                     "Стрелочки - передвинуть карточки на поле",
                     "Кнопка Е - увеличить карточку", "Пробел - начать новую линию карточек"]

            if screen != None:
                screen.fill((0, 0, 0))
                layers.draw(screen)
                screen.blit(text, (WIDTH - 150, 20))
                for i, text in enumerate(text2):
                    rend = self.f2.render(text, True, (255, 255, 255))
                    screen.blit(rend, (WIDTH - 300, 80 + i * 20))
            pg.display.flip()

        pg.quit()
