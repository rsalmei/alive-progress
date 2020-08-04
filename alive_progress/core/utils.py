import sys
import unicodedata
from itertools import chain

ZWJ = '\u200d'  # zero-width joiner (it's the only one that actually worked on my terminal)


def clear_traces():  # pragma: no cover
    # Ansi escape sequence for clearing the entire line: CSI n K -> with n=2.
    sys.__stdout__.write('\033[2K\r')


def hide_cursor():  # pragma: no cover
    # Ansi escape sequence for hiding the cursor: CSI ? 25 l.
    sys.__stdout__.write('\033[?25l')


def show_cursor():  # pragma: no cover
    # Ansi escape sequence for showing the cursor: CSI ? 25 h.
    sys.__stdout__.write('\033[?25h')


def sanitize_text_marking_wide_chars(text):
    text = ' '.join((text or '').split())
    return ''.join(chain.from_iterable(
        (ZWJ, x) if unicodedata.east_asian_width(x) == 'W' else (x,)
        for x in text))


def render_title(title, length):
    if not title:
        return ''
    elif length == 1:
        return '…'

    title = sanitize_text_marking_wide_chars(title)
    if not length:
        return title

    # fixed size left align implementation.
    # there may be more in v2, like other alignments, variable with maximum size, and
    # even scrolling and bouncing.
    data = (length - 1, '…') if len(title) > length else (length, ' ')
    return '{:{}.{}}{}'.format(title, length - 1, *data)[:length]
