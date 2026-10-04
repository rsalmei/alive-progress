import sys

import pytest

from alive_progress.utils.cells import fix_cells, is_wide, print_cells, to_cells
from alive_progress.utils.terminal import get_term


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
    ('asd1 \r\nasd2', 'asd1  asd2'),
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
    ('\nasd1😺\n😺\n\n\rasd2\r', ' asd1😺X 😺X asd2 '),
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


@pytest.mark.parametrize('text', ['e\u0301', 'a\u0308\u0301', 'α\u0301'])
def test_combining_diacritics_use_base_cell_width(text):
    assert not is_wide(text)
    assert to_cells(text) == (text,)


def test_combining_mark_keeps_wide_cjk_base():
    text = '中\u0301'
    assert is_wide(text)
    assert to_cells(text) == (text, None)


@pytest.mark.parametrize('text', ['e\u093e', 'e\u20dd', '1\u20e3'])
def test_spacing_and_enclosing_marks_keep_existing_wide_behavior(text):
    assert is_wide(text)
    assert to_cells(text) == (text, None)


@pytest.mark.parametrize('text', ['❤️', '1️⃣', '🇨🇳', '👩\u200d💻'])
def test_complex_graphemes_keep_existing_wide_behavior(text):
    assert is_wide(text)
    assert to_cells(text) == (text, None)


def test_combining_cluster_render_and_clip_use_one_cell(capsys):
    term = get_term(force_tty=True)
    text = 'Ae\u0301B'
    assert print_cells((to_cells(text),), 2, term) == 2
    term.flush()
    assert capsys.readouterr().out == '\rAe\u0301'


def test_fix_cells_does_not_pad_a_combining_cluster():
    text = 'e\u0301'
    assert fix_cells(to_cells(text)[:1]) == (text,)


@pytest.mark.parametrize('text', ['e\u093e', 'e\u20dd', '1\u20e3'])
def test_non_mn_cluster_clip_keeps_wide_cell_boundary(text, capsys):
    term = get_term(force_tty=True)
    assert print_cells((to_cells(text),), 1, term) == 1
    term.flush()
    assert capsys.readouterr().out == '\r '


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
    term = get_term(force_tty=True)
    assert print_cells(fragments, cols, term) == ret
    term.flush()
    assert capsys.readouterr().out == expected


def test_print_cells_clear(capsys):
    term = get_term(force_tty=True)
    msg = 'loooong'
    assert print_cells((msg,), 100, term, 8) == len(msg)
    term.flush()
    assert capsys.readouterr().out == f'\r{msg}\x1b[K'
