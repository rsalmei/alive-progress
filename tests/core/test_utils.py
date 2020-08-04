import pytest

from alive_progress.core.utils import render_title, sanitize_text_marking_wide_chars, ZWJ


@pytest.mark.parametrize('text, expected', [
    ('', ''),
    (None, ''),
    ('\n', ''),
    (' \n ', ''),
    ('\n \n', ''),
    ('asd\n', 'asd'),
    ('\nasd', 'asd'),
    ('asd1\nasd2', 'asd1 asd2'),
    ('\nasd1\n\n\nasd2\n', 'asd1 asd2'),
])
def test_sanitize_text_normal_chars(text, expected):
    result = sanitize_text_marking_wide_chars(text)
    assert result.replace(ZWJ, 'X') == expected


@pytest.mark.parametrize('text, expected', [
    ('😺', 'X😺'),
    ('\n😺', 'X😺'),
    ('😺 \n 😺', 'X😺 X😺'),
    ('\n 😺\n😺', 'X😺 X😺'),
    ('asd😺\n', 'asdX😺'),
    ('😺\nasd', 'X😺 asd'),
    ('asd1\nasd2😺', 'asd1 asd2X😺'),
    ('\nasd1😺\n😺\n\nasd2\n', 'asd1X😺 X😺 asd2'),
])
def test_sanitize_text_wide_chars(text, expected):
    result = sanitize_text_marking_wide_chars(text)
    assert result.replace(ZWJ, 'X') == expected


@pytest.mark.parametrize('text, length, expected', [
    (None, 0, ''),
    ('', 0, ''),
    ('cool bar title', 0, 'cool bar title'),
    ('cool bar title', 1, '…'),
    ('cool bar title', 5, 'cool…'),
    ('cool bar title', 14, 'cool bar title'),
    ('cool bar title', 20, 'cool bar title      '),
])
def test_render_title(text, length, expected):
    assert render_title(text, length) == expected
