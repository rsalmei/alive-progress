# coding=utf-8
from __future__ import absolute_import, division, print_function, unicode_literals

import pytest

from alive_progress.animations.utils import repeating, sliding_window_factory, spinner_player


@pytest.mark.parametrize('length, natural, text, expected', [
    (0, 0, '', ''),
    (0, 0, 'no length, everything is output', 'no length, everything is output'),
    (10, 0, '', ''),
    (10, 0, 'abc', 'abc'),
    (10, 0, 'more than len', 'more than '),
    (10, 2, '', ''),
    (10, 2, 'abc ', 'abc abc ab'),
    (10, 2, 'more than len', 'more than '),
])
def test_repeating(length, natural, text, expected):
    @repeating(length, natural)
    def func():
        yield text

    assert next(func()) == expected


def test_repeating_empty():
    @repeating(10, 0)
    def func():
        return ()

    with pytest.raises(StopIteration):
        next(func())


@pytest.mark.parametrize('length, content, step, expected_3', [
    (1, 'ab', 1, ('a', 'b', 'a')),
    (1, 'abc', -1, ('a', 'c', 'b')),
])
def test_sliding_window(length, content, step, expected_3):
    ribbon = sliding_window_factory(length, content, step, 0)
    assert tuple(next(ribbon) for _ in range(3)) == expected_3


def test_sliding_window_error():
    with pytest.raises(AssertionError):
        sliding_window_factory(100, 'window that slides', 1, 0)


def spinner_cycle_test():
    # noinspection PyUnusedLocal
    def inner_factory(length=None):
        def inner_spinner():
            for c in '123':  # TODO python 2.7...
                yield c

        return inner_spinner

    return inner_factory


def test_spinner_player():
    player = spinner_player(spinner_cycle_test()())
    assert tuple(next(player) for _ in range(4)) == ('1', '2', '3', '1')
