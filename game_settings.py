import json
from os.path import exists

from enums import size_tpl
from utils import get_attributes


class GameSettings:
    WIN_SIZE = size_tpl(800, 600)
    GAME_SPEED = 60
    MARGIN_TOP = 8
    MARGIN_BOTTOM = 8
    MARGIN_LEFT = 15
    MARGIN_RIGHT = 15
    PADDLE_SPEED = 10
    PADDLE_SIZE = size_tpl(10, 100)
    BALL_RADIUS = 8
    BALL_BASE_SPEED = 7
    BALL_MAX_SPEED = 18
    BALL_ACCELERATION = .2

    def __init__(self, load_file: bool = True):
        if load_file:
            if not exists("config.json"):
                with open("config.json", 'w') as f:
                    json.dump(dict(), f)

            with open("config.json", 'r') as temp:
                temp_set: dict = json.load(temp)

            for k, v in temp_set.items():
                if attr := getattr(self, k, None):
                    if isinstance(attr, size_tpl):
                        setattr(self, k, size_tpl(*v))
                    else:
                        setattr(self, k, v)

    def save_config(self):
        to_save = dict()
        temp = GameSettings()
        for attr in get_attributes(self):
            if getattr(temp, attr) != (value := getattr(self, attr)):
                to_save[attr] = value
        with open("config.json", 'w') as f:
            json.dump(to_save, f)
