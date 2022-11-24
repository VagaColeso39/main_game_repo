import uuid
from multiprocessing import Process
import requests
from time import sleep

from sprites import *

cur_turn = 0

class Game:
    def __init__(self, cards, name):
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

        self.player = Player(cards)

        for card in self.player.cards:
            self.all_sprites.add(card)

        self.f1 = pg.font.Font(None, 40)
        self.f2 = pg.font.Font(None, 20)

        self.desk = Desk()
        self.all_sprites.add(self.desk.cards[0])

        self.takeButton = Button(settings["takeCard"])
        self.all_sprites.add(self.takeButton)
        self.hintButton = Button(settings["helpCard"])
        self.hintButton.rect.center = (100, 250)
        self.all_sprites.add(self.hintButton)

        self.holding = 0

    def run(self):
        global curCard
        user_id = str(uuid.UUID(int=uuid.getnode()))
        url = 'https://vagacoleso.pythonanywhere.com'
        url = "http://127.0.0.1:5000"

        def check_desk():
            data = {"user_id": user_id, "command": "get_desk", "name": self.name}
            req = requests.post(url + "/game", json=data)
            if req:
                global cur_turn
                cur_turn = req.json()['turn']
                cards_on_desk = [req.json()['cards'][key] for key in req.json()['cards'].keys()]
                for i, temp in enumerate(cards_on_desk):
                    cards_on_desk[i] = Card(temp[0][0], temp[0][1], isplaced=True, number=temp[1], layer=0)
                temp = set(cards_on_desk) | set(self.desk.cards)
                for card in temp:  # сделать нормально, карты в класс карт добавить, починить сравнение и добавление карт
                    self.desk.cards.append(card)
                    self.all_sprites.add(card)
            sleep(0.5)

        checking_process = Process(target=check_desk())
        checking_process.start()

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

                    if happen and answer:  # я ТУТ, Прописать метод для запроса поля раз в секунду если не мой ход + переписать остаток методов
                        data = {"user_id": user_id, "command": "is_my_turn", "name": self.name}
                        check = requests.post(url + "/game", json=data)
                        if check:
                            if check.text == "YES":
                                data["command"] = "put_card"
                                data['card_id'] = int(self.player.cards[self.holding].card[0][3:5])
                                data['angle'] = self.player.cards[self.holding].angle
                                data['rect'] = (self.player.cards[self.holding].rect.x + self.x_move,
                                                self.player.cards[self.holding].rect.y + self.y_move)
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
                            card.angle = (card.angle + 90) % 360
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
                                        data['card_id'] = int(self.player.cards[self.holding].card[0][3:5])
                                        data['angle'] = self.player.cards[self.holding].angle
                                        data['rect'] = (self.player.cards[self.holding].rect.x + self.x_move,
                                                        self.player.cards[self.holding].rect.y + self.y_move)
                                        data['score'] = self.player.score
                                        requests.post(url + "/game", json=data)
                                        self.player.cards.pop(i)
                                        self.desk.cards.append(card)
                                        pg.sprite.LayeredUpdates.change_layer(layers, self.desk.cards[-1], 0)
                                        break
                            else:
                                card.rect.center = save
                                break
                elif event.type == pg.QUIT:
                    self.running = False

            self.all_sprites.update()
            screen.fill((0, 0, 0))
            layers.draw(screen)
            text = self.f1.render(f"Счет: {self.player.score}", True, (255, 153, 51))
            screen.blit(text, (WIDTH - 150, 20))

            text = ["ЛКМ - установка карточек игрока", "ПКМ - поворот карточки",
                    "Стрелочки - передвинуть карточки на поле",
                    "Кнопка Е - увеличить карточку", "Пробел - начать новую линию карточек"]
            for i, text in enumerate(text):
                rend = self.f2.render(text, True, (255, 255, 255))
                screen.blit(rend, (WIDTH - 300, 80 + i * 20))

            pg.display.flip()

        pg.quit()
