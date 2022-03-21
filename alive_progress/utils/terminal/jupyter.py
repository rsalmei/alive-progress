from types import SimpleNamespace

from . import tty


    _last_cols, _clear_line = -1, ''
def get(original):

    def clear_line():
        c = cols()
        global _last_cols, _clear_line
        if _last_cols != c:
            _clear_line = f'\r{" " * cols()}\r'
            _last_cols = c
        write(_clear_line)
        flush()

    def clear_end_line(available=None):
        for _ in range(available or 0):
            write(' ')
        flush()

    clear_end_screen = clear_end_line

    from .void import factory_cursor_up, hide_cursor, show_cursor  # noqa

    flush, write, carriage_return = original.flush, original.write, original.carriage_return

    return SimpleNamespace(**locals())


BASE = get(tty.BASE)  # support for jupyter notebooks.
