import random
import re

import pygame
import pygame_menu

from enums import Colors, Keys, GameFocus, size_tpl
from game_settings import GameSettings
from utils import add_arrays, detect_oob_exclu, detect_oob_inclu, is_between, threshold_limit

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
                self.main_menu()
            elif self.last_menu_choice == GameFocus.PLAY:
                self.mainloop()
            elif self.last_menu_choice == GameFocus.SETTINGS:
                self.settings_menu()
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

        self.game_tick(False)
        pygame.time.delay(1000)
        # self.wait_for_key(None)

    def wait_for_key(self, key: int = None):
        """
        loop = True
        while loop:
            for event in pygame.event.get():
                if event.type == pygame.KEYDOWN and key in [None, event.key]:
                    if key == [None, event.key]:
                        loop = False

            self.game_tick(False)
        """
        raise NotImplementedError

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

    def mainloop(self):
        print("Calling mainloop...")

        p1 = Player(1, self)
        p2 = AI(2, self)

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

    def main_menu(self):
        print("Calling main menu...")
        cursor = 0
        title = self.TITLE_FONT.render("PONG", True, Colors.WHITE)

        play_text = self.FONT.render("Play", True, Colors.WHITE)
        settings_text = self.FONT.render("Settings", True, Colors.WHITE)
        exit_text = self.FONT.render("Exit", True, Colors.WHITE)

        def format_blit(surface: pygame.Surface, y_pos: float, return_value=None):
            base = (surface,
                    (self.settings.WIN_SIZE.width / 2 - surface.get_width() / 2,
                     self.settings.WIN_SIZE.height * y_pos - surface.get_height() / 2))
            if return_value:
                return base + (return_value,)
            else:
                return base

        blits = [
            format_blit(play_text, .6, GameFocus.PLAY),
            format_blit(settings_text, .7, GameFocus.SETTINGS),
            format_blit(exit_text, .8, GameFocus.EXIT),
        ]

        while True:
            self.window.fill(Colors.BLACK)

            self.window.blit(*format_blit(title, .3))
            for blit in blits:
                self.window.blit(*blit[:-1])

            # draw rect around selection
            pygame.draw.rect(self.window,
                             Colors.WHITE,
                             blits[cursor][0].get_rect().move(*blits[cursor][1]).inflate(15, 5),
                             2)
            pygame.display.flip()

            for event in pygame.event.get():
                if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key in Keys.EXIT):
                    self.last_menu_choice = GameFocus.EXIT
                    return
                elif event.type == pygame.KEYDOWN:
                    if event.key in Keys.UP:
                        cursor -= 1
                    elif event.key in Keys.DOWN:
                        cursor += 1
                    cursor %= len(blits)

                    if event.key in Keys.SELECT:
                        self.last_menu_choice = blits[cursor][-1]
                        return

    def settings_menu(self):
        print("Calling Settings...")
        self.last_menu_choice = GameFocus.MAIN_MENU

        menu = pygame_menu.Menu("Settings",
                                *self.settings.WIN_SIZE,
                                theme=pygame_menu.themes.THEME_DARK,
                                onclose=pygame_menu.events.CLOSE)

        # WIN_SIZE
        menu.add.text_input("Resolution: ",
                            default="x".join(map(str, self.settings.WIN_SIZE)),
                            textinput_id="WIN_SIZE")
        # GAME_SPEED
        menu.add.text_input("FPS: ",
                            default=self.settings.GAME_SPEED,
                            input_type=pygame_menu.locals.INPUT_INT,
                            textinput_id="GAME_SPEED")
        # PADDLE_SPEED
        menu.add.text_input("Paddle Speed: ",
                            default=self.settings.PADDLE_SPEED,
                            input_type=pygame_menu.locals.INPUT_INT,
                            textinput_id="PADDLE_SPEED")
        # PADDLE_SIZE
        menu.add.text_input("Paddle Size: ",
                            default="x".join(map(str, self.settings.PADDLE_SIZE)),
                            textinput_id="PADDLE_SIZE")
        # BALL_RADIUS
        menu.add.text_input("Ball Radius: ",
                            default=self.settings.BALL_RADIUS,
                            input_type=pygame_menu.locals.INPUT_INT,
                            textinput_id="BALL_RADIUS")
        # BALL_BASE_SPEED
        menu.add.text_input("Ball Base Speed: ",
                            default=self.settings.BALL_BASE_SPEED,
                            input_type=pygame_menu.locals.INPUT_INT,
                            textinput_id="BALL_BASE_SPEED")
        # BALL_MAX_SPEED
        menu.add.text_input("Ball Max Speed: ",
                            default=self.settings.BALL_MAX_SPEED,
                            input_type=pygame_menu.locals.INPUT_INT,
                            textinput_id="BALL_MAX_SPEED")
        # BALL_ACCELERATION
        menu.add.text_input("Ball Acceleration: ",
                            default=self.settings.BALL_ACCELERATION,
                            input_type=pygame_menu.locals.INPUT_FLOAT,
                            textinput_id="BALL_ACCELERATION").set_margin(0, 25)

        def save_settings():
            data = menu.get_input_data()
            errors = list()
            for k, v in data.items():
                if isinstance(getattr(self.settings, k), size_tpl):
                    if match := re.match(r"(\d+)x(\d+)", v):
                        setattr(self.settings, k, size_tpl(*map(int, match.groups())))
                    else:
                        errors.append(k)
                else:
                    setattr(self.settings, k, v)
            if errors:
                return

            self.settings.save_config()
            menu.close()

        # Save & close
        menu.add.button("Save & Close", save_settings)
        # Close without saving
        menu.add.button("Close without saving", pygame_menu.events.CLOSE)

        menu.mainloop(self.window)


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
