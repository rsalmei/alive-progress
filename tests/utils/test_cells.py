import sys

import pytest

from alive_progress.utils.cells import to_cells, print_cells
from alive_progress.utils.terminal import tty


@pytest.mark.parametrize('text, expected', [
    ('', ''),
    (None, ''),
    ('a text', 'a text'),
    ('\n', ' '),
    (' \n ', '   '),
    ('\n \n', '   '),
    ('\r', ' '),
    (' \r ', '   '),
    ('\r \n', '   '),
    ('asd\n', 'asd '),
    ('\nasd', ' asd'),
    ('asd1\nasd2', 'asd1 asd2'),
    ('asd1 \nasd2', 'asd1  asd2'),
    ('asd1 \r\nasd2', 'asd1   asd2'),
    ('\nasd1\n \r \nasd2\r', ' asd1     asd2 '),
])
def test_sanitize_text_normal_chars(text, expected, show_marks):
    result = to_cells(text)
    assert show_marks(result) == expected


@pytest.mark.parametrize('text, expected', [
    ('😺', '😺X'),
    ('\n😺', ' 😺X'),
    ('😺 \n 😺', '😺X   😺X'),
    ('\n 😺\n😺', '  😺X 😺X'),
    ('asd😺\n', 'asd😺X '),
    ('😺\nasd', '😺X asd'),
    ('asd1\rasd2😺', 'asd1 asd2😺X'),
    ('\nasd1😺\n😺\n\rasd2\r', ' asd1😺X 😺X  asd2 '),
])
def test_sanitize_text_wide_chars(text, expected, show_marks):
    result = to_cells(text)
    assert show_marks(result) == expected


@pytest.mark.parametrize('text, expected', [
    ('ok', 'ok'),
    ('😺', '😺X'),
    ('😺😺', '😺X😺X'),
    ('😺ok😺', '😺Xok😺X'),
])
def test_sanitize_text_double(text, expected, show_marks):
    result = to_cells(text)
    assert show_marks(result) == expected


@pytest.mark.parametrize('fragments, cols, ret, expected', [
    (('ok', ' ', '1'), 10, 4, '\rok 1'),
    (('ok', ' ', '1'), 4, 4, '\rok 1'),
    (('ok', ' ', '1'), 3, 3, '\rok '),
    (('ok', '1'), 3, 3, '\rok1'),
    (('ok', '1'), 1, 1, '\ro'),
    (('rogerio', '\n', '1'), 3, 1, '\rrog\x1b[K\n1'),
    (('rogerio', '\n', '12345'), 3, 3, '\rrog\x1b[K\n123'),
])
def test_print_cells(fragments, cols, ret, expected, capsys):
    term = tty.get(sys.stdout)
    assert print_cells(fragments, cols, _term=term) == ret
    term.flush()
    assert capsys.readouterr().out == expected


def test_print_cells_clear(capsys):
    term = tty.get(sys.stdout)
    msg = 'loooong'
    assert print_cells((msg,), 100, 8, _term=term) == len(msg)
    term.flush()
    assert capsys.readouterr().out == f'\r{msg}\x1b[K'
