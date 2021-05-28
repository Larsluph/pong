import re
from typing import TYPE_CHECKING

import pygame
import pygame_menu

from enums import Colors, GameFocus, Keys, size_tpl

if TYPE_CHECKING:
    from game import Game


def main_menu(instance: "Game"):
    print("Calling main menu...")
    cursor = 0
    title = instance.TITLE_FONT.render("PONG", True, Colors.WHITE)

    solo_text = instance.FONT.render("Solo", True, Colors.WHITE)
    local_text = instance.FONT.render("Local", True, Colors.WHITE)
    settings_text = instance.FONT.render("Settings", True, Colors.WHITE)
    exit_text = instance.FONT.render("Exit", True, Colors.WHITE)

    def format_blit(surface: pygame.Surface, y_pos: float, return_value=None):
        base = (surface,
                (instance.settings.WIN_SIZE.width / 2 - surface.get_width() / 2,
                 instance.settings.WIN_SIZE.height * y_pos - surface.get_height() / 2))
        if return_value:
            return base + (return_value,)
        else:
            return base

    blits = [
        format_blit(solo_text, .55, GameFocus.PLAY_SOLO),
        format_blit(local_text, .65, GameFocus.PLAY_LOCAL),
        format_blit(settings_text, .75, GameFocus.SETTINGS),
        format_blit(exit_text, .85, GameFocus.EXIT),
    ]

    while True:
        instance.window.fill(Colors.BLACK)

        instance.window.blit(*format_blit(title, .3))
        for blit in blits:
            instance.window.blit(*blit[:-1])

        # draw rect around selection
        pygame.draw.rect(instance.window,
                         Colors.WHITE,
                         blits[cursor][0].get_rect().move(*blits[cursor][1]).inflate(15, 5),
                         2)
        pygame.display.flip()

        for event in pygame.event.get():
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key in Keys.EXIT):
                instance.last_menu_choice = GameFocus.EXIT
                return
            elif event.type == pygame.KEYDOWN:
                if event.key in Keys.UP:
                    cursor -= 1
                elif event.key in Keys.DOWN:
                    cursor += 1
                cursor %= len(blits)

                if event.key in Keys.SELECT:
                    instance.last_menu_choice = blits[cursor][-1]
                    return


def settings_menu(instance):
    print("Calling Settings...")
    instance.last_menu_choice = GameFocus.MAIN_MENU

    menu = pygame_menu.Menu("Settings",
                            *instance.settings.WIN_SIZE,
                            theme=pygame_menu.themes.THEME_DARK,
                            onclose=pygame_menu.events.CLOSE)

    # WIN_SIZE
    menu.add.text_input("Resolution: ",
                        default="x".join(map(str, instance.settings.WIN_SIZE)),
                        textinput_id="WIN_SIZE")
    # GAME_SPEED
    menu.add.text_input("FPS: ",
                        default=instance.settings.GAME_SPEED,
                        input_type=pygame_menu.locals.INPUT_INT,
                        textinput_id="GAME_SPEED")
    # PADDLE_SPEED
    menu.add.text_input("Paddle Speed: ",
                        default=instance.settings.PADDLE_SPEED,
                        input_type=pygame_menu.locals.INPUT_INT,
                        textinput_id="PADDLE_SPEED")
    # PADDLE_SIZE
    menu.add.text_input("Paddle Size: ",
                        default="x".join(map(str, instance.settings.PADDLE_SIZE)),
                        textinput_id="PADDLE_SIZE")
    # BALL_RADIUS
    menu.add.text_input("Ball Radius: ",
                        default=instance.settings.BALL_RADIUS,
                        input_type=pygame_menu.locals.INPUT_INT,
                        textinput_id="BALL_RADIUS")
    # BALL_BASE_SPEED
    menu.add.text_input("Ball Base Speed: ",
                        default=instance.settings.BALL_BASE_SPEED,
                        input_type=pygame_menu.locals.INPUT_INT,
                        textinput_id="BALL_BASE_SPEED")
    # BALL_MAX_SPEED
    menu.add.text_input("Ball Max Speed: ",
                        default=instance.settings.BALL_MAX_SPEED,
                        input_type=pygame_menu.locals.INPUT_INT,
                        textinput_id="BALL_MAX_SPEED")
    # BALL_ACCELERATION
    menu.add.text_input("Ball Acceleration: ",
                        default=instance.settings.BALL_ACCELERATION,
                        input_type=pygame_menu.locals.INPUT_FLOAT,
                        textinput_id="BALL_ACCELERATION").set_margin(0, 25)

    def save_settings():
        data = menu.get_input_data()
        print(data)
        errors = list()
        need_to_reload = False
        for k, v in data.items():
            if k == "WIN_SIZE" and v != "x".join(map(str, instance.settings.WIN_SIZE)):
                need_to_reload = True

            if isinstance(getattr(instance.settings, k), size_tpl):
                if match := re.match(r"(\d+)x(\d+)", v):
                    setattr(instance.settings, k, size_tpl(*map(int, match.groups())))
                else:
                    errors.append(k)
            else:
                if len(v) < 1:
                    errors.append(k)
                else:
                    setattr(instance.settings, k, v)

        if errors:
            return
        elif need_to_reload:
            instance.last_menu_choice = GameFocus.EXIT

        instance.settings.save_config()
        menu.close()

    # Save & close
    menu.add.button("Save & Close", save_settings)
    # Close without saving
    menu.add.button("Close without saving", pygame_menu.events.CLOSE)

    menu.mainloop(instance.window)
