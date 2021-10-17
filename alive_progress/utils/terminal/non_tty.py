import sys

from .tty import flush, write  # noqa
from .void import clear_end, clear_line, factory_cursor_up, hide_cursor, show_cursor  # noqa


def cols():
    return sys.maxsize  # do not truncate when there's no tty.


carriage_return = ''
