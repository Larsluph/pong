from typing import Iterable, Union

import pygame


def add_arrays(base: list, *others: Iterable):
    for i, *y in zip(range(len(base)), *others):
        base[i] += sum(y)


def threshold_limit(data: int, lower_bound: int, upper_bound: int):
    return min(upper_bound, max(data, lower_bound))


def detect_oob_exclu(data, lower, upper):
    if data < lower:
        return -1
    elif data > upper:
        return 1
    else:
        return 0


def detect_oob_inclu(data, lower, upper):
    if data <= lower:
        return -1
    elif data >= upper:
        return 1
    else:
        return 0


def is_between(lower, value, upper):
    return lower < value < upper


def get_attributes(obj):
    return (attr for attr in dir(obj) if not attr.startswith("_") and attr[0].isupper())


def is_key_pressed(key: Union[None, int, Iterable] = None) -> bool:
    for event in pygame.event.get():
        if event.type != pygame.KEYDOWN:
            continue
        if (
            (hasattr(key, "__iter__") and event.key in key)
            or (isinstance(key, int) and event.key == key)
            or key is None
        ):
            return True
    return False
