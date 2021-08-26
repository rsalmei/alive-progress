import pytest

from alive_progress.utils.cells import to_cells


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
