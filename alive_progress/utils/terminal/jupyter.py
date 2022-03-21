from types import SimpleNamespace

from . import tty


def get(original):
    def cols():
        # it seems both `jupyter notebook` and `jupyter-lab` do not return cols, only 80 default.
        return 120

    def clear_line():
        write(_clear_line)
        flush()

    def clear_end_line(available=None):
        for _ in range(available or 0):
            write(' ')
        flush()

    clear_end_screen = clear_end_line

    # it seems spaces are appropriately handled to not wrap lines.
    _clear_line = f'\r{" " * cols()}\r'

    from .void import factory_cursor_up, hide_cursor, show_cursor  # noqa

    flush, write, carriage_return = original.flush, original.write, original.carriage_return

    return SimpleNamespace(**locals())


BASE = get(tty.BASE)  # support for jupyter notebooks.
