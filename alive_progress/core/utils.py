# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import sys


def clear_traces():
    # Ansi escape sequence for clearing the entire line: CSI n K -> with n=2.
    sys.__stdout__.write('\033[2K\r')


def hide_cursor():
    # Ansi escape sequence for hiding the cursor: CSI ? 25 l.
    sys.__stdout__.write('\033[?25l')


def show_cursor():
    # Ansi escape sequence for showing the cursor: CSI ? 25 h.
    sys.__stdout__.write('\033[?25h')


def sanitize_text(text):
    return ' '.join(str(text).splitlines())
