import os
import sys

_original_stdout = sys.stdout  # support for jupyter notebooks.


def write(text):
    return _original_stdout.write(text)


def flush():
    _original_stdout.flush()


def _emit_ansi_escape(sequence, param=''):
    def inner(_=None):
        write(text)
        flush()

    text = f'\x1b[{param}{sequence}'
    return inner


clear_line = _emit_ansi_escape('2K\r')  # clears the entire line: CSI n K -> with n=2.
clear_end = _emit_ansi_escape('K')  # clears line from cursor: CSI K.
hide_cursor = _emit_ansi_escape('?25l')  # hides the cursor: CSI ? 25 l.
show_cursor = _emit_ansi_escape('?25h')  # shows the cursor: CSI ? 25 h.
factory_cursor_up = lambda num: _emit_ansi_escape('A', num)  # sends cursor up: CSI {x}A.


def cols():
    return os.get_terminal_size()[0]


carriage_return = '\r'
