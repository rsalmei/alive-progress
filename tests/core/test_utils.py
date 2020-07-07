# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from alive_progress.core.utils import sanitize_text


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
