import os
import sys
from functools import partial

if sys.stdout.isatty():
    def _send(sequence):  # pragma: no cover
        def inner():
            sys.__stdout__.write(sequence)

        return inner


    def terminal_cols():  # pragma: no cover
        return os.get_terminal_size()[0]


    carriage_return = '\r'
else:
    def _send(_sequence):  # pragma: no cover
        def __noop():
            return 0

        return __noop


    def terminal_cols():  # pragma: no cover
        return sys.maxsize  # do not truncate if there's no tty.


    carriage_return = ''


def _send_ansi_escape(sequence, param=''):  # pragma: no cover
    return _send(f'\x1b[{param}{sequence}')


clear_line = _send_ansi_escape('2K\r')  # clears the entire line: CSI n K -> with n=2.
clear_end = _send_ansi_escape('K')  # clears line from cursor: CSI K.
hide_cursor = _send_ansi_escape('?25l')  # hides the cursor: CSI ? 25 l.
show_cursor = _send_ansi_escape('?25h')  # shows the cursor: CSI ? 25 h.
factory_cursor_up = partial(_send_ansi_escape, 'A')  # sends cursor up: CSI {x}A.
cursor_up_1 = factory_cursor_up(1)

# work around a bug on Windows OS command prompt, where ANSI escape codes are disabled by default.
if sys.platform == 'win32':
    os.system('')
