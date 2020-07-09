# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from alive_progress.core.utils import render_title, sanitize_text


@pytest.mark.parametrize('text, expected', [
    ('', ''),
    (None, 'None'),
    ('\n', ''),
    ('asd\n', 'asd'),
    ('\nasd', 'asd'),
    ('asd1\nasd2', 'asd1 asd2'),
    ('\nasd1\n\n\nasd2\n', 'asd1 asd2'),
])
def test_sanitize_text(text, expected):
    assert sanitize_text(text) == expected


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
