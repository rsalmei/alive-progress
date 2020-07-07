# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import os
import sys


def clear_traces():  # pragma: no cover
    # Ansi escape sequence for clearing the entire line: CSI n K -> with n=2.
    sys.__stdout__.write('\033[2K\r')


def hide_cursor():  # pragma: no cover
    # Ansi escape sequence for hiding the cursor: CSI ? 25 l.
    sys.__stdout__.write('\033[?25l')


def show_cursor():  # pragma: no cover
    # Ansi escape sequence for showing the cursor: CSI ? 25 h.
    sys.__stdout__.write('\033[?25h')


def sanitize_text(text):
    return ' '.join(str(text).split())


def terminal_columns():  # pragma: no cover
    """Gets the size of the terminal.

    This should work only on *nix, macOS included.
    Heavily based on console.py in https://stackoverflow.com/a/566752/1296256
    # TODO use shutil on python 3.

    At least this seems extremely fast, so no problem calling it in all refreshes:
    In [3]: %timeit terminal_columns()
    2.39 µs ± 28.7 ns per loop (mean ± std. dev. of 7 runs, 100000 loops each)

    Returns:
        int: number of columns in the current interactive terminal.

    """

    def ioctl_GWINSZ(fd):
        try:
            import fcntl, termios, struct
            return struct.unpack('hh', fcntl.ioctl(fd, termios.TIOCGWINSZ, '1234'))  # noqa
        except:
            pass

    cr = ioctl_GWINSZ(0) or ioctl_GWINSZ(1) or ioctl_GWINSZ(2)
    if not cr:
        try:
            fd = os.open(os.ctermid(), os.O_RDONLY)
            cr = ioctl_GWINSZ(fd)
            os.close(fd)
        except:
            pass
    if not cr:
        cr = None, os.getenv('COLUMNS', 80)
    return int(cr[1])
