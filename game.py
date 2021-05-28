import random

import pygame

import menus
from enums import Colors, GameFocus
from game_settings import GameSettings
from utils import add_arrays, detect_oob_exclu, detect_oob_inclu, is_between, threshold_limit, is_key_pressed

pygame.init()


class Game:
    last_menu_choice: GameFocus = GameFocus.MAIN_MENU

    players = list()
    ball_pos = list()
    ball_speed = list()

    def __init__(self):
        self.settings = GameSettings()

        self.FONT = pygame.font.SysFont("Ubuntu", 40)
        self.TITLE_FONT = pygame.font.SysFont("Ubuntu", 85)
        self.window = pygame.display.set_mode(self.settings.WIN_SIZE)

        pygame.display.set_caption("Pong Game")

        while self.last_menu_choice != GameFocus.EXIT:
            if self.last_menu_choice == GameFocus.MAIN_MENU:
                menus.main_menu(self)
            elif self.last_menu_choice == GameFocus.PLAY_SOLO:
                self.mainloop(1)
            elif self.last_menu_choice == GameFocus.PLAY_LOCAL:
                self.mainloop(2)
            elif self.last_menu_choice == GameFocus.PLAY_NET:
                raise NotImplementedError
            elif self.last_menu_choice == GameFocus.SETTINGS:
                menus.settings_menu(self)
            else:
                print("Invalid focus choice!")
                return

    def init_ball(self):
        self.init_ball_pos()
        self.init_ball_speed()

    def init_ball_pos(self):
        self.ball_pos = [
            round(self.settings.WIN_SIZE.width / 2),
            round(self.settings.WIN_SIZE.height / 2)
        ]

    def init_ball_speed(self):
        self.ball_speed = [-self.settings.BALL_BASE_SPEED, 0]

    def reset(self):
        self.init_ball()
        for player in self.players:
            player.init_pos()

        while not is_key_pressed(None):
            self.game_tick(False)

    def draw_game_scene(self):
        # draw players[0] paddle
        pygame.draw.rect(
            self.window,
            Colors.WHITE,
            (
                *self.players[0].pos,
                *self.settings.PADDLE_SIZE
            )
        )

        # draw players[1] paddle
        pygame.draw.rect(
            self.window,
            Colors.WHITE,
            (
                *self.players[1].pos,
                *self.settings.PADDLE_SIZE
            )
        )

        # draw ball
        pygame.draw.circle(
            self.window,
            Colors.WHITE,
            self.ball_pos,
            self.settings.BALL_RADIUS
        )

        # render font Surface
        score = self.FONT.render(
            f"{self.players[0].score} - {self.players[1].score}",
            False,
            Colors.WHITE
        )

        self.window.blit(
            score,
            (
                round(self.settings.WIN_SIZE.width / 2 - score.get_width() / 2),
                self.settings.MARGIN_TOP
            )
        )

    def game_tick(self, update_movs: bool = True):
        self.window.fill(Colors.BLACK)
        if update_movs:
            self.update_ball_movement()
            self.update_player_movement()
        self.draw_game_scene()
        pygame.display.flip()

        pygame.time.delay(round(1 / self.settings.GAME_SPEED * 1000))

    def update_player_movement(self):
        for player in self.players:
            player.update_pos()

    def update_ball_movement(self):
        new_ball_pos = (
            self.ball_pos[0] + self.ball_speed[0],
            self.ball_pos[1] + self.ball_speed[1]
        )

        limit_left = self.settings.BALL_RADIUS
        limit_right = self.settings.WIN_SIZE.width - self.settings.BALL_RADIUS

        limit_top = self.settings.MARGIN_TOP
        limit_bottom = self.settings.WIN_SIZE.height - self.settings.MARGIN_BOTTOM

        # if x_ball OOB
        if oob := detect_oob_exclu(new_ball_pos[0], limit_left, limit_right):
            # SCORE
            if oob > 0:
                # players[0] scored
                self.players[0].score += 1
            else:
                # players[1] scored
                self.players[1].score += 1
            self.reset()

        # if y_ball OOB
        if detect_oob_inclu(new_ball_pos[1], limit_top, limit_bottom):
            self.ball_speed[1] = -self.ball_speed[1]

        # p1 paddle collision
        if is_between(
                self.players[0].pos[0],
                new_ball_pos[0],
                self.players[0].pos[0] + self.settings.PADDLE_SIZE.width + self.settings.BALL_RADIUS
        ) and is_between(
            self.players[0].pos[1] - self.settings.BALL_RADIUS,
            new_ball_pos[1],
            self.players[0].pos[1] + self.settings.PADDLE_SIZE.height + self.settings.BALL_RADIUS
        ):
            self.ball_speed = [
                min(round(abs(self.ball_speed[0]) + self.settings.BALL_ACCELERATION, 1), self.settings.BALL_MAX_SPEED),
                -round((self.players[0].pos[1] + self.settings.PADDLE_SIZE.height / 2 - self.ball_pos[1]) / 15)
            ]
            self.players[0].on_collision_with_ball()

        # p2 paddle collision
        if is_between(
                self.players[1].pos[0] - self.settings.BALL_RADIUS,
                new_ball_pos[0],
                self.players[1].pos[0] + self.settings.PADDLE_SIZE.width
        ) and is_between(
            self.players[1].pos[1] - self.settings.BALL_RADIUS,
            new_ball_pos[1],
            self.players[1].pos[1] + self.settings.PADDLE_SIZE.height + self.settings.BALL_RADIUS
        ):
            self.ball_speed = [
                -min(round(abs(self.ball_speed[0]) + self.settings.BALL_ACCELERATION, 1), self.settings.BALL_MAX_SPEED),
                -round((self.players[1].pos[1] + self.settings.PADDLE_SIZE.height / 2 - self.ball_pos[1]) / 15)
            ]
            self.players[1].on_collision_with_ball()

        add_arrays(self.ball_pos, self.ball_speed)

    def mainloop(self, player_nbr: int):
        print("Calling mainloop...")

        p1 = Player(1, self)
        if player_nbr == 1:
            p2 = AI(2, self)
        else:
            p2 = Player(2, self)

        self.players = [p1, p2]

        self.init_ball()
        for player in self.players:
            player.init_pos()
            self.game_tick(False)

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.last_menu_choice = GameFocus.EXIT
                    return

                elif event.type == pygame.KEYDOWN:
                    if event.key == self.players[0].key_up:
                        self.players[0].mov = -1
                    elif event.key == self.players[0].key_down:
                        self.players[0].mov = 1

                    if event.key == self.players[1].key_up:
                        self.players[1].mov = -1
                    elif event.key == self.players[1].key_down:
                        self.players[1].mov = 1

                elif event.type == pygame.KEYUP:
                    if event.key in [self.players[0].key_up, self.players[0].key_down]:
                        self.players[0].mov = 0
                    elif event.key in [self.players[1].key_up, self.players[1].key_down]:
                        self.players[1].mov = 0

            self.game_tick()


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
        self.offset = random.randint(1, self.settings.PADDLE_SIZE.height)
