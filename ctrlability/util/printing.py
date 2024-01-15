import logging
import pprint


def print_line(length: int = 80, symbol: str = "-"):
    print(symbol * length)


def debug_pprint(data):
    if logging.getLogger().isEnabledFor(logging.DEBUG):
        pprint.pprint(data)
