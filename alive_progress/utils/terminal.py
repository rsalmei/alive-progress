import sys
from functools import partial


def _send_ansi_escape(*sequence):  # pragma: no cover
    return partial(sys.__stdout__.write, ''.join(f'\x1b[{s}' for s in sequence))


if sys.stdout.isatty():
    clear_traces = _send_ansi_escape('2K\r')  # clears the entire line: CSI n K -> with n=2.
    hide_cursor = _send_ansi_escape('?25l')  # hides the cursor: CSI ? 25 l.
    show_cursor = _send_ansi_escape('?25h')  # shows the cursor: CSI ? 25 h.

    from os import get_terminal_size


    def terminal_cols():
        return get_terminal_size()[0]
else:
    def __noop():
        pass


    clear_traces = hide_cursor = show_cursor = __noop


    def terminal_cols():
        return 10000  # do not truncate if there's no tty.
