# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import sys

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


if sys.version_info >= (3, 6):
    # 2.7 doesn't mark those chars as Wide (ucd 5.2), so this test fails.
    #   -> but curiously it does work in terminal, since they are encoded with 2 bytes.
    # 3.5 doesn't mark those chars as Wide either (ucd 8.0), so this test also fails.
    #   -> and here it doesn't work in terminal, since they are encoded with 1 byte.
    # more details in https://github.com/rsalmei/alive-progress/issues/19#issuecomment-657120695
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
