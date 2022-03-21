import sys
from types import SimpleNamespace

from . import tty


def get(original):
    def cols():
        return sys.maxsize  # do not truncate when there's no tty.

    from .void import clear_end_line, clear_end_screen, clear_line  # noqa
    from .void import factory_cursor_up, hide_cursor, show_cursor  # noqa

    flush, write, carriage_return = original.flush, original.write, ''

    return SimpleNamespace(**locals())


BASE = get(tty.BASE)  # support for jupyter notebooks.
