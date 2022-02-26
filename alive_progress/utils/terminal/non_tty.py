import sys
from types import SimpleNamespace

from . import tty


def get(tty):
    def cols():
        return sys.maxsize  # do not truncate when there's no tty.

    from .void import clear_end, clear_line, factory_cursor_up, hide_cursor, show_cursor  # noqa

    flush, write = tty.flush, tty.write
    carriage_return = ''

    return SimpleNamespace(**locals())


BASE = get(tty.BASE)  # support for jupyter notebooks.
