from random import randint

import pygame

from game import Game
from utils import threshold_limit, detect_oob_exclu


class Player:
    score = 0
    mov = 0
    pos = list()

    def __init__(self, player_id: int, game: Game):
        self.game = game
        self.settings = game.settings
        if player_id == 1:
            self.base_pos = [
                self.settings.MARGIN_LEFT,
                round(self.settings.WIN_SIZE.height / 2 - self.settings.PADDLE_SIZE.height / 2)
            ]

            self.key_up = pygame.K_z
            self.key_down = pygame.K_s
        else:
            self.base_pos = [
                self.settings.WIN_SIZE.width - self.settings.MARGIN_RIGHT - self.settings.PADDLE_SIZE.width,
                round(self.settings.WIN_SIZE.height / 2 - self.settings.PADDLE_SIZE.height / 2)
            ]

            self.key_up = pygame.K_UP
            self.key_down = pygame.K_DOWN

        self.init_pos()

    def init_pos(self):
        self.pos = self.base_pos.copy()

    def update_pos(self):
        pos = self.calc_new_pos(self.mov)
        self.pos[1] = threshold_limit(
            pos,
            self.settings.MARGIN_TOP,
            self.settings.WIN_SIZE.height - self.settings.MARGIN_BOTTOM - self.settings.PADDLE_SIZE.height
        )

    def calc_new_pos(self, mov):
        return self.pos[1] + mov * self.settings.PADDLE_SPEED

    def on_collision_with_ball(self):
        return


class AI(Player):
    offset = 0

    def update_pos(self):
        y_pos = self.pos[1]
        self.mov = detect_oob_exclu(self.game.ball_pos[1], y_pos + self.offset, y_pos + self.offset)
        super().update_pos()

    def on_collision_with_ball(self):
        self.offset = randint(1, self.settings.PADDLE_SIZE.height)
