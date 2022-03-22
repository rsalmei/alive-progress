import sys
from types import SimpleNamespace

from . import jupyter, non_tty, tty, void

# work around a bug on Windows' command prompt, where ANSI escape codes are disabled by default.
if sys.platform == 'win32':
    import os

    os.system('')


def _create(mod, interactive):
    terminal = SimpleNamespace(
        interactive=interactive,
        cursor_up_1=mod.factory_cursor_up(1),

        # directly from terminal impl.
        write=mod.write,
        flush=mod.flush,
        cols=mod.cols,
        carriage_return=mod.carriage_return,
        clear_line=mod.clear_line,
        clear_end_line=mod.clear_end_line,
        clear_end_screen=mod.clear_end_screen,
        hide_cursor=mod.hide_cursor,
        show_cursor=mod.show_cursor,
        factory_cursor_up=mod.factory_cursor_up,
    )
    return terminal


def _is_notebook():
    """This detection is tricky, because by design there's no way to tell which kind
    of frontend is connected, there may even be more than one with different types!
    Also, there may be other types I'm not aware of...
    So, I've chosen what I thought it was the safest method, with a negative logic:
    if it _isn't_ None or TerminalInteractiveShell, it should be the "jupyter" type.
    The jupyter type does not emit any ANSI Escape Codes.
    """
    if 'IPython' not in sys.modules:
        # if IPython hasn't been imported, there's nothing to check.
        return False

    # noinspection PyPackageRequirements
    from IPython import get_ipython
    class_ = get_ipython().__class__.__name__
    return class_ != 'TerminalInteractiveShell'


FULL = _create(jupyter.BASE if _is_notebook() else tty.BASE, True)
NON_TTY = _create(non_tty.BASE, False)
VOID = _create(void, False)
