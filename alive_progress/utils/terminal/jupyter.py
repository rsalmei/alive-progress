from types import SimpleNamespace

from . import tty


def get(tty):
    _last_cols, _clear_line = -1, ''

    def clear_line():
        c = cols()
        global _last_cols, _clear_line
        if _last_cols != c:
            _clear_line = f'\r{" " * cols()}\r'
            _last_cols = c
        write(_clear_line)
        flush()

    def clear_end(available):
        for _ in range(available):
            write(' ')
        flush()

    from .void import factory_cursor_up, hide_cursor, show_cursor  # noqa

    flush, write = tty.flush, tty.write
    carriage_return, cols = tty.carriage_return, tty.cols

    return SimpleNamespace(**locals())


BASE = get(tty.BASE)  # support for jupyter notebooks.
