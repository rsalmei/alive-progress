import sys
from types import SimpleNamespace

from . import jupyter, non_tty, tty, void

# work around a bug on Windows' command prompt, where ANSI escape codes are disabled by default.
if sys.platform == 'win32':
    import os

    os.system('')


def _create(mod):
    def emit(text):
        mod.write(text)
        mod.flush()

    terminal = SimpleNamespace(
        emit=emit,
        cursor_up_1=mod.factory_cursor_up(1),

        # from mod terminal impl.
        write=mod.write,
        flush=mod.flush,
        cols=mod.cols,
        cr=mod.carriage_return,
        clear_line=mod.clear_line,
        clear_end=mod.clear_end,
        hide_cursor=mod.hide_cursor,
        show_cursor=mod.show_cursor,
        factory_cursor_up=mod.factory_cursor_up,
    )
    return terminal


TTY = _create(tty)
JUPYTER = _create(jupyter)
NON_TTY = _create(non_tty)
VOID = _create(void)
