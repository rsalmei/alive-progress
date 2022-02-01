import shutil
import sys
from types import SimpleNamespace


def get(original_stdout):
    write = original_stdout.write
    flush = original_stdout.flush

    def cols():
        # more resilient one, although 7x slower than os' one.
        return shutil.get_terminal_size()[0]

    def _ansi_escape_code(sequence, param=''):
        def inner(_available=None):  # because of jupyter.
            write(text)

        text = f'\x1b[{param}{sequence}'
        return inner

    clear_line = _ansi_escape_code('2K\r')  # clears the entire line: CSI n K -> with n=2.
    clear_end = _ansi_escape_code('K')  # clears line from cursor: CSI K.
    hide_cursor = _ansi_escape_code('?25l')  # hides the cursor: CSI ? 25 l.
    show_cursor = _ansi_escape_code('?25h')  # shows the cursor: CSI ? 25 h.
    factory_cursor_up = lambda num: _ansi_escape_code('A', num)  # sends cursor up: CSI {x}A.
    carriage_return = '\r'

    return SimpleNamespace(**locals())


BASE = get(sys.stdout)  # support for jupyter notebooks.
