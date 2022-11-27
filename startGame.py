import sys
import uuid
from multiprocessing import Process
from time import sleep

import pygame as pg
import requests
from PyQt5 import uic
from PyQt5.QtWidgets import QWidget, QApplication

from game import Game

layers = pg.sprite.LayeredUpdates()
user_id = str(uuid.UUID(int=uuid.getnode()))
carryOn = True
size = (1200, 700)
screen = pg.display.set_mode(size, pg.RESIZABLE)
screen.fill((102, 102, 153))
pg.display.set_caption("choose game")
clock = pg.time.Clock()
url = 'https://vagacoleso.pythonanywhere.com'
games_list = []
pg.font.init()
f1 = pg.font.Font(None, 40)
all_sprites = pg.sprite.Group()
app = QApplication(sys.argv)


class CreateGame(QWidget):
    def __init__(self):
        super().__init__()
        uic.loadUi("gameCreateDesign.ui", self)
        self.pushButton.clicked.connect(self.game_create)

    def game_create(self):
        name = self.lineEdit.text()
        password = self.lineEdit_2.text()
        players_max = self.spinBox.value()
        create_game(name, password, players_max)
        self.close()


class JoinGame(QWidget):
    def __init__(self, name):
        super().__init__()
        self.name = name
        uic.loadUi("gameJoinDesign.ui", self)
        self.pushButton.clicked.connect(self.game_join)

    def game_join(self):
        password = self.lineEdit.text()
        join_game(self.name, password)
        self.close()


class GameShow(pg.sprite.Sprite):
    def __init__(self, name, players, max_players, number):
        pg.sprite.Sprite.__init__(self)
        self.surf = pg.Surface((size[0], 30))
        self.surf.fill((153, 255, 102))
        self.rect = self.surf.get_rect()
        self.y = number * 35
        self.rect.center = (size[0] // 2, self.y + 15)
        self.name = name
        self.players = players
        self.max_players = players
        self.text = f1.render(f"{name}, игроков сейчас: {players}/{max_players}", True, (255, 153, 51))

    def update(self):
        screen.blit(self.surf, (0, self.y))
        screen.blit(self.text, (0, self.y))


class NewGame(pg.sprite.Sprite):
    def __init__(self, number):
        pg.sprite.Sprite.__init__(self)
        self.surf = pg.Surface((size[0], 30))
        self.surf.fill((153, 255, 102))
        self.y = number * 35
        self.rect = self.surf.get_rect()
        self.rect.center = (size[0] // 2, self.y + 15)
        self.text = f1.render(f"Создать новую игру", True, (255, 153, 51))

    def update(self):
        screen.blit(self.surf, (0, self.y))
        screen.blit(self.text, (0, self.y))


class LeaveGame(pg.sprite.Sprite):
    def __init__(self, number):
        pg.sprite.Sprite.__init__(self)
        self.surf = pg.Surface((size[0], 30))
        self.surf.fill((153, 255, 102))
        self.y = number * 35
        self.rect = self.surf.get_rect()
        self.rect.center = (size[0] // 2, self.y + 15)
        self.text = f1.render(f"Выйти из текущей игры", True, (255, 153, 51))

    def update(self):
        screen.blit(self.surf, (0, self.y))
        screen.blit(self.text, (0, self.y))


class UpdateGame(pg.sprite.Sprite):
    def __init__(self, number):
        pg.sprite.Sprite.__init__(self)
        self.surf = pg.Surface((size[0], 30))
        self.surf.fill((153, 255, 102))
        self.y = number * 35
        self.rect = self.surf.get_rect()
        self.rect.center = (size[0] // 2, self.y + 15)
        self.text = f1.render(f"Обновить список игр", True, (255, 153, 51))

    def update(self):
        screen.blit(self.surf, (0, self.y))
        screen.blit(self.text, (0, self.y))


class StartGame(pg.sprite.Sprite):
    def __init__(self, number):
        pg.sprite.Sprite.__init__(self)
        self.surf = pg.Surface((size[0], 30))
        self.surf.fill((153, 255, 102))
        self.y = number * 35
        self.rect = self.surf.get_rect()
        self.rect.center = (size[0] // 2, self.y + 15)
        self.text = f1.render(f"Начать текущую игру (только для ее создателя)", True, (255, 153, 51))

    def update(self):
        screen.blit(self.surf, (0, self.y))
        screen.blit(self.text, (0, self.y))


def get_games():
    x = requests.get(url + "/games")
    if x:
        global games_list
        games_list.clear()
        all_sprites.empty()
        x = x.json()
        for i, key in enumerate(x.keys()):
            games_list.append(GameShow(key, x[key][0], x[key][1], i))
            all_sprites.add(games_list[-1])
        games_list.append(NewGame(len(x.keys())))
        all_sprites.add(games_list[-1])
        games_list.append(LeaveGame(len(x.keys()) + 1))
        all_sprites.add(games_list[-1])
        games_list.append(UpdateGame(len(x.keys()) + 2))
        all_sprites.add(games_list[-1])
        games_list.append(StartGame(len(x.keys()) + 3))
        all_sprites.add(games_list[-1])
        temp = pg.Surface((size[0], 30))  # топ костыль, ничего не скажешь
        temp.fill((102, 102, 153))
        screen.blit(temp, (0, (len(x.keys()) + 4) * 35))


def create_game(name, password, players_max):
    data = {"name": name, "password": password, "creator": user_id, "players_max": players_max}
    requests.post(url + "/create", json=data)
    join_game(name, password)
    get_games()


def join_game(name, password):
    data = {"game_name": name, "password": password, "user": user_id}
    req = requests.post(url + "/join", json=data)
    if req:
        print(req.text)


def leave_game():
    data = {"user_id": user_id}
    req = requests.post(url + "/leave", json=data)
    if req:
        print(req.text)
    get_games()


def start_game():
    data = {"user_id": user_id}
    req = requests.post(url + "/start", json=data)
    if req:
        print(req.text)


def check_game():
    data = {"user_id": user_id}
    while True:
        req = requests.post(url + "/check", json=data)
        if req and req.text != "Not active":
            print(req.json())
            print(user_id)
            print(req.json()[user_id])
            cards = req.json()[user_id]
            name = req.json()["name"]
            game = Game(cards, name)  # вылет игры при выходе через крестик. try except pygame.error: display Surface quit ?
            # Error Process Process-1:
            game.run()
        sleep(1)


if __name__ == "__main__":
    checking_process = Process(target=check_game)
    checking_process.start()

    get_games()
    while carryOn:
        for event in pg.event.get():
            if event.type == pg.QUIT:
                carryOn = False
            elif event.type == pg.KEYDOWN:
                if event.key == pg.K_r:
                    get_games()

            elif event.type == pg.MOUSEBUTTONDOWN and event.button == 1:
                if games_list:
                    if games_list[-4].rect.collidepoint(event.pos):
                        ex = CreateGame()
                        ex.show()
                        app.exec_()
                    elif games_list[-3].rect.collidepoint(event.pos):
                        leave_game()
                    elif games_list[-2].rect.collidepoint(event.pos):
                        get_games()
                    elif games_list[-1].rect.collidepoint(event.pos):
                        start_game()
                    else:
                        for game in games_list:
                            if game.rect.collidepoint(event.pos):
                                ex = JoinGame(game.name)
                                ex.show()
                                app.exec_()
                                break

        all_sprites.update()
        pg.display.flip()
        clock.tick(60)

    pg.quit()
