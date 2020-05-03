# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from alive_progress.animations.bars import standard_bar_factory, unknown_bar_factory


@pytest.mark.parametrize('percent, end, expected', [
    (0.0, False, '|>.........|'),
    (0.1, False, '|=>........|'),
    (0.5, False, '|=====>....|'),
    (0.55, False, '|=====->...|'),
    (1.0, False, '|==========|'),
    (1.1, False, '|==========x'),
    (0.5, True, '|=====!    |'),
    (0.55, True, '|=====-!   |'),
    (1.0, True, '|==========|'),
    (1.1, True, '|==========x'),
])
def test_standard_bar(percent, end, expected):
    bar_gen = standard_bar_factory(chars='-=', borders='||', background='.', tip='>', errors='!x')
    bar_gen = bar_gen(length=10)
    assert bar_gen(percent=percent, end=end) == expected


@pytest.mark.parametrize('end, expected', [
    (False, '|1234567890|'),
    (True, '|==========|'),
])
def test_unknown_bar(end, expected, spinner_test):
    bar_gen = unknown_bar_factory(spinner_test(('1234567890',)))(length=10)
    assert bar_gen(end=end) == expected
