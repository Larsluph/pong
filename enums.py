from collections import namedtuple
from enum import IntEnum

import pygame


class Colors:
    BLACK = (0, 0, 0)
    WHITE = (255, 255, 255)


class Keys:
    SELECT = (pygame.K_RETURN, pygame.K_SPACE, pygame.K_KP_ENTER)
    UP = (pygame.K_UP, pygame.K_z)
    DOWN = (pygame.K_DOWN, pygame.K_s)
    LEFT = (pygame.K_LEFT, pygame.K_q)
    RIGHT = (pygame.K_RIGHT, pygame.K_d)
    EXIT = (pygame.K_ESCAPE,)


class GameFocus(IntEnum):
    EXIT = -1
    MAIN_MENU = 1
    PLAY_SOLO = 2  # solo play
    PLAY_LOCAL = 3  # local multiplayer
    PLAY_NET = 4  # networking play
    SETTINGS = 5


size_tpl = namedtuple("Size", ("width", "height"))
