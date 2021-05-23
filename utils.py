from typing import Iterable


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
